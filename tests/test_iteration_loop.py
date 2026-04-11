"""Tests for iteration loop in coordinator"""

from unittest.mock import AsyncMock, patch

import pytest

from flows.coordinator import run
from schemas.outline import CommentaryOutline
from schemas.research import ResearchBrief
from schemas.script import Clip, FinalScript, NarrationScript, ScriptFeedback, ScriptScore

MOCK_BRIEF = ResearchBrief(key_facts=["fact1"], key_tensions=[], relevant_examples=[], caveats=[], source_notes=[])
MOCK_OUTLINE = CommentaryOutline(hook="hook", thesis="thesis", sections=[], emotional_progression="", closing_idea="end")
MOCK_SCRIPT = FinalScript(opening="open", body="body", closing="close")
MOCK_SCRIPT_V2 = FinalScript(opening="improved open", body="improved body", closing="improved close")
MOCK_SCRIPT_V3 = FinalScript(opening="best open", body="best body", closing="best close")
MOCK_NARRATION = NarrationScript(text="Narration ready")
MOCK_CLIPS = [Clip(hook="H1", body="B1", closing="C1")]


def make_mock_score(overall: float) -> ScriptScore:
    """Helper to create a ScriptScore with given overall score."""
    return ScriptScore(
        clarity_score=overall,
        argument_score=overall,
        emotional_impact=overall,
        factual_grounding=overall,
        overall_score=overall,
    )


@pytest.mark.asyncio
async def test_iteration_loop_single_iteration():
    """Test that max_iterations=1 runs evaluator once."""
    feedback = ScriptFeedback(weaknesses=["weak"], missing_angles=[], improvement_suggestions=[])
    score = make_mock_score(7.0)

    with (
        patch("flows.coordinator.run_research", new=AsyncMock(return_value=MOCK_BRIEF)),
        patch("flows.coordinator.run_outline", new=AsyncMock(return_value=MOCK_OUTLINE)),
        patch("flows.coordinator.run_script", new=AsyncMock(return_value=MOCK_SCRIPT)),
        patch("flows.coordinator.run_evaluator", new=AsyncMock(return_value=(feedback, score))) as mock_eval,
        patch("flows.coordinator.run_voice", new=AsyncMock(return_value=MOCK_NARRATION)),
        patch("flows.coordinator.run_clips", new=AsyncMock(return_value=MOCK_CLIPS)),
    ):
        result = await run(topic="Test", max_iterations=1)

    assert mock_eval.call_count == 1
    assert result.score.overall_score == 7.0


@pytest.mark.asyncio
async def test_iteration_loop_multiple_iterations():
    """Test that max_iterations=3 runs evaluator three times."""
    feedback = ScriptFeedback(weaknesses=[], missing_angles=[], improvement_suggestions=[])
    score1 = make_mock_score(6.0)
    score2 = make_mock_score(7.5)
    score3 = make_mock_score(8.0)

    with (
        patch("flows.coordinator.run_research", new=AsyncMock(return_value=MOCK_BRIEF)),
        patch("flows.coordinator.run_outline", new=AsyncMock(return_value=MOCK_OUTLINE)),
        patch("flows.coordinator.run_script", new=AsyncMock(side_effect=[MOCK_SCRIPT, MOCK_SCRIPT_V2, MOCK_SCRIPT_V3])),
        patch("flows.coordinator.run_evaluator", new=AsyncMock(side_effect=[
            (feedback, score1),
            (feedback, score2),
            (feedback, score3),
        ])) as mock_eval,
        patch("flows.coordinator.run_voice", new=AsyncMock(return_value=MOCK_NARRATION)),
        patch("flows.coordinator.run_clips", new=AsyncMock(return_value=MOCK_CLIPS)),
    ):
        result = await run(topic="Test", max_iterations=3)

    assert mock_eval.call_count == 3


@pytest.mark.asyncio
async def test_iteration_loop_stops_early_on_low_improvement():
    """Test that loop stops when improvement is below threshold."""
    feedback = ScriptFeedback(weaknesses=[], missing_angles=[], improvement_suggestions=[])
    # Improvement from 7.0 to 7.1 is only 0.1, below default threshold of 0.2
    score1 = make_mock_score(7.0)
    score2 = make_mock_score(7.1)
    score3 = make_mock_score(9.0)  # Should never reach this

    with (
        patch("flows.coordinator.run_research", new=AsyncMock(return_value=MOCK_BRIEF)),
        patch("flows.coordinator.run_outline", new=AsyncMock(return_value=MOCK_OUTLINE)),
        patch("flows.coordinator.run_script", new=AsyncMock(side_effect=[MOCK_SCRIPT, MOCK_SCRIPT_V2, MOCK_SCRIPT_V3])),
        patch("flows.coordinator.run_evaluator", new=AsyncMock(side_effect=[
            (feedback, score1),
            (feedback, score2),
            (feedback, score3),
        ])) as mock_eval,
        patch("flows.coordinator.run_voice", new=AsyncMock(return_value=MOCK_NARRATION)),
        patch("flows.coordinator.run_clips", new=AsyncMock(return_value=MOCK_CLIPS)),
    ):
        result = await run(topic="Test", max_iterations=3, improvement_threshold=0.2)

    # Should stop after iteration 2 (improvement 0.1 < 0.2)
    assert mock_eval.call_count == 2


