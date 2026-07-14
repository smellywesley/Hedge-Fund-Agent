import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from packages.mcp.fred.client import SERIES, get_series


def test_no_key_returns_blocked_not_crash(monkeypatch):
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    r = get_series("DGS10")
    assert r["blocked"] is True
    assert r["source"] == "FRED"
    assert r["seriesId"] == "DGS10"
    assert "FRED_API_KEY" in r["reason"]
    assert "observations" not in r  # nothing fabricated


def test_series_map_covers_core_macro():
    for sid in ("DGS10", "DGS2", "VIXCLS", "UNRATE", "CPIAUCSL"):
        assert sid in SERIES
