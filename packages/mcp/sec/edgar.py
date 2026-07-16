"""SEC EDGAR filings connector — keyless, real primary-source filing metadata.

Uses two public, no-API-key endpoints:
  - https://www.sec.gov/files/company_tickers.json   (ticker -> CIK)
  - https://data.sec.gov/submissions/CIK##########.json  (recent filings)

SEC requires a descriptive User-Agent on every request. Connector contract
(docs/data_sources.md): every row carries source + a real sec.gov URL + a
fetch timestamp; any failure returns [] and the caller warns — nothing faked.

All HTTP goes through _get_json so tests run fully offline against fixtures.
"""
from datetime import datetime, timezone

USER_AGENT = "Terminal Alpha educational research (contact: research@example.com)"
_ticker_cache: dict[str, str] = {}          # TICKER -> zero-padded CIK
_submissions_cache: dict[str, dict] = {}    # CIK -> submissions json
_facts_cache: dict[str, dict] = {}          # CIK -> companyfacts json

# us-gaap concept name candidates per metric (first present wins).
_CONCEPTS = {
    "revenue": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet"],
    "gross_profit": ["GrossProfit"],
    "operating_income": ["OperatingIncomeLoss"],
    "net_income": ["NetIncomeLoss"],
    "assets": ["Assets"],
    "equity": ["StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"],
    "cash": ["CashAndCashEquivalentsAtCarryingValue", "CashAndCashEquivalentsAtCarryingValueIncludingDiscontinuedOperations"],
    "long_term_debt": ["LongTermDebtNoncurrent", "LongTermDebt", "LongTermDebtAndCapitalLeaseObligations"],
}


def _get_json(url: str) -> dict:
    """Single choke point for network I/O — monkeypatched in tests."""
    import requests

    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
    resp.raise_for_status()
    return resp.json()


def _load_cik_map() -> dict[str, str]:
    if _ticker_cache:
        return _ticker_cache
    data = _get_json("https://www.sec.gov/files/company_tickers.json")
    # company_tickers.json is keyed by arbitrary index -> {cik_str, ticker, title}
    for row in data.values():
        _ticker_cache[str(row["ticker"]).upper()] = str(row["cik_str"]).zfill(10)
    return _ticker_cache


def get_cik(symbol: str) -> str | None:
    return _load_cik_map().get(symbol.strip().upper())


def _latest_annual(concept: dict):
    """Latest annual (FY, 10-K/20-F) USD value for one XBRL concept."""
    units = concept.get("units", {})
    usd = units.get("USD") or next(iter(units.values()), [])
    annual = [x for x in usd if x.get("fp") == "FY" and x.get("form") in ("10-K", "20-F")]
    pool = annual or usd
    if not pool:
        return None
    latest = max(pool, key=lambda x: x.get("end", ""))
    return latest.get("val"), latest.get("fy"), latest.get("end")


def get_company_facts(symbol: str) -> dict:
    """Latest-annual fundamentals from SEC XBRL company facts (keyless).
    Returns {revenue, gross_profit, operating_income, net_income, assets,
    equity, cash, long_term_debt, fiscal_year, source, asOf} — or {} on failure."""
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        cik = get_cik(symbol)
        if not cik:
            return {}
        if cik not in _facts_cache:
            _facts_cache[cik] = _get_json(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json")
        gaap = _facts_cache[cik].get("facts", {}).get("us-gaap", {})
        out: dict = {}
        for metric, names in _CONCEPTS.items():
            for name in names:
                if name in gaap:
                    v = _latest_annual(gaap[name])
                    if v and v[0] is not None:
                        out[metric] = v[0]
                        out.setdefault("fiscal_year", v[1])
                        break
        if not out:
            return {}
        dei = _facts_cache[cik].get("facts", {}).get("dei", {})
        if "EntityCommonStockSharesOutstanding" in dei:
            sv = _latest_annual(dei["EntityCommonStockSharesOutstanding"])
            if sv and sv[0]:
                out["shares"] = sv[0]
        out["source"] = "SEC EDGAR XBRL"
        out["asOf"] = now
        return out
    except Exception:
        return {}


def get_recent_filings(symbol, forms=("10-K", "10-Q", "8-K"), limit=10) -> list[dict]:
    """Recent filings for `symbol`, newest first. Returns [] on any failure
    (unknown ticker, network error) — the caller surfaces a warning."""
    forms = set(forms)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        cik = get_cik(symbol)
        if not cik:
            return []
        if cik not in _submissions_cache:
            _submissions_cache[cik] = _get_json(f"https://data.sec.gov/submissions/CIK{cik}.json")
        recent = _submissions_cache[cik].get("filings", {}).get("recent", {})
        forms_list = recent.get("form", [])
        dates = recent.get("filingDate", [])
        accns = recent.get("accessionNumber", [])
        docs = recent.get("primaryDocument", [])
        cik_int = int(cik)  # URL path uses the un-padded CIK
        out = []
        for i, form in enumerate(forms_list):
            if form not in forms:
                continue
            accn = accns[i] if i < len(accns) else ""
            accn_nodash = accn.replace("-", "")
            doc = docs[i] if i < len(docs) else ""
            url = (f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{accn_nodash}/{doc}"
                   if accn_nodash and doc else f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}")
            out.append({
                "formType": form,
                "filingDate": dates[i] if i < len(dates) else "",
                "accessionNumber": accn,
                "primaryDocUrl": url,
                "title": f"{symbol.upper()} {form}",
                "source": "SEC EDGAR",
                "asOf": now,
            })
            if len(out) >= limit:
                break
        return out
    except Exception:
        return []
