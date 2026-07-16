"""Financial Modeling Prep (FMP) analyst-estimates connector.

The lightweight, deploy-safe way to get the data OpenBB would wrap: forward
analyst revenue estimates → a real growth_momentum score component. Keyed
(free tier at financialmodelingprep.com); blocked-not-faked without a key,
like the FRED connector.

HTTP goes through _get_json so tests run offline.
"""
import os
from datetime import datetime, timezone


def _get_json(url: str):
    import requests

    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()


def get_estimates(symbol: str, api_key: str | None = None) -> dict:
    """Forward revenue-estimate growth for `symbol`. Returns
    {blocked: False, forwardRevenueGrowth, source, asOf} or a blocked marker."""
    key = api_key or os.environ.get("FMP_API_KEY")
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    if not key:
        return {"blocked": True, "reason": "FMP_API_KEY not configured — free key at financialmodelingprep.com",
                "source": "FMP", "asOf": now}
    try:
        data = _get_json(f"https://financialmodelingprep.com/api/v3/analyst-estimates/{symbol}?limit=6&apikey={key}")
        if not isinstance(data, list) or not data:
            return {"blocked": True, "reason": "no estimates returned", "source": "FMP", "asOf": now}
        ests = sorted(data, key=lambda x: x.get("date", ""))  # oldest → newest
        rev = [e.get("estimatedRevenueAvg") for e in ests if e.get("estimatedRevenueAvg")]
        if len(rev) < 2 or not rev[-2]:
            return {"blocked": True, "reason": "insufficient estimate history", "source": "FMP", "asOf": now}
        return {"blocked": False, "forwardRevenueGrowth": rev[-1] / rev[-2] - 1,
                "source": "FMP", "asOf": now}
    except Exception as e:
        return {"blocked": True, "reason": f"FMP fetch failed: {e}", "source": "FMP", "asOf": now}
