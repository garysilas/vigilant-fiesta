import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from engine_agents.voice import run_voice
from schemas.script import FinalScript, NarrationScript

MOCK_SCRIPT = FinalScript(
    opening="Here's something nobody talks about...",
    body="The data is clear. Young men are falling behind in education and earnings.",
    closing="The question is: what are we going to do about it?",
)

MOCK_RESPONSE = {
    "text": "Here's something **nobody** talks about... [PAUSE] The data is clear. [PAUSE 2s] Young men are falling behind in education and earnings. [PAUSE] The question is: what are *we* going to do about it?",
}


@pytest.fixture
def mock_runner_result():
    result = MagicMock()
    result.final_output = json.dumps(MOCK_RESPONSE)
    return result


@pytest.mark.asyncio
async def test_run_voice_returns_narration_script(mock_runner_result):
    with patch("engine_agents.voice.Runner.run", new=AsyncMock(return_value=mock_runner_result)):
        narration = await run_voice(script=MOCK_SCRIPT)

    assert isinstance(narration, NarrationScript)
    assert narration.text
    assert "nobody" in narration.text


@pytest.mark.asyncio
async def test_run_voice_output_differs_from_original(mock_runner_result):
    """Voice agent should transform the script, not just echo it."""
    with patch("engine_agents.voice.Runner.run", new=AsyncMock(return_value=mock_runner_result)):
        narration = await run_voice(script=MOCK_SCRIPT)

    original_text = MOCK_SCRIPT.full_text()
    # The output should be different (has pauses, emphasis markers)
    assert narration.text != original_text


@pytest.mark.asyncio
async def test_run_voice_preserves_meaning(mock_runner_result):
    """Voice agent should preserve the core meaning of the script."""
    with patch("engine_agents.voice.Runner.run", new=AsyncMock(return_value=mock_runner_result)):
        narration = await run_voice(script=MOCK_SCRIPT)

    # Core content should still be present
    assert "nobody" in narration.text or "something" in narration.text
    assert "young men" in narration.text.lower() or "falling behind" in narration.text


@pytest.mark.asyncio
async def test_run_voice_prompt_includes_script(mock_runner_result):
    with patch("engine_agents.voice.Runner.run", new=AsyncMock(return_value=mock_runner_result)) as mock_run:
        await run_voice(script=MOCK_SCRIPT)
        prompt = mock_run.call_args[0][1]
        assert "Here's something nobody talks about" in prompt
        assert "Young men are falling behind" in prompt


@pytest.mark.asyncio
async def test_run_voice_prompt_includes_tone_and_style(mock_runner_result):
    with patch("engine_agents.voice.Runner.run", new=AsyncMock(return_value=mock_runner_result)) as mock_run:
        await run_voice(script=MOCK_SCRIPT, tone="serious", style="documentary")
        prompt = mock_run.call_args[0][1]
        assert "serious" in prompt
        assert "documentary" in prompt


@pytest.mark.asyncio
async def test_run_voice_empty_script():
    empty_script = FinalScript()
    response = {"text": "[PAUSE] [PAUSE 2s]"}
    result = MagicMock()
    result.final_output = json.dumps(response)

    with patch("engine_agents.voice.Runner.run", new=AsyncMock(return_value=result)):
        narration = await run_voice(script=empty_script)

    assert narration.text == "[PAUSE] [PAUSE 2s]"
