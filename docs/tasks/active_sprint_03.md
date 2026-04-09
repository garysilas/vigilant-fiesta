# Sprint 3 — Voice & Output Quality (v3a)

## Status
ACTIVE

## Goal

Upgrade the content engine from:
"technically correct outputs"

→ to:

"publishable, high-quality, voice-driven content"

This sprint focuses on:
- writing quality
- narrative strength
- voice consistency
- output expansion (narration + clips)

DO NOT implement long-term memory yet.

---

## Success Criteria

The system is successful when:

- scripts have strong hooks
- narrative flow feels intentional and engaging
- tone/style is consistent across the entire script
- narration version sounds natural when read aloud
- clips can stand alone as short-form content
- outputs feel publishable without heavy editing

---

## Constraints

- Do NOT change core architecture
- Do NOT introduce agent-to-agent calls
- Keep coordinator orchestration intact
- Maintain deterministic pipeline behavior
- All new agents must be independently testable

---

## Tasks

---

### Task 1 — Create Writing Style Guide

#### File:
`docs/style_guide.md`

#### Purpose:
Define a reusable voice system for all future outputs

#### Must include:

- Tone definition
  - serious
  - sharp
  - culturally aware

- Sentence style
  - controlled pacing
  - varied sentence length
  - deliberate pauses

- Hook patterns
  - contradiction
  - uncomfortable truth
  - reframing common belief

- Narrative principles
  - tension → breakdown → escalation → message

- Banned patterns
  - generic filler phrases
  - vague statements
  - unsupported claims

#### Acceptance Criteria:
- File exists
- Script agent can reference it in prompt

---

### Task 2 — Upgrade Script Agent (Narrative Quality)

#### File:
`engine_agents/script.py`

#### Changes:

1. Improve prompt to enforce:
   - strong opening hook (first 2–3 lines)
   - clear thesis
   - structured narrative flow:
     - hook
     - tension
     - breakdown
     - escalation
     - conclusion

2. Require:
   - emotional progression
   - grounded references to research
   - elimination of generic phrasing

3. Inject:
   - tone
   - style
   - (NEW) style guide content

#### Acceptance Criteria:
- Output is noticeably more engaging
- Opening hook is strong and specific
- Script reads like commentary, not summary

---

### Task 3 — Add Voice Agent (Narration Layer)

#### File:
`engine_agents/voice.py`

#### Function:
`run_voice(script: FinalScript, tone: str, style: str) -> NarrationScript`

#### Purpose:
Convert script into narration-ready format

#### Responsibilities:

- Add:
  - pauses
  - emphasis markers
  - sentence rhythm adjustments

- Improve:
  - readability aloud
  - pacing

#### Output:
`NarrationScript`

#### Acceptance Criteria:
- Output reads naturally when spoken
- Sentences are not overly dense
- Clear cadence is present

---

### Task 4 — Add Clips Agent (Short-Form Extraction)

#### File:
`engine_agents/clips.py`

#### Function:
`run_clips(script: FinalScript) -> List[Clip]`

#### Responsibilities:

- Extract 3–5 clips from script
- Each clip must include:
  - hook
  - body
  - closing/punchline

#### Rules:

- Must be self-contained
- Must make sense without full script
- Should feel like TikTok / Shorts content

#### Acceptance Criteria:
- At least 3 clips generated
- Each clip is independently understandable
- Hooks are attention-grabbing

---

### Task 5 — Update Coordinator

#### File:
`flows/coordinator.py`

#### Changes:

Extend pipeline:

```python
research → outline → script → voice → clips
```

Requirements:
- Maintain strict ordering
- Pass tone/style through all steps
- Return extended result:

class EngineResult:
    research: ResearchBrief
    outline: CommentaryOutline
    script: FinalScript
    narration: NarrationScript
    clips: List[Clip]

Acceptance Criteria:
- Full pipeline runs without breaking existing steps
- New outputs included in result

---

### Task 6 — Extend CLI Interface

#### File:
`main.py`

Add:

```bash
--output_mode draft | narration | clips | all
```

Behavior:
- draft → script only
- narration → narration output
- clips → clips only
- all → everything

Acceptance Criteria:
- CLI correctly switches output modes
- No breaking changes to existing args

---

### Task 7 — Add Schemas

#### File:
`schemas/script.py` (update or new files)

Add:

```python
class NarrationScript:
    text: str

class Clip:
    hook: str
    body: str
    closing: str

```

Acceptance Criteria:
- Types are validated
- Tests pass

---

### Task 8 — Add Tests

#### New tests:
- tests/test_voice_agent.py
- tests/test_clips_agent.py

Must validate:
Voice Agent:
- output is non-empty
- output differs from original script
- preserves meaning

Clips Agent:
- returns 3–5 clips
- each clip has hook/body/closing
- clips are non-empty

Acceptance Criteria:
- All tests pass
- No regression in existing tests

---

Out of Scope (Strict)
- memory system
- database
- Notion integration
- UI
- scheduling
- publishing automation

---

Definition of Done
- All tasks implemented
- All tests passing
- CLI produces:
  - strong script
  - narration version
  - short-form clips
  - Output quality is noticeably improved

---

### Next Sprint Preview (DO NOT START)

Sprint 4 will introduce:
- lightweight memory layer
- reusable voice profiles
- persistent style injection

---

### End of Sprint 3
