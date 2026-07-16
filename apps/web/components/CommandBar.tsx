"use client";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { apiSend } from "@/lib/api";

// Every supported command, for the router and the HELP overlay.
const COMMANDS: { cmd: string; desc: string }[] = [
  { cmd: "NVDA", desc: "bare ticker → Equity Research" },
  { cmd: "ER NVDA", desc: "Equity Research for a ticker" },
  { cmd: "DCF NVDA", desc: "Model Lab / editable DCF" },
  { cmd: "NEWS NVDA", desc: "News & real SEC filings" },
  { cmd: "RISK PORT", desc: "Risk dashboard" },
  { cmd: "WL ADD NVDA", desc: "add ticker to watchlist (persists)" },
  { cmd: "WL REMOVE NVDA", desc: "remove ticker from watchlist" },
  { cmd: "WL SCORE ALL", desc: "watchlist with live technical scores" },
  { cmd: "BACKTEST NVDA,TSM", desc: "signal backtest (alias: BT) → Reports" },
  { cmd: "FUND HEALTH", desc: "Paper Fund Lab" },
  { cmd: "REPORT NVDA", desc: "Reports tab" },
  { cmd: "MARKET / REGIME / SECTORS", desc: "Markets tab" },
  { cmd: "HELP or ?", desc: "toggle this command list" },
];

// Pure navigation router (mutating WL ADD/REMOVE handled separately in run()).
function route(raw: string): string | null {
  const cmd = raw.trim().toUpperCase();
  if (!cmd) return null;
  const [head, second] = cmd.split(/\s+/);
  if (head === "ER") return "/research";
  if (head === "DCF") return "/models";
  if (head === "NEWS") return "/news";
  if (head === "RISK") return "/risk";
  if (head === "WL") return "/watchlist";  // incl. WL SCORE ALL
  if (head === "FUND") return "/fund";
  if (head === "REPORT") return "/reports";
  if (head === "BACKTEST" || head === "BT") return "/reports";
  if (head === "MARKET" || head === "REGIME" || head === "SECTORS") return "/markets";
  if (/^[A-Z]{1,5}$/.test(head)) return "/research"; // bare ticker
  return null;
}

export function CommandBar() {
  const router = useRouter();
  const [value, setValue] = useState("");
  const [msg, setMsg] = useState<{ text: string; err: boolean } | null>(null);
  const [showHelp, setShowHelp] = useState(false);

  async function run(raw: string) {
    const parts = raw.trim().toUpperCase().split(/\s+/);
    if (parts[0] === "HELP" || parts[0] === "?") {
      setShowHelp((h) => !h); setValue(""); setMsg(null); return;
    }
    // Mutating commands execute against the API before navigating.
    if (parts[0] === "WL" && (parts[1] === "ADD" || parts[1] === "REMOVE") && parts[2]) {
      try {
        if (parts[1] === "ADD") await apiSend("/api/watchlist", "POST", { symbol: parts[2] });
        else await apiSend(`/api/watchlist/${parts[2]}`, "DELETE");
        setMsg({ text: `WL ${parts[1]} ${parts[2]} OK`, err: false });
        router.push("/watchlist");
        router.refresh();
        setValue("");
      } catch (e) {
        setMsg({ text: String(e instanceof Error ? e.message : e), err: true });
      }
      return;
    }
    const target = route(raw);
    if (target) { router.push(target); setValue(""); setMsg(null); }
    else setMsg({ text: `UNKNOWN CMD: ${raw.toUpperCase()}`, err: true });
  }

  return (
    <div className="relative flex flex-1 items-center gap-2">
      <span className="text-term-amber">&gt;</span>
      <input
        className="w-full max-w-xl bg-black/40 px-2 py-1 text-term-amber placeholder-term-dim outline-none border border-term-border focus:border-term-amber"
        placeholder="Command: NVDA · ER · DCF · NEWS · RISK · WL ADD · BACKTEST · FUND HEALTH · REPORT · HELP"
        value={value}
        onChange={(e) => { setValue(e.target.value); setMsg(null); }}
        onKeyDown={(e) => { if (e.key === "Enter") run(value); }}
      />
      <button
        className="border border-term-border px-1 text-[10px] text-term-dim hover:border-term-amber hover:text-term-amber"
        onClick={() => setShowHelp((h) => !h)}
        title="Command list"
      >
        ?
      </button>
      {msg && (
        <span className={`text-[10px] whitespace-nowrap ${msg.err ? "text-term-red" : "text-term-green"}`}>
          {msg.text}
        </span>
      )}
      {showHelp && (
        <div className="absolute left-4 top-9 z-50 w-96 border border-term-border bg-term-panel p-2 shadow-lg">
          <div className="mb-1 flex items-center justify-between">
            <span className="text-[11px] font-bold uppercase tracking-widest text-term-amber">Commands</span>
            <button className="text-term-dim hover:text-term-red" onClick={() => setShowHelp(false)}>✕</button>
          </div>
          <table className="w-full text-[11px]">
            <tbody>
              {COMMANDS.map((c) => (
                <tr key={c.cmd} className="border-b border-term-border/40">
                  <td className="py-0.5 pr-2 align-top text-term-blue whitespace-nowrap">{c.cmd}</td>
                  <td className="py-0.5 text-term-dim">{c.desc}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
