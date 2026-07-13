import { AS_OF, SCREENER_CATEGORIES, SCREENER_RESULTS } from "@/lib/mock";
import { ConfidenceBadge, Panel, Table } from "@/components/ui";

export default function ScreenerPage() {
  return (
    <div className="grid grid-cols-1 gap-2 xl:grid-cols-3">
      <Panel title="Screening Filters (mock)">
        <Table
          headers={["Category", "Example filters"]}
          rows={SCREENER_CATEGORIES.map((c) => [
            <span key="c" className="text-term-blue">{c.category}</span>,
            <span key="f" className="text-term-dim">{c.filters}</span>,
          ])}
        />
        <p className="mt-2 text-[10px] text-term-dim">Phase 3 wires these to live data. Filters are illustrative.</p>
      </Panel>

      <Panel title="Screen Results" className="xl:col-span-2" right={<span className="text-[10px] text-term-dim">AS OF {AS_OF}</span>}>
        <div className="space-y-2">
          {SCREENER_RESULTS.map((r) => (
            <div key={r.symbol} className="border border-term-border p-2">
              <div className="flex items-center justify-between">
                <span><span className="text-term-blue">{r.symbol}</span> · {r.company}</span>
                <ConfidenceBadge level={r.confidence} />
              </div>
              <div className="mt-1 grid gap-1 md:grid-cols-2">
                <div><span className="text-term-green">INCLUDED:</span> {r.reasonIncluded}</div>
                <div><span className="text-term-red">CAREFUL:</span> {r.reasonCareful}</div>
              </div>
              <div className="mt-1 text-term-amber">NEXT: {r.nextAction}</div>
            </div>
          ))}
        </div>
        <p className="mt-2 text-[10px] text-term-dim">
          The screener never outputs "top stocks" — every candidate ships with a reason to be careful.
        </p>
      </Panel>
    </div>
  );
}
