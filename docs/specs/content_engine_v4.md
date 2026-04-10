# Content Engine Spec v4

## Objective

Evolve the content engine from a linear generation pipeline into a learning, self-improving content system.

The system should:
- Generate grounded, high-quality scripts
- Improve outputs through evaluation loops
- Accumulate knowledge over time
- Reuse past research and insights

## System Evolution

v1 — Generation Pipeline (Completed)
- Basic multi-agent pipeline
- Research → Outline → Script

v2 — Grounding (Completed)
- Tool-augmented research
- Source tracking
- Reduced hallucination

v3 — Production Output (Completed)
- Voice agent
- Clips agent
- Style guide
- CLI expansion

v4 — Intelligence Layer (Current)

Introduce:
- Persistent knowledge storage
- Evaluation + feedback loop
- Script refinement pass
- Source quality scoring


## New Capabilities (v4)

### 1. Knowledge Store

Persist:
- ResearchBrief outputs
- Source summaries
- Topic clusters

Goals:
- Avoid redundant research
- Enable context accumulation
- Improve future outputs

### 2. Evaluator Agent

New agent that analyzes scripts for:
- Clarity
- Argument strength
- Emotional impact
- Factual grounding

Output:

ScriptFeedback:
- weaknesses
- missing angles
- improvement suggestions

### 3. Rewrite Loop

Pipeline becomes:

Research → Outline → Script → Evaluate → Rewrite

Goals:
- Improve script quality automatically
- Introduce iteration

### 4. Source Scoring

Extend Source schema with:
- credibility_score
- recency
- bias_flag

Goals:
- Improve research quality
- Prioritize stronger sources

### 5. Structured Logging

Replace print logs with structured logs:
- stage
- duration
- inputs/outputs summary

Goals:
- observability
- debugging
- future analytics

## Updated Pipeline

```mermaid
Input
↓
Research (with tools)
↓
Knowledge Store (read/write)
↓
Outline
↓
Script
↓
Evaluator
↓
Rewrite (optional pass)
↓
Voice
↓
Clips
```

## Non-Goals (Still)
- UI
- Notion integration
- Publishing automation
- Model fine-tuning
