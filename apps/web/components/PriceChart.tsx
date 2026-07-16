"use client";
import { useApi } from "@/lib/api";
import { SourceBadge } from "./SourceBadge";
import { Panel } from "./ui";

interface PricePoint { date: string; close: number; volume: number; ma50: number | null; ma200: number | null; }
interface PricesPayload { symbol: string; source: string; asOf: string; warnings: string[]; series: PricePoint[]; }

const FALLBACK: PricesPayload = { symbol: "—", source: "none", asOf: "", warnings: [], series: [] };
const W = 600, H = 170, PAD = 6, VOL_H = 34;

export function PriceChart({ symbol }: { symbol: string }) {
  const { data, status } = useApi<PricesPayload>(`/api/tickers/${symbol}/prices`, FALLBACK);
  const s = data.series;

  return (
    <Panel
      title={`Price · ${data.symbol !== "—" ? data.symbol : symbol}`}
      right={<SourceBadge status={status} live={data.source.startsWith("yfinance")} />}
    >
      {data.warnings.map((w, i) => <p key={i} className="text-[10px] text-term-amber">⚠ {w}</p>)}
      {s.length < 2 ? (
        <p className="text-term-dim">No price history yet — start the API so it can backfill.</p>
      ) : (
        <Chart series={s} />
      )}
      <div className="mt-1 flex gap-3 text-[10px] text-term-dim">
        <span><span className="text-term-text">━</span> close</span>
        <span><span className="text-term-amber">━</span> 50DMA</span>
        <span><span className="text-term-blue">━</span> 200DMA</span>
        <span><span className="text-term-dim">▮</span> volume</span>
      </div>
    </Panel>
  );
}

function Chart({ series }: { series: PricePoint[] }) {
  const closes = series.map((p) => p.close);
  const priceH = H - VOL_H - PAD;
  const min = Math.min(...closes), max = Math.max(...closes);
  const x = (i: number) => PAD + (i / (series.length - 1)) * (W - 2 * PAD);
  const y = (v: number) => max === min ? priceH / 2 : PAD + (1 - (v - min) / (max - min)) * (priceH - 2 * PAD);

  // Build a polyline for a series with possible nulls (MA overlays) → segments.
  const poly = (getter: (p: PricePoint) => number | null) => {
    const pts: string[] = [];
    series.forEach((p, i) => { const v = getter(p); if (v != null) pts.push(`${x(i)},${y(v)}`); });
    return pts.join(" ");
  };

  const vols = series.map((p) => p.volume);
  const vmax = Math.max(...vols, 1);
  const volY = (v: number) => H - PAD - (v / vmax) * VOL_H;
  const barW = Math.max(1, (W - 2 * PAD) / series.length - 0.5);

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" preserveAspectRatio="none">
      {series.map((p, i) => (
        <rect key={i} x={x(i) - barW / 2} y={volY(p.volume)} width={barW} height={H - PAD - volY(p.volume)} fill="#1e2a36" />
      ))}
      <polyline points={poly((p) => p.ma200)} fill="none" stroke="#4db8ff" strokeWidth="1" opacity="0.8" />
      <polyline points={poly((p) => p.ma50)} fill="none" stroke="#ffb000" strokeWidth="1" opacity="0.8" />
      <polyline points={poly((p) => p.close)} fill="none" stroke="#c8d6e5" strokeWidth="1.5" />
    </svg>
  );
}
