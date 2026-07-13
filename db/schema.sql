-- Terminal Alpha schema (applied in Phase 2 — nothing connects in Phase 1).
-- Paper/simulation portfolio only. No brokerage or execution tables by design.

CREATE TABLE tickers (
  id SERIAL PRIMARY KEY,
  symbol TEXT UNIQUE NOT NULL,
  company_name TEXT,
  exchange TEXT,
  sector TEXT,
  industry TEXT,
  country TEXT,
  currency TEXT,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE market_prices_daily (
  symbol TEXT NOT NULL,
  date DATE NOT NULL,
  open NUMERIC, high NUMERIC, low NUMERIC, close NUMERIC,
  adjusted_close NUMERIC,
  volume BIGINT,
  source TEXT,
  created_at TIMESTAMP DEFAULT now(),
  PRIMARY KEY (symbol, date, source)
);

CREATE TABLE financial_statements (
  id SERIAL PRIMARY KEY,
  symbol TEXT NOT NULL,
  fiscal_period TEXT,
  fiscal_year INT,
  statement_type TEXT,
  metric TEXT,
  value NUMERIC,
  unit TEXT,
  source TEXT,
  source_url TEXT,
  filing_date DATE,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE filings (
  id SERIAL PRIMARY KEY,
  symbol TEXT NOT NULL,
  form_type TEXT,
  filing_date DATE,
  period_end DATE,
  accession_number TEXT,
  source_url TEXT,
  raw_object_path TEXT,
  parsed_text_path TEXT,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE watchlist (
  id SERIAL PRIMARY KEY,
  symbol TEXT UNIQUE NOT NULL,
  next_action TEXT,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE research_scores (
  id SERIAL PRIMARY KEY,
  symbol TEXT NOT NULL,
  score_total NUMERIC,
  score_quality NUMERIC,
  score_growth NUMERIC,
  score_valuation NUMERIC,
  score_technical NUMERIC,
  score_catalyst NUMERIC,
  score_risk NUMERIC,
  confidence TEXT,
  missing_data JSONB,
  generated_at TIMESTAMP DEFAULT now()
);

CREATE TABLE agent_outputs (
  id SERIAL PRIMARY KEY,
  symbol TEXT,
  agent_name TEXT NOT NULL,
  task_name TEXT,
  output_markdown TEXT,
  claims JSONB,
  sources JSONB,
  confidence TEXT,
  warnings JSONB,
  generated_at TIMESTAMP DEFAULT now()
);

CREATE TABLE paper_positions (
  id SERIAL PRIMARY KEY,
  symbol TEXT NOT NULL,
  entry_price NUMERIC,
  current_price NUMERIC,
  quantity NUMERIC,
  position_size_pct NUMERIC,
  thesis TEXT,
  invalidation_point TEXT,
  catalyst_date DATE,
  risk_notes TEXT,
  status TEXT,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

CREATE TABLE decision_journal (
  id SERIAL PRIMARY KEY,
  symbol TEXT,
  decision_type TEXT,
  decision_text TEXT,
  agent_summary TEXT,
  human_note TEXT,
  sources JSONB,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE reports (
  id SERIAL PRIMARY KEY,
  symbol TEXT,
  report_type TEXT,
  title TEXT,
  status TEXT,
  object_path TEXT,
  confidence TEXT,
  generated_at TIMESTAMP DEFAULT now()
);

CREATE TABLE audit_logs (
  id SERIAL PRIMARY KEY,
  event_type TEXT NOT NULL,
  symbol TEXT,
  detail JSONB,
  created_at TIMESTAMP DEFAULT now()
);
