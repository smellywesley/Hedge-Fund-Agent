"""yfinance live-price provider (Phase 3 slice).

Connector contract (docs/data_sources.md): every quote carries source +
timestamp, responses are cached, failures fall back to mock values with an
explicit warning — never silently.

yfinance is a research/fallback source (trust tier 4). OpenBB/SEC/FRED
connectors remain Phase 3 work in packages/mcp.
"""
import time
from datetime import datetime, timezone

# ponytail: module-level TTL cache; swap for redis if this ever needs to scale.
_TTL_SECONDS = 300
_cache: dict[tuple, tuple[float, dict]] = {}


def get_quotes(symbols: list[str]) -> dict[str, dict]:
    """Return {yf_symbol: {last, change_pct, as_of, source}} for whatever
    yfinance can deliver. Missing/failed symbols are simply absent —
    callers fall back to mock and surface a warning."""
    key = tuple(sorted(symbols))
    now = time.time()
    if key in _cache and now - _cache[key][0] < _TTL_SECONDS:
        return _cache[key][1]

    quotes: dict[str, dict] = {}
    try:
        import pandas as pd
        import yfinance as yf

        df = yf.download(
            list(symbols), period="5d", interval="1d",
            progress=False, auto_adjust=True,
        )["Close"]
        if isinstance(df, pd.Series):  # single symbol comes back as a Series
            df = df.to_frame(name=symbols[0])
        as_of = datetime.now(timezone.utc).isoformat(timespec="seconds")
        for sym in symbols:
            if sym not in df.columns:
                continue
            closes = df[sym].dropna()
            if len(closes) < 2:
                continue
            last, prev = float(closes.iloc[-1]), float(closes.iloc[-2])
            quotes[sym] = {
                "last": round(last, 2),
                "changePct": round((last - prev) / prev * 100, 2),
                "asOf": as_of,
                "source": "yfinance",
            }
    except Exception:
        # Offline / rate-limited / symbol change — callers fall back to mock.
        return {}

    if quotes:
        _cache[key] = (now, quotes)
    return quotes


def get_history(symbols: list[str], start: str) -> dict[str, list[dict]]:
    """Daily closes since `start` (ISO date), one HTTP call for all symbols.
    Returns {symbol: [{date, close, volume}, ...]} oldest→newest; failed
    symbols are absent. Empty dict on total failure — callers must warn."""
    out: dict[str, list[dict]] = {}
    try:
        import yfinance as yf

        df = yf.download(list(symbols), start=start, interval="1d",
                         progress=False, auto_adjust=True, group_by="ticker")
        for sym in symbols:
            try:
                sub = df[sym][["Close", "Volume"]].dropna() if len(symbols) > 1 else df[["Close", "Volume"]].dropna()
            except KeyError:
                continue
            rows = [
                {"date": idx.date().isoformat(), "close": round(float(r["Close"]), 4),
                 "volume": float(r["Volume"])}
                for idx, r in sub.iterrows()
            ]
            if rows:
                out[sym] = rows
    except Exception:
        return {}
    return out
