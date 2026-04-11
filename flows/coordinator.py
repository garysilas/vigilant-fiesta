import time
import uuid
from dataclasses import dataclass
from typing import List, Optional

from engine_agents.clips import run_clips
from engine_agents.evaluator import run_evaluator
from engine_agents.outline import run_outline
from engine_agents.research import run_research
from engine_agents.script import run_script
from engine_agents.voice import run_voice
from schemas.outline import CommentaryOutline
from schemas.research import ResearchBrief
from schemas.script import Clip, FinalScript, NarrationScript, ScriptFeedback, ScriptScore
from tools.logger import log_stage
from tools.run_artifacts import create_run_dir, save_json, save_text


@dataclass
class EngineResult:
    brief: ResearchBrief
    outline: CommentaryOutline
    script: FinalScript
    narration: NarrationScript
    clips: List[Clip]
    feedback: Optional[ScriptFeedback] = None
    score: Optional[ScriptScore] = None
    run_id: Optional[str] = None


async def run(
    topic: str,
    angle: str | None = None,
    audience: str | None = None,
    red_lines: str | None = None,
    must_hits: str | None = None,
    tone: str | None = None,
    style: str | None = None,
    run_id: str | None = None,
    save_run: bool = True,
    max_iterations: int = 1,
    improvement_threshold: float = 0.2,
) -> EngineResult:
    # Generate run_id if not provided and saving is enabled
    if save_run and run_id is None:
        run_id = str(uuid.uuid4())[:8]

    # Setup run directory if saving
    run_dir: str | None = None
    if save_run and run_id:
        run_dir = create_run_dir(run_id)
        # Save metadata
        metadata = {
            "run_id": run_id,
            "topic": topic,
            "angle": angle,
            "audience": audience,
            "timestamp": time.time(),
            "config": {
                "tone": tone,
                "style": style,
                "red_lines": red_lines,
                "must_hits": must_hits,
            },
            "version": "v5",
        }
        save_json(f"{run_dir}/metadata.json", metadata)

    with log_stage("coordinator", topic=topic, run_id=run_id):
        brief = await run_research(
            topic=topic,
            angle=angle,
            audience=audience,
            red_lines=red_lines,
            must_hits=must_hits,
            tone=tone,
            style=style,
        )
        if run_dir:
            save_json(f"{run_dir}/research.json", brief)

        outline = await run_outline(
            topic=topic,
            brief=brief,
            angle=angle,
            audience=audience,
            tone=tone,
            style=style,
        )
        if run_dir:
            save_json(f"{run_dir}/outline.json", outline)

        # Initial script generation
        script = await run_script(
            topic=topic,
            outline=outline,
            angle=angle,
            audience=audience,
            tone=tone,
            style=style,
        )

        # Iteration loop: evaluate → score → rewrite (up to max_iterations)
        best_script = script
        best_score = None
        previous_overall = 0.0
        final_feedback = None
        final_score = None

        for iteration in range(1, max_iterations + 1):
            feedback, score = await run_evaluator(script=script)

            if run_dir:
                save_json(f"{run_dir}/feedback_v{iteration}.json", feedback)
                save_json(f"{run_dir}/scores_v{iteration}.json", score)
                save_text(f"{run_dir}/script_v{iteration}.txt", script.full_text())

            # Track best script by overall_score
            if best_score is None or score.overall_score > best_score.overall_score:
                best_script = script
                best_score = score

            # Store final feedback/score from last iteration
            final_feedback = feedback
            final_score = score

            # Check stopping condition (not on first iteration)
            if iteration > 1:
                improvement = score.overall_score - previous_overall
                if improvement < improvement_threshold:
                    break

            previous_overall = score.overall_score

            # Rewrite script with feedback (unless this was the last iteration)
            if iteration < max_iterations:
                script = await run_script(
                    topic=topic,
                    outline=outline,
                    angle=angle,
                    audience=audience,
                    tone=tone,
                    style=style,
                    feedback=feedback,
                )

        # Use best script for voice and clips
        narration = await run_voice(
            script=best_script,
            tone=tone,
            style=style,
        )
        if run_dir:
            save_text(f"{run_dir}/narration.txt", narration.text)
            save_text(f"{run_dir}/best_script.txt", best_script.full_text())

        clips = await run_clips(script=best_script)
        if run_dir:
            save_json(f"{run_dir}/clips.json", clips)

        return EngineResult(
            brief=brief,
            outline=outline,
            script=best_script,
            narration=narration,
            clips=clips,
            feedback=final_feedback,
            score=best_score,
            run_id=run_id,
        )
