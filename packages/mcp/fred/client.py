"""FRED (Federal Reserve Economic Data) connector.

Interface for the official FRED API — used only when a user supplies a free key
(FRED_API_KEY env var; register at fred.stlouisfed.org). Without a key, every
call returns a BLOCKED marker rather than crashing or fabricating data
(connector contract, docs/data_sources.md).

NOTE (Phase decision): the Markets *regime score* does NOT depend on this — it
is computed from macro data already fetched via yfinance (see
packages/research_engine/regime.py). FRED adds series yfinance lacks (CPI,
unemployment, GDP, credit spreads) and is wired only once a key exists.

The free no-key `feedoracle-macro` MCP server is registered separately for
agent-side research; it is an MCP (agent) tool, not callable by this backend.
"""
import os
from datetime import datetime, timezone

# Series the regime/macro views will eventually pull once a key exists.
SERIES = {
    "DGS10": "10-Year Treasury yield",
    "DGS2": "2-Year Treasury yield",
    "T10Y2Y": "10Y-2Y term spread",
    "VIXCLS": "CBOE Volatility Index",
    "DTWEXBGS": "Broad trade-weighted US dollar index",
    "UNRATE": "Unemployment rate",
    "CPIAUCSL": "CPI (all urban consumers)",
    "BAMLH0A0HYM2": "High-yield credit spread",
}


def get_series(series_id: str, api_key: str | None = None) -> dict:
    """Fetch a FRED series. Returns the connector envelope; if no key is
    available the result is BLOCKED (never faked, never raised)."""
    key = api_key or os.environ.get("FRED_API_KEY")
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    if not key:
        return {
            "blocked": True,
            "reason": "FRED_API_KEY not configured — register a free key at fred.stlouisfed.org",
            "source": "FRED",
            "seriesId": series_id,
            "asOf": now,
        }
    # CONNECTOR: real fetch path, exercised only once a key is supplied.
    try:
        import requests

        resp = requests.get(
            "https://api.stlouisfed.org/fred/series/observations",
            params={"series_id": series_id, "api_key": key, "file_type": "json"},
            headers={"User-Agent": "Terminal Alpha educational research"},
            timeout=10,
        )
        resp.raise_for_status()
        obs = resp.json().get("observations", [])
        return {"blocked": False, "source": "FRED", "seriesId": series_id,
                "observations": obs, "asOf": now}
    except Exception as e:  # network/parse failure — reported, not faked
        return {"blocked": True, "reason": f"FRED fetch failed: {e}",
                "source": "FRED", "seriesId": series_id, "asOf": now}
