import { AGENTS, AS_OF } from "@/lib/mock";
import { AiMeta, Panel } from "@/components/ui";

export default function DeskPage() {
  return (
    <div className="space-y-2">
      <Panel title="AI Analyst Desk — Debate Flow" right={<span className="text-[10px] text-term-dim">MOCK · Phase 5 wires Claude subagents</span>}>
        <p className="text-[11px] text-term-dim">
          Data Engineer → Filing Analyst → [Fundamental · Technical · Macro · News] → Bull vs Bear debate →
          Valuation → Risk Manager → Portfolio Manager → Audit Agent gate → human review
        </p>
      </Panel>
      <div className="grid grid-cols-1 gap-2 lg:grid-cols-2 2xl:grid-cols-3">
        {AGENTS.map((a) => (
          <Panel key={a.agentName} title={a.agentName}>
            <div className="text-[10px] uppercase text-term-dim">TASK: {a.task}</div>
            <p className="mt-1">{a.summary}</p>
            <AiMeta sources={a.sources} asOf={AS_OF} confidence={a.confidence} missingData={a.missingData} warnings={a.warnings} />
          </Panel>
        ))}
      </div>
    </div>
  );
}
