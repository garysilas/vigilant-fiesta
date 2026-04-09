from unittest.mock import MagicMock, patch

import pytest

from tools.web_search import SearchResult, web_search


MOCK_RESPONSE = {
    "results": [
        {"title": "Title A", "url": "https://example.com/a", "content": "Snippet A"},
        {"title": "Title B", "url": "https://example.com/b", "content": "Snippet B"},
    ]
}


@patch("tools.web_search.TavilyClient")
def test_web_search_returns_list_of_search_results(mock_client_class, monkeypatch):
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    mock_client = MagicMock()
    mock_client.search.return_value = MOCK_RESPONSE
    mock_client_class.return_value = mock_client

    results = web_search("test query")

    assert isinstance(results, list)
    assert all(isinstance(r, SearchResult) for r in results)


@patch("tools.web_search.TavilyClient")
def test_web_search_maps_fields_correctly(mock_client_class, monkeypatch):
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    mock_client = MagicMock()
    mock_client.search.return_value = MOCK_RESPONSE
    mock_client_class.return_value = mock_client

    results = web_search("test query")

    assert results[0].title == "Title A"
    assert results[0].url == "https://example.com/a"
    assert results[0].snippet == "Snippet A"
    assert results[1].title == "Title B"


@patch("tools.web_search.TavilyClient")
def test_web_search_returns_empty_list_when_no_results(mock_client_class, monkeypatch):
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    mock_client = MagicMock()
    mock_client.search.return_value = {"results": []}
    mock_client_class.return_value = mock_client

    results = web_search("obscure query")

    assert results == []


def test_web_search_raises_if_api_key_missing(monkeypatch):
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)

    with pytest.raises(EnvironmentError, match="TAVILY_API_KEY"):
        web_search("any query")
