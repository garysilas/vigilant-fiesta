import json
import os
from pathlib import Path

from agents import Agent, Runner
from dotenv import load_dotenv

from schemas.outline import CommentaryOutline
from schemas.script import FinalScript, ScriptFeedback
from tools.logger import log_stage

load_dotenv()

SCRIPT_INSTRUCTIONS = """
You are a script agent. Given a topic and a grounded commentary outline, write a compelling, publishable commentary script.

## WRITING STANDARDS

**Tone:** Serious, sharp, culturally aware
- Treat the subject with gravity and respect
- Use precise, incisive language
- Acknowledge social and cultural context

**Sentence Style:**
- Controlled pacing: match rhythm to emotional moment
- Varied sentence length: alternate punchy and flowing constructions
- Deliberate pauses: use punctuation to create breathing room (em-dashes, ellipses)

**Hook Patterns (use one for opening):**
- Contradiction: statement that seems impossible or opposed to common sense
- Uncomfortable Truth: something people know but rarely say aloud
- Reframing Common Belief: flip a widely accepted idea

**Narrative Structure:**
Follow this exact flow:
1. HOOK (first 2-3 lines): Grab attention immediately using one of the hook patterns
2. TENSION: Establish what's at stake, introduce the conflict or problem
3. BREAKDOWN: Examine the mechanics, reveal hidden dynamics or contradictions
4. ESCALATION: Heighten stakes, connect to larger patterns or consequences
5. CONCLUSION: Land the core insight clearly, end with impact (do not summarize)

**Emotional Progression:**
Build emotional investment throughout. The script should feel like a journey, not a report.

**Grounding Requirements:**
- The outline sections contain facts grounded in real research. Use them.
- Do not invent facts, statistics, or claims not present in the outline.
- Reference specific evidence from the outline to support arguments.

**Banned Patterns (NEVER use):**
- Generic filler: "At the end of the day...", "The reality is...", "It's important to note that..."
- Vague statements without specific grounding
- Unsupported claims or statistics without sources
- "In today's world...", "Needless to say..."

**Output Requirements:**
- Script must read like commentary, not summary
- Every word should earn its place; eliminate fluff
- Opening hook must be strong and specific
- Closing must land with impact, not trail off

Return ONLY a valid JSON object with these exact keys:
- opening: string (strong hook, grabs attention immediately)
- body: string (full narration body following narrative structure: tension → breakdown → escalation)
- closing: string (strong closing that lands the thesis with impact)

No markdown. No explanation. JSON only.
"""


def _load_style_guide() -> str:
    """Load the style guide content for injection into prompts."""
    # Try multiple paths to find the style guide
    possible_paths = [
        Path(__file__).parent.parent / "docs" / "style_guide.md",
        Path.cwd() / "docs" / "style_guide.md",
        Path("docs/style_guide.md"),
    ]
    for path in possible_paths:
        if path.exists():
            return path.read_text()
    # Return empty string if not found (graceful degradation)
    return ""

_agent = Agent(
    name="script_agent",
    instructions=SCRIPT_INSTRUCTIONS,
    model="gpt-4o-mini",
)


async def run_script(
    topic: str,
    outline: CommentaryOutline,
    angle: str | None = None,
    audience: str | None = None,
    tone: str | None = None,
    style: str | None = None,
    feedback: ScriptFeedback | None = None,
) -> FinalScript:
    mode = "rewrite" if feedback else "draft"
    with log_stage("script_agent", topic=topic, mode=mode):
        parts = [f"Topic: {topic}"]
        if angle:
            parts.append(f"Angle: {angle}")
        if audience:
            parts.append(f"Audience: {audience}")
        if tone:
            parts.append(f"Tone: {tone}")
        if style:
            parts.append(f"Style: {style}")

        # Inject style guide content
        style_guide = _load_style_guide()
        if style_guide:
            parts.append("\n--- STYLE GUIDE ---")
            parts.append(style_guide)
            parts.append("--- END STYLE GUIDE ---")

        parts.append("\nOutline:")
        parts.append(f"Hook: {outline.hook}")
        parts.append(f"Thesis: {outline.thesis}")
        for i, section in enumerate(outline.sections, 1):
            parts.append(f"Section {i} - {section.title}: {section.argument}")
        parts.append(f"Emotional progression: {outline.emotional_progression}")
        parts.append(f"Closing idea: {outline.closing_idea}")

        if feedback:
            parts.append("\n--- EVALUATOR FEEDBACK (address these in your rewrite) ---")
            if feedback.weaknesses:
                parts.append(f"Weaknesses: {'; '.join(feedback.weaknesses)}")
            if feedback.missing_angles:
                parts.append(f"Missing angles: {'; '.join(feedback.missing_angles)}")
            if feedback.improvement_suggestions:
                parts.append(f"Improvement suggestions: {'; '.join(feedback.improvement_suggestions)}")
            parts.append("--- END FEEDBACK ---")

        prompt = "\n".join(parts)
        result = await Runner.run(_agent, prompt)
        raw = result.final_output

        data = json.loads(raw)
        return FinalScript(
            opening=data.get("opening", ""),
            body=data.get("body", ""),
            closing=data.get("closing", ""),
        )
