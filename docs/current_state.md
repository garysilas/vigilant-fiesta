# Current State

## Last updated
2026-04-10 — Sprint 4 COMPLETE, Sprint 5 Task 1 COMPLETE (Run Artifacts System)

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
- `engine_agents/evaluator.py` — `run_evaluator()`; analyzes `FinalScript`, returns `(ScriptFeedback, ScriptScore)` tuple

### Schemas
- `schemas/research.py` — `Source` (with credibility scoring), `ResearchBrief`
- `schemas/outline.py` — `CommentaryOutline`, `OutlineSection`
- `schemas/script.py` — `FinalScript` (with `full_text()`), `NarrationScript`, `Clip`, `ScriptFeedback`, `ScriptScore`

### Tools
- `tools/web_search.py` — `SearchResult` dataclass + `web_search(query)` via Tavily API
- `tools/knowledge_store.py` — `save_research_brief()`, `load_relevant_knowledge()`; persists to `data/knowledge/`
- `tools/scoring.py` — `select_best_script()`, `ScoreWeights`; script selection by score with optional weighting
- `tools/logger.py` — `log()` for structured JSON logs; `log_stage()` context manager with stage/event/duration/metadata
- `tools/run_artifacts.py` — `create_run_dir()`, `save_json()`, `save_text()`; persists runs to `data/runs/{run_id}/`

### Flows
- `flows/coordinator.py` — orchestrates research → outline → script → (evaluate → score → rewrite){1..N} → voice → clips; iteration loop with early stopping; best script selection; returns `EngineResult` (includes `ScriptFeedback`, `ScriptScore`, `run_id`); saves artifacts when `save_run=True`

### Tests (159 passing)
- `tests/test_schemas.py` — 14 tests (includes ScriptScore)
- `tests/test_research_agent.py` — 7 tests
- `tests/test_outline_agent.py` — 5 tests
- `tests/test_script_agent.py` — 9 tests
- `tests/test_coordinator.py` — 4 tests (updated for iteration loop)
- `tests/test_smoke.py` — 4 tests (1 live, skipped without API keys)
- `tests/test_live_pipeline.py` — 3 tests (skipped without API keys)
- `tests/test_web_search.py` — 4 tests
- `tests/test_voice_agent.py` — 6 tests
- `tests/test_clips_agent.py` — 7 tests
- `tests/test_knowledge_store.py` — 18 tests (includes top_k tests)
- `tests/test_evaluator_agent.py` — 9 tests (includes ScriptScore tests)
- `tests/test_rewrite_flow.py` — 5 tests
- `tests/test_run_artifacts.py` — 13 tests (includes metadata verification)
- `tests/test_cli_flags.py` — 11 tests
- `tests/test_iteration_loop.py` — 7 tests
- `tests/test_scoring_selection.py` — 10 tests
- `tests/test_run_inspector.py` — 11 tests
- `tests/test_final_integration.py` — 11 tests

## Test status
159/159 passing (`.venv/bin/python -m pytest tests/ -v`)

## Sprint status
**Sprint 1 COMPLETE. Sprint 2 COMPLETE. Sprint 3 COMPLETE. Sprint 4 COMPLETE.**

**Sprint 5 COMPLETE — All 10 Tasks Done**

Active sprint file: `docs/tasks/active_sprint_05.md`
Spec: `docs/specs/content_engine_v5.md`

## Sprint 4 — Completed

All 8 tasks completed:
- Task 1: Knowledge store (data/knowledge/, save/load functions)
- Task 2: Evaluator agent (engine_agents/evaluator.py)
- Task 3: Feedback schema (ScriptFeedback in schemas/script.py)
- Task 4: Rewrite pass (script agent accepts feedback)
- Task 5: Coordinator update (evaluator + rewrite integration)
- Task 6: Source scoring (credibility_score, recency, bias_flag)
- Task 7: Structured logging (tools/logger.py)
- Task 8: Tests (all 86 passing)

## Sprint 5 — Task Status

### ✅ Task 1 COMPLETE — Run Artifacts System
- `tools/run_artifacts.py` created with `create_run_dir()`, `save_json()`, `save_text()`
- `flows/coordinator.py` updated to save all stage outputs
- `tests/test_run_artifacts.py` added (10 tests)
- Coordinator saves: metadata.json, research.json, outline.json, script_v1.txt, narration.txt, clips.json, feedback.json

### ✅ Task 2 COMPLETE — Run Metadata
- All required metadata fields verified (run_id, topic, angle, audience, timestamp, config, version)
- 3 additional tests added for metadata structure verification
- Tests verify: all spec fields present, auto-generated run_id, no artifacts when save_run=False

### ✅ Task 3 COMPLETE — CLI Upgrade
- `main.py` updated with Sprint 5 CLI flags:
  - `--save-run` (default true) — enable/disable run artifact saving
  - `--run-id` (optional) — specify custom run ID
  - `--max-iterations` (default 1) — max rewrite iterations
  - `--improvement-threshold` (default 0.2) — stop if improvement below threshold
  - `--no-rewrite` — skip rewrite pass
  - `--export` (json|txt|all) — export output format
  - `--inspect-run <run_id>` — inspect previous run
