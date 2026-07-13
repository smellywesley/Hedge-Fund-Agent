import type { Confidence } from "@/lib/types";

export function Panel({ title, right, children, className = "" }: {
  title: string; right?: React.ReactNode; children: React.ReactNode; className?: string;
}) {
  return (
    <section className={`border border-term-border bg-term-panel ${className}`}>
      <header className="flex items-center justify-between border-b border-term-border px-2 py-1">
        <h2 className="text-[11px] font-bold uppercase tracking-widest text-term-amber">{title}</h2>
        {right}
      </header>
      <div className="p-2">{children}</div>
    </section>
  );
}

export function Pct({ value }: { value: number }) {
  const cls = value > 0 ? "text-term-green" : value < 0 ? "text-term-red" : "text-term-dim";
  return <span className={cls}>{value > 0 ? "+" : ""}{value.toFixed(2)}%</span>;
}

export function ConfidenceBadge({ level }: { level: Confidence }) {
  const cls = { High: "text-term-green border-term-green", Medium: "text-term-amber border-term-amber", Low: "text-term-red border-term-red" }[level];
  return <span className={`border px-1 text-[10px] uppercase ${cls}`}>{level}</span>;
}

export function StatusBadge({ status }: { status: string }) {
  const cls = status.startsWith("PASS") || status === "OK" || status === "READY"
    ? "text-term-green border-term-green"
    : status.startsWith("WARNING") || status.startsWith("PENDING")
    ? "text-term-amber border-term-amber"
    : "text-term-red border-term-red";
  return <span className={`border px-1 text-[10px] uppercase whitespace-nowrap ${cls}`}>{status}</span>;
}

// Audit footer required on every AI/mock output card:
// source, timestamp, confidence, missing-data warnings.
export function AiMeta({ sources, asOf, confidence, missingData, warnings = [] }: {
  sources: string[]; asOf: string; confidence: Confidence; missingData: string[]; warnings?: string[];
}) {
  return (
    <div className="mt-2 border-t border-term-border pt-1 text-[10px] text-term-dim">
      <div>SRC: {sources.join(", ") || "—"} · AS OF: {asOf} · CONF: <ConfidenceBadge level={confidence} /></div>
      {missingData.length > 0 && <div className="text-term-amber">MISSING: {missingData.join("; ")}</div>}
      {warnings.length > 0 && <div className="text-term-red">WARN: {warnings.join("; ")}</div>}
    </div>
  );
}

export function Table({ headers, rows }: { headers: string[]; rows: React.ReactNode[][] }) {
  return (
    <table className="w-full border-collapse text-[11px]">
      <thead>
        <tr className="border-b border-term-border text-left text-[10px] uppercase text-term-dim">
          {headers.map((h) => <th key={h} className="px-1 py-0.5 font-normal">{h}</th>)}
        </tr>
      </thead>
      <tbody>
        {rows.map((cells, i) => (
          <tr key={i} className="border-b border-term-border/40 hover:bg-term-border/20">
            {cells.map((c, j) => <td key={j} className="px-1 py-0.5 align-top">{c}</td>)}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export function Disclaimer() {
  return (
    <p className="border border-term-amber/40 bg-term-amber/5 p-2 text-[10px] text-term-amber">
      Educational paper simulation only. No real money, no brokerage connection, not financial advice.
    </p>
  );
}
