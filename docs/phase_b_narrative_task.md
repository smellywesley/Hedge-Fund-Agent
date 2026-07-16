# Phase B — Real analyst narrative (quant-coder task brief)

**Status:** READY TO RUN. Blocked only by (1) the subagent weekly limit (resets
Jul 18, 6am SGT) and (2) needing a Claude Code session **rooted in this folder**
(`Wesley Financial Agent`) so the `quant-coder` agent and the `vibe-trading` MCP
actually load. Dispatch this then.

## Goal
Replace the **mock research narrative** in `apps/api/app/mock_data.py`
(`RESEARCH_NVDA`: snapshot, business_model, bull_case, bear_case, red_team,
kpis, catalysts, risk_register) with **real, sourced analyst output**, and store
it in the DB rather than a Python literal — starting with NVDA, then generalizing
to any ticker.

## Grounding data already available in the repo (no new build needed)
- `packages/mcp/sec/edgar.get_recent_filings(symbol)` — real 10-K/10-Q/8-K.
- `packages/mcp/sec/edgar.get_company_facts(symbol)` — real XBRL fundamentals.
- `apps/api/app/nav.price_series` / `PriceRow` — real price history.
- The `vibe-trading` MCP (HK agent) research tools — news, sentiment, fundamentals
  (RESEARCH/DATA tools ONLY — never the order-execution connectors).

## What the quant-coder must produce (per the agent contract in docs/agent_contracts.md)
1. A DB table `research_reports` (add to `db.py`) storing, per symbol: snapshot,
   business_model, bull_case, bear_case, red_team, catalysts, risk_register,
   plus `sources` (list), `confidence`, `missing_data`, `generated_at`.
2. A generation flow: Company/Filing/Fundamental/News analysts draft sections →
   Bull vs Bear → Risk → PM synthesis → **Audit Agent gate** (blocks unsourced
   claims, valuation-without-assumptions, missing bear case).
3. Wire `/api/research/{symbol}/run` to actually run it (replace the mock job),
   and `/api/research/{symbol}/latest` to read the stored real report, falling
   back to the mock narrative only when no real report exists (declared).
4. Tests: the generated report must carry ≥1 source per claim section and a
   bear case, or the Audit gate fails the test.

## Hard boundary (unchanged)
Paper/simulation only. The vibe-trading trade-execution tools are OFF LIMITS —
research/data tools only. No broker credentials, ever.

## How to dispatch (from a Wesley-rooted session, after Jul 18)
Invoke the `quant-coder` agent with this file as the task. It loads at
`claude-opus-4-8` / effort `max` with the boundary + conventions in its system
prompt. Because it runs from this folder, `vibe-trading` MCP tools are available.
