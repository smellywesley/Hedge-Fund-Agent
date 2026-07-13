"use client";
import { useApi } from "@/lib/api";

type Health = { status: string; db: string; prices: string; asOf: string };

export function BottomBar() {
  const { data, status } = useApi<Health>("/api/health", { status: "?", db: "?", prices: "?", asOf: "?" });
  const online = status === "api";
  return (
    <footer className="flex items-center justify-between border-t border-term-border bg-term-panel px-3 py-1 text-[10px] text-term-dim">
      <span>
        {online
          ? `DB: ${data.db} · PRICES: ${data.prices} · AS OF: ${data.asOf}`
          : "DATA: local mock fallback · start apps/api for persistence + live prices"}
      </span>
      <span>
        API:{" "}
        <span className={online ? "text-term-green" : status === "loading" ? "text-term-dim" : "text-term-red"}>
          {online ? "ONLINE" : status === "loading" ? "CHECKING" : "OFFLINE"}
        </span>{" "}
        · JOB QUEUE: idle
      </span>
      <span className="text-term-amber">PAPER SIMULATION ONLY — NOT FINANCIAL ADVICE</span>
    </footer>
  );
}
