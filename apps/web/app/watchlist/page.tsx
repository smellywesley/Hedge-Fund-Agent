"use client";
import { useState } from "react";
import { WATCHLIST } from "@/lib/mock";
import { apiSend, useApi } from "@/lib/api";
import type { WatchlistItem } from "@/lib/types";
import { SourceBadge } from "@/components/SourceBadge";
import { ConfidenceBadge, Panel, Pct, Table } from "@/components/ui";

type Row = WatchlistItem & { source?: string };

export default function WatchlistPage() {
  const { data, status, refetch } = useApi<Row[]>("/api/watchlist", WATCHLIST);
  const [symbol, setSymbol] = useState("");
  const [error, setError] = useState("");
  const live = data.some((r) => r.source === "yfinance");

  async function mutate(action: () => Promise<unknown>) {
    setError("");
    try { await action(); refetch(); } catch (e) { setError(String(e instanceof Error ? e.message : e)); }
  }

  return (
    <Panel title="Watchlist" right={<SourceBadge status={status} live={live} />}>
      <div className="mb-2 flex items-center gap-2">
        <input
          className="w-28 border border-term-border bg-black/40 px-2 py-0.5 text-term-amber outline-none focus:border-term-amber"
          placeholder="TICKER"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value.toUpperCase())}
          onKeyDown={(e) => { if (e.key === "Enter" && symbol) mutate(() => apiSend("/api/watchlist", "POST", { symbol })).then(() => setSymbol("")); }}
        />
        <button
          className="border border-term-border px-2 py-0.5 text-term-dim hover:border-term-amber hover:text-term-amber"
          onClick={() => { if (symbol) { mutate(() => apiSend("/api/watchlist", "POST", { symbol })); setSymbol(""); } }}
        >
          WL ADD
        </button>
        {error && <span className="text-[10px] text-term-red">{error}</span>}
        {status === "fallback" && <span className="text-[10px] text-term-dim">Add/remove needs the API running.</span>}
      </div>

      <Table
        headers={["Sym", "Company", "Price", "Chg", "Src", "Vol/Avg", "Score", "Conf", "Catalyst", "Filing", "News Risk", "Next Action", ""]}
        rows={data.map((w) => [
          <span key="s" className="text-term-blue">{w.symbol}</span>,
          w.company,
          w.price ? w.price.toFixed(2) : "—",
          <Pct key="p" value={w.changePct} />,
          <span key="src" className={w.source === "yfinance" ? "text-term-green" : "text-term-dim"}>{w.source ?? "MOCK"}</span>,
          w.volumeVsAvg ? `${w.volumeVsAvg.toFixed(1)}x` : "—",
          <span key="sc" className={w.score >= 70 ? "text-term-green" : "text-term-text"}>{w.score || "—"}</span>,
          <ConfidenceBadge key="c" level={w.confidence} />,
          w.catalyst,
          w.latestFiling,
          w.newsRisk === "None flagged" ? <span key="n" className="text-term-dim">{w.newsRisk}</span> : <span key="n" className="text-term-amber">{w.newsRisk}</span>,
          <span key="a" className="text-term-amber">{w.nextAction}</span>,
          <button key="x" title="Remove" className="px-1 text-term-red hover:bg-term-red/20"
            onClick={() => mutate(() => apiSend(`/api/watchlist/${w.symbol}`, "DELETE"))}>✕</button>,
        ])}
      />
      <p className="mt-2 text-[10px] text-term-dim">
        Persisted in the database — survives refresh. Prices live via yfinance when available; score/catalyst
        metadata is still mock (Phase 3/4). Score is a research-prioritization signal, not buy/sell advice.
      </p>
    </Panel>
  );
}
