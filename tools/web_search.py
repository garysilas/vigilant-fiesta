import os
from dataclasses import dataclass

from tavily import TavilyClient

from tools.logger import log


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str


def web_search(query: str) -> list[SearchResult]:
    log("web_search", "query", query=query)

    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise EnvironmentError("TAVILY_API_KEY is not set")

    client = TavilyClient(api_key=api_key)
    response = client.search(query)

    results = []
    for item in response.get("results", []):
        results.append(SearchResult(
            title=item.get("title", ""),
            url=item.get("url", ""),
            snippet=item.get("content", ""),
        ))

    return results
