# Content Engine Spec v5

## Objective

Evolve the engine into a controllable, inspectable, and scalable content system with persistent run artifacts, scoring, and iterative optimization.

The system should:
- Persist every run (artifacts + metadata)
- Iterate with measurable improvements
- Score and select best outputs
- Enable inspection, comparison, and reuse

## System Evolution

v1 — Generation Pipeline (Completed)

v2 — Grounding (Completed)

v3 — Production Output (Completed)

v4 — Intelligence Layer (Completed)

v5 — Orchestration & Control (Current)

Introduce:
- Run artifacts + metadata
- Iterative optimization loop (N passes)
- Script scoring + selection
- CLI controls for runs and exports
- Run inspection and comparison

    ⸻

## New Capabilities (v5)

### 1. Run Artifacts

Persist per execution:

`/data/runs/{run_id}/`
- `metadata.json`
- `research.json`
- `outline.json`
- `script_v1.txt`
- `script_v2.txt` (…N)
- `narration.txt`
- `clips.json`
- `feedback.json` (…N)
- `scores.json` (…N)
- `logs.json`

Goals:
- Reproducibility
- Debugging
- Comparison across runs

### 2. Run Metadata

`metadata.json`:
- `run_id`
- `topic`, `angle`, `audience`
- `timestamp`
- `config` (tone, style, flags)
- `version` (engine spec version)

### 3. Iterative Optimization Loop

Replace single rewrite with controlled loop:

Script → Evaluate → Score → Rewrite (repeat up to N)

Stop when:
- `max_iterations` reached
- score improvement < threshold

### 4. Script Scoring

Extend evaluator to output ScriptScore:
- `clarity_score` (0–10)
- `argument_score` (0–10)
- `emotional_impact` (0–10)
- `factual_grounding` (0–10)
- `overall_score` (0–10)

Store per iteration.

### 5. Output Selection

Coordinator returns:
- `best_script`
- `all_versions`
- `scores`
- `feedback_history`

Selection:
- highest `overall_score` (tie-breaker: `factual_grounding`)

### 6. CLI Controls

Add flags:
- `–save-run true|false`
- `–run-id `
- `–max-iterations N`
- `–improvement-threshold float`
- `–no-rewrite`
- `–export json|txt|all`
- `–inspect-run <run_id>`

### 7. Knowledge Store Upgrade

Enhance retrieval:
- tag by topic/theme
- store embeddings or keywords (lightweight ok)
- top-k relevant retrieval

### 8. Run Inspection

CLI:

```bash
python main.py –inspect-run <run_id>
```

Outputs:
- metadata summary
- scores per version
- best script
- sources used

## Updated Pipeline (v5)

```mermaid
Input
↓
Research (tools)
↓
Knowledge Store (read/write)
↓
Outline
↓
Script (v1)
↓
[ Loop: Evaluate → Score → Rewrite ] x N
↓
Select Best Script
↓
Voice
↓
Clips
↓
Persist Artifacts
```

## Non-Goals (Still)
- UI (separate sprint)
- Notion sync
- Publishing automation
- Model fine-tuning
