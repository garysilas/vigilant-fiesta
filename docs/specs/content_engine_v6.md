# Content Engine Spec v6

## Objective

Evolve the content engine from a functional multi-agent pipeline into a:

> **self-improving, observable, and replayable content system**

The system should:

- retain iteration history
- expose internal decision-making
- improve output quality over time
- support debugging and inspection at a deep level

---

## Core Theme (v6)

### Memory + Observability + Control

v5 built the engine  
v6 makes it *intelligent over time*

---

## System Overview (v6)

```text
Input 
  → Research 
  → Knowledge Store 
  → Outline 
  → Script 
  → [Evaluate → Score → Rewrite] × N 
  → Select Best 
  → Persist (Artifacts + Logs + History)
  → (Optional) Learn from Run
  → Voice 
  → Clips

### New Capabilities

#### 1. Iteration History Tracking

The engine must retain full history across iterations.

Add to EngineResult

```python
all_versions: List[FinalScript]
feedback_history: List[ScriptFeedback]
scores: List[ScriptScore]
```

Requirements

- Every iteration appends:
- generated script
- evaluator feedback
- score
- Order must be preserved
- Final selected script must exist in all_versions

### 2. Correct Output Selection (Tie-Breaker Fix)

#### Problem (v5)

Tie-breaking uses first occurrence (incorrect)

#### Requirement (v6)

If weighted scores are equal:

Select script with highest:

```text
1. factual_grounding
2. clarity (fallback)
```

#### Implementation

Update `select_best_script()` in:

```code
tools/scoring.py
```

### 3. Run Logging System (logs.json)

Each run must persist structured logs.

File

```code
data/runs/{run_id}/logs.json
```

Log Schema

```json
[
  {
    "stage": "script_generation",
    "iteration": 1,
    "event": "generated",
    "timestamp": "...",
    "metadata": {}
  },
  {
    "stage": "evaluation",
    "iteration": 1,
    "event": "scored",
    "score": {...},
    "feedback_summary": "...",
    "timestamp": "..."
  },
  {
    "stage": "selection",
    "event": "best_script_selected",
    "chosen_index": 2,
    "reason": "highest weighted score"
  }
]

#### Requirements
- Append-only
- Structured (JSON list)
- One file per run
- Written via tools/logger.py


### 4. Run Replay & Inspection Upgrade

Enhance run inspection to support full replay.

#### New Capabilities
- Load a run and display:
- all script versions
- score progression
- feedback progression
- Highlight:
- best version
- improvement trajectory

#### CLI Extension

```bash
python main.py --inspect-run <run_id> --show-history
```

#### Output

- iteration-by-iteration breakdown
- optional pretty formatting

### 5. Knowledge Store v2 (Learning Layer)

Extend knowledge storage beyond research.

#### New Storage Type

Store best-performing outputs:

```text
data/knowledge/scripts/
```

#### Stored Data

```json
{
  "topic": "...",
  "script": "...",
  "score": {...},
  "timestamp": "...",
  "tags": ["economics", "culture"]
}
```

#### Retrieval

Update:

```code
load_relevant_knowledge()
```

To optionally include:

- past high-performing scripts
- not just research briefs

#### Goal

Allow future runs to:

- reuse successful structures
- improve tone consistency

### 6. Evaluator Calibration (Control Layer)

Allow tuning of scoring weights.

#### Add

```python
class ScoreWeights:
    clarity: float
    emotional_impact: float
    factual_grounding: float
```

#### CLI Support

```bash
--weight-clarity 0.3
--weight-emotion 0.4
--weight-factual 0.3
```

#### Requirements

- Defaults must match v5 behavior
- User overrides must be respected
- Passed into:
- evaluator
- scoring system

### 7. Deterministic Structured Logging

Unify logging across all stages.

#### Required Fields

```json
{
  "stage": "...",
  "iteration": int | null,
  "event": "...",
  "timestamp": "...",
  "data": {}
}
```

#### Replace

- ad-hoc logs
- inconsistent messages

#### With

- structured logging via log() / log_stage()

### 8. Artifact Completeness

Each run directory must now contain:

```code
data/runs/{run_id}/

- research.json
- outline.json
- script_v1.txt
- script_v2.txt
- ...
- final_script.txt
- narration.txt
- clips.json
- scores.json
- feedback.json
- logs.json   ← NEW (required)
- metadata.json
```

### Non-Goals (v6)

Do NOT implement:

- UI (web or desktop)
- Notion integration
- Publishing automation
- Voice synthesis APIs
- Video rendering

### Definition of Done

v6 is complete when:

- EngineResult includes:
- all_versions
- feedback_history
- scores
- logs.json is created and populated
- tie-breaker uses factual grounding
- run inspection shows iteration history
- knowledge store includes scripts
- scoring weights configurable via CLI
- all tests pass (existing + new)

### Testing Requirements

#### New Tests

- iteration history integrity
- tie-breaker correctness
- logs.json creation + schema
- run replay output correctness
- knowledge store script persistence
- CLI weight overrides

#### Existing Tests

- must remain green
- no regression allowed

### Risks

#### Risk Mitigation

- Logging drift / inconsistency: enforce schema in logger
- Knowledge pollution: only store high-scoring scripts
- Overfitting to past outputs: limit retrieval count
- CLI complexity: keep defaults stable

### Sprint 6 Summary

This sprint transforms the engine into:

a system that remembers, explains itself, and improves over time

### System Evolution Path

- v5 → functional pipeline
- v6 → observable + learning system
- v7 → autonomous content engine (Notion + publishing)
- v8 → multi-channel distribution system
