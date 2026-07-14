import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from packages.research_engine.regime import compute_regime_score


def test_calm_broad_rally_is_risk_on():
    r = compute_regime_score(vix=12, sector_change_pcts=[1.0] * 9,
                             yield_curve_spread=1.5, dollar_change_pct=-1.0)
    assert r["label"] == "RISK-ON"
    assert r["score"] >= 90  # near-max on every driver


def test_panic_broad_selloff_is_risk_off():
    r = compute_regime_score(vix=35, sector_change_pcts=[-1.0] * 9,
                             yield_curve_spread=-1.0, dollar_change_pct=1.0)
    assert r["label"] == "RISK-OFF"
    assert r["score"] <= 10


def test_mixed_is_neutral_ish():
    r = compute_regime_score(vix=20, sector_change_pcts=[1, -1, 1, -1, 1, -1, 1, -1, 1],
                             yield_curve_spread=0.0, dollar_change_pct=0.0)
    assert 40 <= r["score"] <= 70
    assert set(r["drivers"]) == {"vix", "breadth", "curve", "dollar"}


def test_empty_sectors_defaults_to_neutral_breadth():
    r = compute_regime_score(vix=20, sector_change_pcts=[],
                             yield_curve_spread=0.0, dollar_change_pct=0.0)
    assert r["drivers"]["breadth"] == 15.0  # 0.5 × 30
