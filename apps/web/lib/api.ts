"use client";
// Phase 2: pages fetch the backend and fall back to lib/mock.ts if it's down,
// so the UI never renders blank. `status` tells the page which one it got.
import { useCallback, useEffect, useState } from "react";

export const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type ApiStatus = "loading" | "api" | "fallback";

export function useApi<T>(path: string, fallback: T) {
  const [data, setData] = useState<T>(fallback);
  const [status, setStatus] = useState<ApiStatus>("loading");
  const [tick, setTick] = useState(0);

  useEffect(() => {
    let alive = true;
    fetch(`${API}${path}`, { cache: "no-store" })
      .then((r) => { if (!r.ok) throw new Error(`${r.status}`); return r.json(); })
      .then((d: T) => { if (alive) { setData(d); setStatus("api"); } })
      .catch(() => { if (alive) setStatus("fallback"); });
    return () => { alive = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps -- fallback is a stable mock literal
  }, [path, tick]);

  const refetch = useCallback(() => setTick((t) => t + 1), []);
  return { data, status, refetch };
}

export async function apiSend(path: string, method: "POST" | "DELETE" | "PATCH", body?: unknown) {
  const r = await fetch(`${API}${path}`, {
    method,
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!r.ok) {
    const detail = await r.json().then((j) => j.detail).catch(() => r.statusText);
    throw new Error(typeof detail === "string" ? detail : r.statusText);
  }
  return r.json();
}
