"""DCF valuation — pure calculator for the editable Model Lab (backlog item 7).

Pure functions over a plain assumptions dict (house style — see risk.py). No
pandas. A DCF is a thinking tool, not a prediction: the output is only as good
as the assumptions, which the UI shows and lets the user edit.

Simplifications (documented, first real cut):
- Free cash flow ≈ NOPAT − capex, where NOPAT = revenue·operating_margin·(1−tax).
  D&A and working-capital changes are folded into the margin/capex inputs
  rather than modeled separately. Mark with a ponytail note where relevant.
- Single revenue growth rate across the explicit horizon (extend to a per-year
  vector later if needed — the math below already sums year by year).

Educational / paper simulation only — not investment advice.
"""

DEFAULTS = {
    "projection_years": 10,
    "revenue_growth": 0.10,
    "operating_margin": 0.25,
    "tax_rate": 0.15,
    "capex_pct": 0.05,      # capex as a fraction of revenue
    "wacc": 0.09,
    "terminal_growth": 0.03,  # used if terminal_multiple is absent
    "terminal_multiple": None,  # EV/FCF exit multiple on final-year FCF; overrides terminal_growth if set
    "shares_out": 1.0,
    "net_cash": 0.0,        # + = net cash, − = net debt; same units as base_revenue
}


def dcf_fair_value(assumptions: dict) -> dict:
    """Discounted-cash-flow fair value per share.

    Required (falling back to DEFAULTS): base_revenue, revenue_growth,
    operating_margin, tax_rate, capex_pct, wacc, shares_out, net_cash, and
    either terminal_growth (Gordon) or terminal_multiple (exit multiple).

    Returns {fairValuePerShare, enterpriseValue, equityValue, pvExplicit,
    pvTerminal, terminalMethod, projectionYears, note}. Raises ValueError on
    incoherent inputs (non-positive wacc/shares, or wacc <= terminal_growth
    which makes the Gordon terminal value blow up).
    """
    a = {**DEFAULTS, **assumptions}
    base_revenue = a.get("base_revenue")
    if base_revenue is None:
        raise ValueError("base_revenue is required")
    wacc = a["wacc"]
    shares = a["shares_out"]
    if wacc <= 0:
        raise ValueError("wacc must be positive")
    if shares <= 0:
        raise ValueError("shares_out must be positive")
    years = int(a["projection_years"])
    g = a["revenue_growth"]
    op_margin = a["operating_margin"]
    tax = a["tax_rate"]
    capex_pct = a["capex_pct"]

    pv_explicit = 0.0
    revenue = base_revenue
    fcf = 0.0
    for t in range(1, years + 1):
        revenue = revenue * (1 + g)
        ebit = revenue * op_margin
        nopat = ebit * (1 - tax)
        capex = revenue * capex_pct
        fcf = nopat - capex  # ponytail: D&A/WC folded into margin+capex inputs
        pv_explicit += fcf / (1 + wacc) ** t

    # Terminal value: exit multiple if given, else Gordon growth.
    if a.get("terminal_multiple") is not None:
        terminal_value = fcf * a["terminal_multiple"]
        terminal_method = f"exit multiple {a['terminal_multiple']}x final-year FCF"
    else:
        tg = a["terminal_growth"]
        if wacc <= tg:
            raise ValueError(f"wacc ({wacc}) must exceed terminal_growth ({tg}) for a finite Gordon terminal value")
        terminal_value = fcf * (1 + tg) / (wacc - tg)
        terminal_method = f"Gordon growth {tg:.1%}"
    pv_terminal = terminal_value / (1 + wacc) ** years

    enterprise_value = pv_explicit + pv_terminal
    equity_value = enterprise_value + a["net_cash"]
    return {
        "fairValuePerShare": round(equity_value / shares, 2),
        "enterpriseValue": round(enterprise_value, 2),
        "equityValue": round(equity_value, 2),
        "pvExplicit": round(pv_explicit, 2),
        "pvTerminal": round(pv_terminal, 2),
        "terminalMethod": terminal_method,
        "projectionYears": years,
        "note": "DCF output depends entirely on the assumptions above. Educational / paper simulation only — not investment advice.",
    }


def scenario_values(bear: dict, base: dict, bull: dict) -> dict:
    """Fair value under three assumption sets. Convenience for the Model Lab's
    bear/base/bull columns."""
    return {
        "bear": dcf_fair_value(bear),
        "base": dcf_fair_value(base),
        "bull": dcf_fair_value(bull),
    }
