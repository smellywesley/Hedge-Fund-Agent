"""Clearly-fake sample data for the Phase 1 MVP shell.

All values are illustrative. source is always "MOCK". Phase 3 replaces this
module with provider connectors (packages/mcp: OpenBB, yfinance, SEC EDGAR,
FRED) — see docs/data_sources.md.
"""

AS_OF = "2026-07-06T09:00:00Z"
SOURCE = "MOCK"

TICKERS = {
    "NVDA": {"symbol": "NVDA", "company_name": "NVIDIA Corp (mock)", "exchange": "NASDAQ", "sector": "Technology", "industry": "Semiconductors", "country": "US", "currency": "USD"},
    "AAPL": {"symbol": "AAPL", "company_name": "Apple Inc (mock)", "exchange": "NASDAQ", "sector": "Technology", "industry": "Consumer Electronics", "country": "US", "currency": "USD"},
    "MSFT": {"symbol": "MSFT", "company_name": "Microsoft Corp (mock)", "exchange": "NASDAQ", "sector": "Technology", "industry": "Software", "country": "US", "currency": "USD"},
    "GOOGL": {"symbol": "GOOGL", "company_name": "Alphabet Inc (mock)", "exchange": "NASDAQ", "sector": "Communication Services", "industry": "Internet", "country": "US", "currency": "USD"},
    "TSM": {"symbol": "TSM", "company_name": "Taiwan Semiconductor (mock)", "exchange": "NYSE", "sector": "Technology", "industry": "Semiconductors", "country": "TW", "currency": "USD"},
    "LLY": {"symbol": "LLY", "company_name": "Eli Lilly (mock)", "exchange": "NYSE", "sector": "Healthcare", "industry": "Pharmaceuticals", "country": "US", "currency": "USD"},
}

MARKET_SNAPSHOT = {
    "as_of": AS_OF,
    "source": SOURCE,
    "indices": [
        {"symbol": "SPY", "name": "S&P 500 ETF", "last": 612.40, "change_pct": 0.42},
        {"symbol": "QQQ", "name": "Nasdaq 100 ETF", "last": 548.10, "change_pct": 0.85},
        {"symbol": "DIA", "name": "Dow ETF", "last": 447.20, "change_pct": -0.12},
        {"symbol": "IWM", "name": "Russell 2000 ETF", "last": 231.55, "change_pct": -0.34},
    ],
    "rates": [
        {"symbol": "US2Y", "name": "2Y Treasury", "last": 3.82, "change_pct": 0.01},
        {"symbol": "US10Y", "name": "10Y Treasury", "last": 4.21, "change_pct": 0.03},
        {"symbol": "US30Y", "name": "30Y Treasury", "last": 4.55, "change_pct": 0.02},
    ],
    "fx": [
        {"symbol": "DXY", "name": "Dollar Index", "last": 101.3, "change_pct": -0.15},
        {"symbol": "EURUSD", "name": "EUR/USD", "last": 1.112, "change_pct": 0.10},
        {"symbol": "USDJPY", "name": "USD/JPY", "last": 148.9, "change_pct": 0.22},
        {"symbol": "USDSGD", "name": "USD/SGD", "last": 1.318, "change_pct": -0.05},
    ],
    "commodities": [
        {"symbol": "GC", "name": "Gold", "last": 2712.0, "change_pct": 0.31},
        {"symbol": "CL", "name": "WTI Crude", "last": 71.4, "change_pct": -1.20},
        {"symbol": "HG", "name": "Copper", "last": 4.62, "change_pct": 0.55},
        {"symbol": "NG", "name": "Nat Gas", "last": 2.84, "change_pct": 1.10},
    ],
    "volatility": [
        {"symbol": "VIX", "name": "VIX", "last": 14.8, "change_pct": -2.60},
        {"symbol": "MOVE", "name": "MOVE", "last": 92.1, "change_pct": 0.40},
    ],
    "sectors": [
        {"symbol": "XLK", "name": "Technology", "change_pct": 1.10},
        {"symbol": "XLF", "name": "Financials", "change_pct": 0.20},
        {"symbol": "XLE", "name": "Energy", "change_pct": -0.90},
        {"symbol": "XLV", "name": "Healthcare", "change_pct": 0.35},
        {"symbol": "XLY", "name": "Cons. Discretionary", "change_pct": 0.60},
        {"symbol": "XLI", "name": "Industrials", "change_pct": -0.15},
        {"symbol": "XLP", "name": "Cons. Staples", "change_pct": 0.05},
        {"symbol": "XLU", "name": "Utilities", "change_pct": -0.40},
        {"symbol": "XLB", "name": "Materials", "change_pct": 0.25},
    ],
    "regime": {
        "label": "RISK-ON (mock)",
        "score": 68,
        "notes": "Mock regime: mega-cap tech leadership, low VIX, stable rates.",
    },
    "ai_brief": {
        "agent": "Macro Analyst",
        "as_of": AS_OF,
        "confidence": "Medium",
        "sources": ["MOCK market feed"],
        "missing_data": ["No live FRED series ingested (Phase 3)"],
        "bullets": [
            "Mock: Equity breadth narrow; leadership concentrated in AI infrastructure names.",
            "Mock: 10Y stable near 4.2%; no rate shock priced for next FOMC.",
            "Mock: VIX under 15 signals complacency risk into earnings season.",
            "Mock: Dollar softening supports large-cap multinational revenue.",
            "Mock: Semis sector +1.1% leading; energy lagging on crude weakness.",
        ],
    },
}

