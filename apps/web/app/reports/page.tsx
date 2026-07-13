import { REPORTS } from "@/lib/mock";
import { ConfidenceBadge, Panel, StatusBadge, Table } from "@/components/ui";

const GENERATORS = [
  { name: "Flash Note", desc: "1 page — quick review after news/earnings" },
  { name: "Investment Memo", desc: "5–10 pages — serious research" },
  { name: "Initiating Coverage", desc: "25–40 pages — full report" },
];

export default function ReportsPage() {
  return (
    <div className="space-y-2">
      <div className="grid grid-cols-1 gap-2 md:grid-cols-3">
        {GENERATORS.map((g) => (
          <Panel key={g.name} title={g.name}>
            <p className="text-term-dim">{g.desc}</p>
            <button className="mt-2 border border-term-border px-3 py-1 text-term-dim hover:border-term-amber hover:text-term-amber" title="Phase 6: generation + markdown export">
              GENERATE (placeholder)
            </button>
          </Panel>
        ))}
      </div>

      <Panel title="Report History" right={<span className="text-[10px] text-term-dim">Markdown export lands in Phase 6</span>}>
        <Table
          headers={["ID", "Symbol", "Type", "Title", "Status", "Generated", "Conf", "Export"]}
          rows={REPORTS.map((r) => [
            r.id,
            <span key="s" className="text-term-blue">{r.symbol}</span>,
            r.reportType,
            r.title,
            <StatusBadge key="st" status={r.status} />,
            r.generatedAt,
            <ConfidenceBadge key="c" level={r.confidence} />,
            <button key="e" className="border border-term-border px-1 text-[10px] text-term-dim" title="Phase 6">MD ↓</button>,
          ])}
        />
        <p className="mt-2 text-[10px] text-term-dim">
          Reports are only exportable after the Audit Agent passes them — note the blocked LLY draft.
        </p>
      </Panel>
    </div>
  );
}
