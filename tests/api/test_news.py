import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "apps" / "api"))

from app import prices


def _fake_yf(news_items):
    mod = types.ModuleType("yfinance")

    class FakeTicker:
        def __init__(self, sym):
            self.news = news_items
    mod.Ticker = FakeTicker
    return mod


def test_get_news_normalizes_both_shapes(monkeypatch):
    items = [
        {"content": {"title": "T1", "provider": {"displayName": "Prov"}, "pubDate": "2026-07-14"}},
        {"title": "T2", "publisher": "Pub", "providerPublishTime": 123},
        {"content": {"title": ""}},  # empty title dropped
    ]
    monkeypatch.setitem(sys.modules, "yfinance", _fake_yf(items))
    prices._news_cache.clear()
    out = prices.get_news("TEST1")
    assert out == [
        {"title": "T1", "publisher": "Prov", "published": "2026-07-14"},
        {"title": "T2", "publisher": "Pub", "published": 123},
    ]


def test_get_news_failure_returns_empty(monkeypatch):
    mod = types.ModuleType("yfinance")

    class Boom:
        def __init__(self, sym):
            raise RuntimeError("feed down")
    mod.Ticker = Boom
    monkeypatch.setitem(sys.modules, "yfinance", mod)
    prices._news_cache.clear()
    assert prices.get_news("TEST2") == []
