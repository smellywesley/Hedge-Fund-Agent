"""Research scoring engine — Phase 1 mock implementation.

Component-weighted score (never a single opaque AI number) plus a separate
confidence rating driven by data completeness/freshness/agreement.

Phase 4 will replace the mock component inputs with computed features from
live data (OpenBB / yfinance / SEC / FRED connectors in packages/mcp).
All output is educational research scoring — not investment advice.
"""

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
