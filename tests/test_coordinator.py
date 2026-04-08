from unittest.mock import AsyncMock, patch

import pytest

from flows.coordinator import EngineResult, run
from schemas.outline import CommentaryOutline, OutlineSection
from schemas.research import ResearchBrief
from schemas.script import FinalScript

MOCK_BRIEF = ResearchBrief(key_facts=["fact1"], key_tensions=[], relevant_examples=[], caveats=[], source_notes=[])
MOCK_OUTLINE = CommentaryOutline(hook="hook", thesis="thesis", sections=[], emotional_progression="", closing_idea="end")
MOCK_SCRIPT = FinalScript(opening="open", body="body", closing="close")


@pytest.mark.asyncio
async def test_run_returns_engine_result():
    with (
        patch("flows.coordinator.run_research", new=AsyncMock(return_value=MOCK_BRIEF)),
        patch("flows.coordinator.run_outline", new=AsyncMock(return_value=MOCK_OUTLINE)),
        patch("flows.coordinator.run_script", new=AsyncMock(return_value=MOCK_SCRIPT)),
    ):
        result = await run(topic="Test topic")

    assert isinstance(result, EngineResult)
    assert result.brief is MOCK_BRIEF
    assert result.outline is MOCK_OUTLINE
    assert result.script is MOCK_SCRIPT


@pytest.mark.asyncio
async def test_run_passes_topic_and_optionals():
    research_mock = AsyncMock(return_value=MOCK_BRIEF)
    outline_mock = AsyncMock(return_value=MOCK_OUTLINE)
    script_mock = AsyncMock(return_value=MOCK_SCRIPT)

    with (
        patch("flows.coordinator.run_research", new=research_mock),
        patch("flows.coordinator.run_outline", new=outline_mock),
        patch("flows.coordinator.run_script", new=script_mock),
    ):
        await run(topic="T", angle="A", audience="AU", red_lines="R", must_hits="M")

    research_mock.assert_called_once_with(topic="T", angle="A", audience="AU", red_lines="R", must_hits="M")
    outline_mock.assert_called_once_with(topic="T", brief=MOCK_BRIEF, angle="A", audience="AU")
    script_mock.assert_called_once_with(topic="T", outline=MOCK_OUTLINE, angle="A", audience="AU")


@pytest.mark.asyncio
async def test_run_sequential_order():
    call_order = []

    async def mock_research(**_):
        call_order.append("research")
        return MOCK_BRIEF

    async def mock_outline(**_):
        call_order.append("outline")
        return MOCK_OUTLINE

    async def mock_script(**_):
        call_order.append("script")
        return MOCK_SCRIPT

    with (
        patch("flows.coordinator.run_research", new=mock_research),
        patch("flows.coordinator.run_outline", new=mock_outline),
        patch("flows.coordinator.run_script", new=mock_script),
    ):
        await run(topic="Test topic")

    assert call_order == ["research", "outline", "script"]
