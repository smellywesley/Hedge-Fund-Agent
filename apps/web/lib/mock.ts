// Clearly-fake sample data for the Phase 1 MVP shell. Mirrors
// apps/api/app/mock_data.py. Phase 2 replaces these imports with API calls
// (lib/api.ts) — that swap is a Phase 2 success criterion by design.

import type {
  AgentOutput, DecisionJournalEntry, Filing, FinancialStatementMetric,
  MarketSnapshot, PaperPosition, ResearchReport, ResearchScore, RiskSummary,
  ScreenerResult, WatchlistItem,
} from "./types";

export const AS_OF = "2026-07-06T09:00:00Z";
export const SOURCE = "MOCK";
export const DISCLAIMER =
  "Educational paper simulation only. No real money, no brokerage connection, not financial advice.";

export const TICKER_STRIP = [
  { symbol: "SPY", last: 612.4, changePct: 0.42 },
  { symbol: "QQQ", last: 548.1, changePct: 0.85 },
  { symbol: "VIX", last: 14.8, changePct: -2.6 },
  { symbol: "10Y", last: 4.21, changePct: 0.03 },
  { symbol: "DXY", last: 101.3, changePct: -0.15 },
  { symbol: "BTC", last: 118450, changePct: 1.9 },
  { symbol: "GOLD", last: 2712, changePct: 0.31 },
  { symbol: "OIL", last: 71.4, changePct: -1.2 },
];

export const MARKET: MarketSnapshot = {
  asOf: AS_OF,
  source: SOURCE,
  indices: [
    { symbol: "SPY", name: "S&P 500 ETF", last: 612.4, changePct: 0.42 },
    { symbol: "QQQ", name: "Nasdaq 100 ETF", last: 548.1, changePct: 0.85 },
    { symbol: "DIA", name: "Dow ETF", last: 447.2, changePct: -0.12 },
    { symbol: "IWM", name: "Russell 2000 ETF", last: 231.55, changePct: -0.34 },
  ],
  rates: [
    { symbol: "US2Y", name: "2Y Treasury", last: 3.82, changePct: 0.01 },
    { symbol: "US10Y", name: "10Y Treasury", last: 4.21, changePct: 0.03 },
    { symbol: "US30Y", name: "30Y Treasury", last: 4.55, changePct: 0.02 },
  ],
  fx: [
    { symbol: "DXY", name: "Dollar Index", last: 101.3, changePct: -0.15 },
    { symbol: "EURUSD", name: "EUR/USD", last: 1.112, changePct: 0.1 },
    { symbol: "USDJPY", name: "USD/JPY", last: 148.9, changePct: 0.22 },
    { symbol: "USDSGD", name: "USD/SGD", last: 1.318, changePct: -0.05 },
  ],
  commodities: [
    { symbol: "GC", name: "Gold", last: 2712, changePct: 0.31 },
    { symbol: "CL", name: "WTI Crude", last: 71.4, changePct: -1.2 },
    { symbol: "HG", name: "Copper", last: 4.62, changePct: 0.55 },
    { symbol: "NG", name: "Nat Gas", last: 2.84, changePct: 1.1 },
  ],
  volatility: [
    { symbol: "VIX", name: "VIX", last: 14.8, changePct: -2.6 },
    { symbol: "MOVE", name: "MOVE", last: 92.1, changePct: 0.4 },
  ],
  sectors: [
    { symbol: "XLK", name: "Technology", changePct: 1.1 },
    { symbol: "XLF", name: "Financials", changePct: 0.2 },
    { symbol: "XLE", name: "Energy", changePct: -0.9 },
    { symbol: "XLV", name: "Healthcare", changePct: 0.35 },
    { symbol: "XLY", name: "Cons. Disc.", changePct: 0.6 },
    { symbol: "XLI", name: "Industrials", changePct: -0.15 },
    { symbol: "XLP", name: "Staples", changePct: 0.05 },
    { symbol: "XLU", name: "Utilities", changePct: -0.4 },
    { symbol: "XLB", name: "Materials", changePct: 0.25 },
  ],
  regime: {
    label: "RISK-ON (mock)",
    score: 68,
    notes: "Mock regime: mega-cap tech leadership, low VIX, stable rates. Narrow breadth is the caveat.",
  },
  aiBrief: {
    agent: "Macro Analyst",
    asOf: AS_OF,
    confidence: "Medium",
    sources: ["MOCK market feed"],
    missingData: ["No live FRED series ingested (Phase 3)"],
    bullets: [
      "Mock: Equity breadth narrow; leadership concentrated in AI infrastructure names.",
      "Mock: 10Y stable near 4.2%; no rate shock priced for next FOMC.",
      "Mock: VIX under 15 signals complacency risk into earnings season.",
      "Mock: Dollar softening supports large-cap multinational revenue.",
      "Mock: Semis +1.1% leading; energy lagging on crude weakness.",
    ],
  },
};

