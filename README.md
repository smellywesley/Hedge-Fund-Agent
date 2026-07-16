# Terminal Alpha

Bloomberg-inspired AI equity research terminal — **educational research and
paper-portfolio simulator**. No brokerage execution, no real-money trading,
no auto-trading, not financial advice. All portfolio functionality is
paper/simulation only.

Current state: **Phase 2 (persistence) + a Phase 3 slice (live prices)**.

- Watchlist, paper positions, decision journal, and audit log persist in a
  database (SQLite by default, zero setup; Postgres via `DATABASE_URL`).
- Prices are **live via yfinance** (5-min cache) with automatic mock fallback
  and explicit warnings when the fetch fails. Paper-fund P&L, AUM, exposure,
  and every risk rule are computed from real prices + DB positions.
- Research reports, agent outputs, filings, and news content are still mock
  (Phases 3–5).

## Runbook (local, no Docker)

Prereqs: Node 20+, Python 3.11+.

**1. Backend (terminal 1):**

```bash
cd apps/api
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
# → http://localhost:8000/api/health  (interactive docs at /docs)
# First run creates + seeds apps/api/terminal_alpha.db (SQLite)
```

**2. Frontend (terminal 2):**

```bash
cd apps/web
npm install
npm run dev
# → http://localhost:3000  (redirects to /markets)
```

The ticker strip shows `LIVE` when yfinance quotes are flowing; panel badges
show `LIVE · yfinance`, `DB + MOCK PRICES`, or `API OFFLINE — MOCK FALLBACK`.
Command bar: `NVDA`, `ER NVDA`, `DCF NVDA`, `NEWS NVDA`, `RISK PORT`,
`WL ADD NVDA` / `WL REMOVE NVDA` (persists to DB), `FUND HEALTH`, `REPORT NVDA`.

### Using Postgres instead of SQLite

```bash
docker compose up -d postgres
pip install psycopg2-binary
set DATABASE_URL=postgresql://terminal:terminal@localhost:5432/terminal_alpha  # PowerShell: $env:DATABASE_URL=...
uvicorn app.main:app --reload --port 8000
```

## Runbook (Docker)

```bash
docker compose up --build web api
```

## Tests

```bash
pip install pytest httpx fastapi sqlalchemy
python -m pytest tests/ -q
# Tests run against a throwaway SQLite DB and never call Yahoo.
```

## Repository map

```text
apps/web                  Next.js terminal UI (10 tabs; lib/api.ts fetches backend,
                          lib/mock.ts is the offline fallback)
apps/api                  FastAPI backend: app/db.py (persistence), app/prices.py
                          (yfinance provider), app/main.py (endpoints)
packages/research_engine  Component scoring + confidence logic
packages/agents           13 analyst-agent prompt files (Phase 5 orchestration)
packages/mcp              OpenBB / SEC / FRED / custom connector placeholders
db/schema.sql             Full Postgres target schema (app models a subset so far)
docs/                     architecture, product spec, data sources, agent contracts,
                          scoring methodology, report templates
tests/                    scoring engine + API endpoint tests (17)
```

## Phase roadmap

1. ~~UI shell + mock API~~ ✅
2. ~~Persistence (watchlist, paper positions, journal, audit logs)~~ ✅
3. ~~Data connectors — yfinance prices + history, SEC EDGAR filings, real regime from macro~~ ✅ (OpenBB deferred)
4. Real research engine — ✅ NAV history, real P&L, cash bookkeeping, beta/vol/drawdown/correlations, backtest engine, editable DCF, **5 of 9 score components real** (technical/liquidity from prices; business-quality/balance-sheet/valuation from SEC XBRL)
5. Claude subagent (quant-coder) — real analyst narrative — **prepped, see `docs/phase_b_narrative_task.md`** (runs Jul 18+)
6. Report export (md/HTML/PDF) + user accounts — pending

**Deploy:** ready — see `DEPLOY.md` (Vercel web + Railway API/Postgres).

## Score components — real vs mock (as of Phase C)

| Real (5) | Source | Mock (4) |
|---|---|---|
| technical_trend | price history (50/200DMA, RS) | growth_momentum |
| liquidity_risk | dollar ADV | catalyst_strength |
| business_quality | SEC XBRL margins | estimate_revision |
| balance_sheet | SEC XBRL leverage/cash | news_sentiment |
| valuation | SEC XBRL earnings yield | |
