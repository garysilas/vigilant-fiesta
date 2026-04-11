import json

from agents import Agent, Runner
from dotenv import load_dotenv

from schemas.script import FinalScript, ScriptFeedback, ScriptScore
from tools.logger import log_stage

load_dotenv()

EVALUATOR_INSTRUCTIONS = """
You are a script evaluator agent. Given a commentary script, analyze it for quality across four dimensions:
- Clarity: Is the argument easy to follow? Are transitions smooth?
- Argument strength: Are claims well-supported? Is the logic sound?
- Emotional impact: Does the script build emotional investment? Does it feel like a journey?
- Factual grounding: Are claims specific and evidence-based, not vague or invented?

Based on your analysis, return ONLY a valid JSON object with these exact keys:
- weaknesses: list of strings identifying specific weak points in the script
- missing_angles: list of strings identifying perspectives or arguments the script should consider
- improvement_suggestions: list of strings with concrete, actionable suggestions to improve the script
- scores: object with numeric scores (0-10 scale) for:
  - clarity_score: float
  - argument_score: float
  - emotional_impact: float
  - factual_grounding: float
  - overall_score: float (aggregate of the above)

Be specific and constructive. Reference exact parts of the script when possible.
No markdown. No explanation. JSON only.
"""

_agent = Agent(
    name="evaluator_agent",
    instructions=EVALUATOR_INSTRUCTIONS,
    model="gpt-4o-mini",
)


async def run_evaluator(script: FinalScript) -> tuple[ScriptFeedback, ScriptScore]:
    with log_stage("evaluator_agent"):
        prompt = f"Evaluate this commentary script:\n\n{script.full_text()}"
        result = await Runner.run(_agent, prompt)
        raw = result.final_output

        data = json.loads(raw)
        feedback = ScriptFeedback(
            weaknesses=data.get("weaknesses", []),
            missing_angles=data.get("missing_angles", []),
            improvement_suggestions=data.get("improvement_suggestions", []),
        )

        scores_data = data.get("scores", {})
        score = ScriptScore(
            clarity_score=scores_data.get("clarity_score", 0.0),
            argument_score=scores_data.get("argument_score", 0.0),
            emotional_impact=scores_data.get("emotional_impact", 0.0),
            factual_grounding=scores_data.get("factual_grounding", 0.0),
            overall_score=scores_data.get("overall_score", 0.0),
        )

        return feedback, score
