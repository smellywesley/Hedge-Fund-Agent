"""Dependency-light backtester over stored historical price series.

Pure functions over plain lists/dicts (house style — see risk.py). No pandas,
no numpy: series are short (≤ a few hundred daily closes) and plain Python
keeps the logic trivially unit-testable and free of look-ahead surprises.

Model (the deliberate simplification):
  equal-weight, rebalanced-EVERY-step, long-only paper strategy
  vs. benchmark buy-and-hold, over the common trailing window.

At each step boundary t the signal picks which symbols to hold for the
interval [t, t+1] using ONLY prices up to and including index t. The interval
return of an equal-weight basket is the mean of its members' simple returns;
an empty pick means cash (0% for that interval). Compounding those interval
returns gives the strategy's cumulative return; the benchmark is a simple
buy-and-hold over the same window.

Everything here is educational / paper simulation only — not a live trading
system, not investment advice.
"""

# Type alias for a per-step signal: given the step index and the price history
# visible SO FAR (each series truncated to length step+1), return the symbols
# to hold for the next interval. Receiving only the prefix is what structurally
# guarantees no look-ahead — the engine never hands a signal a future price.
SelectFn = "Callable[[int, dict[str, list[float]]], list[str]]"


def _common_window(benchmark: list[float], prices_by_symbol: dict[str, list[float]]) -> int:
    """Length of the trailing overlap shared by the benchmark and every symbol.

    ponytail: trailing-overlap alignment (like risk.py) assumes all series end
    on the same date and share one trading calendar — true for the app's feed,
    which backfills every symbol to today over the benchmark date spine. If
    calendars ever diverge or series carry interior gaps, feed date-aligned
    (forward-filled) series instead; this length math stays the same.
    """
    lengths = [len(benchmark)] + [len(v) for v in prices_by_symbol.values()]
    return min(lengths) if lengths else 0


def backtest_signal(
    prices_by_symbol: dict[str, list[float]],
    selected_symbols_per_step_fn,
    benchmark: list[float],
) -> dict:
    """Backtest a per-step long-only signal against a buy-and-hold benchmark.

    Args:
        prices_by_symbol: {symbol: [close, ...]} oldest→newest. The tradable
            universe. Series are aligned by trailing overlap to the common
            window (see _common_window).
        selected_symbols_per_step_fn: SelectFn. Called once per interval as
            fn(step_index, history) where history[symbol] is that symbol's
            closes truncated to [0 .. step_index] (length step_index+1).
            Returns the symbols to hold equal-weight for [step_index,
            step_index+1]. Symbols not in the tradable universe are ignored
            (recorded as a warning); an empty/all-ignored pick holds cash.
        benchmark: [close, ...] oldest→newest for the buy-and-hold benchmark.

    Returns:
        On success:
            {available: True, strategyReturnPct, benchmarkReturnPct, excessPct,
             window, steps, trace: [{step, held, stratRetPct, benchRetPct}...],
             warnings, note, source-agnostic}
        When the window is too short (<2 aligned points):
            {available: False, note} — blocked and reported, never faked
            (connector contract, docs/data_sources.md).
    """
    window = _common_window(benchmark, prices_by_symbol)
    if window < 2:
        return {
            "available": False,
            "note": "Common price window too short — need at least 2 aligned closes across the benchmark and universe.",
        }

    # Trailing-overlap alignment to the common window.
    bench = benchmark[-window:]
    aligned = {sym: series[-window:] for sym, series in prices_by_symbol.items()}

    strat_growth = 1.0
    bench_growth = 1.0
    trace: list[dict] = []
    warnings: list[str] = []
    unknown_seen: set[str] = set()

    for t in range(window - 1):
        # No look-ahead: hand the signal only closes up to and including t.
        # ponytail: rebuilds a prefix dict each step — O(window·|universe|)
        # total, fine for ≤ few-hundred-point series; stream a view if it grows.
        history = {sym: series[: t + 1] for sym, series in aligned.items()}
        picked = selected_symbols_per_step_fn(t, history)

        held = []
        for sym in picked:
            if sym not in aligned:
                if sym not in unknown_seen:
                    unknown_seen.add(sym)
                    warnings.append(f"Signal selected '{sym}' which is not in the tradable universe — ignored.")
                continue
            held.append(sym)

        # Equal-weight basket return over [t, t+1]; empty basket = cash (0%).
        member_rets = []
        for sym in held:
            prev, cur = aligned[sym][t], aligned[sym][t + 1]
            if prev == 0:
                warnings.append(f"'{sym}' has a zero close at step {t} — excluded from that interval.")
                continue
            member_rets.append(cur / prev - 1)
        step_ret = sum(member_rets) / len(member_rets) if member_rets else 0.0

        prev_b, cur_b = bench[t], bench[t + 1]
        if prev_b == 0:
            return {
                "available": False,
                "note": f"Benchmark has a zero close at step {t} — cannot compute buy-and-hold return.",
            }
        bench_ret = cur_b / prev_b - 1

        strat_growth *= 1 + step_ret
        bench_growth *= 1 + bench_ret
        trace.append({
            "step": t,
            "held": held,
            "stratRetPct": round(step_ret * 100, 4),
            "benchRetPct": round(bench_ret * 100, 4),
        })

    strat_pct = (strat_growth - 1) * 100
    bench_pct = (bench_growth - 1) * 100
    return {
        "available": True,
        "strategyReturnPct": round(strat_pct, 2),
        "benchmarkReturnPct": round(bench_pct, 2),
        # Excess from raw growths (not the two rounded numbers) to avoid drift.
        "excessPct": round((strat_growth - bench_growth) * 100, 2),
        "window": window,
        "steps": window - 1,
        "trace": trace,
        "warnings": warnings,
        "note": "Equal-weight, rebalanced-each-step, long-only strategy vs benchmark buy-and-hold. Paper simulation only — not investment advice.",
    }


def score_threshold_signal(scores_by_symbol: dict[str, float], threshold: float):
    """Concrete example signal: hold every name whose research score exceeds
    `threshold`, equal-weight, held the same way every step.

    Returns a SelectFn usable directly as backtest_signal's
    selected_symbols_per_step_fn. `scores_by_symbol` is a point-in-time snapshot
    (e.g. the `score_total` values from research_engine.scoring), so the pick is
    static across steps — it never peeks at future prices, preserving the
    no-look-ahead guarantee.

    ponytail: static point-in-time scores. If per-step score HISTORY ever
    exists, add a sibling that indexes scores_by_symbol[sym][step] instead.
    """
    picks = [sym for sym, score in scores_by_symbol.items() if score > threshold]

    def _fn(step_index: int, history: dict[str, list[float]]) -> list[str]:
        # Only hold names we actually have prices for at this step.
        return [sym for sym in picks if sym in history]

    return _fn
