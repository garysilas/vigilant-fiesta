from dataclasses import dataclass

from engine_agents.outline import run_outline
from engine_agents.research import run_research
from engine_agents.script import run_script
from schemas.outline import CommentaryOutline
from schemas.research import ResearchBrief
from schemas.script import FinalScript


@dataclass
class EngineResult:
    brief: ResearchBrief
    outline: CommentaryOutline
    script: FinalScript


async def run(
    topic: str,
    angle: str | None = None,
    audience: str | None = None,
    red_lines: str | None = None,
    must_hits: str | None = None,
    tone: str | None = None,
    style: str | None = None,
) -> EngineResult:
    print(f"[Coordinator] Starting pipeline for topic: {topic}")

    brief = await run_research(
        topic=topic,
        angle=angle,
        audience=audience,
        red_lines=red_lines,
        must_hits=must_hits,
        tone=tone,
        style=style,
    )

    outline = await run_outline(
        topic=topic,
        brief=brief,
        angle=angle,
        audience=audience,
        tone=tone,
        style=style,
    )

    script = await run_script(
        topic=topic,
        outline=outline,
        angle=angle,
        audience=audience,
        tone=tone,
        style=style,
    )

    print("[Coordinator] Pipeline complete")
    return EngineResult(brief=brief, outline=outline, script=script)
