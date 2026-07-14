import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from packages.research_engine.valuation import dcf_fair_value, scenario_values


def test_flat_fcf_perpetuity_is_horizon_independent():
    # Flat FCF of 20/yr (rev=100, margin=20%, tax=0, capex=0), wacc=10%, g=0.
    # A level perpetuity discounted at 10% is worth exactly FCF/wacc = 200,
    # and this must hold regardless of the explicit projection horizon.
    base = {
        "base_revenue": 100.0, "revenue_growth": 0.0, "operating_margin": 0.20,
        "tax_rate": 0.0, "capex_pct": 0.0, "wacc": 0.10, "terminal_growth": 0.0,
        "shares_out": 10.0, "net_cash": 0.0,
    }
    for years in (1, 5, 10, 30):
        r = dcf_fair_value({**base, "projection_years": years})
        assert r["enterpriseValue"] == pytest.approx(200.0, abs=0.01), f"years={years}"
        assert r["fairValuePerShare"] == pytest.approx(20.0, abs=0.01)


def test_net_cash_adds_to_equity_value():
    base = {
        "base_revenue": 100.0, "revenue_growth": 0.0, "operating_margin": 0.20,
        "tax_rate": 0.0, "capex_pct": 0.0, "wacc": 0.10, "terminal_growth": 0.0,
        "shares_out": 10.0, "net_cash": 50.0,
    }
    r = dcf_fair_value(base)
    assert r["equityValue"] == pytest.approx(250.0, abs=0.01)  # 200 EV + 50 cash
    assert r["fairValuePerShare"] == pytest.approx(25.0, abs=0.01)


def test_wacc_must_exceed_terminal_growth():
    with pytest.raises(ValueError):
        dcf_fair_value({"base_revenue": 100.0, "wacc": 0.03, "terminal_growth": 0.03})
    with pytest.raises(ValueError):
        dcf_fair_value({"base_revenue": 100.0, "wacc": 0.02, "terminal_growth": 0.05})


def test_missing_revenue_and_bad_shares_raise():
    with pytest.raises(ValueError):
        dcf_fair_value({"wacc": 0.09})  # no base_revenue
    with pytest.raises(ValueError):
        dcf_fair_value({"base_revenue": 100.0, "shares_out": 0})


def test_exit_multiple_overrides_gordon():
    r = dcf_fair_value({
        "base_revenue": 100.0, "revenue_growth": 0.0, "operating_margin": 0.20,
        "tax_rate": 0.0, "capex_pct": 0.0, "wacc": 0.10, "terminal_multiple": 15,
        "shares_out": 10.0, "projection_years": 5,
    })
    assert "exit multiple" in r["terminalMethod"]


def test_scenario_ordering_bear_lt_base_lt_bull():
    common = {"base_revenue": 100.0, "operating_margin": 0.20, "tax_rate": 0.15,
              "capex_pct": 0.05, "shares_out": 10.0, "net_cash": 0.0, "wacc": 0.10}
    bear = {**common, "revenue_growth": 0.02, "terminal_growth": 0.01}
    base = {**common, "revenue_growth": 0.10, "terminal_growth": 0.03}
    bull = {**common, "revenue_growth": 0.20, "terminal_growth": 0.045}
    s = scenario_values(bear, base, bull)
    assert s["bear"]["fairValuePerShare"] < s["base"]["fairValuePerShare"] < s["bull"]["fairValuePerShare"]
