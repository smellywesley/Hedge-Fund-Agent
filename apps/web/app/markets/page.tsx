"use client";
import { MARKET } from "@/lib/mock";
import { useApi } from "@/lib/api";
import type { MarketSnapshot, Quote } from "@/lib/types";
import { SourceBadge } from "@/components/SourceBadge";
import { AiMeta, Panel, Pct, Table } from "@/components/ui";

type Drivers = { vix: number; breadth: number; curve: number; dollar: number };
type Snapshot = MarketSnapshot & {
  live?: boolean; warnings?: string[];
  regime: MarketSnapshot["regime"] & { drivers?: Drivers };
};

function QuotePanel({ title, quotes }: { title: string; quotes: Quote[] }) {
  return (
    <Panel title={title}>
      <Table
        headers={["Sym", "Name", "Last", "Chg"]}
        rows={quotes.map((q) => [
          <span key="s" className="text-term-blue">{q.symbol}</span>,
          q.name,
          q.last.toLocaleString(),
          <Pct key="p" value={q.changePct} />,
        ])}
      />
    </Panel>
  );
}

export default function MarketsPage() {
  const { data, status } = useApi<Snapshot>("/api/markets/snapshot", MARKET);
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between border border-term-border bg-term-panel px-2 py-1">
        <span className="text-[10px] text-term-dim">MARKET SNAPSHOT · AS OF {data.asOf}</span>
        <SourceBadge status={status} live={data.live} />
      </div>
      {(data.warnings ?? []).map((w, i) => (
        <p key={i} className="border border-term-amber/40 bg-term-amber/5 p-1 text-[10px] text-term-amber">⚠ {w}</p>
      ))}

      <div className="grid grid-cols-1 gap-2 xl:grid-cols-3">
        <QuotePanel title="Global Indices" quotes={data.indices} />
        <QuotePanel title="Rates" quotes={data.rates} />
        <QuotePanel title="FX" quotes={data.fx} />
        <QuotePanel title="Commodities" quotes={data.commodities} />
        <QuotePanel title="Volatility" quotes={data.volatility} />

        <Panel title="Market Regime" right={<SourceBadge status={status} live={data.live} />}>
          <div className={`text-lg ${data.regime.label === "RISK-ON" ? "text-term-green" : data.regime.label === "RISK-OFF" ? "text-term-red" : "text-term-amber"}`}>
            {data.regime.label}
          </div>
          <div className="text-term-dim">Regime score: {data.regime.score}/100</div>
          {data.regime.drivers && (
            <div className="mt-1 grid grid-cols-4 gap-1 text-center text-[10px]">
              {([["VIX", data.regime.drivers.vix, 40], ["Breadth", data.regime.drivers.breadth, 30],
                 ["Curve", data.regime.drivers.curve, 20], ["Dollar", data.regime.drivers.dollar, 10]] as const).map(
                ([label, val, max]) => (
                  <div key={label} className="border border-term-border p-1">
                    <div className="text-term-dim">{label}</div>
                    <div className="text-term-text">{val}/{max}</div>
                  </div>
                ))}
            </div>
          )}
          <p className="mt-1">{data.regime.notes}</p>
        </Panel>

        <Panel title="Sector Heatmap" className="xl:col-span-2">
          <div className="grid grid-cols-3 gap-1">
            {data.sectors.map((s) => (
              <div
                key={s.symbol}
                className={`border border-term-border p-2 text-center ${
                  s.changePct >= 0 ? "bg-term-green/10" : "bg-term-red/10"
                }`}
              >
                <div className="text-term-blue">{s.symbol}</div>
                <div className="text-[10px] text-term-dim">{s.name}</div>
                <Pct value={s.changePct} />
              </div>
            ))}
          </div>
        </Panel>

        <Panel title="AI Market Brief">
          <ul className="list-inside list-disc space-y-1">
            {data.aiBrief.bullets.map((b, i) => <li key={i}>{b}</li>)}
          </ul>
          <AiMeta
            sources={data.aiBrief.sources}
            asOf={data.aiBrief.asOf}
            confidence={data.aiBrief.confidence}
            missingData={data.aiBrief.missingData}
          />
        </Panel>
      </div>
    </div>
  );
}
