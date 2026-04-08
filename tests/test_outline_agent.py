import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from engine_agents.outline import run_outline
from schemas.outline import CommentaryOutline, OutlineSection
from schemas.research import ResearchBrief

MOCK_BRIEF = ResearchBrief(
    key_facts=["fact1"],
    key_tensions=["tension1"],
    relevant_examples=["example1"],
    caveats=["caveat1"],
    source_notes=["source1"],
)

MOCK_RESPONSE = {
    "hook": "Did you know...",
    "thesis": "Young men face structural disadvantages.",
    "sections": [
        {"title": "Act 1", "argument": "Setup the problem"},
        {"title": "Act 2", "argument": "Evidence"},
    ],
    "emotional_progression": "curiosity → tension → resolution",
    "closing_idea": "Systemic change is needed.",
}


@pytest.fixture
def mock_runner_result():
    result = MagicMock()
    result.final_output = json.dumps(MOCK_RESPONSE)
    return result


@pytest.mark.asyncio
async def test_run_outline_returns_outline(mock_runner_result):
    with patch("engine_agents.outline.Runner.run", new=AsyncMock(return_value=mock_runner_result)):
        outline = await run_outline(topic="Test topic", brief=MOCK_BRIEF)

    assert isinstance(outline, CommentaryOutline)
    assert outline.hook == "Did you know..."
    assert outline.thesis == "Young men face structural disadvantages."
    assert len(outline.sections) == 2
    assert isinstance(outline.sections[0], OutlineSection)
    assert outline.sections[0].title == "Act 1"
    assert outline.sections[1].argument == "Evidence"
    assert outline.emotional_progression == "curiosity → tension → resolution"
    assert outline.closing_idea == "Systemic change is needed."


@pytest.mark.asyncio
async def test_run_outline_prompt_includes_brief(mock_runner_result):
    with patch("engine_agents.outline.Runner.run", new=AsyncMock(return_value=mock_runner_result)) as mock_run:
        await run_outline(topic="Test topic", brief=MOCK_BRIEF, angle="economic", audience="young men")
        prompt = mock_run.call_args[0][1]
        assert "fact1" in prompt
        assert "tension1" in prompt
        assert "economic" in prompt
        assert "young men" in prompt


@pytest.mark.asyncio
async def test_run_outline_empty_sections():
    empty_response = {**MOCK_RESPONSE, "sections": []}
    result = MagicMock()
    result.final_output = json.dumps(empty_response)

    with patch("engine_agents.outline.Runner.run", new=AsyncMock(return_value=result)):
        outline = await run_outline(topic="Test topic", brief=MOCK_BRIEF)

    assert outline.sections == []
