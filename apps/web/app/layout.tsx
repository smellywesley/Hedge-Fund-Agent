import type { Metadata } from "next";
import "./globals.css";
import { BottomBar } from "@/components/BottomBar";
import { CommandBar } from "@/components/CommandBar";
import { Sidebar } from "@/components/Sidebar";
import { TickerStrip } from "@/components/TickerStrip";

export const metadata: Metadata = {
  title: "Terminal Alpha",
  description: "Educational AI equity research terminal — paper simulation only",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="flex h-screen flex-col overflow-hidden">
        <header className="flex items-center gap-4 border-b border-term-border bg-term-panel px-3 py-1.5">
          <span className="whitespace-nowrap text-sm font-bold tracking-[0.3em] text-term-amber">
            TERMINAL ALPHA
          </span>
          <CommandBar />
          <span className="whitespace-nowrap text-[10px] text-term-green">MKT: OPEN (mock)</span>
        </header>
        <TickerStrip />
        <div className="flex min-h-0 flex-1">
          <Sidebar />
          <main className="min-w-0 flex-1 overflow-y-auto p-2">{children}</main>
        </div>
        <BottomBar />
      </body>
    </html>
  );
}
