import pytest

from tools import create_fit_card, search_listings, suggest_outfit
from utils.data_loader import get_empty_wardrobe, get_example_wardrobe


class _FakeResponse:
    def __init__(self, content: str):
        self.choices = [type("Choice", (), {"message": type("Message", (), {"content": content})()})()]


class _FakeCompletions:
    def __init__(self, content: str):
        self._content = content

    def create(self, **kwargs):
        return _FakeResponse(self._content)


class _FakeChat:
    def __init__(self, content: str):
        self.completions = _FakeCompletions(content)


class _FakeClient:
    def __init__(self, content: str):
        self.chat = _FakeChat(content)


def test_search_returns_results():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    assert isinstance(results, list)
    assert len(results) > 0


def test_search_empty_results():
    results = search_listings("designer ballgown", size="XXS", max_price=5)
    assert results == []


def test_search_price_filter():
    results = search_listings("jacket", size=None, max_price=10)
    assert all(item["price"] <= 10 for item in results)


def test_suggest_outfit_empty_wardrobe(monkeypatch):
    monkeypatch.setattr("tools._get_groq_client", lambda: _FakeClient("Try pairing it with high-waisted denim and chunky shoes."))
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    suggestion = suggest_outfit(results[0], get_empty_wardrobe())
    assert isinstance(suggestion, str)
    assert suggestion.strip()


def test_create_fit_card_empty_outfit():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    caption = create_fit_card("", results[0])
    assert "incomplete" in caption.lower()


def test_create_fit_card_uses_llm_output(monkeypatch):
    monkeypatch.setattr("tools._get_groq_client", lambda: _FakeClient("grabbed this tee off depop and it hits different 🖤"))
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    caption = create_fit_card("Pair it with baggy jeans.", results[0])
    assert "depop" in caption.lower() or "grabbed" in caption.lower()