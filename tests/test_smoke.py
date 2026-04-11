"""
Smoke tests for the full pipeline contract.
All tests run without a live API key by mocking the three agent functions.

Integration test (requires OPENAI_API_KEY) is marked with pytest.mark.integration
and skipped by default. Run with: pytest -m integration
"""
import os
from unittest.mock import AsyncMock, patch

import pytest

from flows.coordinator import EngineResult, run
from schemas.outline import CommentaryOutline, OutlineSection
from schemas.research import ResearchBrief
from schemas.script import FinalScript, ScriptFeedback, ScriptScore

_BRIEF = ResearchBrief(
    key_facts=["wages stagnated since 1970s"],
    key_tensions=["productivity vs pay gap"],
    relevant_examples=["manufacturing decline"],
    caveats=["data varies by region"],
    source_notes=["BLS, Pew Research"],
)
_OUTLINE = CommentaryOutline(
    hook="Nobody talks about this.",
    thesis="Young men are losing ground economically.",
    sections=[OutlineSection("The data", "Wages flat, costs up"), OutlineSection("The causes", "Structural shifts")],
    emotional_progression="curiosity → alarm → call to action",
    closing_idea="Policy change is overdue.",
)
_SCRIPT = FinalScript(
    opening="Here's what the numbers actually say.",
    body="Since the 1970s, real wages for young men without college degrees have fallen...",
    closing="The question isn't whether this is happening. It's whether we care enough to fix it.",
)
_FEEDBACK = ScriptFeedback(weaknesses=["needs more data"], missing_angles=[], improvement_suggestions=[])
_SCORE = ScriptScore(overall_score=7.0)
_REWRITTEN_SCRIPT = FinalScript(
    opening="Here's what the numbers actually say — and why it matters.",
    body="Since the 1970s, real wages for young men without college degrees have fallen sharply...",
    closing="The question isn't whether this is happening. It's whether we care enough to fix it.",
)


@pytest.mark.asyncio
async def test_pipeline_smoke_returns_engine_result():
    with (
        patch("flows.coordinator.run_research", new=AsyncMock(return_value=_BRIEF)),
        patch("flows.coordinator.run_outline", new=AsyncMock(return_value=_OUTLINE)),
        patch("flows.coordinator.run_script", new=AsyncMock(side_effect=[_SCRIPT, _REWRITTEN_SCRIPT])),
        patch("flows.coordinator.run_evaluator", new=AsyncMock(return_value=(_FEEDBACK, _SCORE))),
    ):
        result = await run(topic="Why young men are struggling financially")

    assert isinstance(result, EngineResult)
    assert isinstance(result.brief, ResearchBrief)
    assert isinstance(result.outline, CommentaryOutline)
    assert isinstance(result.script, FinalScript)


@pytest.mark.asyncio
async def test_pipeline_smoke_full_text_non_empty():
    with (
        patch("flows.coordinator.run_research", new=AsyncMock(return_value=_BRIEF)),
        patch("flows.coordinator.run_outline", new=AsyncMock(return_value=_OUTLINE)),
        patch("flows.coordinator.run_script", new=AsyncMock(side_effect=[_SCRIPT, _REWRITTEN_SCRIPT])),
        patch("flows.coordinator.run_evaluator", new=AsyncMock(return_value=(_FEEDBACK, _SCORE))),
    ):
        result = await run(topic="Why young men are struggling financially")

    full = result.script.full_text()
    assert len(full) > 0
    assert result.outline.hook != ""
    assert len(result.brief.key_facts) > 0


@pytest.mark.asyncio
async def test_pipeline_smoke_all_optionals_forwarded():
    research_mock = AsyncMock(return_value=_BRIEF)
    outline_mock = AsyncMock(return_value=_OUTLINE)
    script_mock = AsyncMock(side_effect=[_SCRIPT, _REWRITTEN_SCRIPT])
    evaluator_mock = AsyncMock(return_value=(_FEEDBACK, _SCORE))

    with (
        patch("flows.coordinator.run_research", new=research_mock),
        patch("flows.coordinator.run_outline", new=outline_mock),
        patch("flows.coordinator.run_script", new=script_mock),
        patch("flows.coordinator.run_evaluator", new=evaluator_mock),
    ):
        await run(
            topic="T",
            angle="economic lens",
            audience="young men 18-30",
            red_lines="no partisan framing",
            must_hits="mention wage data",
        )

    _, research_kwargs = research_mock.call_args
    assert research_kwargs["angle"] == "economic lens"
    assert research_kwargs["red_lines"] == "no partisan framing"
    assert research_kwargs["must_hits"] == "mention wage data"

    _, outline_kwargs = outline_mock.call_args
    assert outline_kwargs["audience"] == "young men 18-30"

    _, script_kwargs = script_mock.call_args
    assert script_kwargs["angle"] == "economic lens"


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"),
    reason="Requires OPENAI_API_KEY to be set",
)
async def test_pipeline_live_end_to_end():
    result = await run(topic="Why young men are struggling financially")

    assert isinstance(result, EngineResult)
    assert len(result.brief.key_facts) > 0
    assert result.outline.hook != ""
    assert len(result.script.full_text()) > 100
