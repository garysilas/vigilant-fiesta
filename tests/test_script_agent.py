import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from engine_agents.script import run_script
from schemas.outline import CommentaryOutline, OutlineSection
from schemas.script import FinalScript, ScriptFeedback

MOCK_OUTLINE = CommentaryOutline(
    hook="Did you know...",
    thesis="Young men face structural disadvantages.",
    sections=[
        OutlineSection(title="Act 1", argument="Setup the problem"),
        OutlineSection(title="Act 2", argument="Evidence"),
    ],
    emotional_progression="curiosity → tension → resolution",
    closing_idea="Systemic change is needed.",
)

MOCK_RESPONSE = {
    "opening": "Here's something nobody talks about...",
    "body": "The data is clear. Young men are falling behind...",
    "closing": "The question is: what are we going to do about it?",
}


@pytest.fixture
def mock_runner_result():
    result = MagicMock()
    result.final_output = json.dumps(MOCK_RESPONSE)
    return result


@pytest.mark.asyncio
async def test_run_script_returns_final_script(mock_runner_result):
    with patch("engine_agents.script.Runner.run", new=AsyncMock(return_value=mock_runner_result)):
        script = await run_script(topic="Test topic", outline=MOCK_OUTLINE)

    assert isinstance(script, FinalScript)
    assert script.opening == "Here's something nobody talks about..."
    assert "Young men" in script.body
    assert script.closing == "The question is: what are we going to do about it?"


@pytest.mark.asyncio
async def test_run_script_full_text_combines_parts(mock_runner_result):
    with patch("engine_agents.script.Runner.run", new=AsyncMock(return_value=mock_runner_result)):
        script = await run_script(topic="Test topic", outline=MOCK_OUTLINE)

    full = script.full_text()
    assert script.opening in full
    assert script.body in full
    assert script.closing in full


@pytest.mark.asyncio
async def test_run_script_prompt_includes_outline(mock_runner_result):
    with patch("engine_agents.script.Runner.run", new=AsyncMock(return_value=mock_runner_result)) as mock_run:
        await run_script(topic="Test topic", outline=MOCK_OUTLINE, angle="economic", audience="young men")
        prompt = mock_run.call_args[0][1]
        assert "Did you know" in prompt
        assert "Act 1" in prompt
        assert "economic" in prompt
        assert "young men" in prompt


@pytest.mark.asyncio
async def test_run_script_prompt_includes_tone_and_style(mock_runner_result):
    with patch("engine_agents.script.Runner.run", new=AsyncMock(return_value=mock_runner_result)) as mock_run:
        await run_script(topic="Test topic", outline=MOCK_OUTLINE, tone="serious", style="documentary")
        prompt = mock_run.call_args[0][1]
        assert "serious" in prompt
        assert "documentary" in prompt


@pytest.mark.asyncio
async def test_run_script_empty_outline():
    empty_outline = CommentaryOutline()
    response = {"opening": "Start.", "body": "Middle.", "closing": "End."}
    result = MagicMock()
    result.final_output = json.dumps(response)

    with patch("engine_agents.script.Runner.run", new=AsyncMock(return_value=result)):
        script = await run_script(topic="Test topic", outline=empty_outline)

    assert script.opening == "Start."
    assert script.full_text() == "Start.\n\nMiddle.\n\nEnd."


MOCK_FEEDBACK = ScriptFeedback(
    weaknesses=["Opening lacks specificity"],
    missing_angles=["No global context"],
    improvement_suggestions=["Add a concrete statistic"],
)


@pytest.mark.asyncio
async def test_run_script_with_feedback_injects_weaknesses(mock_runner_result):
    with patch("engine_agents.script.Runner.run", new=AsyncMock(return_value=mock_runner_result)) as mock_run:
        await run_script(topic="Test topic", outline=MOCK_OUTLINE, feedback=MOCK_FEEDBACK)
        prompt = mock_run.call_args[0][1]
        assert "Opening lacks specificity" in prompt
        assert "EVALUATOR FEEDBACK" in prompt


@pytest.mark.asyncio
async def test_run_script_with_feedback_injects_missing_angles(mock_runner_result):
    with patch("engine_agents.script.Runner.run", new=AsyncMock(return_value=mock_runner_result)) as mock_run:
        await run_script(topic="Test topic", outline=MOCK_OUTLINE, feedback=MOCK_FEEDBACK)
        prompt = mock_run.call_args[0][1]
        assert "No global context" in prompt


@pytest.mark.asyncio
async def test_run_script_with_feedback_injects_suggestions(mock_runner_result):
    with patch("engine_agents.script.Runner.run", new=AsyncMock(return_value=mock_runner_result)) as mock_run:
        await run_script(topic="Test topic", outline=MOCK_OUTLINE, feedback=MOCK_FEEDBACK)
        prompt = mock_run.call_args[0][1]
        assert "Add a concrete statistic" in prompt


@pytest.mark.asyncio
async def test_run_script_without_feedback_no_feedback_section(mock_runner_result):
    with patch("engine_agents.script.Runner.run", new=AsyncMock(return_value=mock_runner_result)) as mock_run:
        await run_script(topic="Test topic", outline=MOCK_OUTLINE)
        prompt = mock_run.call_args[0][1]
        assert "EVALUATOR FEEDBACK" not in prompt
