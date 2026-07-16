"use client";
import { useState } from "react";
import { DCF } from "@/lib/mock";
import { apiSend } from "@/lib/api";
import { Panel, Table } from "@/components/ui";

type Scenario = "bear" | "base" | "bull";
type Assumptions = Record<string, number>;

// Editable DCF inputs (key, label). Revenue/net_cash in $bn; shares in bn.
const FIELDS: { key: string; label: string }[] = [
  { key: "base_revenue", label: "Base revenue ($bn)" },
  { key: "revenue_growth", label: "Revenue growth" },
  { key: "operating_margin", label: "Operating margin" },
  { key: "tax_rate", label: "Tax rate" },
  { key: "capex_pct", label: "Capex / revenue" },
  { key: "wacc", label: "WACC" },
  { key: "terminal_growth", label: "Terminal growth" },
  { key: "shares_out", label: "Shares out (bn)" },
  { key: "net_cash", label: "Net cash ($bn)" },
];

const SEED: Record<Scenario, Assumptions> = {
  bear: { base_revenue: 148, revenue_growth: 0.08, operating_margin: 0.48, tax_rate: 0.15, capex_pct: 0.06, wacc: 0.11, terminal_growth: 0.02, shares_out: 24.5, net_cash: 38.9 },
  base: { base_revenue: 148, revenue_growth: 0.22, operating_margin: 0.58, tax_rate: 0.15, capex_pct: 0.045, wacc: 0.095, terminal_growth: 0.03, shares_out: 24.5, net_cash: 38.9 },
  bull: { base_revenue: 148, revenue_growth: 0.35, operating_margin: 0.63, tax_rate: 0.14, capex_pct: 0.035, wacc: 0.085, terminal_growth: 0.045, shares_out: 24.5, net_cash: 38.9 },
};

interface DcfResult { fairValuePerShare: number; enterpriseValue: number; pvExplicit: number; pvTerminal: number; terminalMethod: string; }

export default function ModelsPage() {
  const [inputs, setInputs] = useState<Record<Scenario, Assumptions>>(SEED);
  const [result, setResult] = useState<Record<Scenario, DcfResult> | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  function setField(sc: Scenario, key: string, v: string) {
    setInputs((prev) => ({ ...prev, [sc]: { ...prev[sc], [key]: v === "" ? 0 : Number(v) } }));
  }

  async function recompute() {
    setError(""); setBusy(true);
    try {
      const r = await apiSend("/api/valuation/dcf", "POST", inputs);
      setResult({ bear: r.bear, base: r.base, bull: r.bull });
    } catch (e) {
      setResult(null);
      setError(String(e instanceof Error ? e.message : e));
    } finally {
      setBusy(false);
    }
  }

  const cols: { sc: Scenario; cls: string }[] = [
    { sc: "bear", cls: "text-term-red" }, { sc: "base", cls: "text-term-amber" }, { sc: "bull", cls: "text-term-green" },
  ];

  return (
    <div className="space-y-2">
      <p className="border border-term-amber/40 bg-term-amber/5 p-2 text-[10px] text-term-amber">
        {DCF.disclaimer} Edit any assumption and press Recompute — the fair value is computed live by the research engine.
      </p>

      <div className="grid grid-cols-1 gap-2 xl:grid-cols-2">
        <Panel
          title="Editable DCF Assumptions"
          right={
            <button onClick={recompute} disabled={busy}
              className="border border-term-amber px-2 py-0.5 text-term-amber hover:bg-term-amber/10 disabled:opacity-50">
              {busy ? "…" : "RECOMPUTE"}
            </button>
          }
        >
          <table className="w-full text-[11px]">
            <thead>
              <tr className="border-b border-term-border text-left text-[10px] uppercase text-term-dim">
                <th className="px-1 py-0.5 font-normal">Assumption</th>
                <th className="px-1 py-0.5 font-normal text-term-red">Bear</th>
                <th className="px-1 py-0.5 font-normal text-term-amber">Base</th>
                <th className="px-1 py-0.5 font-normal text-term-green">Bull</th>
              </tr>
            </thead>
            <tbody>
              {FIELDS.map((f) => (
                <tr key={f.key} className="border-b border-term-border/40">
                  <td className="px-1 py-0.5">{f.label}</td>
                  {cols.map(({ sc, cls }) => (
                    <td key={sc} className="px-1 py-0.5">
                      <input
                        type="number" step="any"
                        className={`w-16 border border-term-border bg-black/40 px-1 outline-none focus:border-term-amber ${cls}`}
                        value={inputs[sc][f.key]}
                        onChange={(e) => setField(sc, f.key, e.target.value)}
                      />
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
          {error && <p className="mt-2 text-term-red">⚠ {error}</p>}
        </Panel>

        <Panel title="Fair Value (computed live)">
          {!result && !error && <p className="text-term-dim">Press Recompute to value the three scenarios.</p>}
          {result && (
            <>
              <div className="mb-2 flex justify-around text-center">
                {cols.map(({ sc, cls }) => (
                  <div key={sc}>
                    <div className="text-[10px] uppercase text-term-dim">{sc}</div>
                    <div className={`text-xl ${cls}`}>${result[sc].fairValuePerShare}</div>
                  </div>
                ))}
              </div>
              <Table
                headers={["Case", "Fair Value", "EV ($bn)", "Terminal method"]}
                rows={cols.map(({ sc, cls }) => [
                  <span key="n" className={cls}>{sc}</span>,
                  `$${result[sc].fairValuePerShare}`,
                  result[sc].enterpriseValue.toLocaleString(),
                  <span key="t" className="text-[10px] text-term-dim">{result[sc].terminalMethod}</span>,
                ])}
              />
              <p className="mt-2 text-term-amber">
                Spread ${result.bear.fairValuePerShare} – ${result.bull.fairValuePerShare}: terminal assumptions dominate — treat point estimates with suspicion.
              </p>
            </>
          )}
        </Panel>

        <Panel title="Sensitivity Table (placeholder)">
          <p className="text-term-dim">Future: WACC × terminal-growth grid showing fair-value fragility. Every model must show sensitivity to its key assumptions.</p>
        </Panel>
        <Panel title="Comparable Multiples (placeholder)">
          <p className="text-term-dim">Future: peer P/E, EV/EBITDA, P/S, FCF yield vs sector and vs own history.</p>
        </Panel>
        <Panel title="Monte Carlo (placeholder)">
          <p className="text-term-dim">Future: scenario distribution over assumption ranges — a distribution, never certainty.</p>
        </Panel>
        <Panel title="Model Rules">
          <ul className="list-inside list-disc space-y-1 text-term-dim">
            <li>Every model shows its assumptions (now editable above).</li>
            <li>Every model supports bear/base/bull.</li>
            <li>Invalid inputs (e.g. WACC ≤ terminal growth) are rejected with a clear error, never a fake number.</li>
            <li>Educational / paper simulation only — not investment advice.</li>
          </ul>
        </Panel>
      </div>
    </div>
  );
}
