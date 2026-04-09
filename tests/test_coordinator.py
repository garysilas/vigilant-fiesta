from unittest.mock import AsyncMock, patch

import pytest

from flows.coordinator import EngineResult, run
from schemas.outline import CommentaryOutline, OutlineSection
from schemas.research import ResearchBrief
from schemas.script import Clip, FinalScript, NarrationScript

MOCK_BRIEF = ResearchBrief(key_facts=["fact1"], key_tensions=[], relevant_examples=[], caveats=[], source_notes=[])
MOCK_OUTLINE = CommentaryOutline(hook="hook", thesis="thesis", sections=[], emotional_progression="", closing_idea="end")
MOCK_SCRIPT = FinalScript(opening="open", body="body", closing="close")
MOCK_NARRATION = NarrationScript(text="Narration ready script with pauses")
MOCK_CLIPS = [Clip(hook="H1", body="B1", closing="C1"), Clip(hook="H2", body="B2", closing="C2")]


@pytest.mark.asyncio
async def test_run_returns_engine_result():
    with (
        patch("flows.coordinator.run_research", new=AsyncMock(return_value=MOCK_BRIEF)),
        patch("flows.coordinator.run_outline", new=AsyncMock(return_value=MOCK_OUTLINE)),
        patch("flows.coordinator.run_script", new=AsyncMock(return_value=MOCK_SCRIPT)),
        patch("flows.coordinator.run_voice", new=AsyncMock(return_value=MOCK_NARRATION)),
        patch("flows.coordinator.run_clips", new=AsyncMock(return_value=MOCK_CLIPS)),
    ):
        result = await run(topic="Test topic")

    assert isinstance(result, EngineResult)
    assert result.brief is MOCK_BRIEF
    assert result.outline is MOCK_OUTLINE
    assert result.script is MOCK_SCRIPT
    assert result.narration is MOCK_NARRATION
    assert result.clips is MOCK_CLIPS


@pytest.mark.asyncio
async def test_run_passes_topic_and_optionals():
    research_mock = AsyncMock(return_value=MOCK_BRIEF)
    outline_mock = AsyncMock(return_value=MOCK_OUTLINE)
    script_mock = AsyncMock(return_value=MOCK_SCRIPT)
    voice_mock = AsyncMock(return_value=MOCK_NARRATION)
    clips_mock = AsyncMock(return_value=MOCK_CLIPS)

    with (
        patch("flows.coordinator.run_research", new=research_mock),
        patch("flows.coordinator.run_outline", new=outline_mock),
        patch("flows.coordinator.run_script", new=script_mock),
        patch("flows.coordinator.run_voice", new=voice_mock),
        patch("flows.coordinator.run_clips", new=clips_mock),
    ):
        await run(topic="T", angle="A", audience="AU", red_lines="R", must_hits="M")

    research_mock.assert_called_once_with(topic="T", angle="A", audience="AU", red_lines="R", must_hits="M", tone=None, style=None)
    outline_mock.assert_called_once_with(topic="T", brief=MOCK_BRIEF, angle="A", audience="AU", tone=None, style=None)
    script_mock.assert_called_once_with(topic="T", outline=MOCK_OUTLINE, angle="A", audience="AU", tone=None, style=None)
    voice_mock.assert_called_once_with(script=MOCK_SCRIPT, tone=None, style=None)
    clips_mock.assert_called_once_with(script=MOCK_SCRIPT)


@pytest.mark.asyncio
async def test_run_forwards_tone_and_style():
    research_mock = AsyncMock(return_value=MOCK_BRIEF)
    outline_mock = AsyncMock(return_value=MOCK_OUTLINE)
    script_mock = AsyncMock(return_value=MOCK_SCRIPT)
    voice_mock = AsyncMock(return_value=MOCK_NARRATION)
    clips_mock = AsyncMock(return_value=MOCK_CLIPS)

    with (
        patch("flows.coordinator.run_research", new=research_mock),
        patch("flows.coordinator.run_outline", new=outline_mock),
        patch("flows.coordinator.run_script", new=script_mock),
        patch("flows.coordinator.run_voice", new=voice_mock),
        patch("flows.coordinator.run_clips", new=clips_mock),
    ):
        await run(topic="T", tone="serious", style="documentary")

    assert research_mock.call_args.kwargs["tone"] == "serious"
    assert research_mock.call_args.kwargs["style"] == "documentary"
    assert outline_mock.call_args.kwargs["tone"] == "serious"
    assert outline_mock.call_args.kwargs["style"] == "documentary"
    assert script_mock.call_args.kwargs["tone"] == "serious"
    assert script_mock.call_args.kwargs["style"] == "documentary"
    assert voice_mock.call_args.kwargs["tone"] == "serious"
    assert voice_mock.call_args.kwargs["style"] == "documentary"


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

    async def mock_voice(**_):
        call_order.append("voice")
        return MOCK_NARRATION

    async def mock_clips(**_):
        call_order.append("clips")
        return MOCK_CLIPS

    with (
        patch("flows.coordinator.run_research", new=mock_research),
        patch("flows.coordinator.run_outline", new=mock_outline),
        patch("flows.coordinator.run_script", new=mock_script),
        patch("flows.coordinator.run_voice", new=mock_voice),
        patch("flows.coordinator.run_clips", new=mock_clips),
    ):
        await run(topic="Test topic")

    assert call_order == ["research", "outline", "script", "voice", "clips"]
