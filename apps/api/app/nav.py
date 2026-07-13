"""Paper-fund NAV engine.

Inception is SIMULATED at 2026-01-02 (user decision): the seeded holdings are
treated as held since that date and NAV history is reconstructed from real
historical closes. From then on, NAV rows are append-only — one row per
trading day, reflecting whatever cash/positions actually exist that day, so
trades made through the app are captured from the next append onward.

All values are paper simulation only.
"""
from datetime import date, datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from packages.research_engine.risk import max_drawdown_pct, realized_vol_pct

from .db import FundRow, NavRow, PositionRow, PriceRow, audit
from .prices import get_history, get_quotes

INCEPTION = "2026-01-02"
BENCHMARK = "SPY"


def _open_positions(s: Session) -> list[PositionRow]:
    return s.query(PositionRow).filter_by(status="OPEN").all()


def _cash(s: Session) -> float:
    return s.query(FundRow).first().cash_usd


def backfill_prices(s: Session, symbols: list[str]) -> int:
    """Fetch and store daily closes since inception for symbols missing
    history. Idempotent: (symbol, date) pairs already stored are skipped."""
    have: dict[str, set[str]] = {}
    for sym, d in s.query(PriceRow.symbol, PriceRow.date).all():
        have.setdefault(sym, set()).add(d)

    today = date.today()

    def needs_fetch(sym: str) -> bool:
        dates = have.get(sym)
        if not dates or len(dates) < 10:
            return True
        # Refetch when stored history has gone stale — otherwise beta/vol/
        # correlations silently degrade as their windows age out.
        return (today - date.fromisoformat(max(dates))).days > 5

    missing = [sym for sym in symbols if needs_fetch(sym)]
    if not missing:
        return 0
    history = get_history(missing, INCEPTION)
    added = 0
    for sym, rows in history.items():
        seen = have.get(sym, set())
        for r in rows:
            if r["date"] not in seen:
                s.add(PriceRow(symbol=sym, date=r["date"], close=r["close"], volume=r["volume"]))
                added += 1
    if added:
        audit(s, "price_backfill", detail_symbols=",".join(missing), rows=added)
        s.commit()
    return added


def price_series(s: Session, symbol: str) -> tuple[list[str], list[float]]:
    rows = (s.query(PriceRow).filter_by(symbol=symbol)
            .order_by(PriceRow.date).all())
    return [r.date for r in rows], [r.close for r in rows]


def rebuild_nav_backfill(s: Session) -> int:
    """One-time reconstruction from inception using current holdings + cash.
    Runs only when nav_history is empty (append-only afterwards)."""
    if s.query(NavRow).first():
        return 0
    positions = _open_positions(s)
    cash = _cash(s)
    # Trading-day spine = benchmark dates.
    dates, _ = price_series(s, BENCHMARK)
    if not dates:
        return 0
    closes: dict[str, dict[str, float]] = {}
    for p in positions:
        d, c = price_series(s, p.symbol)
        closes[p.symbol] = dict(zip(d, c))
    added = 0
    last_known: dict[str, float] = {}
    for day in dates:
        nav = cash
        complete = True
        for p in positions:
            px = closes.get(p.symbol, {}).get(day) or last_known.get(p.symbol)
            if px is None:
                complete = False
                break
            last_known[p.symbol] = px
            nav += p.quantity * px
        if complete:
            s.add(NavRow(date=day, nav=round(nav, 2)))
            added += 1
    if added:
        audit(s, "nav_backfill", rows=added, inception=INCEPTION)
        s.commit()
    return added


def append_today(s: Session) -> None:
    """Upsert today's NAV from live quotes (fallback: last stored close)."""
    today = date.today().isoformat()
    positions = _open_positions(s)
    live = get_quotes([p.symbol for p in positions]) if positions else {}
    nav = _cash(s)
    for p in positions:
        q = live.get(p.symbol)
        if q:
            px = q["last"]
        else:
            _, series = price_series(s, p.symbol)
            if not series:
                return  # no price at all — skip rather than store garbage
            px = series[-1]
        nav += p.quantity * px
    row = s.query(NavRow).filter_by(date=today).first()
    if row:
        row.nav = round(nav, 2)
    else:
        s.add(NavRow(date=today, nav=round(nav, 2)))
    s.commit()


def nav_series(s: Session) -> tuple[list[str], list[float]]:
    rows = s.query(NavRow).order_by(NavRow.date).all()
    return [r.date for r in rows], [r.nav for r in rows]


def nav_metrics(s: Session) -> dict:
    """P&L and risk metrics from the stored NAV series."""
    dates, navs = nav_series(s)
    if len(navs) < 2:
        return {"available": False, "note": "NAV history too short — needs at least 2 trading days"}
    daily = (navs[-1] / navs[-2] - 1) * 100
    weekly = (navs[-1] / navs[-6] - 1) * 100 if len(navs) >= 6 else None
    inception = (navs[-1] / navs[0] - 1) * 100
    return {
        "available": True,
        "asOf": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "inceptionDate": dates[0],
        "inceptionNote": f"Simulated inception {INCEPTION}: seeded holdings backfilled over real historical prices. Paper simulation only.",
        "latestNav": navs[-1],
        "dailyPnlPct": round(daily, 2),
        "weeklyPnlPct": round(weekly, 2) if weekly is not None else None,
        "inceptionPnlPct": round(inception, 2),
        "maxDrawdownPct": max_drawdown_pct(navs),
        "realizedVolPct": realized_vol_pct(navs),
        "points": len(navs),
    }


def startup_refresh(s: Session) -> None:
    """Idempotent daily refresh: backfill prices, reconstruct NAV once,
    append today. Network failures leave existing data untouched."""
    from .db import WatchlistRow  # local import to avoid cycle noise
    symbols = {p.symbol for p in _open_positions(s)}
    symbols |= {w.symbol for w in s.query(WatchlistRow).all()}
    symbols.add(BENCHMARK)
    backfill_prices(s, sorted(symbols))
    rebuild_nav_backfill(s)
    append_today(s)
