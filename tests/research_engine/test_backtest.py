import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from packages.research_engine.backtest import (
    backtest_signal, score_threshold_signal,
)


def _hold(*symbols):
    """A trivial SelectFn that always holds the given symbols."""
    return lambda step, history: list(symbols)


def test_always_holding_outperformer_beats_benchmark():
    # WIN compounds +20%/step (→ +44%); benchmark +10%/step (→ +21%).
    prices = {"WIN": [100.0, 120.0, 144.0], "MEH": [100.0, 101.0, 102.0]}
    bench = [100.0, 110.0, 121.0]
    # score_threshold_signal must pick WIN (80) and drop MEH (40) at threshold 50.
    signal = score_threshold_signal({"WIN": 80, "MEH": 40}, threshold=50)

    r = backtest_signal(prices, signal, bench)
    assert r["available"] is True
    assert r["strategyReturnPct"] == 44.0
    assert r["benchmarkReturnPct"] == 21.0
    assert r["excessPct"] == 23.0
    assert r["excessPct"] > 0
    # The signal really held only WIN every step (MEH filtered by threshold).
    assert all(entry["held"] == ["WIN"] for entry in r["trace"])


def test_holding_benchmark_itself_yields_zero_excess():
    # A non-trivial benchmark path; strategy holds a symbol equal to it.
    bench = [100.0, 105.0, 99.0, 110.0]
    prices = {"SPY": list(bench)}
    r = backtest_signal(prices, _hold("SPY"), bench)
    assert r["available"] is True
    assert r["strategyReturnPct"] == r["benchmarkReturnPct"]
    assert r["excessPct"] == 0.0  # exactly zero, not merely ~0


def test_equal_weight_basket_averages_member_returns():
    # A +20%, B +40% over one interval → equal-weight basket = +30% (mean),
    # NOT +60% (sum). Benchmark +10%.
    prices = {"A": [100.0, 120.0], "B": [100.0, 140.0]}
    bench = [100.0, 110.0]
    r = backtest_signal(prices, _hold("A", "B"), bench)
    assert r["strategyReturnPct"] == 30.0
    assert r["benchmarkReturnPct"] == 10.0
    assert r["excessPct"] == 20.0


def test_empty_pick_holds_cash():
    # No selection → 0% strategy return while the benchmark rises → negative excess.
    prices = {"X": [100.0, 200.0]}
    bench = [100.0, 110.0]
    r = backtest_signal(prices, lambda step, history: [], bench)
    assert r["strategyReturnPct"] == 0.0
    assert r["benchmarkReturnPct"] == 10.0
    assert r["excessPct"] == -10.0


def test_no_lookahead_signal_only_sees_prefix_up_to_step():
    # The engine must hand the signal ONLY closes[0..t] at step t — length t+1,
    # and must NEVER reveal the final close to a decision. If the engine leaked
    # the full series, the recorded length would be `window` at every call.
    bench = [100.0, 101.0, 102.0, 103.0]
    prices = {"WIN": [100.0, 110.0, 121.0, 133.1]}
    seen = []

    def spy(step, history):
        seen.append((step, len(history["WIN"])))
        return ["WIN"]

    r = backtest_signal(prices, spy, bench)
    window = r["window"]
    assert window == 4
    # Called for steps 0..window-2; at step t the prefix length is exactly t+1.
    assert seen == [(t, t + 1) for t in range(window - 1)]
    # The largest prefix ever shown is window-1 — the final close is realized,
    # never decided upon (this is the no-look-ahead guarantee).
    assert max(length for _, length in seen) == window - 1


def test_trailing_overlap_alignment_trims_to_common_window():
    # Benchmark longer than the universe symbol → both trimmed to the common
    # trailing window (len 3). If the full benchmark were used the answer would
    # be +142%, not +21%.
    bench = [50.0, 100.0, 110.0, 121.0]
    prices = {"A": [100.0, 120.0, 144.0]}
    r = backtest_signal(prices, _hold("A"), bench)
    assert r["window"] == 3
    assert r["steps"] == 2
    assert r["benchmarkReturnPct"] == 21.0   # 121/100 - 1, NOT 121/50 - 1
    assert r["strategyReturnPct"] == 44.0


def test_unknown_selected_symbol_is_warned_and_treated_as_cash():
    prices = {"A": [100.0, 110.0]}
    bench = [100.0, 100.0]
    r = backtest_signal(prices, _hold("GHOST"), bench)
    assert r["strategyReturnPct"] == 0.0            # held cash
    assert any("GHOST" in w for w in r["warnings"])  # reported, not silently dropped


def test_short_window_is_blocked_not_faked():
    r = backtest_signal({"A": [100.0]}, _hold("A"), [100.0])
    assert r["available"] is False
    assert "note" in r
