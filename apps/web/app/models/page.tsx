import { DCF } from "@/lib/mock";
import { Panel, Table } from "@/components/ui";

export default function ModelsPage() {
  return (
    <div className="space-y-2">
      <p className="border border-term-amber/40 bg-term-amber/5 p-2 text-[10px] text-term-amber">
        {DCF.disclaimer}
      </p>

      <div className="grid grid-cols-1 gap-2 xl:grid-cols-2">
        <Panel title="DCF Assumptions (NVDA mock)">
          <Table
            headers={["Assumption", "Bear", "Base", "Bull"]}
            rows={DCF.assumptions.map((a) => [
              a.name,
              <span key="be" className="text-term-red">{a.bear}</span>,
              <span key="ba" className="text-term-amber">{a.base}</span>,
              <span key="bu" className="text-term-green">{a.bull}</span>,
            ])}
          />
          <p className="mt-2 text-[10px] text-term-dim">Phase 4 makes these editable with live recalculation.</p>
        </Panel>

        <Panel title="Scenario Cases">
          <Table
            headers={["Case", "Fair Value", "Narrative"]}
            rows={DCF.cases.map((c) => [
              <span key="n" className={c.name === "Bull" ? "text-term-green" : c.name === "Bear" ? "text-term-red" : "text-term-amber"}>{c.name}</span>,
              c.fairValue,
              <span key="no" className="text-term-dim">{c.note}</span>,
            ])}
          />
          <p className="mt-2 text-term-amber">Range $95–$240: terminal assumptions dominate — treat point estimates with suspicion.</p>
        </Panel>

        <Panel title="Sensitivity Table (placeholder)">
          <p className="text-term-dim">Phase 4: WACC × terminal-growth grid showing fair-value fragility. Every model must show sensitivity to its key assumptions.</p>
        </Panel>
        <Panel title="Comparable Multiples (placeholder)">
          <p className="text-term-dim">Phase 4: peer P/E, EV/EBITDA, P/S, FCF yield vs sector and vs own history.</p>
        </Panel>
        <Panel title="Monte Carlo (placeholder)">
          <p className="text-term-dim">Phase 4: scenario distribution over assumption ranges — a distribution, never certainty.</p>
        </Panel>
        <Panel title="Model Rules">
          <ul className="list-inside list-disc space-y-1 text-term-dim">
            <li>Every model shows its assumptions.</li>
            <li>Every model supports bear/base/bull.</li>
            <li>Every model shows sensitivity to key assumptions.</li>
            <li>Every valuation output carries confidence + missing-data warnings.</li>
          </ul>
        </Panel>
      </div>
    </div>
  );
}
