"""Scoring and selection utilities for script evaluation"""

from dataclasses import dataclass

from schemas.script import FinalScript, ScriptScore


@dataclass
class ScoreWeights:
    """Weights for calculating weighted overall score.

    All weights default to 1.0 (equal weighting).
    """

    clarity: float = 1.0
    argument: float = 1.0
    emotional_impact: float = 1.0
    factual_grounding: float = 1.0

    def calculate_weighted_score(self, score: ScriptScore) -> float:
        """Calculate weighted score from individual dimensions."""
        total_weight = self.clarity + self.argument + self.emotional_impact + self.factual_grounding
        if total_weight == 0:
            return score.overall_score

        weighted_sum = (
            self.clarity * score.clarity_score
            + self.argument * score.argument_score
            + self.emotional_impact * score.emotional_impact
            + self.factual_grounding * score.factual_grounding
        )
        return weighted_sum / total_weight


def select_best_script(
    candidates: list[tuple[FinalScript, ScriptScore]],
    weights: ScoreWeights | None = None,
) -> FinalScript:
    """Select the best script from candidates based on score.

    Args:
        candidates: List of (script, score) tuples
        weights: Optional ScoreWeights for weighted selection. If None, uses overall_score.

    Returns:
        The FinalScript with the highest score

    Raises:
        ValueError: If candidates list is empty
    """
    if not candidates:
        raise ValueError("Cannot select best script from empty candidates list")

    if len(candidates) == 1:
        return candidates[0][0]

    best_script = candidates[0][0]
    best_score_value = _get_score_value(candidates[0][1], weights)

    for script, score in candidates[1:]:
        score_value = _get_score_value(score, weights)
        # Use > for highest score wins; ties keep first occurrence
        if score_value > best_score_value:
            best_script = script
            best_score_value = score_value

    return best_script


def _get_score_value(score: ScriptScore, weights: ScoreWeights | None = None) -> float:
    """Get the score value to use for comparison."""
    if weights is None:
        return score.overall_score
    return weights.calculate_weighted_score(score)
