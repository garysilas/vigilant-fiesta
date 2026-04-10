"""
Tests for the evaluator → rewrite flow integrated into the coordinator.
"""
from unittest.mock import AsyncMock, patch

import pytest

from flows.coordinator import EngineResult, run
from schemas.outline import CommentaryOutline
from schemas.research import ResearchBrief
from schemas.script import Clip, FinalScript, NarrationScript, ScriptFeedback

MOCK_BRIEF = ResearchBrief(key_facts=["fact1"])
MOCK_OUTLINE = CommentaryOutline(hook="hook", thesis="thesis")
MOCK_INITIAL_SCRIPT = FinalScript(opening="draft open", body="draft body", closing="draft close")
MOCK_FEEDBACK = ScriptFeedback(
    weaknesses=["weak opener"],
    missing_angles=["global context"],
    improvement_suggestions=["add statistic"],
)
MOCK_REWRITTEN_SCRIPT = FinalScript(opening="improved open", body="improved body", closing="improved close")
MOCK_NARRATION = NarrationScript(text="narration text")
MOCK_CLIPS = [Clip(hook="H", body="B", closing="C")]


@pytest.mark.asyncio
async def test_rewrite_flow_returns_rewritten_script():
    with (
        patch("flows.coordinator.run_research", new=AsyncMock(return_value=MOCK_BRIEF)),
        patch("flows.coordinator.run_outline", new=AsyncMock(return_value=MOCK_OUTLINE)),
        patch("flows.coordinator.run_script", new=AsyncMock(side_effect=[MOCK_INITIAL_SCRIPT, MOCK_REWRITTEN_SCRIPT])),
        patch("flows.coordinator.run_evaluator", new=AsyncMock(return_value=MOCK_FEEDBACK)),
        patch("flows.coordinator.run_voice", new=AsyncMock(return_value=MOCK_NARRATION)),
        patch("flows.coordinator.run_clips", new=AsyncMock(return_value=MOCK_CLIPS)),
    ):
        result = await run(topic="Test")

    assert result.script is MOCK_REWRITTEN_SCRIPT
    assert result.script.opening == "improved open"


@pytest.mark.asyncio
async def test_rewrite_flow_includes_feedback_in_result():
    with (
        patch("flows.coordinator.run_research", new=AsyncMock(return_value=MOCK_BRIEF)),
        patch("flows.coordinator.run_outline", new=AsyncMock(return_value=MOCK_OUTLINE)),
        patch("flows.coordinator.run_script", new=AsyncMock(side_effect=[MOCK_INITIAL_SCRIPT, MOCK_REWRITTEN_SCRIPT])),
        patch("flows.coordinator.run_evaluator", new=AsyncMock(return_value=MOCK_FEEDBACK)),
        patch("flows.coordinator.run_voice", new=AsyncMock(return_value=MOCK_NARRATION)),
        patch("flows.coordinator.run_clips", new=AsyncMock(return_value=MOCK_CLIPS)),
    ):
        result = await run(topic="Test")

    assert result.feedback is MOCK_FEEDBACK
    assert result.feedback.weaknesses == ["weak opener"]
    assert result.feedback.missing_angles == ["global context"]
    assert result.feedback.improvement_suggestions == ["add statistic"]


@pytest.mark.asyncio
async def test_rewrite_flow_evaluator_receives_initial_script():
    evaluator_mock = AsyncMock(return_value=MOCK_FEEDBACK)
    with (
        patch("flows.coordinator.run_research", new=AsyncMock(return_value=MOCK_BRIEF)),
        patch("flows.coordinator.run_outline", new=AsyncMock(return_value=MOCK_OUTLINE)),
        patch("flows.coordinator.run_script", new=AsyncMock(side_effect=[MOCK_INITIAL_SCRIPT, MOCK_REWRITTEN_SCRIPT])),
        patch("flows.coordinator.run_evaluator", new=evaluator_mock),
        patch("flows.coordinator.run_voice", new=AsyncMock(return_value=MOCK_NARRATION)),
        patch("flows.coordinator.run_clips", new=AsyncMock(return_value=MOCK_CLIPS)),
    ):
        await run(topic="Test")

    evaluator_mock.assert_called_once_with(script=MOCK_INITIAL_SCRIPT)


@pytest.mark.asyncio
async def test_rewrite_flow_script_called_twice():
    script_mock = AsyncMock(side_effect=[MOCK_INITIAL_SCRIPT, MOCK_REWRITTEN_SCRIPT])
    with (
        patch("flows.coordinator.run_research", new=AsyncMock(return_value=MOCK_BRIEF)),
        patch("flows.coordinator.run_outline", new=AsyncMock(return_value=MOCK_OUTLINE)),
        patch("flows.coordinator.run_script", new=script_mock),
        patch("flows.coordinator.run_evaluator", new=AsyncMock(return_value=MOCK_FEEDBACK)),
        patch("flows.coordinator.run_voice", new=AsyncMock(return_value=MOCK_NARRATION)),
        patch("flows.coordinator.run_clips", new=AsyncMock(return_value=MOCK_CLIPS)),
    ):
        await run(topic="Test")

    assert script_mock.call_count == 2
    first_call = script_mock.call_args_list[0]
    second_call = script_mock.call_args_list[1]
    assert "feedback" not in first_call.kwargs or first_call.kwargs.get("feedback") is None
    assert second_call.kwargs["feedback"] is MOCK_FEEDBACK


@pytest.mark.asyncio
async def test_rewrite_flow_voice_and_clips_use_rewritten():
    voice_mock = AsyncMock(return_value=MOCK_NARRATION)
    clips_mock = AsyncMock(return_value=MOCK_CLIPS)
    with (
        patch("flows.coordinator.run_research", new=AsyncMock(return_value=MOCK_BRIEF)),
        patch("flows.coordinator.run_outline", new=AsyncMock(return_value=MOCK_OUTLINE)),
        patch("flows.coordinator.run_script", new=AsyncMock(side_effect=[MOCK_INITIAL_SCRIPT, MOCK_REWRITTEN_SCRIPT])),
        patch("flows.coordinator.run_evaluator", new=AsyncMock(return_value=MOCK_FEEDBACK)),
        patch("flows.coordinator.run_voice", new=voice_mock),
        patch("flows.coordinator.run_clips", new=clips_mock),
    ):
        await run(topic="Test")

    voice_mock.assert_called_once_with(script=MOCK_REWRITTEN_SCRIPT, tone=None, style=None)
    clips_mock.assert_called_once_with(script=MOCK_REWRITTEN_SCRIPT)
