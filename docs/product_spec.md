# Product Spec — Terminal Alpha MVP

**Boundary:** Educational research + paper-portfolio simulation only. Never
brokerage execution, real-money trading, auto-trading, or financial advice.

**Core promise:** Type a ticker → auditable research workflow out: business
summary, financials, news, filings, bull/bear debate, valuation, risk, score,
exportable report.

## Tabs

| Tab | Purpose | Phase 1 content |
|---|---|---|
| Markets | Broad context before single-stock work | Indices, rates, FX, commodities, vol, sector heatmap, regime, AI brief |
| Watchlist | Track names | Table: price, %chg, vol vs avg, score, confidence, catalyst, filing, news risk, next action |
| Screener | Find candidates | Filter categories + results with "reason included / reason careful" |
| Equity Research | **Killer feature** | Full mock NVDA report: snapshot, model, financials, KPIs, catalysts, risk register, bull/bear, red-team, report builder |
| AI Analyst Desk | Analyst committee | 13 agent cards with task/summary/confidence/sources/missing data/warnings |
| Paper Fund Lab | Simulated portfolio | AUM, cash, P&L, positions with thesis + invalidation, journal, exposure, exit rules |
| Risk Dashboard | Risk-adjusted view | Sector/name concentration, metric placeholders, catalyst clustering, rules checklist |
| News & Filings | Primary-source intel | Filing list + summaries, news feed, risk flags, trust hierarchy |
| Model Lab | Inspectable assumptions | DCF assumptions table, bear/base/bull, sensitivity + comps + Monte Carlo placeholders |
| Reports | Exportable artifacts | Flash Note / Memo / Initiating Coverage generators (placeholder), history table |

## Command bar

`NVDA` → research · `ER NVDA` → research · `DCF NVDA` → Model Lab ·
`NEWS NVDA` → News & Filings · `RISK PORT` → Risk · `WL ADD NVDA` → Watchlist ·
`FUND HEALTH` → Paper Fund · `REPORT NVDA` → Reports

## API (Phase 1, all mock)

```text
GET  /api/health
GET  /api/markets/snapshot
GET  /api/tickers/search?q=
GET  /api/tickers/{symbol}/overview|financials|filings|news
GET  /api/research/{symbol}/latest      # full NVDA report + score
POST /api/research/{symbol}/run         # mock job, returns READY
GET  /api/agents/outputs                # 13 agent cards
GET|POST /api/watchlist  DELETE /api/watchlist/{symbol}
GET|POST /api/paper-fund/positions
GET  /api/paper-fund/risk
GET  /api/reports
```

## Global UI rules

Dark Bloomberg-style density; every AI/mock card shows source, timestamp,
confidence, and missing-data warnings; human-in-the-loop — the system
recommends research actions, never executes trades.
