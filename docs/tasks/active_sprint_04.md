# Active Sprint 04 — Intelligence Layer

## Sprint Goal

Transform the engine from a static generator into a self-improving system.

## Task 1 — Knowledge Store

Create:
- `data/knowledge/`

Implement:
- `save_research_brief()`
- `load_relevant_knowledge(topic)`

Integrate into:
- research agent (write)
- outline agent (read)


## Task 2 — Evaluator Agent

Create:
- `engine_agents/evaluator.py`

Function:
- `run_evaluator(script: FinalScript) -> ScriptFeedback`


## Task 3 — Feedback Schema

Add to schemas/script.py:

ScriptFeedback:
- `weaknesses: list[str]`
- `missing_angles: list[str]`
- `improvement_suggestions: list[str]`


## Task 4 — Rewrite Pass

Update script agent:
- accept optional feedback
- produce improved version


## Task 5 — Coordinator Update

Update flow:
- call evaluator after script
- optionally trigger rewrite


## Task 6 — Source Scoring

Update Source schema:
- `credibility_score: float`
- `recency: str`
- `bias_flag: str`

Update research agent to populate fields


## Task 7 — Structured Logging

Replace prints with structured logs:
- `stage`
- `duration`
- `metadata`


## Task 8 — Tests

Add:
    - `test_evaluator_agent.py`
- `test_rewrite_flow.py`
- `test_knowledge_store.py`


## Completion Criteria
- Evaluator agent integrated
- Rewrite loop functioning
- Knowledge store persists and retrieves data
- Source scoring implemented
- All tests passing


## Status

Sprint 4 — READY TO START