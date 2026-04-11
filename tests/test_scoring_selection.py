"""Tests for scoring and selection logic"""

import pytest

from schemas.script import FinalScript, ScriptScore
from tools.scoring import ScoreWeights, select_best_script


@pytest.fixture
def mock_scripts():
    """Create mock scripts with different scores."""
    script1 = FinalScript(opening="Script 1", body="Body 1", closing="Close 1")
    script2 = FinalScript(opening="Script 2", body="Body 2", closing="Close 2")
    script3 = FinalScript(opening="Script 3", body="Body 3", closing="Close 3")
    return script1, script2, script3


@pytest.fixture
def mock_scores():
    """Create mock scores with different overall scores."""
    score_low = ScriptScore(
        clarity_score=5.0,
        argument_score=5.0,
        emotional_impact=5.0,
        factual_grounding=5.0,
        overall_score=5.0,
    )
    score_medium = ScriptScore(
        clarity_score=7.0,
        argument_score=7.0,
        emotional_impact=7.0,
        factual_grounding=7.0,
        overall_score=7.0,
    )
    score_high = ScriptScore(
        clarity_score=9.0,
        argument_score=9.0,
        emotional_impact=9.0,
        factual_grounding=9.0,
        overall_score=9.0,
    )
    return score_low, score_medium, score_high


class TestSelectBestScript:
    """Tests for select_best_script function."""

    def test_highest_score_wins(self, mock_scripts, mock_scores):
        """Test that script with highest overall_score is selected."""
        script1, script2, script3 = mock_scripts
        score_low, score_medium, score_high = mock_scores

        candidates = [
            (script1, score_low),
            (script2, score_medium),
            (script3, score_high),
        ]

        result = select_best_script(candidates)
        assert result is script3  # Highest score wins

    def test_single_candidate_returns_immediately(self, mock_scripts, mock_scores):
        """Test that single candidate is returned without comparison."""
        script1, _, _ = mock_scripts
        score_low, _, _ = mock_scores

        candidates = [(script1, score_low)]
        result = select_best_script(candidates)
        assert result is script1

    def test_tie_breaking_first_occurrence_wins(self, mock_scripts):
        """Test that when scores tie, first occurrence is selected."""
        script1, script2, script3 = mock_scripts
        same_score = ScriptScore(
            clarity_score=7.0,
            argument_score=7.0,
            emotional_impact=7.0,
            factual_grounding=7.0,
            overall_score=7.0,
        )

        candidates = [
            (script1, same_score),
            (script2, same_score),
            (script3, same_score),
        ]

        result = select_best_script(candidates)
        assert result is script1  # First occurrence wins on tie

    def test_empty_candidates_raises_error(self):
        """Test that empty candidates list raises ValueError."""
        with pytest.raises(ValueError, match="empty candidates list"):
            select_best_script([])

    def test_varied_scores_selection(self, mock_scripts):
        """Test selection with varied score distributions."""
        script1, script2, script3 = mock_scripts

        # Script1: high clarity, low argument
        score1 = ScriptScore(
            clarity_score=9.0,
            argument_score=4.0,
            emotional_impact=5.0,
            factual_grounding=5.0,
            overall_score=5.5,  # Low overall
        )

        # Script2: balanced medium
        score2 = ScriptScore(
            clarity_score=6.0,
            argument_score=6.0,
            emotional_impact=6.0,
            factual_grounding=6.0,
            overall_score=6.0,  # Medium overall
        )

        # Script3: low clarity, high argument
        score3 = ScriptScore(
            clarity_score=4.0,
            argument_score=9.0,
            emotional_impact=5.0,
            factual_grounding=5.0,
            overall_score=5.5,  # Low overall
        )

        candidates = [
            (script1, score1),
            (script2, score2),
            (script3, score3),
        ]

        result = select_best_script(candidates)
        assert result is script2  # Highest overall_score


class TestWeightedSelection:
    """Tests for weighted score selection."""

    def test_weighted_selection_changes_winner(self, mock_scripts):
        """Test that different weights can change which script wins."""
        script1, script2, _ = mock_scripts

        # Script1: high clarity, low argument
        score1 = ScriptScore(
            clarity_score=9.0,
            argument_score=4.0,
            emotional_impact=5.0,
            factual_grounding=5.0,
            overall_score=5.5,
        )

        # Script2: low clarity, high argument
        score2 = ScriptScore(
            clarity_score=4.0,
            argument_score=9.0,
            emotional_impact=5.0,
            factual_grounding=5.0,
            overall_score=5.5,  # Same overall as script1
        )

        candidates = [(script1, score1), (script2, score2)]

        # With equal weights, first wins (tie)
        result = select_best_script(candidates)
        assert result is script1

        # With argument weighted higher, script2 wins
        weights = ScoreWeights(clarity=1.0, argument=3.0, emotional_impact=1.0, factual_grounding=1.0)
        result = select_best_script(candidates, weights=weights)
        assert result is script2

    def test_weighted_score_calculation(self):
        """Test that ScoreWeights calculates weighted score correctly."""
        score = ScriptScore(
            clarity_score=8.0,
            argument_score=6.0,
            emotional_impact=7.0,
            factual_grounding=9.0,
        )

        # Equal weights: (8+6+7+9)/4 = 7.5
        equal_weights = ScoreWeights(clarity=1.0, argument=1.0, emotional_impact=1.0, factual_grounding=1.0)
        assert equal_weights.calculate_weighted_score(score) == 7.5

        # Clarity weighted double: (8*2 + 6 + 7 + 9)/5 = 38/5 = 7.6
        clarity_weights = ScoreWeights(clarity=2.0, argument=1.0, emotional_impact=1.0, factual_grounding=1.0)
        assert clarity_weights.calculate_weighted_score(score) == 7.6

    def test_weighted_selection_with_zero_weights_uses_overall(self, mock_scripts):
        """Test that zero weights fall back to overall_score."""
        script1, script2, _ = mock_scripts

        score1 = ScriptScore(
            clarity_score=9.0,
            argument_score=9.0,
            emotional_impact=9.0,
            factual_grounding=9.0,
            overall_score=7.0,  # Lower overall
        )

        score2 = ScriptScore(
            clarity_score=5.0,
            argument_score=5.0,
            emotional_impact=5.0,
            factual_grounding=5.0,
            overall_score=8.0,  # Higher overall
        )

        candidates = [(script1, score1), (script2, score2)]

        # With zero total weight, should use overall_score
        zero_weights = ScoreWeights(clarity=0.0, argument=0.0, emotional_impact=0.0, factual_grounding=0.0)
        result = select_best_script(candidates, weights=zero_weights)
        assert result is script2  # Higher overall_score wins


class TestScoreWeights:
    """Tests for ScoreWeights dataclass."""

    def test_default_weights_are_equal(self):
        """Test that default weights are all 1.0."""
        weights = ScoreWeights()
        assert weights.clarity == 1.0
        assert weights.argument == 1.0
        assert weights.emotional_impact == 1.0
        assert weights.factual_grounding == 1.0

    def test_custom_weights(self):
        """Test that custom weights can be set."""
        weights = ScoreWeights(clarity=2.0, argument=3.0, emotional_impact=0.5, factual_grounding=1.5)
        assert weights.clarity == 2.0
        assert weights.argument == 3.0
        assert weights.emotional_impact == 0.5
        assert weights.factual_grounding == 1.5
