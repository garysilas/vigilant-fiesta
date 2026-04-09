# Sprint 2 — Grounding & Tooling

## Objective

Transform the content engine from a closed LLM pipeline into a tool-augmented, reality-grounded system that produces credible, source-backed outputs.

## Success Criteria

- Research agent uses at least one real external data tool
- Research output includes structured sources (title, url, summary)
- Sources propagate through outline and script generation
- End-to-end pipeline produces fact-grounded content
- At least one live (non-mocked) pipeline test passes
- CLI supports extended arguments (style, tone, etc.)


## Non-Goals
- No UI work
- No memory systems
- No database integration
- No multi-agent autonomy upgrades beyond tooling
- No optimization of prompts beyond necessity

## Architecture Changes

### 1. Introduce Tool Layer

Create a real tools package:

```bash
tools/
  web_search.py
```

This module will expose callable functions for agents.

## Research Agent Upgrade

Convert research agent from:
- pure LLM call

To:
- tool-augmented agent

Capabilities:
- perform web search
- extract relevant information
- return structured sources

## Schema Expansion

New: Source Object

```python
class Source:
    title: str
    url: str
    summary: str
```
Update: ResearchBrief

```python
class ResearchBrief:
    topic: str
    insights: List[str]
    sources: List[Source]
```

## Pipeline Data Flow

Ensure the following flow:


```mermaid
ResearchBrief (with sources)
    ↓
Outline Agent (references sources)
    ↓
Script Agent (uses grounded info)
```

Agents should explicitly incorporate:
- facts from sources
- attribution where appropriate

## CLI Improvements

Update main.py to support:

```bash
--topic
--tone
--style
--length (optional)
```

Example:
```bash
python main.py --topic "Black wealth gap" --tone "serious" --style "documentary"
```


## Logging / Observability (Basic)

Add lightweight logging:
- agent start/finish messages
- tool usage indicators

Example:
```
[Research Agent] Starting...
[Tool:web_search] Querying...
[Research Agent] Completed
```


---
## Task Breakdown

### Task 1 — Implement Web Search Tool

Create:
```bash
tools/web_search.py
```

Requirements:
- Accept query string
- Return structured results (title, url, snippet)
- Keep implementation simple and swappable

### Task 2 — Integrate Tool into Research Agent

Update:

```bash
engine_agents/research.py
```

Requirements:
- call web_search tool
- synthesize results into ResearchBrief
- extract:
  - key insights
  - source summaries

### Task 3 — Update Schemas

Modify:

```bash
schemas/research.py
```

Add:
- Source class
- sources field in ResearchBrief

Update any dependent code accordingly

### Task 4 — Update Outline Agent

Modify:

```bash
engine_agents/outline.py
```

Requirements:
- accept ResearchBrief with sources
- incorporate facts into outline sections
- optionally tag sections with source references

### Task 5 — Update Script Agent

Modify:

```bash
engine_agents/script.py
```

Requirements:
- generate script using grounded insights
- maintain narrative tone (Black Street Journal style)
- avoid hallucinated claims

### Task 6 — CLI Enhancement

Modify:

```bash
main.py
```
Add argument parsing:
- topic (required)
- tone (optional)
- style (optional)

Pass arguments through coordinator → agents

### Task 7 — Add Live Pipeline Test

Create:

```bash
tests/test_live_pipeline.py
```

Requirements:
- runs full pipeline with real API/tool
- skipped if API key missing
- validates:
- sources exist
- script is non-empty

### Task 8 — Add Logging

Add simple logging across:
- coordinator
- agents
- tools

No external logging library required (keep simple)

##	Definition of Done
- All tasks completed
- All existing tests pass
- New live test passes (or skips correctly)
- CLI works with new arguments
- Research output includes real sources
- Pipeline produces coherent, grounded script

##	 Risks
- Tool API instability
- Rate limits
- Poor search result quality

Mitigation:
- keep tool abstraction simple
- allow easy swapping of providers

##	Future Considerations (DO NOT IMPLEMENT IN THIS SPRINT)
- Multi-tool system (search + scraping + summarization)
- Citation formatting in final script
- Memory layer (Notion or local DB)
- Autonomous planning agents
- UI layer

##	Notes

This sprint is the transition from:

“LLM demo” → “Real system”

Do not over-engineer.

Focus on:
- correctness
- simplicity
- real data integration

##	End of Sprint 2 Spec