WATCHLIST = [
    {"symbol": "NVDA", "company": "NVIDIA (mock)", "price": 182.40, "change_pct": 1.85, "volume_vs_avg": 1.4, "score": 79, "confidence": "Medium", "catalyst": "Earnings 2026-08-26", "latest_filing": "10-Q 2026-05-28", "news_risk": "None flagged", "next_action": "Update valuation"},
    {"symbol": "AAPL", "company": "Apple (mock)", "price": 236.10, "change_pct": -0.30, "volume_vs_avg": 0.9, "score": 64, "confidence": "High", "catalyst": "WWDC follow-through", "latest_filing": "10-Q 2026-05-02", "news_risk": "None flagged", "next_action": "No action"},
    {"symbol": "MSFT", "company": "Microsoft (mock)", "price": 512.75, "change_pct": 0.55, "volume_vs_avg": 1.1, "score": 71, "confidence": "High", "catalyst": "Earnings 2026-07-29", "latest_filing": "10-Q 2026-04-30", "news_risk": "None flagged", "next_action": "Review"},
    {"symbol": "TSM", "company": "TSMC (mock)", "price": 224.30, "change_pct": 2.10, "volume_vs_avg": 1.6, "score": 74, "confidence": "Medium", "catalyst": "Earnings 2026-07-17", "latest_filing": "20-F 2026-04-15", "news_risk": "Geopolitical headline flag", "next_action": "Research"},
    {"symbol": "LLY", "company": "Eli Lilly (mock)", "price": 792.60, "change_pct": -1.10, "volume_vs_avg": 1.2, "score": 69, "confidence": "Medium", "catalyst": "FDA decision Q3", "latest_filing": "10-Q 2026-05-08", "news_risk": "Pricing policy headlines", "next_action": "Review"},
]

FINANCIALS_NVDA = [
    {"symbol": "NVDA", "statement_type": "income", "metric": "Revenue", "fiscal_period": "FY2026", "value": 148.5, "unit": "USD bn", "source": SOURCE},
    {"symbol": "NVDA", "statement_type": "income", "metric": "Gross margin", "fiscal_period": "FY2026", "value": 74.2, "unit": "%", "source": SOURCE},
    {"symbol": "NVDA", "statement_type": "income", "metric": "Operating margin", "fiscal_period": "FY2026", "value": 61.8, "unit": "%", "source": SOURCE},
    {"symbol": "NVDA", "statement_type": "income", "metric": "Net income", "fiscal_period": "FY2026", "value": 81.3, "unit": "USD bn", "source": SOURCE},
    {"symbol": "NVDA", "statement_type": "cashflow", "metric": "Free cash flow", "fiscal_period": "FY2026", "value": 62.7, "unit": "USD bn", "source": SOURCE},
    {"symbol": "NVDA", "statement_type": "balance", "metric": "Net cash", "fiscal_period": "FY2026", "value": 38.9, "unit": "USD bn", "source": SOURCE},
]

