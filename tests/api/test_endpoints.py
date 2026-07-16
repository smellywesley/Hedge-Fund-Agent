import os
import sys
import tempfile
from datetime import date as _date
from datetime import timedelta
from pathlib import Path

# Isolated throwaway DB + no live price calls: set env before importing the app.
os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mkdtemp()}/test.db"

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "apps" / "api"))

from fastapi.testclient import TestClient

from app import main
from app import nav as navmod
from app.db import init_db
from app.main import app

# ponytail: monkeypatch-by-assignment — tests must never hit Yahoo or SEC.
main.get_quotes = lambda symbols: {}
navmod.get_quotes = lambda symbols: {}
main.sec_get_filings = lambda symbol, forms=None, limit=10: (
    [{"formType": "10-Q", "filingDate": "2026-05-28", "accessionNumber": "x",
      "primaryDocUrl": "https://www.sec.gov/Archives/edgar/data/1045810/x/nvda.htm",
      "title": "NVDA 10-Q", "source": "SEC EDGAR", "asOf": "2026-07-14T00:00:00Z"}]
    if symbol.upper() == "NVDA" else []
)
# SEC XBRL fundamentals fixture (offline) → business_quality/balance_sheet/valuation real.
main.get_company_facts = lambda symbol: ({
    "revenue": 60_922e6, "gross_profit": 44_301e6, "operating_income": 32_972e6,
    "net_income": 29_760e6, "assets": 65_728e6, "cash": 7_280e6,
    "long_term_debt": 8_459e6, "shares": 2_464e6, "fiscal_year": 2024, "source": "SEC EDGAR XBRL",
} if symbol.upper() == "NVDA" else {})

# Deterministic fake history: 70 trading days from the simulated inception.
# SPY follows a zigzag return pattern (net-positive drift); every stock moves
# at exactly 2× SPY's daily return. So: pairwise stock correlation is 1.0 and
# date-ALIGNED portfolio beta is strongly positive, while a 1-day series
# misalignment destroys the covariance — a real regression guard.
_DAYS: list[str] = []
_d = _date(2026, 1, 2)
while len(_DAYS) < 70:
    if _d.weekday() < 5:
        _DAYS.append(_d.isoformat())
    _d += timedelta(days=1)

_RETS = [(((i * 37) % 7) - 3 + 0.5) / 100 for i in range(70)]  # -2.5% … +3.5%
_SPY, _STK = [100.0], [100.0]
for r in _RETS[1:]:
    _SPY.append(round(_SPY[-1] * (1 + r), 4))
    _STK.append(round(_STK[-1] * (1 + 2 * r), 4))
FINAL_CLOSE = _STK[-1]


def _fake_history(symbols, start):
    return {
        sym: [{"date": day, "close": (_SPY if sym == "SPY" else _STK)[i], "volume": 1e6}
              for i, day in enumerate(_DAYS)]
        for sym in symbols
    }


navmod.get_history = _fake_history

init_db()  # TestClient(app) without a context manager skips startup events
client = TestClient(app)
client.post("/api/paper-fund/refresh")  # backfill prices + NAV from fake history


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_nvda_research_report_complete():
    r = client.get("/api/research/NVDA/latest")
    assert r.status_code == 200
    body = r.json()
    for key in ("snapshot", "business_model", "bull_case", "bear_case",
                "red_team", "catalysts", "risk_register", "score", "confidence"):
        assert key in body, f"missing {key}"
    assert body["score"]["score_total"] > 0
    assert body["missing_data"]


def test_unknown_ticker_404():
    assert client.get("/api/research/ZZZZ/latest").status_code == 404


def test_agent_desk_has_all_13_agents():
    agents = client.get("/api/agents/outputs").json()
    assert len(agents) == 13
    for a in agents:
        for key in ("agent_name", "task", "summary", "confidence",
                    "sources", "missing_data", "warnings"):
            assert key in a


def test_markets_snapshot_falls_back_to_mock():
    body = client.get("/api/markets/snapshot").json()
    assert body["live"] is False
    assert body["warnings"]
    assert len(body["indices"]) == 4
    assert all(row["source"] == "MOCK" for row in body["indices"])


def test_watchlist_crud_persists():
    before = {w["symbol"] for w in client.get("/api/watchlist").json()}
    assert "NVDA" in before  # seeded

    r = client.post("/api/watchlist", json={"symbol": "amzn"})
    assert r.status_code == 201 and r.json()["persisted"] is True
    assert "AMZN" in {w["symbol"] for w in client.get("/api/watchlist").json()}

    assert client.post("/api/watchlist", json={"symbol": "AMZN"}).status_code == 409
    assert client.post("/api/watchlist", json={"symbol": "not a sym!"}).status_code == 422

    assert client.delete("/api/watchlist/AMZN").status_code == 200
    assert "AMZN" not in {w["symbol"] for w in client.get("/api/watchlist").json()}
    assert client.delete("/api/watchlist/AMZN").status_code == 404


