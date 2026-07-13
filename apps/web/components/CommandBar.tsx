"use client";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { apiSend } from "@/lib/api";

// Command router. WL ADD/REMOVE hit the persistence API; the rest navigate.
// Supported: NVDA | ER NVDA | DCF NVDA | NEWS NVDA | RISK PORT |
//            WL ADD NVDA | WL REMOVE NVDA | FUND HEALTH | REPORT NVDA
function route(raw: string): string | null {
  const cmd = raw.trim().toUpperCase();
  if (!cmd) return null;
  const [head] = cmd.split(/\s+/);
  if (head === "ER") return "/research";
  if (head === "DCF") return "/models";
  if (head === "NEWS") return "/news";
  if (head === "RISK") return "/risk";
  if (head === "WL") return "/watchlist";
  if (head === "FUND") return "/fund";
  if (head === "REPORT") return "/reports";
  if (head === "MARKET" || head === "REGIME" || head === "SECTORS") return "/markets";
  if (/^[A-Z]{1,5}$/.test(head)) return "/research"; // bare ticker
  return null;
}

export function CommandBar() {
  const router = useRouter();
  const [value, setValue] = useState("");
  const [msg, setMsg] = useState<{ text: string; err: boolean } | null>(null);

  async function run(raw: string) {
    const parts = raw.trim().toUpperCase().split(/\s+/);
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
    <div className="flex flex-1 items-center gap-2">
      <span className="text-term-amber">&gt;</span>
      <input
        className="w-full max-w-xl bg-black/40 px-2 py-1 text-term-amber placeholder-term-dim outline-none border border-term-border focus:border-term-amber"
        placeholder="Command: NVDA · ER NVDA · DCF NVDA · NEWS NVDA · RISK PORT · WL ADD NVDA · FUND HEALTH · REPORT NVDA"
        value={value}
        onChange={(e) => { setValue(e.target.value); setMsg(null); }}
        onKeyDown={(e) => { if (e.key === "Enter") run(value); }}
      />
      {msg && (
        <span className={`text-[10px] whitespace-nowrap ${msg.err ? "text-term-red" : "text-term-green"}`}>
          {msg.text}
        </span>
      )}
    </div>
  );
}
