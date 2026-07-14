import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from packages.research_engine.scoring import (
    compute_liquidity_score, compute_technical_trend,
)


def test_short_series_returns_none():
    assert compute_technical_trend([100.0] * 49) is None  # < 50 closes


def test_strong_uptrend_with_positive_rs_scores_max():
    # Steadily rising series: last price above both MAs.
    closes = [100.0 + i for i in range(210)]  # 100..309, clearly above 50/200 MA
    spy = [100.0 + 0.1 * i for i in range(210)]  # rising slower → stock RS positive
    # +40 (>50MA) +30 (>200MA) +30 (RS beats SPY) = 100
    assert compute_technical_trend(closes, spy) == 100.0


def test_downtrend_scores_low():
    closes = [300.0 - i for i in range(210)]  # falling: last price below both MAs
    spy = [100.0 + 0.1 * i for i in range(210)]  # SPY rising → stock RS negative
    # 0 (<50MA) + 0 (<200MA) + 0 (RS worse) = 0
    assert compute_technical_trend(closes, spy) == 0.0


def test_no_benchmark_gives_neutral_rs_credit():
    closes = [100.0 + i for i in range(210)]  # above both MAs
    # +40 +30 +15 (neutral, no benchmark) = 85
    assert compute_technical_trend(closes, None) == 85.0


def test_liquidity_is_monotonic_and_bounded():
    assert compute_liquidity_score(0) == 0.0
    assert compute_liquidity_score(50_000) == 0.0        # below $100k floor → clamped
    assert compute_liquidity_score(1e5) == 0.0           # floor
    assert compute_liquidity_score(1e10) == 100.0        # ceiling
    assert compute_liquidity_score(1e12) == 100.0        # above ceiling → clamped
    # Monotonic increase across the range.
    scores = [compute_liquidity_score(v) for v in (1e6, 1e7, 1e8, 1e9)]
    assert scores == sorted(scores)
    assert scores[0] < scores[-1]


def test_liquidity_midpoint_reasonable():
    # $100M ADV should land in a healthy mid-high band (log midpoint-ish).
    s = compute_liquidity_score(1e8)
    assert 55 <= s <= 65