# ---------------------------------------------------------------- NAV (WS1)

def test_nav_backfill_built_series_from_inception():
    body = client.get("/api/paper-fund/nav").json()
    assert len(body["series"]) >= 70
    assert body["series"][0]["date"] == "2026-01-02"
    m = body["metrics"]
    assert m["available"] is True
    assert m["inceptionDate"] == "2026-01-02"
    assert "Simulated inception" in m["inceptionNote"]
    # Zigzag returns → real dips → drawdown must be negative, drift positive.
    assert m["maxDrawdownPct"] < 0
    assert m["inceptionPnlPct"] > 0


def test_nav_backfill_is_idempotent():
    n1 = len(client.get("/api/paper-fund/nav").json()["series"])
    client.post("/api/paper-fund/refresh")
    n2 = len(client.get("/api/paper-fund/nav").json()["series"])
    assert n1 == n2


def test_fund_pnl_is_real_not_mock():
    body = client.get("/api/paper-fund/positions").json()
    assert body["dailyPnlPct"] is not None
    assert body["inceptionPnlPct"] is not None
    assert "Simulated inception" in body["pnlNote"]
    # Position current prices come from stored closes when offline.
    nvda = next(p for p in body["positions"] if p["symbol"] == "NVDA")
    assert nvda["currentPrice"] == round(FINAL_CLOSE, 2)


def test_paper_fund_computed_and_simulation_only():
    body = client.get("/api/paper-fund/positions").json()
    assert "Paper simulation only" in body["disclaimer"]
    assert body["positions"]
    assert all(p["invalidationPoint"] for p in body["positions"])
    total = body["cashPct"] + sum(p["positionSizePct"] for p in body["positions"])
    assert abs(total - 100) < 1.0
    assert body["journal"]


# ---------------------------------------------- cash bookkeeping (WS1)

def test_buy_debits_cash_and_over_cash_rejected():
    cash_before = client.get("/api/paper-fund/positions").json()["cashUsd"]
    r = client.post("/api/paper-fund/positions", json={
        "symbol": "AAPL", "entryPrice": 230.0, "quantity": 10,
        "thesis": "test thesis", "invalidationPoint": "test invalidation",
        "catalystDate": "2026-08-01",
    })
    assert r.status_code == 201
    assert r.json()["cashRemaining"] == round(cash_before - 2300)

    r = client.post("/api/paper-fund/positions", json={
        "symbol": "MSFT", "entryPrice": 1_000_000.0, "quantity": 100})
    assert r.status_code == 422
    assert "insufficient" in r.json()["detail"].lower()

    assert client.post("/api/paper-fund/positions", json={
        "symbol": "AAPL", "entryPrice": -5, "quantity": 10}).status_code == 422


def test_close_credits_cash_and_journals_realized_pnl():
    pos = client.get("/api/paper-fund/positions").json()
    aapl = next(p for p in pos["positions"] if p["symbol"] == "AAPL")
    cash_before = pos["cashUsd"]

    r = client.patch(f"/api/paper-fund/positions/{aapl['id']}", json={"status": "CLOSED"})
    assert r.status_code == 200
    # Settled at last stored close (238.0) × 10 shares.
    assert r.json()["cashRemaining"] == round(cash_before + FINAL_CLOSE * 10)

    body = client.get("/api/paper-fund/positions").json()
    assert not any(p["id"] == aapl["id"] for p in body["positions"])
    close_entries = [j for j in body["journal"] if j["decisionType"] == "CLOSE"]
    assert close_entries and "realized paper P&L" in close_entries[0]["decisionText"]


# ---------------------------------------------------------------- risk (WS1)

def test_risk_metrics_computed_from_history():
    body = client.get("/api/paper-fund/risk").json()
    metrics = {m["name"]: m["value"] for m in body["metrics"]}
    dd = metrics["Max drawdown (since inception)"]
    assert dd.endswith("%") and float(dd[:-1]) < 0  # zigzag NAV has real dips
    assert "%" in metrics["Realized volatility (20d, annualized)"]
    # Holdings move at 2× SPY's daily return → date-ALIGNED beta is strongly
    # positive (~2× invested weight). A 1-day misalignment (e.g. the weekend
    # NAV append bug) collapses covariance toward zero — this guards it.
    assert float(metrics["Portfolio beta (60d vs SPY)"]) > 0.5

    # All fake stocks move identically → pairwise correlation 1.0
    corrs = body["correlations"]
    assert corrs, "correlation matrix should not be empty"
    pair = next(c for c in corrs if {c["a"], c["b"]} == {"NVDA", "TSM"})
    assert pair["corr"] == 1.0


