# Agent Contracts

13 agents (prompt files in `packages/agents/`). Debate flow:

```text
Data Engineer → Filing Analyst → {Fundamental, Technical, Macro, News} in parallel
→ Bull vs Bear debate → Valuation Analyst (bear/base/bull)
→ Risk Manager → Portfolio Manager memo → Audit Agent gate → human review
```

## Required output schema (every agent)

```json
{
  "agent_name": "Filing Analyst",
  "symbol": "NVDA",
  "task": "Summarize latest 10-K",
  "summary": "...",
  "key_findings": [],
  "risks": [],
  "sources": [],
  "assumptions": [],
  "missing_data": [],
  "confidence": "High | Medium | Low",
  "requires_human_review": true
}
```

Rules:
- Every factual claim cites a source or is labeled an assumption.
- Missing/stale data must appear in `missing_data` and downgrades confidence.
- Bull/Bear are advocacy roles; only the debate (both sides) informs the PM.
- PM output is a *research* action (research/review/watch/paper-simulate),
  never a trade instruction, and always ends with the simulation disclaimer.

## Audit Agent blocking rules

Block or downgrade any output that: has valuation without assumptions; makes
claims without sources; uses stale data without warning; presents a
recommendation as certainty; confuses paper simulation with real trading;
relies on unsupported news/social claims; omits major known risks; or lacks
a bear case. Only logged human review can override.
