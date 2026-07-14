"""Market regime score — real risk-on/off read from macro data already in hand.

Pure function over inputs the Markets snapshot already fetches via yfinance
(VIX level, sector-ETF daily breadth, a Treasury-yield curve spread, and the
dollar's daily move). No FRED key, no new dependency. FRED/feedoracle would
enrich this later with CPI/unemployment/credit spreads, but the market-regime
read stands on free data we already pull.

Educational — a regime heuristic, not a market call or investment advice.
"""


def compute_regime_score(
    vix: float,
    sector_change_pcts: list[float],
    yield_curve_spread: float,   # e.g. 30Y minus 5Y, in percentage points
    dollar_change_pct: float,    # DXY daily % change
) -> dict:
    """0-100 regime score (100 = maximally risk-on) plus label and drivers.

    Blend (documented, first real cut):
      VIX      (0-40): calm markets = risk-on. VIX 12 -> 40, VIX 32 -> 0, linear.
      Breadth  (0-30): fraction of sectors up today × 30.
      Curve    (0-20): a normal (positive) curve is risk-on; inverted is risk-off.
                       spread >= +1.0 -> 20, spread <= -1.0 -> 0, linear.
      Dollar   (0-10): a falling dollar supports risk assets. −0.5% -> 10,
                       +0.5% -> 0, linear.
    """
    def clamp(x, lo=0.0, hi=1.0):
        return max(lo, min(hi, x))

    vix_pts = clamp((32 - vix) / (32 - 12)) * 40
    breadth = (sum(1 for c in sector_change_pcts if c > 0) / len(sector_change_pcts)) if sector_change_pcts else 0.5
    breadth_pts = breadth * 30
    curve_pts = clamp((yield_curve_spread + 1.0) / 2.0) * 20
    dollar_pts = clamp((0.5 - dollar_change_pct) / 1.0) * 10

    score = round(vix_pts + breadth_pts + curve_pts + dollar_pts, 1)
    label = "RISK-ON" if score >= 60 else "RISK-OFF" if score < 40 else "NEUTRAL"
    return {
        "score": score,
        "label": label,
        "drivers": {
            "vix": round(vix_pts, 1),
            "breadth": round(breadth_pts, 1),
            "curve": round(curve_pts, 1),
            "dollar": round(dollar_pts, 1),
        },
        "note": "Regime heuristic from live macro data (VIX, sector breadth, curve, dollar). Educational — not a market call.",
    }
