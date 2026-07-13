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

## ⚠ vibe-trading MCP server — standing risk note

`vibe-trading-ai` (pip) is installed and registered as an MCP server
(`.mcp.json`) for its research/backtesting tools (SEC filings, fundamentals,
news, options data, 54 tools total). **It also includes live order-execution
connectors** (Alpaca, Binance, OKX, Tiger, Futu) with a mandate-gated safety
model on its own side. No broker credentials are configured — the trading
tools are present but dormant.

This directly borders Terminal Alpha's own charter (paper-simulation only,
no real brokerage execution). Standing rule for anyone/anything working in
this repo, human or agent: **never configure broker credentials for this
server, never invoke its order-placement tools.** Use it for research/data/
backtesting reference only. See `.claude/agents/quant-coder.md` for how this
is enforced in the subagent's own system prompt.
