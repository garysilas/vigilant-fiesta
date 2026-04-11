# Active Sprint 05 — Orchestration & Control

## Sprint Goal

Introduce run persistence, scoring, and iterative control to make the system inspectable and scalable.


## Task 1 — Run Artifacts System

Create:
- `data/runs/{run_id}/`

Implement helpers:
- `create_run_dir(run_id)`
- `save_json(path, data)`
- `save_text(path, text)`

Integrate into coordinator (write all stages).


## Task 2 — Run Metadata

Create metadata.json with:
- `run_id`, `topic`, `angle`, `audience`
- `timestamp`
- `config` (tone, style, flags)
- `version` = v5

## Task 3 — CLI Upgrade

Update main.py:
- `--run` (default true)
- `--run-id` (optional; else generate uuid)
- `--max-iterations` (default 1)
- `--improvement-threshold` (default 0.2)
- `--no-rewrite`
- `--export` (json|txt|all)
- `--inspect-run` <run_id>


## Task 4 — Script Score Schema

Add to `schemas/script.py`:

ScriptScore:
- `clarity_score`: float
- `argument_score`: float
- `emotional_impact`: float
- `factual_grounding`: float
- `overall_score`: float


## Task 5 — Evaluator Update

Update `run_evaluator()` to return:
- `ScriptFeedback`
- `ScriptScore`

Persist scores per iteration.


## Task 6 — Iteration Loop

Update coordinator:
- loop up to `max_iterations`
- compute improvement = `current.overall` - `prev.overall`
- break if improvement < threshold

Store:
- `script_v{i}.txt`
- `feedback_{i}.json`
- `scores_{i}.json`


## Task 7 — Output Selection

Implement selection logic:
- choose highest `overall_score`    
- return best + `all_versions` + `scores`


## Task 8 — Knowledge Store Upgrade

Enhance `load_relevant_knowledge()`:
- accept topic
- return top-k relevant entries

(Optional: simple keyword matching or embeddings later)


## Task 9 — Run Inspector

Implement CLI handler:
- load metadata
- load scores
- print summary
- print best script path


## Task 10 — Tests

Add:
- `test_run_artifacts.py`
- `test_iteration_loop.py`
- `test_scoring_selection.py`
- `test_cli_flags.py`
- `test_run_inspector.py`

## Completion Criteria
- Runs persist all artifacts
- Iteration loop works with stopping condition
- Scores generated and stored
- Best script selected correctly
- CLI flags functional
- Inspector returns correct summary
- All tests passing

## Status

Sprint 5 — READY TO START