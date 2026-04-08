import json

from agents import Agent, Runner
from dotenv import load_dotenv

from schemas.research import ResearchBrief

load_dotenv()

RESEARCH_INSTRUCTIONS = """
You are a research agent. Given a topic and optional context, produce a structured research brief.

Return ONLY a valid JSON object with these exact keys:
- key_facts: list of strings
- key_tensions: list of strings
- relevant_examples: list of strings
- caveats: list of strings
- source_notes: list of strings

No markdown. No explanation. JSON only.
"""

_agent = Agent(
    name="research_agent",
    instructions=RESEARCH_INSTRUCTIONS,
    model="gpt-4o-mini",
)


async def run_research(
    topic: str,
    angle: str | None = None,
    audience: str | None = None,
    red_lines: str | None = None,
    must_hits: str | None = None,
) -> ResearchBrief:
    parts = [f"Topic: {topic}"]
    if angle:
        parts.append(f"Angle: {angle}")
    if audience:
        parts.append(f"Audience: {audience}")
    if red_lines:
        parts.append(f"Red lines (avoid): {red_lines}")
    if must_hits:
        parts.append(f"Must hits (include): {must_hits}")

    prompt = "\n".join(parts)
    result = await Runner.run(_agent, prompt)
    raw = result.final_output

    data = json.loads(raw)
    return ResearchBrief(
        key_facts=data.get("key_facts", []),
        key_tensions=data.get("key_tensions", []),
        relevant_examples=data.get("relevant_examples", []),
        caveats=data.get("caveats", []),
        source_notes=data.get("source_notes", []),
    )
