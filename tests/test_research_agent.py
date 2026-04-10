import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from engine_agents.research import run_research
from schemas.research import ResearchBrief, Source
from tools.web_search import SearchResult

MOCK_SEARCH_RESULTS = [
    SearchResult(title="Article A", url="https://example.com/a", snippet="Snippet A"),
]

MOCK_RESPONSE = {
    "key_facts": ["fact1", "fact2"],
    "key_tensions": ["tension1"],
    "relevant_examples": ["example1"],
    "caveats": ["caveat1"],
    "source_notes": ["source1"],
    "sources": [{"title": "Article A", "url": "https://example.com/a", "summary": "Snippet A", "credibility_score": 0.85, "recency": "2024", "bias_flag": "none"}],
}


@pytest.fixture
def mock_runner_result():
    result = MagicMock()
    result.final_output = json.dumps(MOCK_RESPONSE)
    return result


@pytest.mark.asyncio
async def test_run_research_returns_brief(mock_runner_result):
    with patch("engine_agents.research.web_search", return_value=MOCK_SEARCH_RESULTS), \
         patch("engine_agents.research.Runner.run", new=AsyncMock(return_value=mock_runner_result)):
        brief = await run_research(topic="Test topic")

    assert isinstance(brief, ResearchBrief)
    assert brief.key_facts == ["fact1", "fact2"]
    assert brief.key_tensions == ["tension1"]
    assert brief.relevant_examples == ["example1"]
    assert brief.caveats == ["caveat1"]
    assert brief.source_notes == ["source1"]


@pytest.mark.asyncio
async def test_run_research_populates_sources(mock_runner_result):
    with patch("engine_agents.research.web_search", return_value=MOCK_SEARCH_RESULTS), \
         patch("engine_agents.research.Runner.run", new=AsyncMock(return_value=mock_runner_result)):
        brief = await run_research(topic="Test topic")

    assert len(brief.sources) == 1
    assert isinstance(brief.sources[0], Source)
    assert brief.sources[0].title == "Article A"
    assert brief.sources[0].url == "https://example.com/a"
    assert brief.sources[0].summary == "Snippet A"
    assert brief.sources[0].credibility_score == 0.85
    assert brief.sources[0].recency == "2024"
    assert brief.sources[0].bias_flag == "none"


@pytest.mark.asyncio
async def test_run_research_calls_web_search(mock_runner_result):
    with patch("engine_agents.research.web_search", return_value=MOCK_SEARCH_RESULTS) as mock_ws, \
         patch("engine_agents.research.Runner.run", new=AsyncMock(return_value=mock_runner_result)):
        await run_research(topic="Test topic")

    mock_ws.assert_called_once_with("Test topic")


@pytest.mark.asyncio
async def test_run_research_with_optional_inputs(mock_runner_result):
    with patch("engine_agents.research.web_search", return_value=MOCK_SEARCH_RESULTS), \
         patch("engine_agents.research.Runner.run", new=AsyncMock(return_value=mock_runner_result)) as mock_run:
        await run_research(
            topic="Test topic",
            angle="economic angle",
            audience="young men",
            red_lines="no politics",
            must_hits="mention wage gap",
        )
        call_args = mock_run.call_args
        prompt = call_args[0][1]
        assert "economic angle" in prompt
        assert "young men" in prompt
        assert "no politics" in prompt
        assert "mention wage gap" in prompt


@pytest.mark.asyncio
async def test_run_research_prompt_includes_tone_and_style(mock_runner_result):
    with patch("engine_agents.research.web_search", return_value=MOCK_SEARCH_RESULTS), \
         patch("engine_agents.research.Runner.run", new=AsyncMock(return_value=mock_runner_result)) as mock_run:
        await run_research(topic="Test topic", tone="serious", style="documentary")
        prompt = mock_run.call_args[0][1]
        assert "serious" in prompt
        assert "documentary" in prompt


@pytest.mark.asyncio
async def test_run_research_empty_fields():
    empty_response = {k: [] for k in MOCK_RESPONSE}
    result = MagicMock()
    result.final_output = json.dumps(empty_response)

    with patch("engine_agents.research.web_search", return_value=[]), \
         patch("engine_agents.research.Runner.run", new=AsyncMock(return_value=result)):
        brief = await run_research(topic="Empty topic")

    assert brief.key_facts == []
    assert brief.source_notes == []
    assert brief.sources == []


@pytest.mark.asyncio
async def test_run_research_source_scoring_defaults():
    response_no_scoring = {
        "key_facts": [],
        "key_tensions": [],
        "relevant_examples": [],
        "caveats": [],
        "source_notes": [],
        "sources": [{"title": "X", "url": "https://x.com", "summary": "s"}],
    }
    result = MagicMock()
    result.final_output = json.dumps(response_no_scoring)

    with patch("engine_agents.research.web_search", return_value=[]), \
         patch("engine_agents.research.Runner.run", new=AsyncMock(return_value=result)):
        brief = await run_research(topic="Test")

    assert len(brief.sources) == 1
    assert brief.sources[0].credibility_score == 0.0
    assert brief.sources[0].recency == ""
    assert brief.sources[0].bias_flag == ""