export const WATCHLIST: WatchlistItem[] = [
  { symbol: "NVDA", company: "NVIDIA (mock)", price: 182.4, changePct: 1.85, volumeVsAvg: 1.4, score: 79, confidence: "Medium", catalyst: "Earnings 08-26", latestFiling: "10-Q 05-28", newsRisk: "None flagged", nextAction: "Update valuation" },
  { symbol: "AAPL", company: "Apple (mock)", price: 236.1, changePct: -0.3, volumeVsAvg: 0.9, score: 64, confidence: "High", catalyst: "WWDC follow-through", latestFiling: "10-Q 05-02", newsRisk: "None flagged", nextAction: "No action" },
  { symbol: "MSFT", company: "Microsoft (mock)", price: 512.75, changePct: 0.55, volumeVsAvg: 1.1, score: 71, confidence: "High", catalyst: "Earnings 07-29", latestFiling: "10-Q 04-30", newsRisk: "None flagged", nextAction: "Review" },
  { symbol: "TSM", company: "TSMC (mock)", price: 224.3, changePct: 2.1, volumeVsAvg: 1.6, score: 74, confidence: "Medium", catalyst: "Earnings 07-17", latestFiling: "20-F 04-15", newsRisk: "Geopolitical flag", nextAction: "Research" },
  { symbol: "LLY", company: "Eli Lilly (mock)", price: 792.6, changePct: -1.1, volumeVsAvg: 1.2, score: 69, confidence: "Medium", catalyst: "FDA decision Q3", latestFiling: "10-Q 05-08", newsRisk: "Pricing headlines", nextAction: "Review" },
];

export const SCREENER_CATEGORIES = [
  { category: "Fundamental quality", filters: "ROIC > 20%, gross margin > 50%, debt/EBITDA < 1x" },
  { category: "Growth", filters: "Revenue CAGR > 15%, positive estimate revisions" },
  { category: "Valuation", filters: "FCF yield > 2%, EV/EBITDA < sector median" },
  { category: "Technical", filters: "Price > 50DMA & 200DMA, RS top quartile" },
  { category: "Catalyst", filters: "Earnings < 45 days, product launch, regulatory decision" },
  { category: "Risk", filters: "Exclude: earnings miss streak, legal overhang, high leverage" },
  { category: "Liquidity", filters: "Market cap > $10bn, ADV > $100m" },
];

export const SCREENER_RESULTS: ScreenerResult[] = [
  { symbol: "NVDA", company: "NVIDIA (mock)", reasonIncluded: "AI infrastructure exposure, strong estimate revisions, quality metrics", reasonCareful: "Valuation, cyclicality, hyperscaler custom-silicon risk", confidence: "Medium", nextAction: "Run full equity research report" },
  { symbol: "TSM", company: "TSMC (mock)", reasonIncluded: "Leading-edge foundry monopoly, AI wafer demand", reasonCareful: "Geopolitical tail risk, capex intensity", confidence: "Medium", nextAction: "Run research before earnings 07-17" },
  { symbol: "LLY", company: "Eli Lilly (mock)", reasonIncluded: "GLP-1 franchise growth, pipeline optionality", reasonCareful: "Binary pipeline events, pricing policy pressure", confidence: "Medium", nextAction: "Review after FDA decision" },
  { symbol: "MSFT", company: "Microsoft (mock)", reasonIncluded: "Azure AI monetization, durable enterprise moat", reasonCareful: "Capex compressing FCF margin", confidence: "High", nextAction: "Update model post-earnings" },
];

