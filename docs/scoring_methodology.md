# Scoring Methodology

Implemented in `packages/research_engine/scoring.py`. Never a single opaque
"AI score" — always component-weighted with the breakdown shown.

## Research score (0–100)

| Component | Weight |
|---|---:|
| Business Quality | 15% |
| Growth / Estimate Momentum | 15% |
| Balance Sheet Strength | 10% |
| Valuation Attractiveness | 15% |
| Technical Trend | 10% |
| Catalyst Strength | 10% |
| Analyst / Estimate Revision | 10% |
| News / Sentiment | 5% |
| Liquidity / Risk Control | 10% |

Missing components score 0 and are listed in `missing_components` — never
silently filled. Phase 1 feeds mock component values; Phase 4 computes them
from live features (see feature groups in the architecture blueprint).

## Confidence (separate from score, by design)

Five factors, each 0–1: data completeness, data freshness, source quality,
agent agreement, model stability (valuation robustness to assumption tweaks).

- Any single factor < 0.3 → **Low** (one broken leg caps the table)
- Average ≥ 0.75 → **High**; ≥ 0.5 → **Medium**; else **Low**

A high research score with Low confidence means "interesting but unverified,"
and the UI must show both. Scores are research prioritization signals — not
buy/sell advice.