NEWS = {
    "NVDA": [
        {"headline": "Mock: NVDA announces next-gen data center GPU roadmap", "source": "MOCK Wire", "published_at": "2026-07-05T14:00:00Z", "sentiment": "positive"},
        {"headline": "Mock: Hyperscaler capex commentary supports AI infrastructure demand", "source": "MOCK Wire", "published_at": "2026-07-03T11:30:00Z", "sentiment": "positive"},
        {"headline": "Mock: Analysts debate custom-silicon risk to GPU share", "source": "MOCK Wire", "published_at": "2026-07-01T09:00:00Z", "sentiment": "neutral"},
    ]
}

FILINGS = {
    "NVDA": [
        {"symbol": "NVDA", "form_type": "10-Q", "filing_date": "2026-05-28", "period_end": "2026-04-26", "title": "Quarterly report (mock)", "source_url": "https://example.com/mock-10q", "summary": "Mock 10-Q: data center revenue growth, customer concentration disclosure unchanged."},
        {"symbol": "NVDA", "form_type": "8-K", "filing_date": "2026-05-28", "period_end": None, "title": "Earnings release (mock)", "source_url": "https://example.com/mock-8k", "summary": "Mock 8-K: quarterly results and guidance."},
        {"symbol": "NVDA", "form_type": "10-K", "filing_date": "2026-03-01", "period_end": "2026-01-25", "title": "Annual report (mock)", "source_url": "https://example.com/mock-10k", "summary": "Mock 10-K: risk factors include cyclicality, export controls, concentration."},
    ]
}

# Component scores 0-100 fed to research_engine.scoring (Phase 4 computes these).
SCORE_COMPONENTS_NVDA = {
    "business_quality": 90,
    "growth_momentum": 88,
    "balance_sheet": 92,
    "valuation": 45,
    "technical_trend": 80,
    "catalyst_strength": 75,
    "estimate_revision": 82,
    "news_sentiment": 70,
    "liquidity_risk": 95,
}

CONFIDENCE_FACTORS_NVDA = {
    "data_completeness": 0.8,
    "data_freshness": 0.9,
    "source_quality": 0.5,   # mock data, not primary source
    "agent_agreement": 0.6,
    "model_stability": 0.4,  # valuation highly sensitive to terminal assumptions
}

RESEARCH_NVDA = {
    "symbol": "NVDA",
    "as_of": AS_OF,
    "source": SOURCE,
    "confidence": "Medium",
    "missing_data": ["Latest earnings transcript not ingested", "No live consensus estimates (Phase 3)"],
    "snapshot": "Mock: NVIDIA designs GPUs and full-stack accelerated computing platforms. Revenue is dominated by data center AI infrastructure sold to hyperscalers and enterprises.",
    "business_model": "Mock: Sells accelerated compute (GPUs, networking, systems) plus CUDA software ecosystem lock-in. Data center ~88% of revenue; gaming, pro-viz, auto the remainder.",
    "bull_case": "Mock: AI infrastructure capex supercycle persists; CUDA moat holds; networking and software attach expand margins; multi-year visibility from sovereign AI demand.",
    "bear_case": "Mock: Hyperscaler custom silicon erodes share; capex digestion causes an air pocket; valuation embeds flawless execution; export controls cap China revenue.",
    "red_team": "Mock red-team: The thesis assumes demand durability that has never been tested through a capex downturn. Customer concentration (top 4 = ~45% of revenue) means one budget cut breaks the model. Confidence downgraded pending transcript ingestion.",
    "catalysts": [
        {"date": "2026-08-26", "event": "Q2 FY27 earnings (mock)", "type": "earnings"},
        {"date": "2026-09-15", "event": "AI infrastructure summit keynote (mock)", "type": "product"},
        {"date": "2026-10-01", "event": "Export control review window (mock)", "type": "regulatory"},
    ],
    "risk_register": [
        {"category": "Business", "risk": "Customer concentration among top hyperscalers", "severity": "High"},
        {"category": "Financial", "risk": "Inventory/purchase commitments into demand slowdown", "severity": "Medium"},
        {"category": "Legal/Reg", "risk": "Export controls on advanced accelerators", "severity": "High"},
        {"category": "Macro", "risk": "Rate-driven multiple compression", "severity": "Medium"},
        {"category": "Valuation", "risk": "Terminal-value sensitivity dominates DCF", "severity": "High"},
    ],
}

