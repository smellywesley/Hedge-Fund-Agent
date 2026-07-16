"use client";
import { useState } from "react";
import { API } from "@/lib/api";
import { Panel, Pct, Table } from "./ui";

interface TraceStep { step: number; held: string[]; stratRetPct: number; benchRetPct: number; }
interface BacktestResult {
  available: boolean;
  note?: string;
  strategyReturnPct?: number;
  benchmarkReturnPct?: number;
  excessPct?: number;
  window?: number;
  steps?: number;
  trace?: TraceStep[];
  scores?: Record<string, number>;
  signal?: string;
  source?: string;
  asOf?: string;
}

// Compounding equity curve from per-step strategy returns → inline SVG.
function EquityCurve({ trace }: { trace: TraceStep[] }) {
  if (trace.length < 2) return null;
  const W = 560, H = 90, PAD = 4;
  let g = 1;
  const pts = trace.map((t) => (g *= 1 + t.stratRetPct / 100));
  const series = [1, ...pts];
  const min = Math.min(...series), max = Math.max(...series);
  const x = (i: number) => PAD + (i / (series.length - 1)) * (W - 2 * PAD);
  const y = (v: number) => max === min ? H / 2 : PAD + (1 - (v - min) / (max - min)) * (H - 2 * PAD);
  const line = series.map((v, i) => `${x(i)},${y(v)}`).join(" ");
  const up = series[series.length - 1] >= 1;
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" preserveAspectRatio="none">
      <polyline points={line} fill="none" stroke={up ? "#2ee06f" : "#ff4d4d"} strokeWidth="1.5" />
    </svg>
  );
}

export function BacktestPanel() {
  const [symbols, setSymbols] = useState("NVDA,TSM,MSFT");
  const [threshold, setThreshold] = useState(50);
  const [data, setData] = useState<BacktestResult | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function run() {
    setError(""); setBusy(true);
    try {
      const url = `${API}/api/backtest?symbols=${encodeURIComponent(symbols)}&threshold=${threshold}`;
      const r = await fetch(url, { cache: "no-store" });
      if (!r.ok) throw new Error(`API ${r.status}`);
      setData(await r.json());
    } catch (e) {
      setData(null);
      setError(String(e instanceof Error ? e.message : e) + " — is the API running?");
    } finally {
      setBusy(false);
    }
  }

  return (
    <Panel
      title="Signal Backtest"
      right={<span className="text-[10px] text-term-dim">stored price history · paper simulation</span>}
    >
      <div className="mb-2 flex flex-wrap items-center gap-2">
        <input
          className="w-48 border border-term-border bg-black/40 px-2 py-0.5 text-term-amber outline-none focus:border-term-amber"
          value={symbols} onChange={(e) => setSymbols(e.target.value.toUpperCase())} placeholder="NVDA,TSM,MSFT"
        />
        <label className="text-[10px] text-term-dim">score &gt;</label>
        <input
          type="number" className="w-16 border border-term-border bg-black/40 px-1 py-0.5 text-term-amber outline-none focus:border-term-amber"
          value={threshold} onChange={(e) => setThreshold(Number(e.target.value))}
        />
        <button onClick={run} disabled={busy}
          className="border border-term-amber px-2 py-0.5 text-term-amber hover:bg-term-amber/10 disabled:opacity-50">
          {busy ? "…" : "RUN BACKTEST"}
        </button>
      </div>

      {error && <p className="text-term-red">⚠ {error}</p>}
      {data && data.available === false && <p className="text-term-amber">⚠ {data.note}</p>}

      {data && data.available && (
        <>
          <Table
            headers={["Strategy", "Benchmark (SPY)", "Excess", "Window", "Steps"]}
            rows={[[
              <Pct key="s" value={data.strategyReturnPct!} />,
              <Pct key="b" value={data.benchmarkReturnPct!} />,
              <span key="e" className={data.excessPct! >= 0 ? "text-term-green" : "text-term-red"}>
                {data.excessPct! >= 0 ? "+" : ""}{data.excessPct}%
              </span>,
              `${data.window}d`,
              data.steps,
            ]]}
          />
          <div className="mt-2 text-[10px] text-term-dim">Signal: {data.signal}</div>
          <EquityCurve trace={data.trace ?? []} />
          <div className="mt-1 text-[10px]">
            <span className="text-term-dim">Technical scores: </span>
            {Object.entries(data.scores ?? {}).map(([sym, sc]) => (
              <span key={sym} className="mr-2">
                <span className="text-term-blue">{sym}</span> <span className={sc > threshold ? "text-term-green" : "text-term-dim"}>{sc}</span>
              </span>
            ))}
          </div>
          <p className="mt-2 text-[10px] text-term-amber">
            Past simulated performance is not indicative of future results. Educational / paper simulation only — not investment advice.
          </p>
        </>
      )}
    </Panel>
  );
}
