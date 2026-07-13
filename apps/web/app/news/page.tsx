import { AS_OF, FILINGS, NEWS, NEWS_RISK_FLAGS } from "@/lib/mock";
import { Panel, Table } from "@/components/ui";

const TRUST = [
  "1. SEC / exchange filings", "2. Company investor relations", "3. Earnings transcripts",
  "4. Financial data providers", "5. News wires", "6. Social sentiment", "7. AI summaries",
];

export default function NewsPage() {
  return (
    <div className="grid grid-cols-1 gap-2 xl:grid-cols-3">
      <Panel title="Latest Filings" className="xl:col-span-2" right={<span className="text-[10px] text-term-dim">SRC: MOCK (SEC EDGAR in Phase 3)</span>}>
        <Table
          headers={["Form", "Date", "Title", "AI Summary"]}
          rows={FILINGS.map((f) => [
            <span key="f" className="text-term-blue">{f.formType}</span>,
            f.filingDate,
            f.title,
            <span key="s" className="text-term-dim">{f.summary}</span>,
          ])}
        />
      </Panel>

      <Panel title="Source Trust Hierarchy">
        <ul className="space-y-0.5 text-term-dim">
          {TRUST.map((t) => <li key={t}>{t}</li>)}
        </ul>
        <p className="mt-2 text-[10px] text-term-amber">Filings outrank news. AI summaries rank last and always cite upstream sources.</p>
      </Panel>

      <Panel title="News Feed" className="xl:col-span-2" right={<span className="text-[10px] text-term-dim">AS OF {AS_OF}</span>}>
        <Table
          headers={["Headline", "Source", "Published", "Sentiment"]}
          rows={NEWS.map((n) => [
            n.headline,
            n.source,
            n.publishedAt,
            <span key="s" className={n.sentiment === "positive" ? "text-term-green" : n.sentiment === "negative" ? "text-term-red" : "text-term-dim"}>{n.sentiment}</span>,
          ])}
        />
      </Panel>

      <Panel title="Risk Flags">
        {NEWS_RISK_FLAGS.map((f, i) => <p key={i} className="text-term-amber">⚠ {f}</p>)}
        <p className="mt-2 text-[10px] text-term-dim">Earnings transcripts panel lands with Phase 3 ingestion.</p>
      </Panel>
    </div>
  );
}
