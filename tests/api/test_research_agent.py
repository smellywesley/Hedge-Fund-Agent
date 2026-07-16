import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "apps" / "api"))

from app.research_agent import _parse_json, generate_research


def test_no_key_is_blocked_not_faked(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    r = generate_research("NVDA", {"fundamentals": "x"})
    assert r["blocked"] is True
    assert "ANTHROPIC_API_KEY" in r["reason"]
    assert "snapshot" not in r  # nothing fabricated


def test_parse_json_tolerates_fences_and_prose():
    assert _parse_json('{"a": 1}') == {"a": 1}
    assert _parse_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert _parse_json('Here you go:\n{"a": 1, "b": 2}\nThanks') == {"a": 1, "b": 2}
    assert _parse_json("not json at all") is None


from app.research_agent import audit_note


def test_audit_gate_rules():
    # Valid note passes.
    ok, v = audit_note({"sources": ["10-K"], "bear_case": "real risks exist",
                        "confidence": "Medium", "snapshot": "x"})
    assert ok and v == []
    # Unsourced → blocked.
    ok, v = audit_note({"sources": [], "bear_case": "x", "confidence": "Low"})
    assert not ok and any("source" in x.lower() for x in v)
    # No bear case → blocked.
    ok, v = audit_note({"sources": ["s"], "bear_case": "", "confidence": "Low"})
    assert not ok and any("bear" in x.lower() for x in v)
    # Certainty language → blocked.
    ok, v = audit_note({"sources": ["s"], "bear_case": "b", "confidence": "Medium",
                        "bull_case": "This is guaranteed to double"})
    assert not ok and any("certainty" in x.lower() for x in v)
    # Bad confidence → blocked.
    ok, v = audit_note({"sources": ["s"], "bear_case": "b", "confidence": "banana"})
    assert not ok and any("confidence" in x.lower() for x in v)
