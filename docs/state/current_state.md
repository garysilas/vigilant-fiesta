# Current State

## Last updated
2026-04-09 (Sprint 3 RECOVERY — Active Sprint 03 identified)

## Completed tasks (Sprint 1)
- Task 1: Initialize Python project skeleton
- Task 2: Add schemas for research, outline, and script outputs
- Task 3: Implement research agent
- Task 4: Implement outline agent
- Task 5: Implement script agent
- Task 6: Implement coordinator
- Task 7: Add CLI entry point
- Task 8: Add basic tests

## Architecture note
`agents/` was renamed to `engine_agents/` to avoid shadowing the `openai-agents` SDK which also installs as `agents`.

## What exists
- `pyproject.toml` — project metadata; packages: engine_agents, tools, schemas, flows
- `.env` / `.env.example` — OPENAI_API_KEY
- `main.py` — CLI entry point; wired to coordinator; args: --topic, --angle, --audience, --red-lines, --must-hits, --tone, --style, --output_mode (draft/narration/clips/all)
- `engine_agents/research.py` — `run_research()` async function; calls `web_search()`, injects results into prompt, returns `ResearchBrief` with `sources`; logs `[Research Agent] Starting/Completed`
- `engine_agents/outline.py` — `run_outline()` async function; takes topic + `ResearchBrief` (with sources); injects sources into prompt; logs `[Outline Agent] Starting/Completed`
- `engine_agents/script.py` — `run_script()` async function; takes topic + `CommentaryOutline`; returns `FinalScript`; instructions updated for grounded output; logs `[Script Agent] Starting/Completed`
- `tools/__init__.py` — package init
- `tools/web_search.py` — `SearchResult` dataclass + `web_search(query)` function; uses Tavily API; reads `TAVILY_API_KEY` from env
- `schemas/research.py` — `Source` dataclass (title, url, summary) + `ResearchBrief` dataclass (fields: key_facts, key_tensions, relevant_examples, caveats, source_notes, sources)
- `schemas/outline.py` — `CommentaryOutline`, `OutlineSection` dataclasses
- `schemas/script.py` — `FinalScript` dataclass with `full_text()` helper
- `flows/coordinator.py` — `run()` async function; orchestrates research → outline → script → voice → clips; returns `EngineResult` with narration and clips; logs `[Coordinator] Starting/Pipeline complete`
- `tests/test_schemas.py` — 9 schema tests (includes Source + sources)
- `tests/test_research_agent.py` — 6 research agent tests (includes tone/style prompt coverage)
- `tests/test_outline_agent.py` — 5 outline agent tests (includes tone/style prompt coverage)
- `tests/test_script_agent.py` — 5 script agent tests (includes tone/style prompt coverage)
- `tests/test_coordinator.py` — 4 coordinator tests (includes tone/style forwarding)
- `tests/test_smoke.py` — 3 pipeline smoke tests + 1 live integration test (skipped without OPENAI_API_KEY)
- `tests/test_live_pipeline.py` — 3 live integration tests (skipped without OPENAI_API_KEY + TAVILY_API_KEY; validates sources + script)
- `tests/test_web_search.py` — 4 unit tests (mocked TavilyClient)
- `README.md` — setup and usage instructions

## Test status
36/36 passing (`pytest tests/ -v`)

## Sprint status
**Sprint 1 COMPLETE. Sprint 2 COMPLETE. Sprint 3 ACTIVE.**

Active sprint file: `docs/tasks/active_sprint_03.md`

## Sprint 2 — What was implemented (now complete)
- ~~`tools/web_search.py`~~ — **DONE**
- ~~`schemas/research.py`~~ — **DONE** (`Source` + `sources` field added)
- ~~`engine_agents/research.py`~~ — **DONE** (tool-augmented, sources populated)
- ~~`engine_agents/outline.py`~~ — **DONE** (sources injected into prompt, log lines added)
- ~~`engine_agents/script.py`~~ — **DONE** (instructions updated, log lines added)
- ~~`main.py`~~ — **DONE** (`--tone` and `--style` added, forwarded through full pipeline)
- ~~`tests/test_live_pipeline.py`~~ — **DONE** (3 live tests; skip without API keys; validates sources + script)
- ~~Logging across coordinator, agents, and tools~~ — **DONE**

## Sprint 3 — What is missing (not yet implemented)

Per `docs/specs/content_engine_v3.md` and `docs/tasks/active_sprint_03.md`:

### Missing Files
- ~~`docs/style_guide.md`~~ — **DONE** (Task 1)
- ~~`engine_agents/voice.py`~~ — **DONE** (Task 3)
- ~~`engine_agents/clips.py`~~ — **DONE** (Task 4)
- ~~`tests/test_voice_agent.py`~~ — **DONE** (Task 8)
- ~~`tests/test_clips_agent.py`~~ — **DONE** (Task 8)

### Missing Schemas
- ~~`NarrationScript` class — `schemas/script.py`~~ — **DONE** (Task 3)
- ~~`Clip` class — `schemas/script.py`~~ — **DONE** (Task 4)

### Missing Features
- ~~Script agent upgrade for narrative quality — `engine_agents/script.py`~~ — **DONE** (Task 2)
- ~~Voice and clips pipeline stages — `flows/coordinator.py`~~ — **DONE** (Task 5)
- ~~`--output_mode` CLI argument — `main.py`~~ — **DONE** (Task 6)

## Next task
**Sprint 3 COMPLETE**

All 8 tasks in Sprint 3 have been implemented:
- Task 1: Writing Style Guide
- Task 2: Script Agent Upgrade
- Task 3: Voice Agent
- Task 4: Clips Agent
- Task 5: Coordinator Update
- Task 6: CLI Extension
- Task 7: Schemas (NarrationScript, Clip)
- Task 8: Tests (voice agent, clips agent)

See `docs/tasks/active_sprint_03.md` for full details.

## Blockers
None
