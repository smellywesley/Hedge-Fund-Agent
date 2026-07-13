"""Terminal Alpha API — Phase 2 (persistence) + Phase 3 slice (live prices).

Educational research / paper-portfolio simulator. No brokerage execution,
no real-money trading, not financial advice.

- Watchlist / paper fund / journal / audit log persist via SQLAlchemy
  (SQLite default, Postgres via DATABASE_URL) — see app/db.py.
- Live quotes via yfinance with mock fallback — see app/prices.py.
- Research/agents/filings content is still mock; remaining `# CONNECTOR:`
  comments mark the OpenBB / SEC EDGAR / FRED integration points.

New endpoints return camelCase (matches apps/web/lib/types.ts); untouched
Phase 1 mock endpoints keep snake_case until their Phase 3/4 rewrite.
"""
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

# ponytail: path shim instead of packaging the monorepo; replace with proper
# installs if this ever deploys beyond docker-compose.
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from packages.research_engine.risk import beta as risk_beta
from packages.research_engine.risk import correlation_matrix
from packages.research_engine.scoring import compute_confidence, compute_research_score

from . import mock_data as mock
from . import nav
from .db import (
    DATABASE_URL, AuditRow, FundRow, JournalRow, PositionRow, WatchlistRow,
    audit, engine, init_db,
)
from .prices import get_quotes

