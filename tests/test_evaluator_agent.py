import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from engine_agents.evaluator import run_evaluator
from schemas.script import FinalScript, ScriptFeedback, ScriptScore

MOCK_SCRIPT = FinalScript(
    opening="Here's a bold opener.",
    body="The body explores tensions in the economy.",
    closing="And that's the uncomfortable truth.",
)

MOCK_RESPONSE = {
    "weaknesses": ["Opening lacks specificity", "Body transitions are abrupt"],
    "missing_angles": ["No mention of global context"],
    "improvement_suggestions": ["Add a concrete statistic to the opener"],
    "scores": {
        "clarity_score": 7.5,
        "argument_score": 8.0,
        "emotional_impact": 6.5,
        "factual_grounding": 8.5,
        "overall_score": 7.6,
    },
}


@pytest.fixture
def mock_runner_result():
    result = MagicMock()
    result.final_output = json.dumps(MOCK_RESPONSE)
    return result


@pytest.mark.asyncio
async def test_run_evaluator_returns_script_feedback(mock_runner_result):
    with patch("engine_agents.evaluator.Runner.run", new=AsyncMock(return_value=mock_runner_result)):
        feedback, score = await run_evaluator(script=MOCK_SCRIPT)

    assert isinstance(feedback, ScriptFeedback)
    assert isinstance(score, ScriptScore)


@pytest.mark.asyncio
async def test_run_evaluator_populates_weaknesses(mock_runner_result):
    with patch("engine_agents.evaluator.Runner.run", new=AsyncMock(return_value=mock_runner_result)):
        feedback, _ = await run_evaluator(script=MOCK_SCRIPT)

    assert feedback.weaknesses == ["Opening lacks specificity", "Body transitions are abrupt"]


@pytest.mark.asyncio
async def test_run_evaluator_populates_missing_angles(mock_runner_result):
    with patch("engine_agents.evaluator.Runner.run", new=AsyncMock(return_value=mock_runner_result)):
        feedback, _ = await run_evaluator(script=MOCK_SCRIPT)

    assert feedback.missing_angles == ["No mention of global context"]


@pytest.mark.asyncio
async def test_run_evaluator_populates_suggestions(mock_runner_result):
    with patch("engine_agents.evaluator.Runner.run", new=AsyncMock(return_value=mock_runner_result)):
        feedback, _ = await run_evaluator(script=MOCK_SCRIPT)

    assert feedback.improvement_suggestions == ["Add a concrete statistic to the opener"]


@pytest.mark.asyncio
async def test_run_evaluator_prompt_includes_script(mock_runner_result):
    with patch("engine_agents.evaluator.Runner.run", new=AsyncMock(return_value=mock_runner_result)) as mock_run:
        await run_evaluator(script=MOCK_SCRIPT)
        prompt = mock_run.call_args[0][1]
        assert "bold opener" in prompt
        assert "tensions in the economy" in prompt
        assert "uncomfortable truth" in prompt


@pytest.mark.asyncio
async def test_run_evaluator_empty_response():
    empty_response = {"weaknesses": [], "missing_angles": [], "improvement_suggestions": [], "scores": {}}
    result = MagicMock()
    result.final_output = json.dumps(empty_response)

    with patch("engine_agents.evaluator.Runner.run", new=AsyncMock(return_value=result)):
        feedback, score = await run_evaluator(script=MOCK_SCRIPT)

    assert feedback.weaknesses == []
    assert feedback.missing_angles == []
    assert feedback.improvement_suggestions == []
    assert score.clarity_score == 0.0
    assert score.overall_score == 0.0


@pytest.mark.asyncio
async def test_run_evaluator_missing_keys():
    partial_response = {"weaknesses": ["one issue"]}
    result = MagicMock()
    result.final_output = json.dumps(partial_response)

    with patch("engine_agents.evaluator.Runner.run", new=AsyncMock(return_value=result)):
        feedback, score = await run_evaluator(script=MOCK_SCRIPT)

    assert feedback.weaknesses == ["one issue"]
    assert feedback.missing_angles == []
    assert feedback.improvement_suggestions == []
    assert score.clarity_score == 0.0


@pytest.mark.asyncio
async def test_run_evaluator_returns_script_score(mock_runner_result):
    with patch("engine_agents.evaluator.Runner.run", new=AsyncMock(return_value=mock_runner_result)):
        _, score = await run_evaluator(script=MOCK_SCRIPT)

    assert isinstance(score, ScriptScore)
    assert score.clarity_score == 7.5
    assert score.argument_score == 8.0
    assert score.emotional_impact == 6.5
    assert score.factual_grounding == 8.5
    assert score.overall_score == 7.6


@pytest.mark.asyncio
async def test_run_evaluator_score_missing_scores_key():
    response_no_scores = {
        "weaknesses": ["weak"],
        "missing_angles": [],
        "improvement_suggestions": [],
    }
    result = MagicMock()
    result.final_output = json.dumps(response_no_scores)

    with patch("engine_agents.evaluator.Runner.run", new=AsyncMock(return_value=result)):
        feedback, score = await run_evaluator(script=MOCK_SCRIPT)

    assert isinstance(score, ScriptScore)
    assert score.clarity_score == 0.0
    assert score.argument_score == 0.0
    assert score.emotional_impact == 0.0
    assert score.factual_grounding == 0.0
    assert score.overall_score == 0.0
