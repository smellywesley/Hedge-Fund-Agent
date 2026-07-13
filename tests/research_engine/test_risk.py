import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from packages.research_engine.risk import (
    beta, correlation, correlation_matrix, max_drawdown_pct,
    pct_returns, realized_vol_pct,
)


def test_pct_returns():
    assert pct_returns([100, 110, 99]) == pytest.approx([0.10, -0.10])
    assert pct_returns([100]) == []
    with pytest.raises(ValueError):
        pct_returns([100, 0, 50])


def test_max_drawdown_known_answer():
    # Peak 200 → trough 150 = exactly -25%
    assert max_drawdown_pct([100, 200, 180, 150, 190]) == -25.0
    assert max_drawdown_pct([100, 110, 120]) == 0.0  # monotonic up
    assert max_drawdown_pct([100]) == 0.0


def test_realized_vol():
    assert realized_vol_pct([100.0] * 30) == 0.0  # constant series
    assert realized_vol_pct([100, 101]) is None  # too short (1 return)
    # Alternating ±1% has stdev ~1.005% daily → ~15.96% annualized
    series = [100.0]
    for i in range(30):
        series.append(series[-1] * (1.01 if i % 2 == 0 else 0.99))
    vol = realized_vol_pct(series)
    assert 14 < vol < 18


def test_beta_of_identical_series_is_one():
    series = [100.0]
    for i in range(70):
        series.append(series[-1] * (1 + ((i % 7) - 3) / 100))
    assert beta(series, series) == 1.0


def test_beta_of_double_leverage_is_two():
    bench = [100.0]
    for i in range(70):
        bench.append(bench[-1] * (1 + ((i % 5) - 2) / 100))
    asset = [100.0]
    for prev, cur in zip(bench, bench[1:]):
        asset.append(asset[-1] * (1 + 2 * (cur / prev - 1)))
    assert beta(asset, bench) == pytest.approx(2.0, abs=0.01)


def test_beta_insufficient_data():
    assert beta([100, 101, 102], [100, 101, 102]) is None


def test_correlation_bounds():
    a = [100.0]
    for i in range(70):
        a.append(a[-1] * (1 + ((i % 7) - 3) / 100))
    inverse = [100.0]
    for prev, cur in zip(a, a[1:]):
        inverse.append(inverse[-1] * (1 - (cur / prev - 1)))
    assert correlation(a, a) == 1.0
    assert correlation(a, inverse) == -1.0


def test_correlation_matrix_pairs():
    a = [100.0]
    for i in range(70):
        a.append(a[-1] * (1 + ((i % 7) - 3) / 100))
    m = correlation_matrix({"X": a, "Y": a, "Z": [100, 101]})  # Z too short
    assert m == [{"a": "X", "b": "Y", "corr": 1.0}]
