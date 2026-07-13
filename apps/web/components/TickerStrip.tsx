"use client";
import { TICKER_STRIP } from "@/lib/mock";
import { useApi } from "@/lib/api";
import { Pct } from "./ui";

type StripItem = { symbol: string; last: number; changePct: number };
const FALLBACK = { live: false, items: TICKER_STRIP as StripItem[] };

export function TickerStrip() {
  const { data, status } = useApi<typeof FALLBACK>("/api/quotes", FALLBACK);
  const items = [...data.items, ...data.items]; // duplicated for seamless loop
  const liveTag = status === "api" && data.live;
  return (
    <div className="flex items-center overflow-hidden border-b border-term-border bg-black/40">
      <span className={`shrink-0 border-r border-term-border px-2 py-0.5 text-[10px] ${liveTag ? "text-term-green" : "text-term-dim"}`}>
        {liveTag ? "LIVE" : "MOCK"}
      </span>
      <div className="ticker-track flex w-max gap-6 px-2 py-0.5 text-[11px]">
        {items.map((t, i) => (
          <span key={i} className="whitespace-nowrap">
            <span className="text-term-blue">{t.symbol}</span>{" "}
            <span>{t.last.toLocaleString()}</span> <Pct value={t.changePct} />
          </span>
        ))}
      </div>
    </div>
  );
}
