# Current State

## Last Updated

2026-04-11 — Recovery Sprint Task 1 complete; README markdown lint issues (MD040, MD060) cleaned.

## Architecture Note

`agents/` was renamed to `engine_agents/` to avoid shadowing the `openai-agents` SDK which also installs as `agents`.

## System Overview

### Tech Stack

- Python 3.11+, OpenAI Agents SDK (`openai-agents`), Tavily API, pytest + pytest-asyncio
- CLI-only (no frontend, no database, no auth beyond API keys in `.env`)
- File-based persistence: `data/knowledge/`, `data/runs/{run_id}/`

### Architecture

Multi-agent pipeline orchestrated by `flows/coordinator.py`:

```text
Input → Research → Knowledge Store → Outline → Script → [Evaluate → Score → Rewrite]×N → Select Best → Voice → Clips → Persist Artifacts
```

### Core Files

- `pyproject.toml` — project metadata; packages: engine_agents, tools, schemas, flows
- `.env` / `.env.example` — OPENAI_API_KEY, TAVILY_API_KEY
- `main.py` — CLI entry point with all v5 flags + run inspector + export
- `README.md` — setup and usage instructions
- `docs/style_guide.md` — writing style guide

### Agents

- `engine_agents/research.py` — `run_research()`; tool-augmented with `web_search()`; returns `ResearchBrief` with scored `sources`
- `engine_agents/outline.py` — `run_outline()`; takes topic + `ResearchBrief`; injects sources + prior knowledge
- `engine_agents/script.py` — `run_script()`; takes topic + `CommentaryOutline` + optional `ScriptFeedback`; returns `FinalScript`
- `engine_agents/voice.py` — `run_voice()`; converts `FinalScript` to `NarrationScript`
- `engine_agents/clips.py` — `run_clips()`; extracts `Clip` list from `FinalScript`
- `engine_agents/evaluator.py` — `run_evaluator()`; returns `(ScriptFeedback, ScriptScore)` tuple

### Schemas

- `schemas/research.py` — `Source` (with credibility scoring), `ResearchBrief`
- `schemas/outline.py` — `CommentaryOutline`, `OutlineSection`
- `schemas/script.py` — `FinalScript`, `NarrationScript`, `Clip`, `ScriptFeedback`, `ScriptScore`

### Tools

- `tools/web_search.py` — `SearchResult` + `web_search(query)` via Tavily
- `tools/knowledge_store.py` — `save_research_brief()`, `load_relevant_knowledge(topic, top_k)`
- `tools/scoring.py` — `select_best_script()`, `ScoreWeights`, `calculate_weighted_score()`
- `tools/logger.py` — `log()` + `log_stage()` context manager
- `tools/run_artifacts.py` — `create_run_dir()`, `save_json()`, `save_text()`, `load_json()`, `load_text()`

### Flows

- `flows/coordinator.py` — full pipeline with iteration loop, early stopping, best script selection, artifact saving; returns `EngineResult`

## Feature Status (spec v5)

| Feature | Status | Notes |
| --- | --- | --- |
| 1. Run Artifacts | ✅ Implemented | Missing `logs.json` per spec |
| 2. Run Metadata | ✅ Implemented | All fields present |
| 3. Iterative Optimization Loop | ✅ Implemented | |
| 4. Script Scoring | ✅ Implemented | |
| 5. Output Selection | ✅ Implemented | Tie-breaker uses first-occurrence, spec says `factual_grounding` |
| 6. CLI Controls | ✅ Implemented | All 7 flags |
| 7. Knowledge Store Upgrade | ✅ Implemented | |
| 8. Run Inspection | ✅ Implemented | |

## Spec Alignment

### Matches

- All 8 v5 capabilities implemented in code
- Pipeline flow matches spec diagram
- CLI flags match spec
- Data contracts match spec

### Gaps

- `EngineResult` missing `all_versions` and `feedback_history` (spec §5)
- Tie-breaker should use `factual_grounding` not first-occurrence (spec §5)
- `logs.json` not saved to run artifacts (spec §1)

### Deviations

- None beyond gaps above

### Overbuild

- None

## Test Status — GREEN

**Actual: 158 passed** (`.venv/bin/python -m pytest tests/ -v`)

Recovery fix applied: evaluator mocks now return `(ScriptFeedback, ScriptScore)` tuples in:

- `tests/test_rewrite_flow.py`
- `tests/test_smoke.py`
- `tests/test_run_artifacts.py`

### All test files

- `tests/test_schemas.py` — 14 tests
- `tests/test_research_agent.py` — 7 tests
- `tests/test_outline_agent.py` — 5 tests
- `tests/test_script_agent.py` — 9 tests
- `tests/test_coordinator.py` — 4 tests
- `tests/test_smoke.py` — 4 tests
- `tests/test_live_pipeline.py` — 3 tests
- `tests/test_web_search.py` — 4 tests
- `tests/test_voice_agent.py` — 6 tests
- `tests/test_clips_agent.py` — 7 tests
- `tests/test_knowledge_store.py` — 18 tests
- `tests/test_evaluator_agent.py` — 9 tests
- `tests/test_rewrite_flow.py` — 5 tests
- `tests/test_run_artifacts.py` — 13 tests
- `tests/test_cli_flags.py` — 11 tests
- `tests/test_iteration_loop.py` — 7 tests
- `tests/test_scoring_selection.py` — 10 tests
- `tests/test_run_inspector.py` — 11 tests
- `tests/test_final_integration.py` — 11 tests

## Sprint Status

**Sprint 1–5 COMPLETE. Recovery Sprint complete.**

## Active Sprint — Recovery

| # | Task | Priority | Status |
| --- | --- | --- | --- |
| 1 | Fix mock evaluator returns in `test_rewrite_flow.py`, `test_smoke.py`, `test_run_artifacts.py` (return tuple not ScriptFeedback) | HIGH | COMPLETE |
| 2 | Verify full test suite green (158+ passing) | HIGH | COMPLETE |
| 3 | Update `current_state.md` with accurate counts | HIGH | COMPLETE |

## Risks & Blockers

### Risks

- Test mocks fell behind evaluator signature change — pattern could recur

### Blockers

- None — fix is mechanical (update mock return values)

## Cleanup Opportunities

- `test_smoke.py` doesn't mock `run_voice`/`run_clips` — fragile
- `test_live_pipeline.py` JSON decode error on live API — consider flaky marking

## Next Task

Sprint 6 planning (await `docs/specs/content_engine_v6.md`).