def test_risk_dashboard_computed_with_warnings():
    body = client.get("/api/paper-fund/risk").json()
    assert body["sectorExposure"]
    assert any(s["status"] == "WARNING" for s in body["sectorExposure"])  # tech cluster
    assert body["rulesChecklist"]
    missing_rule = next(r for r in body["rulesChecklist"] if "Missing data" in r["rule"])
    assert missing_rule["status"].startswith("WARNING")


def test_audit_log_records_events():
    client.post("/api/research/NVDA/run")
    logs = client.get("/api/audit/logs").json()
    events = {l["eventType"] for l in logs}
    assert "research_run" in events
    assert "watchlist_add" in events
    assert "price_backfill" in events
    assert "nav_backfill" in events
    assert "paper_position_close" in events


# ----------------------------------------------- integration wiring (Wave 1)

def test_markets_regime_is_computed_with_drivers():
    body = client.get("/api/markets/snapshot").json()
    regime = body["regime"]
    assert regime["label"] in ("RISK-ON", "NEUTRAL", "RISK-OFF")
    assert isinstance(regime["score"], (int, float))
    assert set(regime["drivers"]) == {"vix", "breadth", "curve", "dollar"}


def test_research_declares_real_vs_mock_components():
    body = client.get("/api/research/NVDA/latest").json()
    src = body["component_sources"]
    # 5 of 9 now real: 2 from price history, 3 from SEC XBRL fundamentals.
    for k in ("technical_trend", "liquidity_risk", "business_quality", "balance_sheet", "valuation"):
        assert k in src["real"], f"{k} should be real"
    assert "growth_momentum" in src["mock"]  # still mock (no estimates source)
    assert body["score"]["score_total"] > 0


def test_filings_uses_sec_with_source_tag():
    body = client.get("/api/tickers/NVDA/filings").json()
    assert body["source"] == "SEC EDGAR"
    assert body["filings"] and body["filings"][0]["primaryDocUrl"].startswith("https://www.sec.gov/")
    # Unknown ticker → mock fallback with a warning, never a crash.
    zz = client.get("/api/tickers/AAPL/filings").json()
    assert zz["source"] == "MOCK"
    assert zz["warnings"]


def test_watchlist_score_is_real_when_history_exists():
    items = client.get("/api/watchlist").json()
    nvda = next(w for w in items if w["symbol"] == "NVDA")
    # fake history is a strong uptrend at 2x SPY → technical score, live source.
    assert nvda["scoreSource"] == "technical (live)"
    assert isinstance(nvda["score"], (int, float))


def test_backtest_endpoint_runs_over_history():
    r = client.get("/api/backtest?symbols=NVDA,MSFT&threshold=0").json()
    assert r["available"] is True
    assert "strategyReturnPct" in r and "benchmarkReturnPct" in r and "excessPct" in r
    # 2x-SPY names held vs SPY benchmark → strategy beats benchmark.
    assert r["excessPct"] > 0
    assert r["scores"]  # real technical-trend scores surfaced


def test_dcf_endpoint_scenarios_ordered_and_validates():
    common = {"base_revenue": 100.0, "operating_margin": 0.20, "tax_rate": 0.15,
              "capex_pct": 0.05, "shares_out": 10.0, "net_cash": 0.0, "wacc": 0.10}
    body = {
        "bear": {**common, "revenue_growth": 0.02, "terminal_growth": 0.01},
        "base": {**common, "revenue_growth": 0.10, "terminal_growth": 0.03},
        "bull": {**common, "revenue_growth": 0.20, "terminal_growth": 0.045},
    }
    r = client.post("/api/valuation/dcf", json=body).json()
    assert r["bear"]["fairValuePerShare"] < r["base"]["fairValuePerShare"] < r["bull"]["fairValuePerShare"]
    # Invalid (wacc <= terminal_growth) → 422, not a 500.
    bad = client.post("/api/valuation/dcf", json={"assumptions": {"base_revenue": 100, "wacc": 0.02, "terminal_growth": 0.05}})
    assert bad.status_code == 422


def test_prices_endpoint_has_series_and_ma_overlays():
    body = client.get("/api/tickers/NVDA/prices").json()
    assert body["series"], "expected stored price history"
    last = body["series"][-1]
    assert "close" in last and "volume" in last
    # 70 days of fake history → 50DMA present at the end, 200DMA still None.
    assert last["ma50"] is not None
    assert last["ma200"] is None
    # Early points have no 50DMA yet.
    assert body["series"][0]["ma50"] is None
