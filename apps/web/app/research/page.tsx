"use client";
import { RESEARCH_NVDA as R } from "@/lib/mock";
import { useApi } from "@/lib/api";
import { PriceChart } from "@/components/PriceChart";
import { AiMeta, ConfidenceBadge, Panel, StatusBadge, Table } from "@/components/ui";

const meta = { sources: ["MOCK research pack"], asOf: R.asOf, confidence: R.confidence, missingData: R.missingData };

// Human labels + weights for the 9 score components (weights match the engine).
const COMPONENT_META: Record<string, { label: string; weightPct: number }> = {
  business_quality: { label: "Business Quality", weightPct: 15 },
  growth_momentum: { label: "Growth / Estimate Momentum", weightPct: 15 },
  balance_sheet: { label: "Balance Sheet Strength", weightPct: 10 },
  valuation: { label: "Valuation Attractiveness", weightPct: 15 },
  technical_trend: { label: "Technical Trend", weightPct: 10 },
  catalyst_strength: { label: "Catalyst Strength", weightPct: 10 },
  estimate_revision: { label: "Analyst / Estimate Revision", weightPct: 10 },
  news_sentiment: { label: "News / Sentiment", weightPct: 5 },
  liquidity_risk: { label: "Liquidity / Risk Control", weightPct: 10 },
};

interface ResearchLatest {
  confidence: string;
  score: { score_total: number; components: Record<string, number> };
  component_sources: { real: string[]; mock: string[] };
}
const SCORE_FALLBACK: ResearchLatest = {
  confidence: "Medium",
  score: { score_total: 78.8, components: { business_quality: 90, growth_momentum: 88, balance_sheet: 92, valuation: 45, technical_trend: 80, catalyst_strength: 75, estimate_revision: 82, news_sentiment: 70, liquidity_risk: 95 } },
  component_sources: { real: [], mock: Object.keys(COMPONENT_META) },
};

function ScorePanel() {
  const { data } = useApi<ResearchLatest>("/api/research/NVDA/latest", SCORE_FALLBACK);
  const realSet = new Set(data.component_sources?.real ?? []);
  const keys = Object.keys(COMPONENT_META);
  return (
    <Panel
      title="Research Score"
      right={<span className="text-[10px] text-term-dim">{realSet.size} real · {keys.length - realSet.size} mock</span>}
    >
      <div className="mb-1 text-lg text-term-green">
        {data.score.score_total}/100 <ConfidenceBadge level={(data.confidence as "High" | "Medium" | "Low") ?? "Medium"} />
      </div>
      <Table
        headers={["Component", "Wt", "Score", "Source"]}
        rows={keys.map((k) => {
          const v = data.score.components[k] ?? 0;
          const real = realSet.has(k);
          return [
            COMPONENT_META[k].label,
            `${COMPONENT_META[k].weightPct}%`,
            <span key="v" className={v >= 70 ? "text-term-green" : v >= 50 ? "text-term-amber" : "text-term-red"}>{v}</span>,
            <span key="s" className={`border px-1 text-[10px] ${real ? "border-term-green text-term-green" : "border-term-amber text-term-amber"}`}>
              {real ? "REAL" : "MOCK"}
            </span>,
          ];
        })}
      />
      <p className="mt-2 text-[10px] text-term-dim">
        REAL components are computed from live price history; MOCK ones await their own data. Score is a research signal, not advice.
      </p>
    </Panel>
  );
}

export default function ResearchPage() {
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-3 border border-term-border bg-term-panel p-2">
        <span className="text-term-dim">EQUITY RESEARCH:</span>
        <span className="border border-term-amber px-2 py-0.5 text-term-amber">{R.symbol}</span>
        <button className="border border-term-border px-2 py-0.5 text-term-dim" title="Phase 5 runs the agent workflow">RUN RESEARCH (mock)</button>
        <button className="border border-term-border px-2 py-0.5 text-term-dim" title="Phase 6 builds exportable reports">BUILD REPORT (mock)</button>
        <span className="ml-auto text-[10px] text-term-dim">Live price + real score components; narrative is mock (NVDA)</span>
      </div>

      <PriceChart symbol="NVDA" />

      <div className="grid grid-cols-1 gap-2 xl:grid-cols-3">
        <Panel title="Company Snapshot">
          <p>{R.snapshot}</p>
          <AiMeta {...meta} />
        </Panel>
        <Panel title="Business Model">
          <p>{R.businessModel}</p>
          <AiMeta {...meta} />
        </Panel>
        <ScorePanel />

        <Panel title="Financial Statement Summary">
          <Table
            headers={["Statement", "Metric", "Period", "Value"]}
            rows={R.financials.map((f) => [f.statementType, f.metric, f.fiscalPeriod, <span key="v" className="text-term-green">{f.value}</span>])}
          />
        </Panel>
        <Panel title="KPI Dashboard">
          <Table
            headers={["KPI", "Value", "Trend"]}
            rows={R.kpis.map((k) => [
              k.name,
              k.value,
              <span key="t" className={k.trend === "up" ? "text-term-green" : k.trend === "down" ? "text-term-red" : "text-term-dim"}>{k.trend === "up" ? "▲" : k.trend === "down" ? "▼" : "—"}</span>,
            ])}
          />
        </Panel>
        <Panel title="Catalyst Tracker">
          <Table headers={["Date", "Event", "Type"]} rows={R.catalysts.map((c) => [c.date, c.event, <span key="t" className="text-term-blue">{c.type}</span>])} />
        </Panel>

        <Panel title="Filing Reader">
          <p className="text-term-dim">Real 10-K/10-Q/8-K filings are live on the News &amp; Filings tab (SEC EDGAR, keyless).</p>
        </Panel>
        <Panel title="Valuation Lab">
          <p className="text-term-dim">The DCF is now editable with live recomputation on the Model Lab tab (bear/base/bull fair value).</p>
        </Panel>
        <Panel title="Risk Register">
          <Table
            headers={["Category", "Risk", "Severity"]}
            rows={R.riskRegister.map((r) => [r.category, r.risk, <StatusBadge key="s" status={r.severity === "High" ? "HIGH" : "WARNING " + r.severity} />])}
          />
        </Panel>

        <Panel title="Bull Case">
          <p className="text-term-green">{R.bullCase}</p>
          <AiMeta {...meta} warnings={["Advocacy note — read with bear case"]} />
        </Panel>
        <Panel title="Bear Case">
          <p className="text-term-red">{R.bearCase}</p>
          <AiMeta {...meta} warnings={["Advocacy note — read with bull case"]} />
        </Panel>
        <Panel title="Red-Team Critique">
          <p className="text-term-amber">{R.redTeam}</p>
          <AiMeta {...meta} />
        </Panel>
      </div>

      <Panel title="Report Builder">
        <div className="flex gap-2">
          {["Flash Note (1p)", "Investment Memo (5–10p)", "Initiating Coverage (25–40p)"].map((r) => (
            <button key={r} className="border border-term-border px-3 py-1 text-term-dim hover:border-term-amber hover:text-term-amber" title="Phase 6: report generation + export">
              {r}
            </button>
          ))}
          <span className="self-center text-[10px] text-term-dim">Placeholders — generation lands in Phase 6, gated by the Audit Agent.</span>
        </div>
      </Panel>
    </div>
  );
}