@pytest.mark.asyncio
async def test_iteration_loop_continues_on_high_improvement():
    """Test that loop continues when improvement is above threshold."""
    feedback = ScriptFeedback(weaknesses=[], missing_angles=[], improvement_suggestions=[])
    # Improvement from 6.0 to 7.0 is 1.0, above default threshold of 0.2
    score1 = make_mock_score(6.0)
    score2 = make_mock_score(7.0)
    score3 = make_mock_score(7.1)  # Improvement 0.1 < 0.2, should stop

    with (
        patch("flows.coordinator.run_research", new=AsyncMock(return_value=MOCK_BRIEF)),
        patch("flows.coordinator.run_outline", new=AsyncMock(return_value=MOCK_OUTLINE)),
        patch("flows.coordinator.run_script", new=AsyncMock(side_effect=[MOCK_SCRIPT, MOCK_SCRIPT_V2, MOCK_SCRIPT_V3])),
        patch("flows.coordinator.run_evaluator", new=AsyncMock(side_effect=[
            (feedback, score1),
            (feedback, score2),
            (feedback, score3),
        ])) as mock_eval,
        patch("flows.coordinator.run_voice", new=AsyncMock(return_value=MOCK_NARRATION)),
        patch("flows.coordinator.run_clips", new=AsyncMock(return_value=MOCK_CLIPS)),
    ):
        result = await run(topic="Test", max_iterations=3, improvement_threshold=0.2)

    # Should run all 3 iterations (stops after 3rd because improvement < threshold)
    assert mock_eval.call_count == 3


@pytest.mark.asyncio
async def test_iteration_loop_selects_best_script():
    """Test that best script by overall_score is selected."""
    feedback = ScriptFeedback(weaknesses=[], missing_angles=[], improvement_suggestions=[])
    # Middle iteration has highest score
    score1 = make_mock_score(6.0)
    score2 = make_mock_score(9.0)  # Best
    score3 = make_mock_score(7.0)

    with (
        patch("flows.coordinator.run_research", new=AsyncMock(return_value=MOCK_BRIEF)),
        patch("flows.coordinator.run_outline", new=AsyncMock(return_value=MOCK_OUTLINE)),
        patch("flows.coordinator.run_script", new=AsyncMock(side_effect=[MOCK_SCRIPT, MOCK_SCRIPT_V2, MOCK_SCRIPT_V3])),
        patch("flows.coordinator.run_evaluator", new=AsyncMock(side_effect=[
            (feedback, score1),
            (feedback, score2),
            (feedback, score3),
        ])),
        patch("flows.coordinator.run_voice", new=AsyncMock(return_value=MOCK_NARRATION)),
        patch("flows.coordinator.run_clips", new=AsyncMock(return_value=MOCK_CLIPS)),
    ):
        result = await run(topic="Test", max_iterations=3)

    # Should select script with score 9.0 (MOCK_SCRIPT_V2)
    assert result.score.overall_score == 9.0
    assert result.script is MOCK_SCRIPT_V2


@pytest.mark.asyncio
async def test_iteration_loop_uses_best_script_for_voice():
    """Test that voice agent uses the best script, not the last script."""
    feedback = ScriptFeedback(weaknesses=[], missing_angles=[], improvement_suggestions=[])
    score1 = make_mock_score(8.0)  # Best
    score2 = make_mock_score(6.0)

    voice_mock = AsyncMock(return_value=MOCK_NARRATION)

    with (
        patch("flows.coordinator.run_research", new=AsyncMock(return_value=MOCK_BRIEF)),
        patch("flows.coordinator.run_outline", new=AsyncMock(return_value=MOCK_OUTLINE)),
        patch("flows.coordinator.run_script", new=AsyncMock(side_effect=[MOCK_SCRIPT, MOCK_SCRIPT_V2])),
        patch("flows.coordinator.run_evaluator", new=AsyncMock(side_effect=[
            (feedback, score1),
            (feedback, score2),
        ])),
        patch("flows.coordinator.run_voice", new=voice_mock),
        patch("flows.coordinator.run_clips", new=AsyncMock(return_value=MOCK_CLIPS)),
    ):
        result = await run(topic="Test", max_iterations=2)

    # Voice should use first script (score 8.0), not second (score 6.0)
    voice_mock.assert_called_once()
    assert voice_mock.call_args.kwargs["script"] is MOCK_SCRIPT


@pytest.mark.asyncio
async def test_iteration_loop_default_is_single_iteration():
    """Test that default max_iterations=1 runs only one iteration."""
    feedback = ScriptFeedback(weaknesses=[], missing_angles=[], improvement_suggestions=[])
    score = make_mock_score(7.0)

    with (
        patch("flows.coordinator.run_research", new=AsyncMock(return_value=MOCK_BRIEF)),
        patch("flows.coordinator.run_outline", new=AsyncMock(return_value=MOCK_OUTLINE)),
        patch("flows.coordinator.run_script", new=AsyncMock(return_value=MOCK_SCRIPT)),
        patch("flows.coordinator.run_evaluator", new=AsyncMock(return_value=(feedback, score))) as mock_eval,
        patch("flows.coordinator.run_voice", new=AsyncMock(return_value=MOCK_NARRATION)),
        patch("flows.coordinator.run_clips", new=AsyncMock(return_value=MOCK_CLIPS)),
    ):
        result = await run(topic="Test")  # No max_iterations specified

    assert mock_eval.call_count == 1
