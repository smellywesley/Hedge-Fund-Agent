"use client";
// Dependency-free SVG NAV line chart with running-peak (drawdown) reference.
import { useApi } from "@/lib/api";
import { Panel, Pct } from "./ui";

type NavPayload = {
  series: { date: string; nav: number }[];
  metrics: {
    available: boolean;
    note?: string;
    inceptionDate?: string;
    inceptionNote?: string;
    inceptionPnlPct?: number;
    weeklyPnlPct?: number | null;
    maxDrawdownPct?: number;
    realizedVolPct?: number | null;
    latestNav?: number;
  };
};

const W = 600, H = 150, PAD = 6;

export function NavChart() {
  const { data, status } = useApi<NavPayload>("/api/paper-fund/nav", { series: [], metrics: { available: false, note: "API offline" } });
  const { series, metrics } = data;

  if (status === "loading") return <Panel title="Paper NAV"><p className="text-term-dim">Loading…</p></Panel>;
  if (series.length < 2) {
    return <Panel title="Paper NAV"><p className="text-term-dim">{metrics.note ?? "No NAV history yet."}</p></Panel>;
  }

  const navs = series.map((p) => p.nav);
  const min = Math.min(...navs), max = Math.max(...navs);
  const x = (i: number) => PAD + (i / (series.length - 1)) * (W - 2 * PAD);
  const y = (v: number) => max === min ? H / 2 : PAD + (1 - (v - min) / (max - min)) * (H - 2 * PAD);

  const line = navs.map((v, i) => `${x(i)},${y(v)}`).join(" ");
  // Running peak — the gap between this and the NAV line IS the drawdown.
  let peak = navs[0];
  const peakLine = navs.map((v, i) => { peak = Math.max(peak, v); return `${x(i)},${y(peak)}`; }).join(" ");
  const up = (metrics.inceptionPnlPct ?? 0) >= 0;

  return (
    <Panel
      title="Paper NAV (since simulated inception)"
      right={<span className="text-[10px] text-term-dim">{series[0].date} → {series[series.length - 1].date}</span>}
    >
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" preserveAspectRatio="none">
        <polyline points={peakLine} fill="none" stroke="#6b7d8f" strokeWidth="1" strokeDasharray="3 3" />
        <polygon points={`${PAD},${H - PAD} ${line} ${W - PAD},${H - PAD}`} fill={up ? "#2ee06f" : "#ff4d4d"} opacity="0.08" />
        <polyline points={line} fill="none" stroke={up ? "#2ee06f" : "#ff4d4d"} strokeWidth="1.5" />
      </svg>
      <div className="mt-1 flex flex-wrap gap-x-4 gap-y-1 text-[11px]">
        <span>NAV: <span className="text-term-text">${metrics.latestNav?.toLocaleString()}</span></span>
        <span>Inception: {metrics.inceptionPnlPct != null ? <Pct value={metrics.inceptionPnlPct} /> : "—"}</span>
        <span>Weekly: {metrics.weeklyPnlPct != null ? <Pct value={metrics.weeklyPnlPct} /> : "—"}</span>
        <span>Max DD: <span className="text-term-red">{metrics.maxDrawdownPct}%</span></span>
        <span>Vol (20d ann.): <span className="text-term-text">{metrics.realizedVolPct != null ? `${metrics.realizedVolPct}%` : "—"}</span></span>
      </div>
      {metrics.inceptionNote && <p className="mt-1 text-[10px] text-term-amber">{metrics.inceptionNote}</p>}
    </Panel>
  );
}
