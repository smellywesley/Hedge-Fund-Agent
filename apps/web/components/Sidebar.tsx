"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const TABS = [
  { href: "/markets", label: "MARKETS" },
  { href: "/watchlist", label: "WATCHLIST" },
  { href: "/screener", label: "SCREENER" },
  { href: "/research", label: "EQUITY RES." },
  { href: "/desk", label: "AI DESK" },
  { href: "/fund", label: "PAPER FUND" },
  { href: "/risk", label: "RISK" },
  { href: "/news", label: "NEWS/FILINGS" },
  { href: "/models", label: "MODEL LAB" },
  { href: "/reports", label: "REPORTS" },
];

export function Sidebar() {
  const pathname = usePathname();
  return (
    <nav className="w-36 shrink-0 border-r border-term-border bg-term-panel">
      <ul>
        {TABS.map((t) => {
          const active = pathname.startsWith(t.href);
          return (
            <li key={t.href}>
              <Link
                href={t.href}
                className={`block border-b border-term-border/40 px-3 py-2 text-[11px] tracking-widest ${
                  active
                    ? "bg-term-amber/10 text-term-amber border-l-2 border-l-term-amber"
                    : "text-term-dim hover:text-term-text hover:bg-term-border/20"
                }`}
              >
                {t.label}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
