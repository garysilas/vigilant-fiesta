import json

from agents import Agent, Runner
from dotenv import load_dotenv

from schemas.outline import CommentaryOutline, OutlineSection
from schemas.research import ResearchBrief
from tools.knowledge_store import load_relevant_knowledge
from tools.logger import log_stage

load_dotenv()

OUTLINE_INSTRUCTIONS = """
You are an outline agent. Given a topic, a research brief, and grounded sources, produce a structured commentary outline.

Return ONLY a valid JSON object with these exact keys:
- hook: string
- thesis: string
- sections: list of objects, each with "title" (string) and "argument" (string)
- emotional_progression: string
- closing_idea: string

Use the provided sources to ground the outline in real information. Do not invent facts not supported by the brief.
No markdown. No explanation. JSON only.
"""

_agent = Agent(
    name="outline_agent",
    instructions=OUTLINE_INSTRUCTIONS,
    model="gpt-4o-mini",
)


async def run_outline(
    topic: str,
    brief: ResearchBrief,
    angle: str | None = None,
    audience: str | None = None,
    tone: str | None = None,
    style: str | None = None,
) -> CommentaryOutline:
    with log_stage("outline_agent", topic=topic):
        parts = [f"Topic: {topic}"]
        if angle:
            parts.append(f"Angle: {angle}")
        if audience:
            parts.append(f"Audience: {audience}")
        if tone:
            parts.append(f"Tone: {tone}")
        if style:
            parts.append(f"Style: {style}")
        prior_briefs = load_relevant_knowledge(topic)
        if prior_briefs:
            prior_facts = []
            for pb in prior_briefs:
                prior_facts.extend(pb.key_facts)
            if prior_facts:
                parts.append(f"\nPrior knowledge: {', '.join(prior_facts)}")

        parts.append("\nResearch Brief:")
        parts.append(f"Key facts: {', '.join(brief.key_facts)}")
        parts.append(f"Key tensions: {', '.join(brief.key_tensions)}")
        parts.append(f"Relevant examples: {', '.join(brief.relevant_examples)}")
        parts.append(f"Caveats: {', '.join(brief.caveats)}")
        if brief.sources:
            sources_text = "\n".join(
                f"  - {s.title} ({s.url}): {s.summary}" for s in brief.sources
            )
            parts.append(f"\nSources:\n{sources_text}")

        prompt = "\n".join(parts)
        result = await Runner.run(_agent, prompt)
        raw = result.final_output

        data = json.loads(raw)
        sections = [
            OutlineSection(title=s["title"], argument=s["argument"])
            for s in data.get("sections", [])
        ]
        return CommentaryOutline(
            hook=data.get("hook", ""),
            thesis=data.get("thesis", ""),
            sections=sections,
            emotional_progression=data.get("emotional_progression", ""),
            closing_idea=data.get("closing_idea", ""),
        )
