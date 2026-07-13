# MCP Connector Layer

Future home of MCP servers / provider connectors (Phase 3). Nothing here is
wired in Phase 1 — the API serves mock data.

| Folder | Provider | Purpose |
|---|---|---|
| `openbb/` | OpenBB Platform | Fundamentals, market data (https://docs.openbb.co/odp/python) |
| `sec/` | SEC EDGAR | Filings metadata, company facts, XBRL |
| `fred/` | FRED | Macro/rates series |
| `custom_tools/` | Internal | yfinance fallback, scoring tools exposed via MCP |

Connector contract (every provider must):
1. Attach `source`, `timestamp`, and freshness metadata to every dataset.
2. Validate and warn on missing/stale data — never silently fill gaps.
3. Cache responses.
4. Never present data as guaranteed accurate.