export const RESEARCH_NVDA = {
  symbol: "NVDA",
  asOf: AS_OF,
  source: SOURCE,
  confidence: "Medium" as const,
  missingData: ["Latest earnings transcript not ingested", "No live consensus estimates (Phase 3)"],
  snapshot:
    "Mock: NVIDIA designs GPUs and full-stack accelerated computing platforms. Revenue is dominated by data center AI infrastructure sold to hyperscalers and enterprises. Segments: Data Center (~88%), Gaming, Pro Visualization, Automotive.",
  businessModel:
    "Mock: Sells accelerated compute (GPUs, networking, systems) with CUDA software ecosystem lock-in. Pricing power from performance leadership and switching costs; roadmap cadence (annual architecture) sustains upgrade cycles.",
  financials: [
    { statementType: "Income", metric: "Revenue", fiscalPeriod: "FY2026", value: "$148.5bn" },
    { statementType: "Income", metric: "Gross margin", fiscalPeriod: "FY2026", value: "74.2%" },
    { statementType: "Income", metric: "Operating margin", fiscalPeriod: "FY2026", value: "61.8%" },
    { statementType: "Income", metric: "Net income", fiscalPeriod: "FY2026", value: "$81.3bn" },
    { statementType: "Cash flow", metric: "Free cash flow", fiscalPeriod: "FY2026", value: "$62.7bn" },
    { statementType: "Balance", metric: "Net cash", fiscalPeriod: "FY2026", value: "$38.9bn" },
  ] as FinancialStatementMetric[],
  kpis: [
    { name: "Revenue growth YoY", value: "+62%", trend: "up" },
    { name: "Data center mix", value: "88%", trend: "up" },
    { name: "FCF margin", value: "42%", trend: "flat" },
    { name: "ROIC", value: "78%", trend: "up" },
    { name: "Share dilution", value: "-0.8% (buybacks)", trend: "down" },
    { name: "Top-4 customer concentration", value: "~45%", trend: "up" },
  ],
  catalysts: [
    { date: "2026-08-26", event: "Q2 FY27 earnings (mock)", type: "Earnings" },
    { date: "2026-09-15", event: "AI infrastructure summit keynote (mock)", type: "Product" },
    { date: "2026-10-01", event: "Export control review window (mock)", type: "Regulatory" },
  ],
  riskRegister: [
    { category: "Business", risk: "Customer concentration among top hyperscalers", severity: "High" },
    { category: "Financial", risk: "Inventory/purchase commitments into demand slowdown", severity: "Medium" },
    { category: "Legal/Reg", risk: "Export controls on advanced accelerators", severity: "High" },
    { category: "Macro", risk: "Rate-driven multiple compression", severity: "Medium" },
    { category: "Valuation", risk: "Terminal-value sensitivity dominates DCF", severity: "High" },
  ],
  bullCase:
    "Mock: AI infrastructure capex supercycle persists for years; CUDA moat holds against custom silicon; networking and software attach expand margins; sovereign AI adds a new demand pillar with multi-year visibility.",
  bearCase:
    "Mock: Hyperscaler custom silicon erodes share at the margin; capex digestion causes an air pocket quarter; valuation embeds flawless execution; export controls permanently cap China revenue.",
  redTeam:
    "Mock red-team: The thesis assumes demand durability never tested through a capex downturn. Top-4 customers ≈45% of revenue — one budget cut breaks the model. Valuation range is wide enough ($95–$240) that conviction claims are not supported. Confidence capped at Medium pending transcript ingestion.",
};

// scoreTotal matches research_engine.scoring output for these components (API: 79.3)
export const RESEARCH_SCORE: ResearchScore = {
  scoreTotal: 79.3,
  confidence: "Medium",
  missingComponents: [],
  components: [
    { name: "Business Quality", weightPct: 15, value: 90 },
    { name: "Growth / Estimate Momentum", weightPct: 15, value: 88 },
    { name: "Balance Sheet Strength", weightPct: 10, value: 92 },
    { name: "Valuation Attractiveness", weightPct: 15, value: 45 },
    { name: "Technical Trend", weightPct: 10, value: 80 },
    { name: "Catalyst Strength", weightPct: 10, value: 75 },
    { name: "Analyst / Estimate Revision", weightPct: 10, value: 82 },
    { name: "News / Sentiment", weightPct: 5, value: 70 },
    { name: "Liquidity / Risk Control", weightPct: 10, value: 95 },
  ],
};

