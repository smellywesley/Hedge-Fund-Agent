# Architecture

Terminal Alpha is an educational equity-research terminal and paper-portfolio
simulator. No brokerage execution, no real-money trading, no financial advice.

## System flow

```text
Data connectors (Phase 3)          Phase 1: mock data module
→ FastAPI backend (apps/api)
→ Research engine (packages/research_engine: scoring, valuation, risk)
→ Agent layer (packages/agents + packages/mcp, Phase 5)
→ Next.js terminal UI (apps/web)
→ Reports + audit trail (Phase 2+ persistence)
```

## Components

| Component | Location | Current state (Phase 2 + live-price slice) |
|---|---|---|
| Terminal UI | `apps/web` | All 10 tabs; markets/watchlist/fund/risk fetch the API with mock fallback |
| API | `apps/api` | FastAPI: DB-backed CRUD + live quotes; research/agents content still mock |
| Persistence | `apps/api/app/db.py` | SQLAlchemy — SQLite default, Postgres via `DATABASE_URL` |
| Price provider | `apps/api/app/prices.py` | yfinance, 5-min cache, mock fallback with warnings |
| Research engine | `packages/research_engine` | Component scoring + confidence (real logic, mock inputs) |
| Agent prompts | `packages/agents` | 13 prompt files; orchestration in Phase 5 |
| MCP connectors | `packages/mcp` | Placeholders for OpenBB / SEC / FRED / custom |
| Database schema | `db/schema.sql` | Full Postgres target; app models the used subset |
| Docker | `docker-compose.yml` | web + api + postgres (opt-in) + redis (Phase 4+) |

## Frontend

Next.js 14 (App Router) + TypeScript + Tailwind. Custom terminal-style
components (no shadcn — the aesthetic is fully custom). Layout shell:
command bar + ticker strip on top, sidebar tabs left, data-freshness bottom
bar. Dynamic tabs (Markets, Watchlist, Paper Fund, Risk) fetch the backend
via `lib/api.ts` (`useApi` hook) and fall back to `lib/mock.ts` when the API
is down — every panel carries a provenance badge (`LIVE · yfinance`,
`DB + MOCK PRICES`, or `API OFFLINE — MOCK FALLBACK`). Static research
content still renders from mock until Phases 3–5.

## Backend

FastAPI (`apps/api/app/main.py`). Watchlist, paper positions, decision
journal, and audit log are DB-backed CRUD; the paper fund and every risk rule
(concentration, sector limits, catalyst clustering, 7-day review) are
computed from DB positions × live prices. Remaining `# CONNECTOR:` comments
mark OpenBB / SEC EDGAR / FRED integration points. The research score
endpoint runs the real `research_engine.scoring` functions over mock
component inputs. New endpoints return camelCase (matching the frontend
types); legacy mock endpoints stay snake_case until their phase rewrite.

## Data trust hierarchy

SEC filings > investor relations > transcripts > data vendors > news wires >
social sentiment > AI summaries. Every payload carries `source`, `as_of`,
`confidence`, and `missing_data`.

## Phase roadmap

1. ~~UI shell + mock API~~ ✅
2. ~~Persistence (watchlist, paper positions, journal, audit logs)~~ ✅
3. Data connectors — yfinance prices ✅; OpenBB, SEC EDGAR, FRED remain
4. Real research engine (scoring features, DCF, risk, exposure)
5. Claude subagent orchestration + Audit Agent enforcement
6. Report export (md/HTML/PDF)
