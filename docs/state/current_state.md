# Current State

## Last updated
2026-04-09 (Sprint 4, Task 8 COMPLETE — Tests; **SPRINT 4 COMPLETE**)

## Architecture note
`agents/` was renamed to `engine_agents/` to avoid shadowing the `openai-agents` SDK which also installs as `agents`.

## What exists

### Core files
- `pyproject.toml` — project metadata; packages: engine_agents, tools, schemas, flows
- `.env` / `.env.example` — OPENAI_API_KEY, TAVILY_API_KEY
- `main.py` — CLI entry point; args: --topic, --angle, --audience, --red-lines, --must-hits, --tone, --style, --output_mode (draft/narration/clips/all)
- `README.md` — setup and usage instructions
- `docs/style_guide.md` — writing style guide

### Agents
- `engine_agents/research.py` — `run_research()`; tool-augmented with `web_search()`; returns `ResearchBrief` with scored `sources`
- `engine_agents/outline.py` — `run_outline()`; takes topic + `ResearchBrief`; injects sources into prompt
- `engine_agents/script.py` — `run_script()`; takes topic + `CommentaryOutline` + optional `ScriptFeedback`; returns `FinalScript`; supports rewrite pass
- `engine_agents/voice.py` — `run_voice()`; converts `FinalScript` to `NarrationScript`
- `engine_agents/clips.py` — `run_clips()`; extracts `Clip` list from `FinalScript`
- `engine_agents/evaluator.py` — `run_evaluator()`; analyzes `FinalScript`, returns `ScriptFeedback`

### Schemas
- `schemas/research.py` — `Source` (title, url, summary, credibility_score, recency, bias_flag), `ResearchBrief`
- `schemas/outline.py` — `CommentaryOutline`, `OutlineSection`
- `schemas/script.py` — `FinalScript` (with `full_text()`), `NarrationScript`, `Clip`, `ScriptFeedback`

### Tools
- `tools/web_search.py` — `SearchResult` dataclass + `web_search(query)` via Tavily API
- `tools/knowledge_store.py` — `save_research_brief()`, `load_relevant_knowledge()`; persists to `data/knowledge/`
- `tools/logger.py` — `log()` for structured JSON logs; `log_stage()` context manager with stage/event/duration/metadata

### Flows
- `flows/coordinator.py` — orchestrates research → outline → script → evaluator → rewrite → voice → clips; returns `EngineResult` (includes `ScriptFeedback`)

### Tests (86 passing)
- `tests/test_schemas.py` — 11 tests
- `tests/test_research_agent.py` — 7 tests
- `tests/test_outline_agent.py` — 5 tests
- `tests/test_script_agent.py` — 9 tests
- `tests/test_coordinator.py` — 4 tests (updated for evaluator + rewrite)
- `tests/test_smoke.py` — 4 tests (1 live, skipped without API keys)
- `tests/test_live_pipeline.py` — 3 tests (skipped without API keys)
- `tests/test_web_search.py` — 4 tests
- `tests/test_voice_agent.py` — 6 tests
- `tests/test_clips_agent.py` — 7 tests
- `tests/test_knowledge_store.py` — 14 tests
- `tests/test_evaluator_agent.py` — 7 tests
- `tests/test_rewrite_flow.py` — 5 tests

## Test status
86/86 passing (`.venv/bin/python -m pytest tests/ -v`)

## Sprint status
**Sprint 1 COMPLETE. Sprint 2 COMPLETE. Sprint 3 COMPLETE. Sprint 4 COMPLETE.**

Active sprint file: `docs/tasks/active_sprint_04.md`
Spec: `docs/specs/content_engine_v4.md`

## Sprint 4 — What is missing (not yet implemented)

Per `docs/specs/content_engine_v4.md` and `docs/tasks/active_sprint_04.md`:

### Missing Directories
- ~~`data/knowledge/`~~ — **DONE** (Task 1)

### Missing Files
- ~~`engine_agents/evaluator.py`~~ — **DONE** (Task 2)
- ~~`tests/test_evaluator_agent.py`~~ — **DONE** (Task 2)
- ~~`tests/test_rewrite_flow.py`~~ — **DONE** (Task 5)
- ~~`tests/test_knowledge_store.py`~~ — **DONE** (Task 1)

### Missing Schemas
- ~~`ScriptFeedback` (weaknesses, missing_angles, improvement_suggestions) in `schemas/script.py`~~ — **DONE** (Task 3)
- ~~`Source` extensions: `credibility_score`, `recency`, `bias_flag` in `schemas/research.py`~~ — **DONE** (Task 6)

### Missing Features
- ~~Knowledge store: `save_research_brief()`, `load_relevant_knowledge(topic)`~~ — **DONE** (Task 1)
- ~~Evaluator agent: `run_evaluator(script) -> ScriptFeedback`~~ — **DONE** (Task 2)
- ~~Rewrite pass: script agent accepts optional feedback, produces improved version~~ — **DONE** (Task 4)
- ~~Coordinator update: call evaluator after script, optionally trigger rewrite~~ — **DONE** (Task 5)
- ~~Source scoring: research agent populates credibility_score, recency, bias_flag~~ — **DONE** (Task 6)
- ~~Structured logging: replace prints with stage/duration/metadata logs~~ — **DONE** (Task 7)

## Next task
Sprint 4 complete. Awaiting Sprint 5 assignment.

## Blockers
None