export const AGENTS: AgentOutput[] = [
  { agentName: "Data Engineer Agent", task: "Pull, validate, normalize NVDA datasets", summary: "Mock: prices, financials, filings metadata loaded. Transcript feed missing.", confidence: "High", sources: ["MOCK price feed", "MOCK fundamentals"], missingData: ["Earnings transcript"], warnings: ["All data is mock — no live connectors in Phase 1"] },
  { agentName: "Company Analyst", task: "Explain business model and revenue drivers", summary: "Mock: Data center accelerators dominate revenue; CUDA ecosystem is the moat.", confidence: "Medium", sources: ["MOCK 10-K summary"], missingData: [], warnings: [] },
  { agentName: "Filing Analyst", task: "Summarize latest 10-Q/10-K", summary: "Mock: 10-Q shows concentration disclosure unchanged; purchase commitments rising.", confidence: "Medium", sources: ["MOCK 10-Q 2026-05-28"], missingData: ["8-K exhibits not parsed"], warnings: ["Summary from mock filing text"] },
  { agentName: "Fundamental Analyst", task: "Review margins, FCF, balance sheet", summary: "Mock: 74% gross margin, $62.7bn FCF, net cash. Quality metrics exceptional.", confidence: "Medium", sources: ["MOCK financials"], missingData: ["Segment-level ROIC"], warnings: [] },
  { agentName: "Valuation Analyst", task: "DCF + multiples, bear/base/bull", summary: "Mock: Base $175, bull $240, bear $95. Range is wide — terminal assumptions dominate.", confidence: "Low", sources: ["MOCK DCF model"], missingData: ["Live consensus estimates"], warnings: ["High sensitivity to terminal multiple"] },
  { agentName: "Technical Analyst", task: "Trend, moving averages, relative strength", summary: "Mock: Above 50/200DMA, RS strong vs SPX, volume confirming.", confidence: "Medium", sources: ["MOCK OHLCV"], missingData: [], warnings: ["Technicals are descriptive, not predictive"] },
  { agentName: "Macro Analyst", task: "Rates, FX, sector regime context", summary: "Mock: Risk-on regime, stable 10Y, semis leadership — supportive backdrop.", confidence: "Medium", sources: ["MOCK macro feed"], missingData: ["FRED series (Phase 3)"], warnings: [] },
  { agentName: "News Analyst", task: "Market-moving headlines and narrative risk", summary: "Mock: Positive roadmap coverage; custom-silicon debate is the live narrative risk.", confidence: "Low", sources: ["MOCK Wire x3"], missingData: ["Social sentiment feed"], warnings: ["Headline sentiment is noisy"] },
  { agentName: "Bull Researcher", task: "Strongest positive thesis", summary: "Mock: Compute demand is structural; moat + roadmap cadence sustain share and margins.", confidence: "Medium", sources: ["MOCK research pack"], missingData: [], warnings: ["Advocacy role — read with bear case"] },
  { agentName: "Bear Researcher", task: "Strongest negative thesis", summary: "Mock: Custom silicon + capex digestion + valuation = asymmetric downside on any demand wobble.", confidence: "Medium", sources: ["MOCK research pack"], missingData: [], warnings: ["Advocacy role — read with bull case"] },
  { agentName: "Risk Manager", task: "Concentration, drawdown, catalyst risk", summary: "Mock: Tech exposure 46.5% — over 40% sector rule. Earnings clustering Jul 17–29.", confidence: "High", sources: ["MOCK paper portfolio"], missingData: ["Correlation matrix (Phase 4)"], warnings: ["Sector concentration breach"] },
  { agentName: "Portfolio Manager", task: "Synthesize paper-portfolio view", summary: "Mock: Status REVIEW. Update NVDA/TSM valuations before next paper decision. Not financial advice; no real trades.", confidence: "Medium", sources: ["All agent notes"], missingData: [], warnings: ["Paper simulation only"] },
  { agentName: "Audit Agent", task: "Check citations, staleness, unsupported claims", summary: "Mock: 2 claims flagged for missing sources; valuation output downgraded to Low pending assumptions table.", confidence: "High", sources: ["Agent output log"], missingData: [], warnings: ["Blocked: 'guaranteed upside' phrasing in draft bull note"] },
];

export const FUND = {
  asOf: AS_OF,
  source: SOURCE,
  aum: 1_000_000,
  cashPct: 45.1,
  dailyPnlPct: 0.62,
  weeklyPnlPct: 1.85,
  exposure: [
    { bucket: "Semiconductors", pct: 25.9 },
    { bucket: "Software/Cloud", pct: 20.6 },
    { bucket: "Healthcare", pct: 8.4 },
    { bucket: "Cash", pct: 45.1 },
  ],
  exitRules: [
    "Thesis invalidation point hit → mandatory review within 24h",
    "Position >15% of paper AUM → trim flag",
    "Earnings within 7 days → no new adds without review",
    "Two consecutive quarters of thesis KPI deterioration → exit review",
  ],
};

