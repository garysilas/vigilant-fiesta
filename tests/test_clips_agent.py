import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from engine_agents.clips import run_clips
from schemas.script import Clip, FinalScript

MOCK_SCRIPT = FinalScript(
    opening="Here's something nobody talks about...",
    body="Young men are falling behind. In 1990, the average 30-year-old man earned more than his father did at that age. Today, that's no longer true. The data is undeniable.",
    closing="We need to ask: what kind of future are we building?",
)

MOCK_RESPONSE = {
    "clips": [
        {
            "hook": "Here's something nobody talks about...",
            "body": "Young men are falling behind. In 1990, the average 30-year-old man earned more than his father did at that age.",
            "closing": "Today, that's no longer true.",
        },
        {
            "hook": "The American Dream is broken for half the population.",
            "body": "We tell young men to work hard and succeed, but the ladder has been pulled up. Earnings are down, debt is up.",
            "closing": "What kind of future are we building?",
        },
        {
            "hook": "1990 vs today: what changed?",
            "body": "In one generation, young men went from out-earning their fathers to falling behind. The data tells a story we ignore.",
            "closing": "It's time to pay attention.",
        },
    ]
}


@pytest.fixture
def mock_runner_result():
    result = MagicMock()
    result.final_output = json.dumps(MOCK_RESPONSE)
    return result


@pytest.mark.asyncio
async def test_run_clips_returns_list_of_clips(mock_runner_result):
    with patch("engine_agents.clips.Runner.run", new=AsyncMock(return_value=mock_runner_result)):
        clips = await run_clips(script=MOCK_SCRIPT)

    assert isinstance(clips, list)
    assert len(clips) > 0
    assert all(isinstance(c, Clip) for c in clips)


@pytest.mark.asyncio
async def test_run_clips_returns_3_to_5_clips(mock_runner_result):
    with patch("engine_agents.clips.Runner.run", new=AsyncMock(return_value=mock_runner_result)):
        clips = await run_clips(script=MOCK_SCRIPT)

    assert 3 <= len(clips) <= 5


@pytest.mark.asyncio
async def test_run_clips_each_clip_has_hook_body_closing(mock_runner_result):
    with patch("engine_agents.clips.Runner.run", new=AsyncMock(return_value=mock_runner_result)):
        clips = await run_clips(script=MOCK_SCRIPT)

    for clip in clips:
        assert hasattr(clip, "hook")
        assert hasattr(clip, "body")
        assert hasattr(clip, "closing")


@pytest.mark.asyncio
async def test_run_clips_clips_are_non_empty(mock_runner_result):
    with patch("engine_agents.clips.Runner.run", new=AsyncMock(return_value=mock_runner_result)):
        clips = await run_clips(script=MOCK_SCRIPT)

    for clip in clips:
        assert clip.hook or clip.body or clip.closing  # At least one field should be non-empty


@pytest.mark.asyncio
async def test_run_clips_prompt_includes_script(mock_runner_result):
    with patch("engine_agents.clips.Runner.run", new=AsyncMock(return_value=mock_runner_result)) as mock_run:
        await run_clips(script=MOCK_SCRIPT)
        prompt = mock_run.call_args[0][1]
        assert "Here's something nobody talks about" in prompt
        assert "Young men are falling behind" in prompt


@pytest.mark.asyncio
async def test_run_clips_empty_script():
    empty_script = FinalScript()
    response = {"clips": []}
    result = MagicMock()
    result.final_output = json.dumps(response)

    with patch("engine_agents.clips.Runner.run", new=AsyncMock(return_value=result)):
        clips = await run_clips(script=empty_script)

    assert clips == []


@pytest.mark.asyncio
async def test_run_clips_single_clip():
    single_clip_script = FinalScript(opening="Hook", body="Body", closing="Closing")
    response = {
        "clips": [
            {"hook": "Only hook", "body": "Only body", "closing": "Only closing"}
        ]
    }
    result = MagicMock()
    result.final_output = json.dumps(response)

    with patch("engine_agents.clips.Runner.run", new=AsyncMock(return_value=result)):
        clips = await run_clips(script=single_clip_script)

    assert len(clips) == 1
    assert clips[0].hook == "Only hook"
    assert clips[0].body == "Only body"
    assert clips[0].closing == "Only closing"
