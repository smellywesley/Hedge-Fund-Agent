"""Live AI research generation — the deployed-app version of the quant-coder.

A Claude Code subagent can't run inside a hosted web app, so the "Run Research"
button calls the Anthropic API directly from the backend, gated by
ANTHROPIC_API_KEY (the user's own key = the "tokens" spent per press). The
prompt is grounded in REAL data already in the app (SEC filings + XBRL facts +
price summary) and the model is instructed to cite sources, include a bear
case, and stay educational / paper-simulation.

No key configured → a BLOCKED marker (never a fabricated report).
"""
import json
import os
from datetime import datetime, timezone

# Public Anthropic API model id — override with RESEARCH_MODEL if your account
# uses a different id. Documented in DEPLOY.md.
DEFAULT_MODEL = os.environ.get("RESEARCH_MODEL", "claude-sonnet-4-5")

SYSTEM = (
    "You are an equity research analyst for an EDUCATIONAL paper-simulation "
    "terminal. Output is research, never investment advice, and no real trades "
    "are ever placed. Rules: ground every claim in the provided data or label it "
    "an assumption; always include a bear case; never present a recommendation as "
    "certainty; note missing data. Respond with ONLY a JSON object, no prose."
)

SCHEMA_HINT = (
    '{"snapshot": str, "business_model": str, "bull_case": str, "bear_case": str, '
    '"red_team": str, "key_risks": [str], "sources": [str], "confidence": '
    '"High|Medium|Low", "missing_data": [str]}'
)


def generate_research(symbol: str, context: dict, api_key: str | None = None,
                      model: str | None = None) -> dict:
    """Generate a real analyst note for `symbol` from `context` (facts/filings/
    price summary). Returns the parsed note + metadata, or a blocked marker."""
    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    if not key:
        return {"blocked": True, "reason": "ANTHROPIC_API_KEY not configured — set it to enable live AI research",
                "symbol": symbol, "asOf": now}
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=key)
        prompt = (
            f"Ticker: {symbol}\n\nReal data available (use it, cite it):\n"
            f"{json.dumps(context, indent=2, default=str)}\n\n"
            f"Produce a concise research note as a JSON object matching exactly this shape:\n{SCHEMA_HINT}"
        )
        msg = client.messages.create(
            model=model or DEFAULT_MODEL,
            max_tokens=2000,
            system=SYSTEM,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(b.text for b in msg.content if getattr(b, "type", None) == "text")
        note = _parse_json(text)
        if note is None:
            return {"blocked": True, "reason": "Model did not return parseable JSON",
                    "symbol": symbol, "asOf": now, "raw": text[:500]}
        return {
            "blocked": False, "symbol": symbol, "asOf": now, "model": model or DEFAULT_MODEL,
            "source": "Anthropic API (live)",
            "usage": {"input_tokens": msg.usage.input_tokens, "output_tokens": msg.usage.output_tokens},
            **note,
        }
    except Exception as e:
        return {"blocked": True, "reason": f"AI research call failed: {e}", "symbol": symbol, "asOf": now}


def audit_note(note: dict) -> tuple[bool, list[str]]:
    """Audit-Agent gate (docs/agent_contracts.md): a generated note is only
    storable if it cites sources, includes a bear case, carries a confidence,
    and never presents the thesis as certainty. Returns (ok, violations)."""
    violations = []
    if not note.get("sources"):
        violations.append("No sources cited — every claim needs a source")
    if not str(note.get("bear_case", "")).strip():
        violations.append("Missing bear case — reports without one are blocked")
    if note.get("confidence") not in ("High", "Medium", "Low"):
        violations.append("Missing or invalid confidence rating")
    text = " ".join(str(note.get(k, "")) for k in ("snapshot", "bull_case", "bear_case", "red_team")).lower()
    for phrase in ("guaranteed", "can't lose", "cannot lose", "certain to", "sure thing", "risk-free"):
        if phrase in text:
            violations.append(f"Certainty language ('{phrase}') — recommendations must never be presented as certainty")
    return (not violations, violations)


def _parse_json(text: str) -> dict | None:
    """Parse the model's JSON, tolerating ```json fences or surrounding prose."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1].removeprefix("json").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if 0 <= start < end:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                return None
        return None