export const POSITIONS: PaperPosition[] = [
  { id: 1, symbol: "NVDA", entryPrice: 148.0, currentPrice: 182.4, quantity: 60, positionSizePct: 13.8, unrealizedPnlPct: 23.2, thesis: "AI infrastructure capex supercycle; CUDA moat", invalidationPoint: "Hyperscaler capex guidance cut >10%", catalystDate: "2026-08-26", riskNotes: "Valuation sensitivity; sector concentration" },
  { id: 2, symbol: "TSM", entryPrice: 190.5, currentPrice: 224.3, quantity: 70, positionSizePct: 12.1, unrealizedPnlPct: 17.7, thesis: "Foundry monopoly on leading edge; AI wafer demand", invalidationPoint: "N2 yield issues or Taiwan-strait escalation", catalystDate: "2026-07-17", riskNotes: "Geopolitical tail risk" },
  { id: 3, symbol: "MSFT", entryPrice: 465.0, currentPrice: 512.75, quantity: 25, positionSizePct: 11.0, unrealizedPnlPct: 10.3, thesis: "Azure AI monetization + Copilot seat expansion", invalidationPoint: "Azure growth <25% two consecutive quarters", catalystDate: "2026-07-29", riskNotes: "Capex intensity compressing FCF" },
  { id: 4, symbol: "LLY", entryPrice: 845.2, currentPrice: 792.6, quantity: 12, positionSizePct: 8.4, unrealizedPnlPct: -6.2, thesis: "GLP-1 franchise expansion into oral formulations", invalidationPoint: "Oral candidate misses efficacy endpoint", catalystDate: "2026-09-30", riskNotes: "Pricing headlines; pipeline binary events" },
  { id: 5, symbol: "GOOGL", entryPrice: 188.0, currentPrice: 201.4, quantity: 55, positionSizePct: 9.6, unrealizedPnlPct: 7.1, thesis: "Search resilience + Gemini enterprise traction, undemanding multiple", invalidationPoint: "Search revenue decline on AI substitution", catalystDate: "2026-07-23", riskNotes: "Antitrust remedies overhang" },
];

export const JOURNAL: DecisionJournalEntry[] = [
  { id: 1, date: "2026-07-03", symbol: "NVDA", decisionType: "REVIEW", decisionText: "Held through roadmap news; thesis intact.", humanNote: "Watch custom-silicon narrative." },
  { id: 2, date: "2026-06-24", symbol: "LLY", decisionType: "ADD", decisionText: "Added 8.4% paper position after pullback.", humanNote: "Sized below 10% due to binary pipeline risk." },
  { id: 3, date: "2026-06-10", symbol: "AMD", decisionType: "PASS", decisionText: "Passed — thesis overlapped NVDA without diversification benefit.", humanNote: "Avoid crowding the same trade." },
];

export const RISK: RiskSummary = {
  asOf: AS_OF,
  source: SOURCE,
  sectorExposure: [
    { sector: "Semiconductors", pct: 25.9, limit: 40, status: "OK" },
    { sector: "Software/Cloud", pct: 20.6, limit: 40, status: "OK" },
    { sector: "Healthcare", pct: 8.4, limit: 40, status: "OK" },
    { sector: "Tech total (semis+software)", pct: 46.5, limit: 40, status: "WARNING" },
  ],
  concentration: [
    { symbol: "NVDA", pct: 13.8, limit: 15, status: "OK" },
    { symbol: "TSM", pct: 12.1, limit: 15, status: "OK" },
    { symbol: "MSFT", pct: 11.0, limit: 15, status: "OK" },
  ],
  metrics: [
    { name: "Portfolio beta", value: "— placeholder", note: "Phase 4: requires price history + factor model" },
    { name: "Realized volatility", value: "— placeholder", note: "Phase 4: requires daily paper NAV series" },
    { name: "Max drawdown", value: "— placeholder", note: "Phase 4: requires simulation history" },
    { name: "Correlation matrix", value: "— placeholder", note: "Phase 4: NVDA/TSM/MSFT likely highly correlated" },
  ],
  catalystWarnings: [
    "3 of 5 paper positions report earnings within a 13-day window (Jul 17 – Jul 29).",
    "NVDA + TSM + MSFT are one correlated AI-infrastructure trade — treat as a single risk cluster.",
  ],
  rulesChecklist: [
    { rule: "No single paper position above 15%", status: "PASS" },
    { rule: "No sector above 40% without warning", status: "WARNING" },
    { rule: "High-vol names have thesis + invalidation point", status: "PASS" },
    { rule: "Earnings within 7 days triggers review warning", status: "PENDING (Jul 17 first event)" },
    { rule: "Missing data triggers confidence downgrade", status: "PASS" },
  ],
};

