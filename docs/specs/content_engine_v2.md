# Content Engine Spec v2

## Objective

Build a Python content engine using the OpenAI Agents SDK that generates:
- long-form commentary scripts
- narration-ready revisions (future)
- short-form clips derived from the script (future)

The system must produce fact-grounded, culturally aware commentary using real-world data.


## Primary User Outcome

Given a topic and optional angle, the system produces a:
- compelling, structured script
- grounded in real information
- with a strong hook, clear argument, and emotional progression


## v1 Scope (Completed)
- coordinator agent
- research agent (LLM-based)
- outline agent
- script agent
- CLI entry point
- typed outputs
- test coverage


## v2 Scope (Current Focus — Grounding)

Enhance the system to:
- use external tools for research
- produce structured, traceable sources
- propagate real data through the pipeline
- reduce hallucination
- improve factual reliability


##  Non-Goals (Still Out of Scope)
- UI
- Notion sync
- publishing automation
- narration generation
- clip extraction from video
- scheduling
- long-term memory


## Inputs
- `topic`: required
- `angle`: optional
- `audience`: optional
- `red_lines`: optional
- `must_hits`: optional
- `tone`: optional (NEW)
- `style`: optional (NEW)


## Outputs

The system must return:
1. Research Brief
- insights
- tensions
- examples
- caveats
- sources (NEW)
2. Commentary Outline
- hook
- thesis
- structured argument
- emotional progression
- closing idea
3.	Final Script
- narration-ready
- grounded in research
- coherent pacing
- strong opening and closing


## Architecture

Pattern: Manager Orchestration

Coordinator controls:
1.	research
2.	outline
3.	script

Rules:
- Sub-agents do NOT call each other directly
- Coordinator owns execution order
- Data flows strictly forward


## Tooling Layer (NEW)

Introduce a tools system:

```code
tools/
  web_search.py
```

Purpose:
- give agents access to real-world data
- enable grounded outputs

Initial capability:
- web search (required)

Future:
- scraping
- summarization tools
- APIs


## Agent Responsibilities (Updated)

### Research Agent (Upgraded)

Produces:
- key facts
- key tensions
- relevant examples
- caveats
- sources (title, url, summary)

Requirements:
- must use tools when available
- must avoid unsupported claims
- must structure outputs for downstream agents


### Outline Agent

Produces:
- hook
- thesis
- section-by-section argument
- emotional progression
- closing idea

Requirements:
- must incorporate research insights
- should reflect real-world context
- must not invent unsupported claims


### Script Agent

Produces:
- narration-ready script
- coherent pacing
- strong opening
- strong closing

Requirements:
- must use grounded insights
- maintain tone and style consistency
- avoid hallucinated facts


## Data Contracts

### ResearchBrief (Updated)
```python
class Source:
    title: str
    url: str
    summary: str

class ResearchBrief:
    topic: str
    insights: List[str]
    sources: List[Source]
```


## Constraints
- Python only
- OpenAI Agents SDK
- minimal abstractions
- typed outputs where useful
- each agent independently testable
- no hidden architectural changes outside the spec
- tools must be modular and swappable


## Success Criteria (Updated)

The system is successful when:
- one command generates research, outline, and script
- research includes real sources
- script reflects grounded information
- flow is deterministic enough to test
- agent work stays within task boundaries
- tool integration works reliably


## CLI Interface (Updated)

```bash
python main.py \
  --topic "Why young men are struggling financially" \
  --tone "serious" \
  --style "documentary"
```

## System Evolution Path
- v1 → structure
- v2 → grounding (current)
- v3 → memory + persistence
- v4 → automation + publishing
- v5 → full content engine (video + voice)


## First Implementation Target (v2)
- implement `web_search` tool
- integrate into research agent
- update `ResearchBrief` schema
- propagate sources through pipeline


## Notes

This system is transitioning from:

LLM pipeline → real-world content engine

Do not over-engineer.

Focus on:
- real data
- clean flow
- reliability

⸻

End of Spec

