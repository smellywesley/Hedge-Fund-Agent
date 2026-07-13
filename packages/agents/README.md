# Agent Prompt Library

One markdown file per analyst agent. In Phase 5 these become Claude Code
subagent system prompts. Every agent must return the contract in
`docs/agent_contracts.md` (structured JSON + markdown summary, with sources,
confidence, missing_data, warnings). The Audit Agent gates all output.

Shared rules for every agent:
- Every factual claim cites a source or is labeled an assumption.
- Never present research as financial advice or certainty.
- Paper/simulation terminology only — no real-trade language.
- Missing or stale data must be declared, and it downgrades confidence.
