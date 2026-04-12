# Current State

## Last Updated

2026-04-12 — Project recovery completed and Sprint 6 rebuilt from current code + spec.

## Recovery Report

### 1. System Overview

#### Tech Stack

- Python 3.11+
- `openai-agents` SDK + `tavily-python`
- `python-dotenv` for env loading
- `pytest` + `pytest-asyncio` test stack

#### Architecture Overview

- Frontend: none (CLI-only application)
- Backend: Python orchestration pipeline in `flows/coordinator.py`
- Database: none (filesystem persistence in `data/knowledge/` and `data/runs/{run_id}/`)
- Auth: API keys via environment variables (`OPENAI_API_KEY`, `TAVILY_API_KEY`)

Pipeline (current):

```text
Input → Research → Knowledge Store → Outline → Script → [Evaluate → Score → Rewrite]×N → Select Best → Voice → Clips → Persist Artifacts
```

#### Key Modules

- `main.py` — CLI entrypoint, generation mode, export mode, and base run inspection
- `flows/coordinator.py` — end-to-end orchestration and artifact persistence
- `engine_agents/` — research, outline, script, evaluator, voice, clips agents
- `schemas/` — typed dataclasses for research, outline, script, feedback, and scores
- `tools/knowledge_store.py` — research brief persistence/retrieval
- `tools/scoring.py` — weighted scoring utilities and script selection helper
- `tools/logger.py` — structured console log primitives (`log`, `log_stage`)
- `tools/run_artifacts.py` — filesystem helpers for run outputs

### 2. Feature Status

Spec baseline used for recovery: `docs/spec.md` / `docs/specs/content_engine_v6.md`.

| Capability (v6) | Status | Notes |
| --- | --- | --- |
| 1. Iteration history tracking (`all_versions`, `feedback_history`, `scores`) | Partially implemented | Iteration files are persisted (`script_vN`, `feedback_vN`, `scores_vN`) but `EngineResult` does not expose full history lists. |
| 2. Tie-breaker fix (`factual_grounding`, then `clarity`) | Missing | `select_best_script()` keeps first occurrence on ties; coordinator also selects by highest `overall_score` directly. |
| 3. Run logging (`logs.json`) | Missing | Logging prints JSON to stdout but no append-only run log file is written. |
| 4. Run replay/inspection (`--show-history`) | Partially implemented | `--inspect-run` exists, but no history replay view, no feedback progression, no best-version highlighting. |
| 5. Knowledge Store v2 (script learning layer) | Missing | Knowledge store persists `ResearchBrief` only; no `data/knowledge/scripts/` flow. |
| 6. Evaluator calibration via CLI weights | Partially implemented | `ScoreWeights` exists in `tools/scoring.py`, but CLI flags and coordinator wiring are not implemented. |
| 7. Deterministic structured logging schema | Partially implemented | Logger has `stage/event/duration/metadata`; required schema fields (`timestamp`, `iteration`, `data`) are not consistently enforced/persisted. |
| 8. Artifact completeness (including `logs.json`) | Partially implemented | Core artifacts are saved; spec-required unified artifacts (`logs.json`, `final_script.txt`, aggregated score/feedback files) are incomplete. |

#### Critical Issues

- Selection logic does not meet v6 tie-breaking rules.
- Iteration history is not exposed through `EngineResult`, limiting observability and replay.
- Run logs are not persisted, so debugging depends on ephemeral stdout.
- Replay tooling is shallow and cannot explain improvement trajectory.
- Knowledge layer cannot learn from best-performing scripts yet.

### 3. Spec Alignment

#### Matches

- Multi-agent pipeline and rewrite loop are operational.
- Source scoring fields exist in `Source` schema.
- Evaluator returns both `ScriptFeedback` and `ScriptScore`.
- Run artifacts and metadata are persisted per run.
- Base run inspection (`--inspect-run`) works for metadata + score files.

#### Gaps

- `EngineResult` missing full iteration history fields required in v6.
- Tie-breaker behavior in selection does not follow v6.
- No `logs.json` persistence and incomplete deterministic logging schema.
- CLI lacks `--show-history` and scoring-weight override flags.
- Knowledge store lacks script persistence and retrieval path.

#### Deviations

- Current scoring utility defaults to first-win tie behavior (v6 requires factual/clarity tie-break).
- Artifact naming differs from v6 expectation (`best_script.txt` exists; `final_script.txt` expected).
- `active_sprint_04.md` still states "READY TO START" while code has progressed beyond Sprint 4, creating documentation drift.

#### Overbuild Areas

- No material overbuild detected; primary issue is under-delivery versus v6 requirements.

### 4. Active Sprint (Reconstructed)

Sprint objective: close the minimum v6 gaps required for an observable, replayable, learning-capable MVP.

| # | Task | Objective | Expected Outcome |
| --- | --- | --- | --- |
| 1 | Add iteration history + correct selection | Extend `EngineResult` with `all_versions`, `feedback_history`, `scores`; route best selection through v6-compliant tie-breaker logic. | Full per-iteration state is preserved and final selection is spec-correct. |
| 2 | Implement persisted run logs | Add append-only structured events and write `data/runs/{run_id}/logs.json` with deterministic schema. | Each run is auditable without relying on console output. |
| 3 | Upgrade run replay CLI | Add `--show-history` and print script/feedback/score progression with best-version marker. | Operators can replay decisions and improvement trajectory from artifacts. |
| 4 | Add Knowledge Store v2 scripts layer | Persist high-scoring scripts to `data/knowledge/scripts/` and optionally retrieve for future runs. | System begins reusing prior successful outputs, not only research briefs. |
| 5 | Expose scoring weight controls in CLI | Add weight flags and wire through coordinator/scoring path with stable defaults. | Users can tune scoring policy without changing code. |

Execution policy: complete tasks in order; keep each task shippable with tests before moving on.

### 5. Risks & Blockers

#### Risks

- `flows/coordinator.py` is high-centrality; regressions can break end-to-end flow.
- Logging/schema drift risk if event shape is not enforced in one place.
- Existing tests assert current tie behavior; they must be deliberately updated with spec-aware expectations.
- Live/integration tests can be noisy and should not gate deterministic unit checks.

#### Blockers

- No hard blockers identified.
- Main prerequisite is disciplined sequencing (selection/history before replay/logging polish).

#### Suggested Fixes

- Introduce a single typed log event contract in `tools/logger.py`.
- Add focused tests per v6 requirement before broader integration checks.
- Keep coordinator changes incremental and covered by `tests/test_iteration_loop.py`, `tests/test_scoring_selection.py`, and new replay/log tests.

### 6. Cleanup Opportunities

#### Code Smells

- Selection logic is duplicated conceptually (coordinator vs scoring utility).
- Artifact filename conventions are inconsistent (`best_script.txt` vs spec `final_script.txt`).
- Documentation drift exists across sprint tracking files.

#### Safe Refactor Suggestions

- Centralize script-selection policy in `tools/scoring.py` and call it from coordinator.
- Centralize artifact filename constants in `tools/run_artifacts.py`.
- Keep sprint/status docs synchronized with actual implementation state during each completed task.

## Validation Snapshot

- Full test suite result: `158 passed` via `.venv/bin/python -m pytest tests -q`.
