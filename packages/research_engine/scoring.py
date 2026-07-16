"""Research scoring engine.

Component-weighted score (never a single opaque AI number) plus a separate
confidence rating driven by data completeness/freshness/agreement.

Two of the nine components are now computed from real stored price history
(compute_technical_trend, compute_liquidity_score below); the other seven
remain mock inputs until their own data lands, and the API declares which are
real vs mock. All output is educational research scoring — not investment advice.
"""
import math

WEIGHTS = {
    "business_quality": 0.15,
    "growth_momentum": 0.15,
    "balance_sheet": 0.10,
    "valuation": 0.15,
    "technical_trend": 0.10,
    "catalyst_strength": 0.10,
    "estimate_revision": 0.10,
    "news_sentiment": 0.05,
    "liquidity_risk": 0.10,
}


def compute_research_score(components: dict) -> dict:
    """components: {component_name: 0-100}. Returns total + breakdown."""
    unknown = set(components) - set(WEIGHTS)
    if unknown:
        raise ValueError(f"Unknown score components: {unknown}")
    missing = [k for k in WEIGHTS if k not in components]
    # Missing components score 0 and are reported, never silently filled.
    total = sum(WEIGHTS[k] * components.get(k, 0) for k in WEIGHTS)
    return {
        "score_total": round(total, 1),
        "components": {k: components.get(k) for k in WEIGHTS},
        "weights": WEIGHTS,
        "missing_components": missing,
    }


def compute_confidence(
    data_completeness: float,  # 0-1
    data_freshness: float,     # 0-1 (1 = updated today)
    source_quality: float,     # 0-1 (1 = SEC/primary source)
    agent_agreement: float,    # 0-1 (1 = bull/bear/risk converge)
    model_stability: float,    # 0-1 (1 = valuation robust to assumption tweaks)
) -> str:
    """Confidence is separate from the research score by design."""
    factors = [data_completeness, data_freshness, source_quality,
               agent_agreement, model_stability]
    if any(not 0 <= f <= 1 for f in factors):
        raise ValueError("Confidence factors must be in [0, 1]")
    avg = sum(factors) / len(factors)
    # Any single very weak factor caps confidence at Low.
    if min(factors) < 0.3:
        return "Low"
    if avg >= 0.75:
        return "High"
    if avg >= 0.5:
        return "Medium"
    return "Low"


# --------------------------------------------------------------------------
# Real score components computed from stored price history (backlog item 2).
# Pure functions over plain lists — house style (see risk.py). Feed these the
# closes from db.PriceRow via nav.price_series(); SPY closes for relative
# strength. Both return a 0-100 component score.
# --------------------------------------------------------------------------

def _mean(xs: list[float]) -> float:
    return sum(xs) / len(xs)


def compute_technical_trend(closes: list[float], spy_closes: list[float] | None = None) -> float | None:
    """0-100 technical-trend score from price vs its 50/200-day moving averages
    and relative strength vs SPY. Discrete, documented blend (first real cut):

        +40  last price >= 50-day MA         (intermediate uptrend)
        +30  last price >= 200-day MA         (long-term uptrend; if <200 closes
             available, the full-length mean is used as a proxy — noted)
        +30  trailing return >= SPY's over the same window (positive RS);
             +15 (neutral) if no benchmark is supplied

    Returns None if fewer than 50 closes — too little to judge a trend (the
    caller declares it missing rather than scoring on noise).
    """
    if len(closes) < 50:
        return None
    price = closes[-1]
    score = 0.0
    score += 40.0 if price >= _mean(closes[-50:]) else 0.0
    ma_long = _mean(closes[-200:]) if len(closes) >= 200 else _mean(closes)
    score += 30.0 if price >= ma_long else 0.0
    if spy_closes and len(spy_closes) >= 2 and len(closes) >= 2:
        w = min(60, len(closes) - 1, len(spy_closes) - 1)
        stock_ret = closes[-1] / closes[-1 - w] - 1
        spy_ret = spy_closes[-1] / spy_closes[-1 - w] - 1
        score += 30.0 if stock_ret >= spy_ret else 0.0
    else:
        score += 15.0  # neutral half-credit when no benchmark is available
    return round(score, 1)


def compute_liquidity_score(dollar_adv: float) -> float:
    """0-100 liquidity score from average daily dollar volume (price × shares).
    Log-scaled between $100k ADV (score 0, effectively untradeable) and $10bn
    ADV (score 100, mega-cap depth). Monotonic; clamps outside the range.

        ~$1M ADV   -> ~20    ~$100M ADV -> ~60    ~$1bn ADV -> ~80
    """
    if dollar_adv <= 0:
        return 0.0
    lo, hi = 1e5, 1e10
    x = max(lo, min(hi, dollar_adv))
    return round((math.log10(x) - math.log10(lo)) / (math.log10(hi) - math.log10(lo)) * 100, 1)


# --------------------------------------------------------------------------
# Fundamentals-based components from SEC XBRL company facts (backlog: OpenBB
# replaced by keyless SEC facts). Pure functions over already-extracted numbers.
# --------------------------------------------------------------------------

def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def compute_business_quality(gross_margin: float, operating_margin: float) -> float:
    """0-100 from profitability. gross_margin/operating_margin are fractions.
    Gross margin scores to 50 at 80%+, operating margin to 50 at 40%+."""
    return round(_clamp01(gross_margin / 0.80) * 50 + _clamp01(operating_margin / 0.40) * 50, 1)


def compute_balance_sheet(total_debt: float, total_assets: float, cash: float) -> float | None:
    """0-100 from leverage + liquidity. Low debt/assets and healthy cash/assets
    score high. None if assets are unknown/zero (can't judge)."""
    if not total_assets or total_assets <= 0:
        return None
    leverage = total_debt / total_assets            # lower is better
    cash_ratio = cash / total_assets                # higher is better
    lev_pts = (1 - _clamp01(leverage / 0.60)) * 60  # 0% debt→60, 60%+→0
    cash_pts = _clamp01(cash_ratio / 0.30) * 40     # 30%+ cash→40
    return round(lev_pts + cash_pts, 1)


def compute_valuation(earnings_yield: float) -> float:
    """0-100 from earnings yield (net income / market cap). Cheaper = higher.
    6%+ earnings yield (~P/E 16 or lower) scores 100; negative earnings → 0."""
    if earnings_yield <= 0:
        return 0.0
    return round(_clamp01(earnings_yield / 0.06) * 100, 1)


def compute_growth_momentum(forward_revenue_growth: float) -> float:
    """0-100 from analyst forward revenue-growth estimate (a fraction). Maps
    -10% → 0, ~0% → ~29, 25%+ → 100."""
    return round(_clamp01((forward_revenue_growth + 0.10) / 0.35) * 100, 1)
