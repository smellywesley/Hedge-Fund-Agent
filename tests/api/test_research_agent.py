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


def test_debate_flow_runs_three_agents_and_aggregates(monkeypatch):
    import sys, types
    from app import research_agent as ra

    fake = types.ModuleType("anthropic")
    fake.Anthropic = lambda api_key=None: object()
    monkeypatch.setitem(sys.modules, "anthropic", fake)

    calls = []
    def fake_call(client, model, system, prompt, max_tokens=1200):
        calls.append((system, prompt))
        if "BULL" in system:
            return "bull says up", {"input_tokens": 10, "output_tokens": 5}
        if "BEAR" in system:
            return "bear says down", {"input_tokens": 10, "output_tokens": 5}
        return ('{"snapshot":"s","business_model":"bm","bull_case":"b+","bear_case":"b-",'
                '"red_team":"rt","key_risks":["k"],"sources":["10-K"],"confidence":"Medium",'
                '"missing_data":[]}',
                {"input_tokens": 20, "output_tokens": 10})
    monkeypatch.setattr(ra, "_call_claude", fake_call)

    r = ra.generate_research("NVDA", {"x": 1}, api_key="test-key", mode="debate")
    assert r["blocked"] is False
    assert r["agents"] == ["bull_researcher", "bear_researcher", "pm_synthesis"]
    assert r["usage"] == {"input_tokens": 40, "output_tokens": 20}  # 3 calls summed
    assert r["bear_case"] == "b-"
    # The PM synthesis actually received BOTH debate notes.
    synth_prompt = calls[-1][1]
    assert "bull says up" in synth_prompt and "bear says down" in synth_prompt
    assert len(calls) == 3


def test_single_mode_is_one_call(monkeypatch):
    import sys, types
    from app import research_agent as ra

    fake = types.ModuleType("anthropic")
    fake.Anthropic = lambda api_key=None: object()
    monkeypatch.setitem(sys.modules, "anthropic", fake)
    calls = []
    def fake_call(client, model, system, prompt, max_tokens=1200):
        calls.append(1)
        return ('{"snapshot":"s","bull_case":"b","bear_case":"br","red_team":"rt",'
                '"sources":["x"],"confidence":"Low","missing_data":[]}',
                {"input_tokens": 5, "output_tokens": 5})
    monkeypatch.setattr(ra, "_call_claude", fake_call)
    r = ra.generate_research("NVDA", {}, api_key="k", mode="single")
    assert r["agents"] == ["single_analyst"] and len(calls) == 1
