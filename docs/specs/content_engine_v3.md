# Content Engine Spec v3

## Objective

Build a Python content engine using the OpenAI Agents SDK that generates:
- long-form commentary scripts
- narration-ready revisions
- short-form clips derived from scripts

The system must produce:
- fact-grounded
- culturally aware
- emotionally compelling content

---

## Primary User Outcome

Given a topic and optional angle, the system produces:
	•	a compelling, structured script
	•	grounded in real information
	•	with a strong hook, clear argument, and emotional progression
	•	written in a distinct, reusable voice

---

## Completed Scope

### v1 — Structure ✅
- coordinator agent
- research agent
- outline agent
- script agent
- CLI entry
- typed outputs
- test coverage

v2 — Grounding ✅
- web_search tool integration
- structured sources
- source propagation across pipeline
- reduced hallucination
- improved factual reliability

---

## v3 Scope (NEW — Controlled Memory + Voice System)

Theme: Identity + Reusability

Enhance the system to:

1. Introduce persistent context (LIGHTWEIGHT MEMORY)
- store reusable writing preferences
- store past successful outputs (optional)
- store style definitions

2. Introduce a formal voice system
- codify tone + style into reusable assets
- ensure consistency across outputs

3. Improve output quality
- stronger hooks
- clearer narrative flow
- better pacing and emphasis

4. Enable multi-output generation
- long-form script
- narration-ready version
- short-form breakdowns

---

### ⚠️ Important Constraint (NEW)

Memory is:

Assistive, not autonomous

- No long-term agent decision-making
- No hidden state mutation
- No black-box behavior

Memory is read-only context injection

---

Non-Goals (Still Out of Scope)
- UI
- Notion sync
- publishing automation
- scheduling
- full video generation
- autonomous agent loops

---

## Inputs (Updated)

```text
topic: required  
angle: optional  
audience: optional  
red_lines: optional  
must_hits: optional  
tone: optional  
style: optional  

# NEW
voice_profile: optional  
output_mode: optional (draft | narration | clips | all)
```
---

## Outputs (Updated)

The system must return:

1. Research Brief
- insights
- tensions
- examples
- caveats
- sources

2. Commentary Outline
- hook
- thesis
- structured argument
- emotional progression
- closing idea

3. Final Script (Draft)
- strong hook
- structured narrative
- grounded content

4. Narration Script (NEW)
- pacing optimized
- pauses + emphasis
- spoken-word ready

5. Short-Form Clips (NEW)
- 3–5 segments
- each with:
- hook
- punchline
- standalone clarity

---

## Architecture (Updated)

Pattern: Manager Orchestration (Strict)

Coordinator controls:
- research
- outline
- script
- voice (NEW)
- clips (NEW)

---

## Rules (Unchanged but Reinforced)
- Agents do NOT call each other
- Coordinator owns execution
- Data flows strictly forward
- No hidden state

---

## 🧠 Memory Layer (NEW — Lightweight)

```text
memory/
  voice_profiles/
  style_guides/
  past_outputs/
```

Purpose
- inject consistent tone + identity
- avoid rewriting style every run

Example

```json
{
  "voice": "Black Street Journal",
  "tone": "serious, sharp, culturally aware",
  "cadence": "measured, building tension"
}
```


---
## 🛠 Tooling Layer (Expanded)

```text
tools/
  web_search.py
```

Future-ready (not required yet):
- summarization tool
- content extraction
- transcript ingestion

---

## Agent Responsibilities (v3)

### Research Agent ✅ (unchanged)
- uses tools
- returns structured sources
- avoids hallucination

---

### Outline Agent (UPGRADED)
- stronger hooks
- clearer emotional progression
- tighter argument flow

---


### Script Agent (UPGRADED)

Now responsible for:
- narrative quality
- pacing
- emotional buildup

Must:
- reflect real-world grounding
- respect tone + style
- produce engaging storytelling

---

## Voice Agent (NEW)
```code
engine_agents/voice.py
```

Purpose:
- convert script → narration-ready version

Adds:
- pauses
- emphasis
- rhythm

---

## Clips Agent (NEW)

```code
engine_agents/clips.py
```

Purpose:
- break script into short-form segments

Outputs:
- 3–5 clips
- each self-contained

---

## Data Contracts (Updated)

### ResearchBrief

(unchanged from v2)

---

### FinalScript

```python
class FinalScript:
    sections: List[str]

    def full_text(self) -> str:
        ...
```

---
### NarrationScript (NEW)

```python
class NarrationScript:
    text: str
```

---
### Clip (NEW)

```python
class Clip:
    hook: str
    body: str
    closing: str
```

---
## CLI Interface (v3)

```bash
python main.py \
  --topic "Why young men are struggling financially" \
  --tone "serious" \
  --style "documentary" \
  --output_mode "all"
```

---
## Success Criteria (v3)

The system is successful when:
- outputs are fact-grounded
- scripts feel publishable
- tone is consistent across runs
- hooks are compelling
- narration flows naturally
- clips can stand alone
- memory improves consistency without breaking determinism
