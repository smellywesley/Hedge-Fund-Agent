import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from packages.research_engine.scoring import (
    WEIGHTS, compute_confidence, compute_research_score,
)


def test_weights_sum_to_one():
    assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9


def test_score_full_components():
    result = compute_research_score({k: 100 for k in WEIGHTS})
    assert result["score_total"] == 100.0
    assert result["missing_components"] == []


def test_score_missing_component_reported_not_filled():
    components = {k: 80 for k in WEIGHTS if k != "valuation"}
    result = compute_research_score(components)
    assert "valuation" in result["missing_components"]
    assert result["score_total"] == pytest.approx(80 * 0.85, abs=0.1)


def test_score_rejects_unknown_component():
    with pytest.raises(ValueError):
        compute_research_score({"vibes": 100})


def test_confidence_bands():
    assert compute_confidence(0.9, 0.9, 0.9, 0.9, 0.9) == "High"
    assert compute_confidence(0.6, 0.6, 0.6, 0.6, 0.6) == "Medium"
    assert compute_confidence(0.4, 0.4, 0.4, 0.4, 0.4) == "Low"


def test_single_weak_factor_caps_confidence_low():
    assert compute_confidence(1.0, 1.0, 1.0, 1.0, 0.2) == "Low"


def test_confidence_rejects_out_of_range():
    with pytest.raises(ValueError):
        compute_confidence(1.5, 0.5, 0.5, 0.5, 0.5)
