import json

from agents import Agent, Runner
from dotenv import load_dotenv

from schemas.outline import CommentaryOutline
from schemas.script import FinalScript

load_dotenv()

SCRIPT_INSTRUCTIONS = """
You are a script agent. Given a topic and a grounded commentary outline, write a narration-ready script.

The outline sections contain facts and arguments grounded in real research. Use them.
Do not invent facts, statistics, or claims not present in the outline.
Maintain tone and style consistency throughout.

Return ONLY a valid JSON object with these exact keys:
- opening: string (strong hook, grabs attention immediately)
- body: string (full narration body, coherent pacing, develops the argument using the outline sections)
- closing: string (strong closing that lands the thesis)

No markdown. No explanation. JSON only.
"""

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
) -> FinalScript:
    print("[Script Agent] Starting...")

    parts = [f"Topic: {topic}"]
    if angle:
        parts.append(f"Angle: {angle}")
    if audience:
        parts.append(f"Audience: {audience}")
    if tone:
        parts.append(f"Tone: {tone}")
    if style:
        parts.append(f"Style: {style}")
    parts.append("\nOutline:")
    parts.append(f"Hook: {outline.hook}")
    parts.append(f"Thesis: {outline.thesis}")
    for i, section in enumerate(outline.sections, 1):
        parts.append(f"Section {i} - {section.title}: {section.argument}")
    parts.append(f"Emotional progression: {outline.emotional_progression}")
    parts.append(f"Closing idea: {outline.closing_idea}")

    prompt = "\n".join(parts)
    result = await Runner.run(_agent, prompt)
    raw = result.final_output

    data = json.loads(raw)
    print("[Script Agent] Completed")
    return FinalScript(
        opening=data.get("opening", ""),
        body=data.get("body", ""),
        closing=data.get("closing", ""),
    )
