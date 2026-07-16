import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from packages.mcp.fmp import client as fmp


def test_no_key_returns_blocked(monkeypatch):
    monkeypatch.delenv("FMP_API_KEY", raising=False)
    r = fmp.get_estimates("NVDA")
    assert r["blocked"] is True
    assert "FMP_API_KEY" in r["reason"]
    assert "forwardRevenueGrowth" not in r


def test_forward_growth_from_estimates(monkeypatch):
    # newest est revenue 120 vs prior 100 → +20% forward growth.
    fixture = [
        {"date": "2026-12-31", "estimatedRevenueAvg": 120.0},
        {"date": "2025-12-31", "estimatedRevenueAvg": 100.0},
        {"date": "2024-12-31", "estimatedRevenueAvg": 90.0},
    ]
    monkeypatch.setattr(fmp, "_get_json", lambda url: fixture)
    r = fmp.get_estimates("NVDA", api_key="test")
    assert r["blocked"] is False
    assert abs(r["forwardRevenueGrowth"] - 0.20) < 1e-9


def test_insufficient_history_blocked(monkeypatch):
    monkeypatch.setattr(fmp, "_get_json", lambda url: [{"date": "2026-12-31", "estimatedRevenueAvg": 120.0}])
    r = fmp.get_estimates("NVDA", api_key="test")
    assert r["blocked"] is True
