// Mirrors apps/api/app/schemas.py. Every AI/mock payload carries source,
// asOf timestamp, confidence, and missing-data warnings.

export type Confidence = "High" | "Medium" | "Low";

export interface Ticker {
  symbol: string;
  companyName: string;
  exchange: string;
  sector: string;
  industry: string;
}

export interface Quote {
  symbol: string;
  name: string;
  last: number;
  changePct: number;
}

export interface MarketSnapshot {
  asOf: string;
  source: string;
  indices: Quote[];
  rates: Quote[];
  fx: Quote[];
  commodities: Quote[];
  volatility: Quote[];
  sectors: { symbol: string; name: string; changePct: number }[];
  regime: { label: string; score: number; notes: string };
  aiBrief: AiCardData & { bullets: string[] };
}

export interface AiCardData {
  agent: string;
  asOf: string;
  confidence: Confidence;
  sources: string[];
  missingData: string[];
  warnings?: string[];
}

export interface WatchlistItem {
  symbol: string;
  company: string;
  price: number;
  changePct: number;
  volumeVsAvg: number;
  score: number;
  confidence: Confidence;
  catalyst: string;
  latestFiling: string;
  newsRisk: string;
  nextAction: string;
}

export interface ScreenerResult {
  symbol: string;
  company: string;
  reasonIncluded: string;
  reasonCareful: string;
  confidence: Confidence;
  nextAction: string;
}

export interface ResearchScore {
  scoreTotal: number;
  components: { name: string; weightPct: number; value: number }[];
  missingComponents: string[];
  confidence: Confidence;
}

export interface AgentOutput {
  agentName: string;
  task: string;
  summary: string;
  confidence: Confidence;
  sources: string[];
  missingData: string[];
  warnings: string[];
}

export interface Filing {
  formType: string;
  filingDate: string;
  title: string;
  summary: string;
  sourceUrl: string;
}

export interface FinancialStatementMetric {
  statementType: string;
  metric: string;
  fiscalPeriod: string;
  value: string;
}

export interface PaperPosition {
  id: number;
  symbol: string;
  entryPrice: number;
  currentPrice: number;
  quantity: number;
  positionSizePct: number;
  unrealizedPnlPct: number;
  thesis: string;
  invalidationPoint: string;
  catalystDate: string;
  riskNotes: string;
}

export interface DecisionJournalEntry {
  id: number;
  date: string;
  symbol: string;
  decisionType: string;
  decisionText: string;
  humanNote: string;
}

export interface RiskSummary {
  asOf: string;
  source: string;
  sectorExposure: { sector: string; pct: number; limit: number; status: string }[];
  concentration: { symbol: string; pct: number; limit: number; status: string }[];
  metrics: { name: string; value: string; note: string }[];
  catalystWarnings: string[];
  rulesChecklist: { rule: string; status: string }[];
}

export interface ResearchReport {
  id: number;
  symbol: string;
  reportType: string;
  title: string;
  status: string;
  generatedAt: string;
  confidence: Confidence;
}
