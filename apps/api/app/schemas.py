"""Pydantic models for Terminal Alpha (Phase 1 shapes).

Mirrors apps/web/lib/types.ts. Every AI/mock payload carries source,
timestamp (as_of), confidence, and missing-data warnings — the audit
contract from docs/agent_contracts.md.
"""
from pydantic import BaseModel


class Ticker(BaseModel):
    symbol: str
    company_name: str
    exchange: str
    sector: str
    industry: str
    country: str = "US"
    currency: str = "USD"


class MarketSnapshot(BaseModel):
    as_of: str
    source: str
    indices: list[dict]
    rates: list[dict]
    fx: list[dict]
    commodities: list[dict]
    volatility: list[dict]
    sectors: list[dict]
    regime: dict
    ai_brief: dict


class WatchlistItem(BaseModel):
    symbol: str
    company: str
    price: float
    change_pct: float
    volume_vs_avg: float
    score: float
    confidence: str
    catalyst: str
    latest_filing: str
    news_risk: str
    next_action: str


class ResearchScore(BaseModel):
    symbol: str
    score_total: float
    components: dict
    weights: dict
    missing_components: list[str]
    confidence: str
    generated_at: str
    source: str


class AgentOutput(BaseModel):
    agent_name: str
    symbol: str | None = None
    task: str
    summary: str
    key_findings: list[str] = []
    sources: list[str]
    assumptions: list[str] = []
    missing_data: list[str]
    warnings: list[str]
    confidence: str
    generated_at: str
    requires_human_review: bool = True


class Filing(BaseModel):
    symbol: str
    form_type: str
    filing_date: str
    period_end: str | None = None
    title: str
    source_url: str
    summary: str | None = None


class FinancialStatementMetric(BaseModel):
    symbol: str
    statement_type: str
    metric: str
    fiscal_period: str
    value: float
    unit: str
    source: str


class PaperPosition(BaseModel):
    id: int
    symbol: str
    entry_price: float
    current_price: float
    quantity: float
    position_size_pct: float
    unrealized_pnl_pct: float
    thesis: str
    invalidation_point: str
    catalyst_date: str
    risk_notes: str
    status: str = "OPEN"


class DecisionJournalEntry(BaseModel):
    id: int
    date: str
    symbol: str
    decision_type: str
    decision_text: str
    human_note: str


class RiskSummary(BaseModel):
    as_of: str
    source: str
    sector_exposure: list[dict]
    concentration: list[dict]
    metrics: list[dict]
    catalyst_warnings: list[str]
    rules_checklist: list[dict]


class ResearchReport(BaseModel):
    id: int
    symbol: str
    report_type: str
    title: str
    status: str
    generated_at: str
    confidence: str
