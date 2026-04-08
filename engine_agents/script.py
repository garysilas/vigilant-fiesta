import json

from agents import Agent, Runner
from dotenv import load_dotenv

from schemas.outline import CommentaryOutline
from schemas.script import FinalScript

load_dotenv()

SCRIPT_INSTRUCTIONS = """
You are a script agent. Given a topic and a commentary outline, write a narration-ready script.

Return ONLY a valid JSON object with these exact keys:
- opening: string (strong hook, grabs attention immediately)
- body: string (full narration body, coherent pacing, develops the argument)
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
) -> FinalScript:
    parts = [f"Topic: {topic}"]
    if angle:
        parts.append(f"Angle: {angle}")
    if audience:
        parts.append(f"Audience: {audience}")
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
    return FinalScript(
        opening=data.get("opening", ""),
        body=data.get("body", ""),
        closing=data.get("closing", ""),
    )
