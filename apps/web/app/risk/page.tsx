"use client";
import { RISK } from "@/lib/mock";
import { useApi } from "@/lib/api";
import type { RiskSummary } from "@/lib/types";
import { SourceBadge } from "@/components/SourceBadge";
import { Panel, StatusBadge, Table } from "@/components/ui";

type Risk = RiskSummary & { live?: boolean; correlations?: { a: string; b: string; corr: number }[] };

export default function RiskPage() {
  const { data, status } = useApi<Risk>("/api/paper-fund/risk", RISK);
  return (
    <div className="space-y-2">
      <Panel
        title="Catalyst Clustering Warnings"
        right={<span className="flex items-center gap-2 text-[10px] text-term-dim">{data.source} <SourceBadge status={status} live={data.live} /></span>}
      >
        {data.catalystWarnings.length === 0 && <p className="text-term-dim">No clustering warnings.</p>}
        {data.catalystWarnings.map((w, i) => (
          <p key={i} className="text-term-amber">⚠ {w}</p>
        ))}
      </Panel>

      <div className="grid grid-cols-1 gap-2 xl:grid-cols-2">
        <Panel title="Sector Exposure (computed from paper positions)">
          <Table
            headers={["Sector", "Exposure", "Limit", "Status"]}
            rows={data.sectorExposure.map((s) => [s.sector, `${s.pct}%`, `${s.limit}%`, <StatusBadge key="st" status={s.status} />])}
          />
        </Panel>
        <Panel title="Single-Name Concentration (computed)">
          <Table
            headers={["Symbol", "Size", "Limit", "Status"]}
            rows={data.concentration.map((c) => [
              <span key="s" className="text-term-blue">{c.symbol}</span>, `${c.pct}%`, `${c.limit}%`, <StatusBadge key="st" status={c.status} />,
            ])}
          />
        </Panel>
        <Panel title="Portfolio Metrics (computed from NAV history)">
          <Table
            headers={["Metric", "Value", "Note"]}
            rows={data.metrics.map((m) => [m.name, <span key="v" className="text-term-text">{m.value}</span>, <span key="n" className="text-term-dim">{m.note}</span>])}
          />
        </Panel>
        <Panel title="Holdings Correlation (60d daily returns)">
          {!data.correlations?.length && <p className="text-term-dim">Needs price history — start the API and refresh.</p>}
          {!!data.correlations?.length && (
            <Table
              headers={["Pair", "Correlation"]}
              rows={data.correlations.map((c) => [
                <span key="p" className="text-term-blue">{c.a} / {c.b}</span>,
                <span key="c" className={c.corr >= 0.8 ? "text-term-red" : c.corr >= 0.5 ? "text-term-amber" : "text-term-green"}>
                  {c.corr.toFixed(2)}{c.corr >= 0.8 ? " ⚠ crowded" : ""}
                </span>,
              ])}
            />
          )}
          <p className="mt-2 text-[10px] text-term-dim">Pairs ≥0.80 flag one crowded trade wearing two tickers.</p>
        </Panel>
        <Panel title="Risk Rules Checklist (computed)">
          <Table
            headers={["Rule", "Status"]}
            rows={data.rulesChecklist.map((r) => [r.rule, <StatusBadge key="s" status={r.status} />])}
          />
        </Panel>
      </div>
    </div>
  );
}