AGENTS = [
    {"agent_name": "Data Engineer Agent", "task": "Pull, validate, normalize NVDA datasets", "summary": "Mock: prices, financials, filings metadata loaded. Transcript feed missing.", "sources": ["MOCK price feed", "MOCK fundamentals"], "missing_data": ["Earnings transcript"], "warnings": ["All data is mock — no live connectors in Phase 1"], "confidence": "High"},
    {"agent_name": "Company Analyst", "task": "Explain business model and revenue drivers", "summary": "Mock: Data center accelerators dominate revenue; CUDA ecosystem is the moat.", "sources": ["MOCK 10-K summary"], "missing_data": [], "warnings": [], "confidence": "Medium"},
    {"agent_name": "Filing Analyst", "task": "Summarize latest 10-Q/10-K", "summary": "Mock: 10-Q shows concentration disclosure unchanged; purchase commitments rising.", "sources": ["MOCK 10-Q 2026-05-28"], "missing_data": ["8-K exhibits not parsed"], "warnings": ["Summary from mock filing text"], "confidence": "Medium"},
    {"agent_name": "Fundamental Analyst", "task": "Review margins, FCF, balance sheet", "summary": "Mock: 74% gross margin, $62.7bn FCF, net cash. Quality metrics exceptional.", "sources": ["MOCK financials"], "missing_data": ["Segment-level ROIC"], "warnings": [], "confidence": "Medium"},
    {"agent_name": "Valuation Analyst", "task": "DCF + multiples, bear/base/bull", "summary": "Mock: Base $175, bull $240, bear $95. Range is wide — terminal assumptions dominate.", "sources": ["MOCK DCF model"], "missing_data": ["Live consensus estimates"], "warnings": ["High sensitivity to terminal multiple"], "confidence": "Low"},
    {"agent_name": "Technical Analyst", "task": "Trend, moving averages, relative strength", "summary": "Mock: Above 50/200DMA, RS strong vs SPX, volume confirming.", "sources": ["MOCK OHLCV"], "missing_data": [], "warnings": ["Technicals are descriptive, not predictive"], "confidence": "Medium"},
    {"agent_name": "Macro Analyst", "task": "Rates, FX, sector regime context", "summary": "Mock: Risk-on regime, stable 10Y, semis leadership — supportive backdrop.", "sources": ["MOCK macro feed"], "missing_data": ["FRED series (Phase 3)"], "warnings": [], "confidence": "Medium"},
    {"agent_name": "News Analyst", "task": "Market-moving headlines and narrative risk", "summary": "Mock: Positive roadmap coverage; custom-silicon debate is the live narrative risk.", "sources": ["MOCK Wire x3"], "missing_data": ["Social sentiment feed"], "warnings": ["Headline sentiment is noisy"], "confidence": "Low"},
    {"agent_name": "Bull Researcher", "task": "Strongest positive thesis", "summary": "Mock: Compute demand is structural; moat + roadmap cadence sustain share and margins.", "sources": ["MOCK research pack"], "missing_data": [], "warnings": ["Advocacy role — read with bear case"], "confidence": "Medium"},
    {"agent_name": "Bear Researcher", "task": "Strongest negative thesis", "summary": "Mock: Custom silicon + capex digestion + valuation = asymmetric downside on any demand wobble.", "sources": ["MOCK research pack"], "missing_data": [], "warnings": ["Advocacy role — read with bull case"], "confidence": "Medium"},
    {"agent_name": "Risk Manager", "task": "Concentration, drawdown, catalyst risk", "summary": "Mock: Paper fund semis exposure 41% — over 40% sector rule. Earnings clustering in late Aug.", "sources": ["MOCK paper portfolio"], "missing_data": ["Correlation matrix (Phase 4)"], "warnings": ["Sector concentration breach"], "confidence": "High"},
    {"agent_name": "Portfolio Manager", "task": "Synthesize paper-portfolio view", "summary": "Mock: Status REVIEW. Update NVDA/TSM valuations before next paper decision. Not financial advice; no real trades.", "sources": ["All agent notes"], "missing_data": [], "warnings": ["Paper simulation only"], "confidence": "Medium"},
    {"agent_name": "Audit Agent", "task": "Check citations, staleness, unsupported claims", "summary": "Mock: 2 claims flagged for missing sources; valuation output downgraded to Low confidence pending assumptions table.", "sources": ["Agent output log"], "missing_data": [], "warnings": ["Blocked: 'guaranteed upside' phrasing in draft bull note"], "confidence": "High"},
]

