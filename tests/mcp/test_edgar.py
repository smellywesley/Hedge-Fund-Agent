import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from packages.mcp.sec import edgar

# Trimmed, realistic fixtures mirroring the real SEC JSON shapes.
_TICKERS = {
    "0": {"cik_str": 1045810, "ticker": "NVDA", "title": "NVIDIA CORP"},
    "1": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."},
}
_SUBMISSIONS = {
    "filings": {
        "recent": {
            "form": ["10-Q", "8-K", "4", "10-K", "8-K"],
            "filingDate": ["2026-05-28", "2026-05-28", "2026-05-10", "2026-03-01", "2026-02-15"],
            "accessionNumber": ["0001045810-26-000101", "0001045810-26-000100",
                                 "0001045810-26-000099", "0001045810-26-000050",
                                 "0001045810-26-000040"],
            "primaryDocument": ["nvda-10q.htm", "nvda-8k.htm", "form4.xml",
                                "nvda-10k.htm", "nvda-8k2.htm"],
        }
    }
}


def _fake_get_json(url):
    if "company_tickers" in url:
        return _TICKERS
    if "submissions" in url:
        return _SUBMISSIONS
    raise AssertionError(f"unexpected url {url}")


def _reset_caches(monkeypatch):
    monkeypatch.setattr(edgar, "_get_json", _fake_get_json)
    edgar._ticker_cache.clear()
    edgar._submissions_cache.clear()


def test_cik_lookup_zero_padded(monkeypatch):
    _reset_caches(monkeypatch)
    assert edgar.get_cik("nvda") == "0001045810"
    assert edgar.get_cik("AAPL") == "0000320193"


def test_recent_filings_filters_forms_and_builds_real_url(monkeypatch):
    _reset_caches(monkeypatch)
    rows = edgar.get_recent_filings("NVDA")
    # The Form 4 must be filtered out (default forms = 10-K/10-Q/8-K).
    assert [r["formType"] for r in rows] == ["10-Q", "8-K", "10-K", "8-K"]
    q = rows[0]
    assert q["source"] == "SEC EDGAR"
    # Real archive URL: unpadded CIK + accession-without-dashes + primary doc.
    assert q["primaryDocUrl"] == "https://www.sec.gov/Archives/edgar/data/1045810/000104581026000101/nvda-10q.htm"
    assert q["accessionNumber"] == "0001045810-26-000101"


def test_limit_is_honored(monkeypatch):
    _reset_caches(monkeypatch)
    rows = edgar.get_recent_filings("NVDA", limit=2)
    assert len(rows) == 2


def test_form_filter_can_select_only_10k(monkeypatch):
    _reset_caches(monkeypatch)
    rows = edgar.get_recent_filings("NVDA", forms=("10-K",))
    assert all(r["formType"] == "10-K" for r in rows)
    assert len(rows) == 1


def test_unknown_ticker_returns_empty(monkeypatch):
    _reset_caches(monkeypatch)
    assert edgar.get_recent_filings("ZZZZ") == []


def test_network_failure_returns_empty(monkeypatch):
    def boom(url):
        raise RuntimeError("network down")
    monkeypatch.setattr(edgar, "_get_json", boom)
    edgar._ticker_cache.clear()
    edgar._submissions_cache.clear()
    assert edgar.get_recent_filings("NVDA") == []
