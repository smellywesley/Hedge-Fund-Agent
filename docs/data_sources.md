# Data Sources

**Active:** yfinance live quotes (`apps/api/app/prices.py`) — 5-minute TTL
cache, automatic mock fallback with explicit warnings, per-row `source` tags.
Research content (filings, news, fundamentals, agent output) is still
clearly-fake mock data (`source: "MOCK"`).

## Trust hierarchy (highest first)

1. SEC filings / official exchange filings
2. Company investor relations pages
3. Earnings call transcripts
4. Reputable financial data providers
5. News wires
6. Social/news sentiment
7. AI-generated summaries

## Planned connectors (Phase 3, in packages/mcp)

| Provider | Data | Link |
|---|---|---|
| OpenBB | Fundamentals, prices, estimates | https://docs.openbb.co/odp/python |
| SEC EDGAR | Filings, company facts, XBRL | https://www.sec.gov/search-filings/edgar-application-programming-interfaces |
| FRED | Macro/rates series | https://fred.stlouisfed.org/docs/api/fred/ |
| yfinance ✅ live | Quotes (done); OHLCV history + info later | https://github.com/ranaroussi/yfinance |
| FMP / Finnhub | Optional statements/news | https://site.financialmodelingprep.com/developer/docs |

## Connector contract

Every dataset returned must carry `source`, `timestamp`, freshness metadata,
and validation warnings. Missing/stale data is declared and downgrades
confidence — never silently filled. Responses are cached. Data is never
presented as guaranteed accurate.
