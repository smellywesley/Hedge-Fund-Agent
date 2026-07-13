"use client";
import { FUND, JOURNAL, POSITIONS } from "@/lib/mock";
import { useApi } from "@/lib/api";
import type { DecisionJournalEntry, PaperPosition } from "@/lib/types";
import { NavChart } from "@/components/NavChart";
import { SourceBadge } from "@/components/SourceBadge";
import { Disclaimer, Panel, Pct, Table } from "@/components/ui";

type FundPayload = {
  asOf: string;
  live?: boolean;
  warnings?: string[];
  aum: number;
  cashPct: number;
  cashUsd?: number;
  dailyPnlPct: number | null;
  weeklyPnlPct: number | null;
  inceptionPnlPct?: number | null;
  pnlNote?: string;
  positions: (PaperPosition & { priceSource?: string })[];
  journal: DecisionJournalEntry[];
  exposure: { bucket: string; pct: number }[];
  exitRules: string[];
};

const FALLBACK: FundPayload = {
  asOf: FUND.asOf, aum: FUND.aum, cashPct: FUND.cashPct,
  dailyPnlPct: null, weeklyPnlPct: null, inceptionPnlPct: null,
  pnlNote: "API offline — P&L needs the backend's NAV history",
  positions: POSITIONS, journal: JOURNAL, exposure: FUND.exposure, exitRules: FUND.exitRules,
};

const pct = (v: number | null | undefined) => (v == null ? <span className="text-term-dim">—</span> : <Pct value={v} />);

export default function FundPage() {
  const { data, status } = useApi<FundPayload>("/api/paper-fund/positions", FALLBACK);
  return (
    <div className="space-y-2">
      <Disclaimer />
      {(data.warnings ?? []).map((w, i) => (
        <p key={i} className="border border-term-amber/40 bg-term-amber/5 p-1 text-[10px] text-term-amber">⚠ {w}</p>
      ))}

      <div className="grid grid-cols-2 gap-2 md:grid-cols-4">
        {[
          { label: "Paper AUM (computed)", value: `$${data.aum.toLocaleString()}` },
          { label: "Cash (bookkept)", value: `${data.cashPct}%` },
          { label: "Daily paper P&L", value: pct(data.dailyPnlPct) },
          { label: "Since inception", value: pct(data.inceptionPnlPct) },
        ].map((s) => (
          <div key={s.label} className="border border-term-border bg-term-panel p-2">
            <div className="text-[10px] uppercase text-term-dim">{s.label}</div>
            <div className="text-lg">{s.value}</div>
          </div>
        ))}
      </div>

      <NavChart />

      <Panel title="Paper Positions" right={<SourceBadge status={status} live={data.live} />}>
        <Table
          headers={["Sym", "Entry", "Current", "Src", "Unrl P&L", "Size %", "Thesis", "Invalidation Point", "Catalyst", "Risk Notes"]}
          rows={data.positions.map((p) => [
            <span key="s" className="text-term-blue">{p.symbol}</span>,
            p.entryPrice.toFixed(2),
            p.currentPrice.toFixed(2),
            <span key="src" className={p.priceSource === "yfinance" ? "text-term-green" : "text-term-dim"}>{p.priceSource ?? "MOCK"}</span>,
            <Pct key="p" value={p.unrealizedPnlPct} />,
            `${p.positionSizePct}%`,
            p.thesis,
            <span key="i" className="text-term-amber">{p.invalidationPoint}</span>,
            p.catalystDate,
            <span key="r" className="text-term-dim">{p.riskNotes}</span>,
          ])}
        />
        {data.pnlNote && !data.inceptionPnlPct && <p className="mt-1 text-[10px] text-term-dim">{data.pnlNote}</p>}
      </Panel>

      <div className="grid grid-cols-1 gap-2 xl:grid-cols-3">
        <Panel title="Exposure Map">
          {data.exposure.map((e) => (
            <div key={e.bucket} className="mb-1">
              <div className="flex justify-between text-[10px]"><span>{e.bucket}</span><span>{e.pct}%</span></div>
              <div className="h-2 bg-term-border/40">
                <div className={`h-2 ${e.bucket === "Cash" ? "bg-term-dim" : "bg-term-blue"}`} style={{ width: `${Math.min(e.pct, 100)}%` }} />
              </div>
            </div>
          ))}
        </Panel>

        <Panel title="Decision Journal">
          <Table
            headers={["Date", "Sym", "Type", "Decision", "Note"]}
            rows={data.journal.map((j) => [
              j.date,
              <span key="s" className="text-term-blue">{j.symbol}</span>,
              <span key="t" className="text-term-amber">{j.decisionType}</span>,
              j.decisionText,
              <span key="n" className="text-term-dim">{j.humanNote}</span>,
            ])}
          />
        </Panel>

        <Panel title="Exit Rules">
          <ul className="list-inside list-disc space-y-1">
            {data.exitRules.map((r, i) => <li key={i}>{r}</li>)}
          </ul>
        </Panel>
      </div>
    </div>
  );
}