app = FastAPI(title="Terminal Alpha API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup():
    init_db()
    # Daily NAV/price refresh — network failure must never block boot.
    try:
        with Session(engine) as s:
            nav.startup_refresh(s)
    except Exception:
        pass


def get_session():
    with Session(engine) as s:
        yield s


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ---------------------------------------------------------------- quotes

# (display symbol, name, yfinance symbol, scale applied to last)
INDICES = [("SPY", "S&P 500 ETF", "SPY", 1), ("QQQ", "Nasdaq 100 ETF", "QQQ", 1), ("DIA", "Dow ETF", "DIA", 1), ("IWM", "Russell 2000 ETF", "IWM", 1)]
RATES = [("US5Y", "5Y Treasury", "^FVX", 0.1), ("US10Y", "10Y Treasury", "^TNX", 0.1), ("US30Y", "30Y Treasury", "^TYX", 0.1)]
FX = [("DXY", "Dollar Index", "DX-Y.NYB", 1), ("EURUSD", "EUR/USD", "EURUSD=X", 1), ("USDJPY", "USD/JPY", "JPY=X", 1), ("USDSGD", "USD/SGD", "SGD=X", 1)]
COMMODITIES = [("GC", "Gold", "GC=F", 1), ("CL", "WTI Crude", "CL=F", 1), ("HG", "Copper", "HG=F", 1), ("NG", "Nat Gas", "NG=F", 1)]
VOLATILITY = [("VIX", "VIX", "^VIX", 1), ("MOVE", "MOVE", "^MOVE", 1)]
SECTORS = [("XLK", "Technology"), ("XLF", "Financials"), ("XLE", "Energy"), ("XLV", "Healthcare"), ("XLY", "Cons. Disc."), ("XLI", "Industrials"), ("XLP", "Staples"), ("XLU", "Utilities"), ("XLB", "Materials")]
STRIP = [("SPY", "SPY", 1), ("QQQ", "QQQ", 1), ("VIX", "^VIX", 1), ("10Y", "^TNX", 0.1), ("DXY", "DX-Y.NYB", 1), ("BTC", "BTC-USD", 1), ("GOLD", "GC=F", 1), ("OIL", "CL=F", 1)]

# Mock fallback (display symbol -> last, changePct), from the Phase 1 dataset.
MOCK_QUOTES = {
    "SPY": (612.4, 0.42), "QQQ": (548.1, 0.85), "DIA": (447.2, -0.12), "IWM": (231.55, -0.34),
    "US5Y": (3.95, 0.01), "US10Y": (4.21, 0.03), "US30Y": (4.55, 0.02), "10Y": (4.21, 0.03),
    "DXY": (101.3, -0.15), "EURUSD": (1.112, 0.1), "USDJPY": (148.9, 0.22), "USDSGD": (1.318, -0.05),
    "GC": (2712.0, 0.31), "CL": (71.4, -1.2), "HG": (4.62, 0.55), "NG": (2.84, 1.1),
    "VIX": (14.8, -2.6), "MOVE": (92.1, 0.4), "BTC": (118450.0, 1.9), "GOLD": (2712.0, 0.31), "OIL": (71.4, -1.2),
    "XLK": (0, 1.1), "XLF": (0, 0.2), "XLE": (0, -0.9), "XLV": (0, 0.35), "XLY": (0, 0.6),
    "XLI": (0, -0.15), "XLP": (0, 0.05), "XLU": (0, -0.4), "XLB": (0, 0.25),
    "NVDA": (182.4, 1.85), "AAPL": (236.1, -0.3), "MSFT": (512.75, 0.55),
    "TSM": (224.3, 2.1), "LLY": (792.6, -1.1), "GOOGL": (201.4, 0.71),
}


def _scaled(last: float, scale: float) -> float:
    """Treasury-yield indexes (^TNX family) have quoted both yield×10 and plain
    yield over time — normalize by magnitude instead of trusting the convention."""
    if scale == 0.1:
        return round(last if last < 20 else last / 10, 2)
    return round(last * scale, 2)


def _quote_rows(spec, live):
    """spec: (display, name, yf_sym, scale) → camelCase rows, live else mock."""
    rows = []
    for display, name, yf_sym, scale in spec:
        q = live.get(yf_sym)
        if q:
            rows.append({"symbol": display, "name": name, "last": _scaled(q["last"], scale), "changePct": q["changePct"], "source": "yfinance"})
        else:
            last, chg = MOCK_QUOTES.get(display, (0.0, 0.0))
            rows.append({"symbol": display, "name": name, "last": last, "changePct": chg, "source": "MOCK"})
    return rows


@app.get("/api/health")
def health():
    return {"status": "ok", "db": "sqlite" if DATABASE_URL.startswith("sqlite") else "postgres",
            "prices": "yfinance+mock-fallback", "asOf": _now()}


@app.get("/api/quotes")
def quotes():
    """Ticker-strip quotes."""
    live = get_quotes([yf for _, yf, _ in STRIP])
    rows = []
    for display, yf_sym, scale in STRIP:
        q = live.get(yf_sym)
        if q:
            rows.append({"symbol": display, "last": _scaled(q["last"], scale), "changePct": q["changePct"], "source": "yfinance"})
        else:
            last, chg = MOCK_QUOTES[display]
            rows.append({"symbol": display, "last": last, "changePct": chg, "source": "MOCK"})
    return {"asOf": _now(), "live": bool(live), "items": rows}


@app.get("/api/markets/snapshot")
def markets_snapshot():
    all_syms = [yf for spec in (INDICES, RATES, FX, COMMODITIES, VOLATILITY) for _, _, yf, _ in spec]
    all_syms += [s for s, _ in SECTORS]
    live = get_quotes(all_syms)
    warnings = [] if live else ["Live price fetch failed — showing mock fallback values"]
    sectors = []
    for sym, name in SECTORS:
        q = live.get(sym)
        sectors.append({"symbol": sym, "name": name, "changePct": q["changePct"] if q else MOCK_QUOTES[sym][1]})
    return {
        "asOf": _now(),
        "source": "yfinance" if live else "MOCK",
        "live": bool(live),
        "warnings": warnings,
        "indices": _quote_rows(INDICES, live),
        "rates": _quote_rows(RATES, live),
        "fx": _quote_rows(FX, live),
        "commodities": _quote_rows(COMMODITIES, live),
        "volatility": _quote_rows(VOLATILITY, live),
        "sectors": sectors,
        # Regime + AI brief stay mock until the research engine computes them (Phase 4).
        "regime": mock.MARKET_SNAPSHOT["regime"],
        "aiBrief": {
            "agent": mock.MARKET_SNAPSHOT["ai_brief"]["agent"],
            "asOf": mock.AS_OF,
            "confidence": mock.MARKET_SNAPSHOT["ai_brief"]["confidence"],
            "sources": mock.MARKET_SNAPSHOT["ai_brief"]["sources"],
            "missingData": mock.MARKET_SNAPSHOT["ai_brief"]["missing_data"],
            "bullets": mock.MARKET_SNAPSHOT["ai_brief"]["bullets"],
        },
    }


# ---------------------------------------------------------------- watchlist

SYMBOL_RE = re.compile(r"^[A-Z][A-Z.\-]{0,7}$")

# Research metadata (score/catalyst/filings) is still mock — Phase 3/4 work.
WATCH_META = {w["symbol"]: w for w in mock.WATCHLIST}


def _validate_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not SYMBOL_RE.match(symbol):
        raise HTTPException(422, f"Invalid ticker symbol: {symbol!r}")
    return symbol


class WatchlistAdd(BaseModel):
    symbol: str = Field(min_length=1, max_length=8)


@app.get("/api/watchlist")
def watchlist(s: Session = Depends(get_session)):
    rows = s.query(WatchlistRow).order_by(WatchlistRow.id).all()
    live = get_quotes([r.symbol for r in rows]) if rows else {}
    items = []
    for r in rows:
        meta = WATCH_META.get(r.symbol, {})
        q = live.get(r.symbol)
        mock_last, mock_chg = MOCK_QUOTES.get(r.symbol, (0.0, 0.0))
        items.append({
            "symbol": r.symbol,
            "company": meta.get("company", r.symbol),
            "price": q["last"] if q else mock_last,
            "changePct": q["changePct"] if q else mock_chg,
            "source": "yfinance" if q else "MOCK",
            "volumeVsAvg": meta.get("volume_vs_avg", 0.0),
            "score": meta.get("score", 0),
            "confidence": meta.get("confidence", "Low"),
            "catalyst": meta.get("catalyst", "—"),
            "latestFiling": meta.get("latest_filing", "—"),
            "newsRisk": meta.get("news_risk", "Not covered (mock meta only)"),
            "nextAction": r.next_action,
        })
    return items


@app.post("/api/watchlist", status_code=201)
def watchlist_add(body: WatchlistAdd, s: Session = Depends(get_session)):
    symbol = _validate_symbol(body.symbol)
    if s.query(WatchlistRow).filter_by(symbol=symbol).first():
        raise HTTPException(409, f"{symbol} already on watchlist")
    s.add(WatchlistRow(symbol=symbol))
    audit(s, "watchlist_add", symbol)
    s.commit()
    return {"added": symbol, "persisted": True}


@app.delete("/api/watchlist/{symbol}")
def watchlist_remove(symbol: str, s: Session = Depends(get_session)):
    symbol = _validate_symbol(symbol)
    row = s.query(WatchlistRow).filter_by(symbol=symbol).first()
    if not row:
        raise HTTPException(404, f"{symbol} not on watchlist")
    s.delete(row)
    audit(s, "watchlist_remove", symbol)
    s.commit()
    return {"removed": symbol, "persisted": True}


# ---------------------------------------------------------------- paper fund

SECTOR_BUCKET = {
    "NVDA": "Semiconductors", "TSM": "Semiconductors", "AMD": "Semiconductors", "AVGO": "Semiconductors",
    "MSFT": "Software/Cloud", "GOOGL": "Software/Cloud", "AAPL": "Hardware", "LLY": "Healthcare",
}

DISCLAIMER = "Paper simulation only. No real money, no brokerage connection, not financial advice."


def _fund_state(s: Session):
    """Compute the paper fund from DB positions + live (or mock) prices."""
    cash = s.query(FundRow).first().cash_usd
    rows = s.query(PositionRow).filter_by(status="OPEN").order_by(PositionRow.id).all()
    live = get_quotes([r.symbol for r in rows]) if rows else {}
    positions = []
    for r in rows:
        q = live.get(r.symbol)
        if q:
            current = q["last"]
        else:
            # Same fallback chain NAV uses: last stored close, then static mock.
            _, closes = nav.price_series(s, r.symbol)
            current = closes[-1] if closes else MOCK_QUOTES.get(r.symbol, (r.entry_price, 0))[0]
        positions.append({
            "id": r.id, "symbol": r.symbol,
            "entryPrice": r.entry_price, "currentPrice": round(current, 2),
            "quantity": r.quantity, "value": r.quantity * current,
            "unrealizedPnlPct": round((current - r.entry_price) / r.entry_price * 100, 2),
            "thesis": r.thesis, "invalidationPoint": r.invalidation_point,
            "catalystDate": r.catalyst_date, "riskNotes": r.risk_notes,
            "priceSource": "yfinance" if q else "MOCK",
        })
    aum = cash + sum(p["value"] for p in positions)
    for p in positions:
        p["positionSizePct"] = round(p.pop("value") / aum * 100, 1)
    return cash, positions, aum, bool(live)


def _current_price(s: Session, symbol: str) -> float | None:
    """Live quote, falling back to last stored close."""
    q = get_quotes([symbol]).get(symbol)
    if q:
        return q["last"]
    _, series = nav.price_series(s, symbol)
    return series[-1] if series else None


def _exposure(positions, cash, aum):
    buckets: dict[str, float] = {}
    for p in positions:
        b = SECTOR_BUCKET.get(p["symbol"], "Other")
        buckets[b] = buckets.get(b, 0) + p["positionSizePct"]
    return buckets


@app.get("/api/paper-fund/positions")
def paper_positions(s: Session = Depends(get_session)):
    cash, positions, aum, live = _fund_state(s)
    buckets = _exposure(positions, cash, aum)
    exposure = [{"bucket": b, "pct": round(v, 1)} for b, v in buckets.items()]
    exposure.append({"bucket": "Cash", "pct": round(cash / aum * 100, 1)})
    journal = s.query(JournalRow).order_by(JournalRow.id.desc()).all()
    metrics = nav.nav_metrics(s)
    return {
        "asOf": _now(),
        "source": "yfinance+db" if live else "MOCK+db",
        "live": live,
        "warnings": [] if live else ["Live price fetch failed — P&L uses mock fallback prices"],
        "disclaimer": DISCLAIMER,
        "aum": round(aum),
        "cashPct": round(cash / aum * 100, 1),
        "cashUsd": round(cash),
        "dailyPnlPct": metrics.get("dailyPnlPct"),
        "weeklyPnlPct": metrics.get("weeklyPnlPct"),
        "inceptionPnlPct": metrics.get("inceptionPnlPct"),
        "pnlNote": metrics.get("inceptionNote", metrics.get("note")),
        "positions": positions,
        "journal": [{"id": j.id, "date": j.date, "symbol": j.symbol, "decisionType": j.decision_type,
                     "decisionText": j.decision_text, "humanNote": j.human_note} for j in journal],
        "exposure": exposure,
        "exitRules": mock.PAPER_FUND["exit_rules"],
    }


class PositionAdd(BaseModel):
    symbol: str = Field(min_length=1, max_length=8)
    entryPrice: float = Field(gt=0)
    quantity: float = Field(gt=0)
    thesis: str = ""
    invalidationPoint: str = ""
    catalystDate: str = ""
    riskNotes: str = ""


class PositionPatch(BaseModel):
    thesis: str | None = None
    invalidationPoint: str | None = None
    catalystDate: str | None = None
    riskNotes: str | None = None
    status: str | None = None
    quantity: float | None = Field(default=None, gt=0)


@app.post("/api/paper-fund/positions", status_code=201)
def paper_position_add(body: PositionAdd, s: Session = Depends(get_session)):
    """Paper buy: debits cash at entry price. Rejected if cash is insufficient."""
    symbol = _validate_symbol(body.symbol)
    fund = s.query(FundRow).first()
    cost = body.entryPrice * body.quantity
    if cost > fund.cash_usd:
        raise HTTPException(422, f"Paper cash insufficient: cost ${cost:,.0f} > cash ${fund.cash_usd:,.0f}")
    fund.cash_usd -= cost
    row = PositionRow(
        symbol=symbol, entry_price=body.entryPrice, quantity=body.quantity,
        thesis=body.thesis, invalidation_point=body.invalidationPoint,
        catalyst_date=body.catalystDate, risk_notes=body.riskNotes,
    )
    s.add(row)
    s.add(JournalRow(date=date.today().isoformat(), symbol=symbol, decision_type="ADD",
                     decision_text=f"Paper buy: {body.quantity} @ {body.entryPrice} (cash -${cost:,.0f})",
                     human_note=body.thesis))
    audit(s, "paper_position_add", symbol, entry_price=body.entryPrice,
          quantity=body.quantity, cash_debit=cost)
    s.commit()
    return {"added": symbol, "id": row.id, "persisted": True,
            "cashRemaining": round(fund.cash_usd), "disclaimer": DISCLAIMER}


@app.patch("/api/paper-fund/positions/{position_id}")
def paper_position_patch(position_id: int, body: PositionPatch, s: Session = Depends(get_session)):
    """Paper edits. Closing or resizing settles cash at the current price and
    journals realized paper P&L."""
    row = s.get(PositionRow, position_id)
    if not row:
        raise HTTPException(404, f"No paper position {position_id}")
    fund = s.query(FundRow).first()
    changes = {k: v for k, v in body.model_dump().items() if v is not None}

    if changes.get("status") == "CLOSED" and row.status == "OPEN":
        px = _current_price(s, row.symbol)
        if px is None:
            raise HTTPException(409, f"No price available to settle {row.symbol} — try again with the API online")
        proceeds = px * row.quantity
        realized = (px - row.entry_price) * row.quantity
        fund.cash_usd += proceeds
        s.add(JournalRow(date=date.today().isoformat(), symbol=row.symbol, decision_type="CLOSE",
                         decision_text=f"Paper close: {row.quantity} @ {px} (cash +${proceeds:,.0f}, realized paper P&L ${realized:+,.0f})",
                         human_note=""))
        audit(s, "paper_position_close", row.symbol, price=px, proceeds=proceeds, realized=realized)

    new_qty = changes.get("quantity")
    if new_qty is not None and new_qty != row.quantity and row.status == "OPEN" and changes.get("status") != "CLOSED":
        px = _current_price(s, row.symbol)
        if px is None:
            raise HTTPException(409, f"No price available to settle {row.symbol} resize")
        delta = new_qty - row.quantity  # + = buy more (debit), - = trim (credit)
        cost = delta * px
        if cost > fund.cash_usd:
            raise HTTPException(422, f"Paper cash insufficient for resize: needs ${cost:,.0f}")
        fund.cash_usd -= cost
        s.add(JournalRow(date=date.today().isoformat(), symbol=row.symbol,
                         decision_type="ADD" if delta > 0 else "TRIM",
                         decision_text=f"Paper resize {row.quantity}→{new_qty} @ {px} (cash {'-' if cost > 0 else '+'}${abs(cost):,.0f})",
                         human_note=""))
        audit(s, "paper_position_resize", row.symbol, from_qty=row.quantity, to_qty=new_qty, price=px)

    field_map = {"thesis": "thesis", "invalidationPoint": "invalidation_point",
                 "catalystDate": "catalyst_date", "riskNotes": "risk_notes",
                 "status": "status", "quantity": "quantity"}
    for k, v in changes.items():
        setattr(row, field_map[k], v)
    if changes:
        audit(s, "paper_position_update", row.symbol, **changes)
        s.commit()
    return {"updated": row.id, "changes": changes, "persisted": True,
            "cashRemaining": round(fund.cash_usd)}


class JournalAdd(BaseModel):
    symbol: str = Field(min_length=1, max_length=8)
    decisionType: str = Field(min_length=1, max_length=20)
    decisionText: str = Field(min_length=1)
    humanNote: str = ""


@app.post("/api/paper-fund/journal", status_code=201)
def journal_add(body: JournalAdd, s: Session = Depends(get_session)):
    symbol = _validate_symbol(body.symbol)
    s.add(JournalRow(date=date.today().isoformat(), symbol=symbol,
                     decision_type=body.decisionType.upper(),
                     decision_text=body.decisionText, human_note=body.humanNote))
    audit(s, "journal_add", symbol)
    s.commit()
    return {"added": symbol, "persisted": True}


# ---------------------------------------------------------------- nav

@app.get("/api/paper-fund/nav")
def paper_nav(s: Session = Depends(get_session)):
    dates, navs = nav.nav_series(s)
    return {
        "series": [{"date": d, "nav": n} for d, n in zip(dates, navs)],
        "metrics": nav.nav_metrics(s),
        "disclaimer": DISCLAIMER,
    }


@app.post("/api/paper-fund/refresh")
def paper_refresh(s: Session = Depends(get_session)):
    """Manual price-history + NAV refresh (same as the startup pass)."""
    nav.startup_refresh(s)
    audit(s, "nav_refresh")
    s.commit()
    return {"refreshed": True, "metrics": nav.nav_metrics(s)}


# ---------------------------------------------------------------- risk

def _risk_metrics(s: Session, positions: list[dict]) -> list[dict]:
    """Computed portfolio metrics from NAV + price history."""
    metrics = nav.nav_metrics(s)
    nav_dates, navs = nav.nav_series(s)
    spy_dates, spy = nav.price_series(s, nav.BENCHMARK)
    if not metrics.get("available"):
        note = metrics.get("note", "insufficient history")
        return [{"name": n, "value": "—", "note": note}
                for n in ("Portfolio beta", "Realized volatility", "Max drawdown")]
    # Align by DATE, not position — NAV can have rows (e.g. weekend appends)
    # that the benchmark doesn't, and a 1-day shift makes beta garbage.
    nav_by_date = dict(zip(nav_dates, navs))
    spy_by_date = dict(zip(spy_dates, spy))
    common = sorted(set(nav_by_date) & set(spy_by_date))
    b = risk_beta([nav_by_date[d] for d in common], [spy_by_date[d] for d in common]) if common else None
    vol = metrics.get("realizedVolPct")
    return [
        {"name": "Portfolio beta (60d vs SPY)", "value": f"{b:.2f}" if b is not None else "—",
         "note": "OLS on daily NAV returns vs SPY" if b is not None else "insufficient overlap with SPY history"},
        {"name": "Realized volatility (20d, annualized)", "value": f"{vol:.1f}%" if vol is not None else "—",
         "note": "stdev of daily NAV returns × √252"},
        {"name": "Max drawdown (since inception)", "value": f"{metrics['maxDrawdownPct']:.1f}%",
         "note": f"peak-to-trough of paper NAV since {metrics['inceptionDate']} (simulated inception)"},
    ]


def _correlations(s: Session, positions: list[dict]) -> list[dict]:
    by_symbol: dict[str, dict[str, float]] = {}
    for p in positions:
        dates, closes = nav.price_series(s, p["symbol"])
        if len(closes) >= 11:
            by_symbol[p["symbol"]] = dict(zip(dates, closes))
    if len(by_symbol) < 2:
        return []
    # Date-align all series on their common trading days.
    common = sorted(set.intersection(*(set(d) for d in by_symbol.values())))
    if len(common) < 11:
        return []
    series = {sym: [d[day] for day in common] for sym, d in by_symbol.items()}
    return correlation_matrix(series)


@app.get("/api/paper-fund/risk")
def paper_risk(s: Session = Depends(get_session)):
    cash, positions, aum, live = _fund_state(s)
    buckets = _exposure(positions, cash, aum)

    sector_exposure = [
        {"sector": b, "pct": round(v, 1), "limit": 40, "status": "WARNING" if v > 40 else "OK"}
        for b, v in buckets.items()
    ]
    tech_total = buckets.get("Semiconductors", 0) + buckets.get("Software/Cloud", 0)
    sector_exposure.append({"sector": "Tech total (semis+software)", "pct": round(tech_total, 1),
                            "limit": 40, "status": "WARNING" if tech_total > 40 else "OK"})

    concentration = [
        {"symbol": p["symbol"], "pct": p["positionSizePct"], "limit": 15,
         "status": "WARNING" if p["positionSizePct"] > 15 else "OK"}
        for p in sorted(positions, key=lambda p: -p["positionSizePct"])
    ]

    today = date.today()

    def days_to_catalyst(p):
        try:
            return (date.fromisoformat(p["catalystDate"]) - today).days
        except ValueError:
            return None

    soon = [(p["symbol"], days_to_catalyst(p)) for p in positions]
    within_21 = [(sym, d) for sym, d in soon if d is not None and 0 <= d <= 21]
    within_7 = [sym for sym, d in soon if d is not None and 0 <= d <= 7]

    catalyst_warnings = []
    if len(within_21) >= 2:
        catalyst_warnings.append(
            f"{len(within_21)} of {len(positions)} paper positions have catalysts within 21 days: "
            + ", ".join(f"{sym} ({d}d)" for sym, d in sorted(within_21, key=lambda x: x[1])))
    if tech_total > 40:
        catalyst_warnings.append(
            f"Semis + Software/Cloud = {tech_total:.1f}% of paper AUM — one correlated "
            "AI-infrastructure trade; treat as a single risk cluster.")

    missing_invalidation = [p["symbol"] for p in positions if not p["invalidationPoint"]]
    over_limit = [c["symbol"] for c in concentration if c["status"] == "WARNING"]
    rules = [
        {"rule": "No single paper position above 15%",
         "status": "WARNING: " + ", ".join(over_limit) if over_limit else "PASS"},
        {"rule": "No sector above 40% without warning",
         "status": "WARNING" if any(r["status"] == "WARNING" for r in sector_exposure) else "PASS"},
        {"rule": "Every position has thesis + invalidation point",
         "status": "WARNING: " + ", ".join(missing_invalidation) if missing_invalidation else "PASS"},
        {"rule": "Earnings/catalyst within 7 days triggers review",
         "status": "WARNING: " + ", ".join(within_7) if within_7 else "PASS"},
        {"rule": "Missing data triggers confidence downgrade",
         "status": "PASS" if live else "WARNING: live prices unavailable, mock fallback in use"},
    ]

    return {
        "asOf": _now(),
        "source": "computed from paper positions" + (" + yfinance" if live else " + MOCK prices"),
        "live": live,
        "sectorExposure": sector_exposure,
        "concentration": concentration,
        "metrics": _risk_metrics(s, positions),
        "correlations": _correlations(s, positions),
        "catalystWarnings": catalyst_warnings,
        "rulesChecklist": rules,
    }


# ---------------------------------------------------------------- audit

@app.get("/api/audit/logs")
def audit_logs(limit: int = 50, s: Session = Depends(get_session)):
    rows = s.query(AuditRow).order_by(AuditRow.id.desc()).limit(min(limit, 200)).all()
    return [{"id": r.id, "eventType": r.event_type, "symbol": r.symbol,
             "detail": r.detail, "createdAt": r.created_at} for r in rows]


# ------------------------------------------------- Phase 1 mock endpoints
# (research/agents/filings/news/reports content is replaced in Phases 3–5)

@app.get("/api/tickers/search")
def ticker_search(q: str = ""):
    q = q.upper()
    return [t for sym, t in mock.TICKERS.items() if q in sym or q in t["company_name"].upper()]


def _require_ticker(symbol: str) -> str:
    symbol = symbol.upper()
    if symbol not in mock.TICKERS:
        raise HTTPException(404, f"Unknown mock ticker: {symbol}. Try {', '.join(mock.TICKERS)}")
    return symbol


@app.get("/api/tickers/{symbol}/overview")
def ticker_overview(symbol: str):
    return mock.TICKERS[_require_ticker(symbol)]


@app.get("/api/tickers/{symbol}/financials")
def ticker_financials(symbol: str):
    # CONNECTOR: SEC EDGAR company facts / OpenBB fundamentals
    _require_ticker(symbol)
    return mock.FINANCIALS_NVDA if symbol.upper() == "NVDA" else []


@app.get("/api/tickers/{symbol}/filings")
def ticker_filings(symbol: str):
    # CONNECTOR: SEC EDGAR full-text search + filing index (packages/mcp/sec)
    _require_ticker(symbol)
    return mock.FILINGS.get(symbol.upper(), [])


@app.get("/api/tickers/{symbol}/news")
def ticker_news(symbol: str):
    # CONNECTOR: news provider (FMP/Finnhub) in Phase 3
    _require_ticker(symbol)
    return mock.NEWS.get(symbol.upper(), [])


@app.get("/api/research/{symbol}/latest")
def research_latest(symbol: str):
    symbol = _require_ticker(symbol)
    if symbol != "NVDA":
        raise HTTPException(404, "Phase 1 ships one full mock report: NVDA")
    score = compute_research_score(mock.SCORE_COMPONENTS_NVDA)
    confidence = compute_confidence(**mock.CONFIDENCE_FACTORS_NVDA)
    return {**mock.RESEARCH_NVDA, "score": score, "confidence": confidence}


@app.post("/api/research/{symbol}/run")
def research_run(symbol: str, s: Session = Depends(get_session)):
    symbol = _require_ticker(symbol)
    # Phase 5 kicks off the real multi-agent job here (see §9.2 lifecycle).
    audit(s, "research_run", symbol, status="READY", mode="mock")
    s.commit()
    return {"symbol": symbol, "job_id": "mock-job-1", "status": "READY",
            "note": "Mock run — returns the canned NVDA report instantly."}


@app.get("/api/agents/outputs")
def agent_outputs():
    return [{**a, "symbol": "NVDA", "generated_at": mock.AS_OF, "requires_human_review": True,
             "key_findings": [], "assumptions": []} for a in mock.AGENTS]


@app.get("/api/reports")
def reports():
    return mock.REPORTS
