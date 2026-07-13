import { RESEARCH_NVDA as R, RESEARCH_SCORE } from "@/lib/mock";
import { AiMeta, ConfidenceBadge, Panel, StatusBadge, Table } from "@/components/ui";

const meta = { sources: ["MOCK research pack"], asOf: R.asOf, confidence: R.confidence, missingData: R.missingData };

export default function ResearchPage() {
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-3 border border-term-border bg-term-panel p-2">
        <span className="text-term-dim">EQUITY RESEARCH:</span>
        <span className="border border-term-amber px-2 py-0.5 text-term-amber">{R.symbol}</span>
        <button className="border border-term-border px-2 py-0.5 text-term-dim" title="Phase 5 runs the agent workflow">RUN RESEARCH (mock)</button>
        <button className="border border-term-border px-2 py-0.5 text-term-dim" title="Phase 6 builds exportable reports">BUILD REPORT (mock)</button>
        <span className="ml-auto text-[10px] text-term-dim">Phase 1 ships one full mock report: NVDA</span>
      </div>

      <div className="grid grid-cols-1 gap-2 xl:grid-cols-3">
        <Panel title="Company Snapshot">
          <p>{R.snapshot}</p>
          <AiMeta {...meta} />
        </Panel>
        <Panel title="Business Model">
          <p>{R.businessModel}</p>
          <AiMeta {...meta} />
        </Panel>
        <Panel title="Research Score">
          <div className="mb-1 text-lg text-term-green">
            {RESEARCH_SCORE.scoreTotal}/100 <ConfidenceBadge level={RESEARCH_SCORE.confidence} />
          </div>
          <Table
            headers={["Component", "Wt", "Score"]}
            rows={RESEARCH_SCORE.components.map((c) => [
              c.name,
              `${c.weightPct}%`,
              <span key="v" className={c.value >= 70 ? "text-term-green" : c.value >= 50 ? "text-term-amber" : "text-term-red"}>{c.value}</span>,
            ])}
          />
        </Panel>

        <Panel title="Financial Statement Summary">
          <Table
            headers={["Statement", "Metric", "Period", "Value"]}
            rows={R.financials.map((f) => [f.statementType, f.metric, f.fiscalPeriod, <span key="v" className="text-term-green">{f.value}</span>])}
          />
        </Panel>
        <Panel title="KPI Dashboard">
          <Table
            headers={["KPI", "Value", "Trend"]}
            rows={R.kpis.map((k) => [
              k.name,
              k.value,
              <span key="t" className={k.trend === "up" ? "text-term-green" : k.trend === "down" ? "text-term-red" : "text-term-dim"}>{k.trend === "up" ? "▲" : k.trend === "down" ? "▼" : "—"}</span>,
            ])}
          />
        </Panel>
        <Panel title="Catalyst Tracker">
          <Table headers={["Date", "Event", "Type"]} rows={R.catalysts.map((c) => [c.date, c.event, <span key="t" className="text-term-blue">{c.type}</span>])} />
        </Panel>

        <Panel title="Filing Reader (placeholder)">
          <p className="text-term-dim">Phase 3: SEC EDGAR ingestion → 10-K/10-Q/8-K summaries with direct citations. See News/Filings tab for mock filing list.</p>
        </Panel>
        <Panel title="Valuation Lab (placeholder)">
          <p className="text-term-dim">Phase 4: DCF, comps, historical multiples, sensitivity. Mock assumptions live in Model Lab tab.</p>
          <p className="mt-1">Mock range: <span className="text-term-red">$95 bear</span> · <span className="text-term-amber">$175 base</span> · <span className="text-term-green">$240 bull</span></p>
        </Panel>
        <Panel title="Risk Register">
          <Table
            headers={["Category", "Risk", "Severity"]}
            rows={R.riskRegister.map((r) => [r.category, r.risk, <StatusBadge key="s" status={r.severity === "High" ? "HIGH" : "WARNING " + r.severity} />])}
          />
        </Panel>

        <Panel title="Bull Case">
          <p className="text-term-green">{R.bullCase}</p>
          <AiMeta {...meta} warnings={["Advocacy note — read with bear case"]} />
        </Panel>
        <Panel title="Bear Case">
          <p className="text-term-red">{R.bearCase}</p>
          <AiMeta {...meta} warnings={["Advocacy note — read with bull case"]} />
        </Panel>
        <Panel title="Red-Team Critique">
          <p className="text-term-amber">{R.redTeam}</p>
          <AiMeta {...meta} />
        </Panel>
      </div>

      <Panel title="Report Builder">
        <div className="flex gap-2">
          {["Flash Note (1p)", "Investment Memo (5–10p)", "Initiating Coverage (25–40p)"].map((r) => (
            <button key={r} className="border border-term-border px-3 py-1 text-term-dim hover:border-term-amber hover:text-term-amber" title="Phase 6: report generation + export">
              {r}
            </button>
          ))}
          <span className="self-center text-[10px] text-term-dim">Placeholders — generation lands in Phase 6, gated by the Audit Agent.</span>
        </div>
      </Panel>
    </div>
  );
}
