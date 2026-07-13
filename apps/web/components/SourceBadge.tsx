import type { ApiStatus } from "@/lib/api";

// Data-provenance badge for panels: live prices, DB-backed mock, or offline fallback.
export function SourceBadge({ status, live }: { status: ApiStatus; live?: boolean }) {
  if (status === "loading") return <span className="text-[10px] text-term-dim">LOADING…</span>;
  if (status === "fallback")
    return <span className="border border-term-red px-1 text-[10px] text-term-red">API OFFLINE — MOCK FALLBACK</span>;
  return live ? (
    <span className="border border-term-green px-1 text-[10px] text-term-green">LIVE · yfinance</span>
  ) : (
    <span className="border border-term-amber px-1 text-[10px] text-term-amber">DB + MOCK PRICES</span>
  );
}
