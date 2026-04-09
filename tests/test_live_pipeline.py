"""
Live end-to-end pipeline test.
Requires both OPENAI_API_KEY and TAVILY_API_KEY to be set.
Skipped automatically if either key is missing.
Run with: pytest -m integration
"""
import os

import pytest

from flows.coordinator import EngineResult, run


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY") or not os.environ.get("TAVILY_API_KEY"),
    reason="Requires OPENAI_API_KEY and TAVILY_API_KEY to be set",
)
async def test_live_pipeline_returns_engine_result():
    result = await run(topic="Why young men are struggling financially")

    assert isinstance(result, EngineResult)


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY") or not os.environ.get("TAVILY_API_KEY"),
    reason="Requires OPENAI_API_KEY and TAVILY_API_KEY to be set",
)
async def test_live_pipeline_brief_has_sources():
    result = await run(topic="Why young men are struggling financially")

    assert len(result.brief.sources) > 0
    first = result.brief.sources[0]
    assert first.title != ""
    assert first.url != ""


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY") or not os.environ.get("TAVILY_API_KEY"),
    reason="Requires OPENAI_API_KEY and TAVILY_API_KEY to be set",
)
async def test_live_pipeline_script_non_empty():
    result = await run(topic="Why young men are struggling financially")

    assert len(result.script.full_text()) > 100