export const FILINGS: Filing[] = [
  { formType: "10-Q", filingDate: "2026-05-28", title: "NVDA Quarterly report (mock)", summary: "Mock 10-Q: data center revenue growth, customer concentration disclosure unchanged, purchase commitments rising.", sourceUrl: "https://example.com/mock-10q" },
  { formType: "8-K", filingDate: "2026-05-28", title: "NVDA Earnings release (mock)", summary: "Mock 8-K: quarterly results and guidance.", sourceUrl: "https://example.com/mock-8k" },
  { formType: "10-K", filingDate: "2026-03-01", title: "NVDA Annual report (mock)", summary: "Mock 10-K: risk factors include cyclicality, export controls, concentration.", sourceUrl: "https://example.com/mock-10k" },
  { formType: "20-F", filingDate: "2026-04-15", title: "TSM Annual report (mock)", summary: "Mock 20-F: leading-edge capacity expansion, geographic risk disclosure.", sourceUrl: "https://example.com/mock-20f" },
];

export const NEWS = [
  { headline: "Mock: NVDA announces next-gen data center GPU roadmap", source: "MOCK Wire", publishedAt: "2026-07-05 14:00Z", sentiment: "positive" },
  { headline: "Mock: Hyperscaler capex commentary supports AI infrastructure demand", source: "MOCK Wire", publishedAt: "2026-07-03 11:30Z", sentiment: "positive" },
  { headline: "Mock: Analysts debate custom-silicon risk to GPU share", source: "MOCK Wire", publishedAt: "2026-07-01 09:00Z", sentiment: "neutral" },
  { headline: "Mock: LLY pricing policy headlines pressure pharma sentiment", source: "MOCK Wire", publishedAt: "2026-06-30 16:00Z", sentiment: "negative" },
];

export const NEWS_RISK_FLAGS = [
  "Mock: TSM — geopolitical headline flag (Taiwan strait exercises).",
  "Mock: LLY — drug pricing policy proposal in committee.",
];

export const DCF = {
  disclaimer:
    "Valuation output depends entirely on assumptions below. Edit them and the answer changes. A model is a thinking tool, not a prediction.",
  assumptions: [
    { name: "Revenue growth Y1–5", bear: "8%", base: "22%", bull: "35%" },
    { name: "Revenue growth Y6–10", bear: "4%", base: "10%", bull: "15%" },
    { name: "Operating margin", bear: "48%", base: "58%", bull: "63%" },
    { name: "Tax rate", bear: "17%", base: "15%", bull: "14%" },
    { name: "Capex / revenue", bear: "6%", base: "4.5%", bull: "3.5%" },
    { name: "WACC", bear: "11%", base: "9.5%", bull: "8.5%" },
    { name: "Terminal growth", bear: "2.0%", base: "3.0%", bull: "4.0%" },
    { name: "Terminal multiple", bear: "14x", base: "22x", bull: "30x" },
  ],
  cases: [
    { name: "Bear", fairValue: "$95", note: "Capex digestion + share loss to custom silicon" },
    { name: "Base", fairValue: "$175", note: "Growth moderates, moat holds, margins stable" },
    { name: "Bull", fairValue: "$240", note: "Supercycle persists, software attach expands" },
  ],
};

export const REPORTS: ResearchReport[] = [
  { id: 1, symbol: "NVDA", reportType: "Investment Memo", title: "NVDA — AI Infrastructure Memo (mock)", status: "READY", generatedAt: "2026-07-02", confidence: "Medium" },
  { id: 2, symbol: "TSM", reportType: "Flash Note", title: "TSM — Pre-earnings Flash (mock)", status: "READY", generatedAt: "2026-07-01", confidence: "Medium" },
  { id: 3, symbol: "PORT", reportType: "Portfolio Health", title: "Weekly Paper Fund Health (mock)", status: "READY", generatedAt: "2026-06-30", confidence: "High" },
  { id: 4, symbol: "LLY", reportType: "Initiating Coverage", title: "LLY — Initiating Coverage draft (mock)", status: "DRAFT — blocked by Audit Agent", generatedAt: "2026-06-28", confidence: "Low" },
];