PAPER_POSITIONS = [
    {"id": 1, "symbol": "NVDA", "entry_price": 148.00, "current_price": 182.40, "quantity": 60, "position_size_pct": 13.8, "unrealized_pnl_pct": 23.2, "thesis": "AI infrastructure capex supercycle; CUDA moat", "invalidation_point": "Hyperscaler capex guidance cut >10%", "catalyst_date": "2026-08-26", "risk_notes": "Valuation sensitivity; sector concentration", "status": "OPEN"},
    {"id": 2, "symbol": "TSM", "entry_price": 190.50, "current_price": 224.30, "quantity": 70, "position_size_pct": 12.1, "unrealized_pnl_pct": 17.7, "thesis": "Foundry monopoly on leading edge; AI wafer demand", "invalidation_point": "N2 yield issues or Taiwan-strait escalation", "catalyst_date": "2026-07-17", "risk_notes": "Geopolitical tail risk", "status": "OPEN"},
    {"id": 3, "symbol": "MSFT", "entry_price": 465.00, "current_price": 512.75, "quantity": 25, "position_size_pct": 11.0, "unrealized_pnl_pct": 10.3, "thesis": "Azure AI monetization + Copilot seat expansion", "invalidation_point": "Azure growth <25% two consecutive quarters", "catalyst_date": "2026-07-29", "risk_notes": "Capex intensity compressing FCF", "status": "OPEN"},
    {"id": 4, "symbol": "LLY", "entry_price": 845.20, "current_price": 792.60, "quantity": 12, "position_size_pct": 8.4, "unrealized_pnl_pct": -6.2, "thesis": "GLP-1 franchise expansion into oral formulations", "invalidation_point": "Oral candidate misses efficacy endpoint", "catalyst_date": "2026-09-30", "risk_notes": "Pricing policy headlines; pipeline binary events", "status": "OPEN"},
    {"id": 5, "symbol": "GOOGL", "entry_price": 188.00, "current_price": 201.40, "quantity": 55, "position_size_pct": 9.6, "unrealized_pnl_pct": 7.1, "thesis": "Search resilience + Gemini enterprise traction, undemanding multiple", "invalidation_point": "Search revenue decline on AI substitution", "catalyst_date": "2026-07-23", "risk_notes": "Antitrust remedies overhang", "status": "OPEN"},
]

