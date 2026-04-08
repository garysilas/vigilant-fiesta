# Content Engine Spec v1

## Objective
Build a Python content engine using the OpenAI Agents SDK that generates:
- long-form commentary scripts
- narration-ready revisions
- short-form clips derived from the script

## Primary user outcome
Given a topic and optional angle, the system should produce a clear, compelling script with a strong hook, coherent structure, and culturally aware tone.

## v1 scope
Implement:
- coordinator agent
- research agent
- outline agent
- script agent

Do not implement yet:
- UI
- Notion sync
- publishing automation
- narration generation
- clip extraction from video
- scheduling

## Inputs
- topic: required
- angle: optional
- audience: optional
- red_lines: optional
- must_hits: optional

## Outputs
v1 must return:
1. research brief
2. commentary outline
3. final script

## Architecture
Pattern: manager orchestration

Coordinator controls the flow:
1. research
2. outline
3. script

Sub-agents do not call each other directly unless later specified.

## Agent responsibilities

### Research Agent
Produces:
- key facts
- key tensions
- relevant examples
- caveats
- source notes

### Outline Agent
Produces:
- hook
- thesis
- section-by-section argument
- emotional progression
- closing idea

### Script Agent
Produces:
- narration-ready script
- coherent pacing
- strong opening
- strong closing

## Constraints
- Python only
- OpenAI Agents SDK
- minimal abstractions
- typed outputs where useful
- each agent independently testable
- no hidden architectural changes outside the spec

## Success criteria
The system is successful when:
- one command generates research, outline, and script
- flow is deterministic enough to test
- agent work stays within current task boundaries

## First implementation target
Build the CLI workflow:
python main.py --topic "Why young men are struggling financially"