import type { ApiStatus } from "@/lib/api";

// Data-provenance badge for panels: live source, DB-backed mock, or offline fallback.
// liveLabel names the live source (default "yfinance"; e.g. "SEC EDGAR").
export function SourceBadge({ status, live, liveLabel = "yfinance", mockLabel = "DB + MOCK PRICES" }: {
  status: ApiStatus; live?: boolean; liveLabel?: string; mockLabel?: string;
}) {
  if (status === "loading") return <span className="text-[10px] text-term-dim">LOADING…</span>;
  if (status === "fallback")
    return <span className="border border-term-red px-1 text-[10px] text-term-red">API OFFLINE — MOCK FALLBACK</span>;
  return live ? (
    <span className="border border-term-green px-1 text-[10px] text-term-green">LIVE · {liveLabel}</span>
  ) : (
    <span className="border border-term-amber px-1 text-[10px] text-term-amber">{mockLabel}</span>
  );
}