- `--save-run`, `--run-id` integrated with coordinator
- `inspect_run()` function implemented for viewing previous runs
- `tests/test_cli_flags.py` added (11 tests)

### ✅ Task 4 COMPLETE — Script Score Schema
- `ScriptScore` dataclass added to `schemas/script.py`:
  - `clarity_score: float` (0-10)
  - `argument_score: float` (0-10)
  - `emotional_impact: float` (0-10)
  - `factual_grounding: float` (0-10)
  - `overall_score: float` (0-10)
- 3 tests added to `tests/test_schemas.py` for defaults, populated, and partial values

### ✅ Task 5 COMPLETE — Evaluator Update
- `engine_agents/evaluator.py` updated:
  - `run_evaluator()` now returns `(ScriptFeedback, ScriptScore)` tuple
  - Prompt updated to request numeric scores for all 5 dimensions
  - Safe parsing with defaults for missing score fields
- `flows/coordinator.py` updated:
  - `EngineResult` now includes `score: Optional[ScriptScore]`
  - Saves `scores_v1.json` alongside feedback
- `tests/test_evaluator_agent.py` updated:
  - All existing tests updated for tuple unpacking
  - 2 new tests for ScriptScore verification

### ✅ Task 6 COMPLETE — Iteration Loop
- `flows/coordinator.py` updated with iteration loop:
  - Added `max_iterations` (default 1) and `improvement_threshold` (default 0.2) parameters
  - Loop: script → evaluate → score → rewrite (up to max_iterations)
  - Early stopping when improvement < threshold
  - Tracks best script by `overall_score`
  - Saves per-iteration artifacts: `script_v{i}.txt`, `scores_v{i}.json`, `feedback_v{i}.json`
  - Saves `best_script.txt` for the winning script
- `tests/test_iteration_loop.py` created with 7 tests:
  - Single iteration (default behavior)
  - Multiple iterations
  - Early stopping on low improvement
  - Continue on high improvement
  - Best script selection
  - Voice uses best script
  - Default is single iteration

### ✅ Task 7 COMPLETE — Output Selection
- `tools/scoring.py` created:
  - `select_best_script(candidates)` — selects script with highest overall_score
  - `ScoreWeights` dataclass — configurable weights for scoring dimensions
  - `calculate_weighted_score()` — computes weighted average across dimensions
  - Tie-breaking: first occurrence wins when scores are equal
  - Zero total weight falls back to overall_score
- `tests/test_scoring_selection.py` created with 10 tests:
  - Highest score wins selection
  - Single candidate handling
  - Tie-breaking (first occurrence)
  - Empty candidates raises ValueError
  - Varied score distributions
  - Weighted selection changes winner
  - Weighted score calculation
  - Zero weights fallback
  - Default weights are equal
  - Custom weights supported

### ✅ Task 8 COMPLETE — Knowledge Store Upgrade
- `tools/knowledge_store.py` enhanced:
  - `save_research_brief()` already accepts `topic` tag (was implemented in Sprint 4)
  - `load_relevant_knowledge()` now accepts `top_k` parameter (default 5)
  - Results sorted by relevance (word overlap match score)
  - Returns top_k most relevant briefs
- Integration already exists:
  - `engine_agents/outline.py` loads relevant knowledge after research
  - Prior knowledge included in outline agent context
- `tests/test_knowledge_store.py` updated with 4 new tests:
  - `top_k` limits results correctly
  - Default `top_k=5` behavior
  - Results sorted by relevance
  - `top_k` larger than available returns all matches

### ✅ Task 9 COMPLETE — Run Inspector Tests
- `tests/test_run_inspector.py` created with 11 tests:
  - `--inspect-run` CLI flag parsing
  - Skips topic validation in inspect mode
  - Valid run inspection with summary display
  - Score iterations display
  - Script path display
  - Non-existent run error handling
  - Missing metadata error handling
  - Missing optional fields show N/A
  - Full directory path display
  - Single iteration display (no scores)
  - Multiple score versions display
- Tests verify `_inspect_run()` function in `main.py`

### Task 10 COMPLETE — Final Integration
- `main.py` updated:
  - `--max-iterations` and `--improvement-threshold` now passed to coordinator
  - `--no-rewrite` flag forces `max_iterations=1`
  - `--export` flag exports results to txt/json files
- `tests/test_final_integration.py` created with 11 tests:
  - max_iterations with iteration loop
  - improvement_threshold with early stopping
  - --no-rewrite flag
  - Best script selection by overall_score
  - Voice uses best script
  - Artifact saving per iteration
  - CLI flag integration tests
- `README.md` updated:
  - v5 features documented
  - CLI reference table
  - Iteration loop explanation
  - All examples verified

### Sprint 5 Summary — COMPLETE
All 10 tasks complete with 159 tests passing:
- Task 1: Run Artifacts System
- Task 2: Run Metadata
- Task 3: CLI Upgrade
- Task 4: Script Score Schema
- Task 5: Evaluator Update
- Task 6: Iteration Loop
- Task 7: Output Selection
- Task 8: Knowledge Store Upgrade
- Task 9: Run Inspector Tests
- Task 10: Final Integration

## Next task
Sprint 6 planning (see `docs/specs/content_engine_v6.md` when ready)

## Blockers
None
