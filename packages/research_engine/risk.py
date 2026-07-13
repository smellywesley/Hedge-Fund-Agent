"""Portfolio risk math — pure functions over price/NAV series.

All inputs are plain lists of floats (oldest → newest). No pandas dependency
here: series are short (≤ a few hundred points) and plain Python keeps these
trivially unit-testable.
"""
import math

TRADING_DAYS = 252


def pct_returns(series: list[float]) -> list[float]:
    """Simple daily returns from a price/NAV series."""
    if len(series) < 2:
        return []
    out = []
    for prev, cur in zip(series, series[1:]):
        if prev == 0:
            raise ValueError("Series contains a zero value — cannot compute return")
        out.append(cur / prev - 1)
    return out


def max_drawdown_pct(series: list[float]) -> float:
    """Largest peak-to-trough decline, as a negative percentage (0.0 if none)."""
    if len(series) < 2:
        return 0.0
    peak = series[0]
    worst = 0.0
    for v in series:
        peak = max(peak, v)
        worst = min(worst, v / peak - 1)
    return round(worst * 100, 2)


def realized_vol_pct(series: list[float], window: int = 20) -> float | None:
    """Annualized stdev of the last `window` daily returns, in %. None if too short."""
    rets = pct_returns(series)[-window:]
    if len(rets) < 2:
        return None
    mean = sum(rets) / len(rets)
    var = sum((r - mean) ** 2 for r in rets) / (len(rets) - 1)
    return round(math.sqrt(var) * math.sqrt(TRADING_DAYS) * 100, 2)


def beta(asset: list[float], benchmark: list[float], window: int = 60) -> float | None:
    """OLS beta of asset returns vs benchmark returns over the last `window`
    days. Series are aligned by trailing overlap. None if under 10 points."""
    n = min(len(asset), len(benchmark))
    a_rets = pct_returns(asset[-n:])[-window:]
    b_rets = pct_returns(benchmark[-n:])[-window:]
    n = min(len(a_rets), len(b_rets))
    if n < 10:
        return None
    a_rets, b_rets = a_rets[-n:], b_rets[-n:]
    mean_a = sum(a_rets) / n
    mean_b = sum(b_rets) / n
    cov = sum((a - mean_a) * (b - mean_b) for a, b in zip(a_rets, b_rets))
    var_b = sum((b - mean_b) ** 2 for b in b_rets)
    if var_b == 0:
        return None
    return round(cov / var_b, 2)


def correlation(a: list[float], b: list[float], window: int = 60) -> float | None:
    """Pearson correlation of daily returns over the trailing window."""
    n = min(len(a), len(b))
    a_rets = pct_returns(a[-n:])[-window:]
    b_rets = pct_returns(b[-n:])[-window:]
    n = min(len(a_rets), len(b_rets))
    if n < 10:
        return None
    a_rets, b_rets = a_rets[-n:], b_rets[-n:]
    mean_a = sum(a_rets) / n
    mean_b = sum(b_rets) / n
    cov = sum((x - mean_a) * (y - mean_b) for x, y in zip(a_rets, b_rets))
    sd_a = math.sqrt(sum((x - mean_a) ** 2 for x in a_rets))
    sd_b = math.sqrt(sum((y - mean_b) ** 2 for y in b_rets))
    if sd_a == 0 or sd_b == 0:
        return None
    return round(cov / (sd_a * sd_b), 2)


def correlation_matrix(series_by_symbol: dict[str, list[float]], window: int = 60) -> list[dict]:
    """Upper-triangle pairwise correlations: [{a, b, corr}], skipping pairs
    with insufficient overlap."""
    symbols = sorted(series_by_symbol)
    out = []
    for i, a in enumerate(symbols):
        for b in symbols[i + 1:]:
            c = correlation(series_by_symbol[a], series_by_symbol[b], window)
            if c is not None:
                out.append({"a": a, "b": b, "corr": c})
    return out