PAPER_FUND = {
    "as_of": AS_OF,
    "source": SOURCE,
    "aum": 1_000_000,
    "cash_pct": 45.1,
    "daily_pnl_pct": 0.62,
    "weekly_pnl_pct": 1.85,
    "disclaimer": "Paper simulation only. No real money, no brokerage connection, not financial advice.",
    "positions": PAPER_POSITIONS,
    "journal": [
        {"id": 1, "date": "2026-07-03", "symbol": "NVDA", "decision_type": "REVIEW", "decision_text": "Held through roadmap news; thesis intact.", "human_note": "Watch custom-silicon narrative."},
        {"id": 2, "date": "2026-06-24", "symbol": "LLY", "decision_type": "ADD", "decision_text": "Added 8.4% paper position after pullback.", "human_note": "Sized below 10% due to binary pipeline risk."},
        {"id": 3, "date": "2026-06-10", "symbol": "AMD", "decision_type": "PASS", "decision_text": "Passed — thesis overlapped NVDA without diversification benefit.", "human_note": "Avoid crowding the same trade."},
    ],
    "exposure": [
        {"bucket": "Semiconductors", "pct": 25.9},
        {"bucket": "Software/Cloud", "pct": 20.6},
        {"bucket": "Healthcare", "pct": 8.4},
        {"bucket": "Cash", "pct": 45.1},
    ],
    "exit_rules": [
        "Thesis invalidation point hit → mandatory review within 24h",
        "Position >15% of paper AUM → trim flag",
        "Earnings within 7 days → no new adds without review",
        "Two consecutive quarters of thesis KPI deterioration → exit review",
    ],
}

RISK_SUMMARY = {
    "as_of": AS_OF,
    "source": SOURCE,
    "sector_exposure": [
        {"sector": "Semiconductors", "pct": 25.9, "limit": 40, "status": "OK"},
        {"sector": "Software/Cloud", "pct": 20.6, "limit": 40, "status": "OK"},
        {"sector": "Healthcare", "pct": 8.4, "limit": 40, "status": "OK"},
        {"sector": "Tech total (semis+software)", "pct": 46.5, "limit": 40, "status": "WARNING"},
    ],
    "concentration": [
        {"symbol": "NVDA", "pct": 13.8, "limit": 15, "status": "OK"},
        {"symbol": "TSM", "pct": 12.1, "limit": 15, "status": "OK"},
        {"symbol": "MSFT", "pct": 11.0, "limit": 15, "status": "OK"},
    ],
    "metrics": [
        {"name": "Portfolio beta", "value": "placeholder (Phase 4)", "note": "Requires price history + factor model"},
        {"name": "Realized volatility", "value": "placeholder (Phase 4)", "note": "Requires daily paper NAV series"},
        {"name": "Max drawdown", "value": "placeholder (Phase 4)", "note": "Requires simulation history"},
        {"name": "Correlation matrix", "value": "placeholder (Phase 4)", "note": "NVDA/TSM/MSFT likely highly correlated"},
    ],
    "catalyst_warnings": [
        "3 of 5 paper positions report earnings within a 13-day window (Jul 17 – Jul 29).",
        "NVDA + TSM + MSFT are one correlated AI-infrastructure trade — treat as a single risk cluster.",
    ],
    "rules_checklist": [
        {"rule": "No single paper position above 15%", "status": "PASS"},
        {"rule": "No sector above 40% without warning", "status": "WARNING"},
        {"rule": "High-vol names have thesis + invalidation point", "status": "PASS"},
        {"rule": "Earnings within 7 days triggers review warning", "status": "PENDING (Jul 17 first event)"},
        {"rule": "Missing data triggers confidence downgrade", "status": "PASS"},
    ],
}

REPORTS = [
    {"id": 1, "symbol": "NVDA", "report_type": "Investment Memo", "title": "NVDA — AI Infrastructure Memo (mock)", "status": "READY", "generated_at": "2026-07-02T10:00:00Z", "confidence": "Medium"},
    {"id": 2, "symbol": "TSM", "report_type": "Flash Note", "title": "TSM — Pre-earnings Flash (mock)", "status": "READY", "generated_at": "2026-07-01T08:00:00Z", "confidence": "Medium"},
    {"id": 3, "symbol": "PORT", "report_type": "Portfolio Health", "title": "Weekly Paper Fund Health (mock)", "status": "READY", "generated_at": "2026-06-30T07:00:00Z", "confidence": "High"},
    {"id": 4, "symbol": "LLY", "report_type": "Initiating Coverage", "title": "LLY — Initiating Coverage draft (mock)", "status": "DRAFT — blocked by Audit Agent (missing sources)", "generated_at": "2026-06-28T16:00:00Z", "confidence": "Low"},
]
