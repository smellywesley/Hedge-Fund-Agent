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
