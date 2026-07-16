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


def _call_claude(client, model: str, system: str, prompt: str, max_tokens: int = 1200):
    """Single Claude call → (text, usage_dict). The seam tests monkeypatch so
    the multi-agent flow is verifiable without ever hitting the API."""
    msg = client.messages.create(
        model=model, max_tokens=max_tokens, system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(b.text for b in msg.content if getattr(b, "type", None) == "text")
    return text, {"input_tokens": msg.usage.input_tokens, "output_tokens": msg.usage.output_tokens}


def _add_usage(total: dict, u: dict) -> dict:
    return {k: total.get(k, 0) + u.get(k, 0) for k in ("input_tokens", "output_tokens")}


def generate_research(symbol: str, context: dict, api_key: str | None = None,
                      model: str | None = None, mode: str = "debate") -> dict:
    """Generate a real analyst note for `symbol` from `context` (facts/filings/
    price summary/headlines). mode="debate" (default) runs a three-agent flow —
    independent Bull and Bear researchers, then a PM synthesis — mirroring the
    agent-desk design; mode="single" is one cheaper call. Returns the parsed
    note + metadata, or a blocked marker."""
    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    if not key:
        return {"blocked": True, "reason": "ANTHROPIC_API_KEY not configured — set it to enable live AI research",
                "symbol": symbol, "asOf": now}
    use_model = model or DEFAULT_MODEL
    data_block = f"Ticker: {symbol}\n\nReal data available (use it, cite it):\n{json.dumps(context, indent=2, default=str)}"
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=key)
        usage = {"input_tokens": 0, "output_tokens": 0}

        if mode == "debate":
            bull, u = _call_claude(
                client, use_model,
                SYSTEM + " You are the BULL researcher — build the strongest honest positive thesis. Advocacy role: your note is read alongside an independent bear note. Plain text, cite the data.",
                data_block, max_tokens=700)
            usage = _add_usage(usage, u)
            bear, u = _call_claude(
                client, use_model,
                SYSTEM + " You are the BEAR researcher — build the strongest honest negative thesis: failure modes, valuation fragility, what breaks the bull case. Plain text, cite the data.",
                data_block, max_tokens=700)
            usage = _add_usage(usage, u)
            synth_prompt = (
                f"{data_block}\n\n--- BULL RESEARCHER NOTE ---\n{bull}\n\n"
                f"--- BEAR RESEARCHER NOTE ---\n{bear}\n\n"
                "As the Portfolio Manager, weigh the debate and produce the final note "
                f"as a JSON object matching exactly this shape:\n{SCHEMA_HINT}\n"
                "The red_team field must state what would prove the synthesis wrong."
            )
            text, u = _call_claude(client, use_model, SYSTEM, synth_prompt, max_tokens=2000)
            usage = _add_usage(usage, u)
            agents = ["bull_researcher", "bear_researcher", "pm_synthesis"]
        else:
            prompt = f"{data_block}\n\nProduce a concise research note as a JSON object matching exactly this shape:\n{SCHEMA_HINT}"
            text, usage = _call_claude(client, use_model, SYSTEM, prompt, max_tokens=2000)
            agents = ["single_analyst"]

        note = _parse_json(text)
        if note is None:
            return {"blocked": True, "reason": "Model did not return parseable JSON",
                    "symbol": symbol, "asOf": now, "raw": text[:500]}
        return {
            "blocked": False, "symbol": symbol, "asOf": now, "model": use_model,
            "mode": mode, "agents": agents,
            "source": "Anthropic API (live)", "usage": usage,
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
