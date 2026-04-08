import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from engine_agents.research import run_research
from schemas.research import ResearchBrief

MOCK_RESPONSE = {
    "key_facts": ["fact1", "fact2"],
    "key_tensions": ["tension1"],
    "relevant_examples": ["example1"],
    "caveats": ["caveat1"],
    "source_notes": ["source1"],
}


@pytest.fixture
def mock_runner_result():
    result = MagicMock()
    result.final_output = json.dumps(MOCK_RESPONSE)
    return result


@pytest.mark.asyncio
async def test_run_research_returns_brief(mock_runner_result):
    with patch("engine_agents.research.Runner.run", new=AsyncMock(return_value=mock_runner_result)):
        brief = await run_research(topic="Test topic")

    assert isinstance(brief, ResearchBrief)
    assert brief.key_facts == ["fact1", "fact2"]
    assert brief.key_tensions == ["tension1"]
    assert brief.relevant_examples == ["example1"]
    assert brief.caveats == ["caveat1"]
    assert brief.source_notes == ["source1"]


@pytest.mark.asyncio
async def test_run_research_with_optional_inputs(mock_runner_result):
    with patch("engine_agents.research.Runner.run", new=AsyncMock(return_value=mock_runner_result)) as mock_run:
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
async def test_run_research_empty_fields():
    empty_response = {k: [] for k in MOCK_RESPONSE}
    result = MagicMock()
    result.final_output = json.dumps(empty_response)

    with patch("engine_agents.research.Runner.run", new=AsyncMock(return_value=result)):
        brief = await run_research(topic="Empty topic")

    assert brief.key_facts == []
    assert brief.source_notes == []
