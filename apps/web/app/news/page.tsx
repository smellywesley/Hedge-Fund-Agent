"use client";
import { useState } from "react";
import { AS_OF, FILINGS, NEWS, NEWS_RISK_FLAGS } from "@/lib/mock";
import { useApi } from "@/lib/api";
import { SourceBadge } from "@/components/SourceBadge";
import { Panel, Table } from "@/components/ui";

const TRUST = [
  "1. SEC / exchange filings", "2. Company investor relations", "3. Earnings transcripts",
  "4. Financial data providers", "5. News wires", "6. Social sentiment", "7. AI summaries",
];

interface Filing {
  formType: string;
  filingDate: string;
  accessionNumber: string;
  primaryDocUrl: string;
  title: string;
  source: string;
}
interface FilingsPayload {
  symbol: string;
  source: string;
  live: boolean;
  warnings: string[];
  asOf: string;
  filings: Filing[];
}

const FALLBACK: FilingsPayload = {
  symbol: "NVDA", source: "MOCK", live: false, warnings: [], asOf: AS_OF,
  filings: FILINGS.map((f) => ({
    formType: f.formType, filingDate: f.filingDate, accessionNumber: "",
    primaryDocUrl: f.sourceUrl, title: f.title, source: "MOCK",
  })),
};

export default function NewsPage() {
  const [symbol, setSymbol] = useState("NVDA");
  const [active, setActive] = useState("NVDA");
  const { data, status } = useApi<FilingsPayload>(`/api/tickers/${active}/filings`, FALLBACK);

  return (
    <div className="grid grid-cols-1 gap-2 xl:grid-cols-3">
      <Panel
        title="Latest Filings"
        className="xl:col-span-2"
        right={<SourceBadge status={status} live={data.live} liveLabel="SEC EDGAR" mockLabel="MOCK FALLBACK" />}
      >
        <div className="mb-2 flex items-center gap-2">
          <input
            className="w-28 border border-term-border bg-black/40 px-2 py-0.5 text-term-amber outline-none focus:border-term-amber"
            placeholder="TICKER"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            onKeyDown={(e) => { if (e.key === "Enter" && symbol) setActive(symbol); }}
          />
          <button
            className="border border-term-border px-2 py-0.5 text-term-dim hover:border-term-amber hover:text-term-amber"
            onClick={() => symbol && setActive(symbol)}
          >
            LOAD FILINGS
          </button>
          <span className="text-[10px] text-term-dim">SRC: {data.source} · {data.symbol}</span>
        </div>
        {data.warnings.map((w, i) => (
          <p key={i} className="mb-1 text-[10px] text-term-amber">⚠ {w}</p>
        ))}
        <Table
          headers={["Form", "Date", "Title (click → sec.gov)", "Accession"]}
          rows={data.filings.map((f) => [
            <span key="f" className="text-term-blue">{f.formType}</span>,
            f.filingDate,
            <a key="t" href={f.primaryDocUrl} target="_blank" rel="noopener noreferrer"
               className="text-term-text underline decoration-term-dim hover:text-term-amber">
              {f.title}
            </a>,
            <span key="a" className="text-[10px] text-term-dim">{f.accessionNumber || "—"}</span>,
          ])}
        />
        {data.filings.length === 0 && <p className="text-term-dim">No filings found for {data.symbol}.</p>}
      </Panel>

      <Panel title="Source Trust Hierarchy">
        <ul className="space-y-0.5 text-term-dim">
          {TRUST.map((t) => <li key={t}>{t}</li>)}
        </ul>
        <p className="mt-2 text-[10px] text-term-amber">
          Filings are LIVE from SEC EDGAR (keyless). AI summaries rank last and always cite upstream sources.
        </p>
      </Panel>

      <Panel
        title="News Feed"
        className="xl:col-span-2"
        right={<span className="border border-term-amber px-1 text-[10px] text-term-amber">MOCK — no news connector</span>}
      >
        <Table
          headers={["Headline", "Source", "Published", "Sentiment"]}
          rows={NEWS.map((n) => [
            n.headline,
            n.source,
            n.publishedAt,
            <span key="s" className={n.sentiment === "positive" ? "text-term-green" : n.sentiment === "negative" ? "text-term-red" : "text-term-dim"}>{n.sentiment}</span>,
          ])}
        />
        <p className="mt-2 text-[10px] text-term-dim">News feed is still mock — a news provider (FMP/Finnhub) is future work. Filings above are real.</p>
      </Panel>

      <Panel title="Risk Flags">
        {NEWS_RISK_FLAGS.map((f, i) => <p key={i} className="text-term-amber">⚠ {f}</p>)}
        <p className="mt-2 text-[10px] text-term-dim">Earnings transcripts panel lands with future ingestion.</p>
      </Panel>
    </div>
  );
}
