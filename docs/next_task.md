# Next Task

## Sprint 6 — Task 1

### Status

Ready to execute.

### Task

Add iteration history tracking and v6-compliant best-script selection.

### Scope

- Extend `EngineResult` with:
  - `all_versions: list[FinalScript]`
  - `feedback_history: list[ScriptFeedback]`
  - `scores: list[ScriptScore]`
- Ensure coordinator appends script/feedback/score per iteration in order.
- Update selection to use `tools/scoring.select_best_script()` with v6 tie-break rule (`factual_grounding`, then `clarity`).
- Keep existing behavior stable for non-tie scenarios.

### Acceptance Criteria

- `EngineResult` exposes complete iteration history.
- Final selected script is included in `all_versions`.
- Tie cases select by `factual_grounding`, then `clarity`.
- Relevant tests are added/updated and green.
