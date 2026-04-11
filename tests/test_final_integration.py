"""Final integration tests for Content Engine v5"""

import json
from io import StringIO
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from flows.coordinator import run
from schemas.outline import CommentaryOutline
from schemas.research import ResearchBrief
from schemas.script import Clip, FinalScript, NarrationScript, ScriptFeedback, ScriptScore

MOCK_BRIEF = ResearchBrief(key_facts=["fact1"], key_tensions=[], relevant_examples=[], caveats=[], source_notes=[])
MOCK_OUTLINE = CommentaryOutline(hook="hook", thesis="thesis", sections=[], emotional_progression="", closing_idea="end")
MOCK_SCRIPT = FinalScript(opening="open", body="body", closing="close")
MOCK_SCRIPT_V2 = FinalScript(opening="improved", body="better body", closing="better close")
MOCK_SCRIPT_V3 = FinalScript(opening="best", body="excellent body", closing="excellent close")
MOCK_NARRATION = NarrationScript(text="narration text")
MOCK_CLIPS = [Clip(hook="H1", body="B1", closing="C1")]


def make_score(overall: float) -> ScriptScore:
    return ScriptScore(
        clarity_score=overall,
        argument_score=overall,
        emotional_impact=overall,
        factual_grounding=overall,
        overall_score=overall,
    )


class TestMaxIterations:
    """Integration tests for --max-iterations flag."""

    @pytest.mark.asyncio
    async def test_max_iterations_1_runs_single_iteration(self):
        """Test that max_iterations=1 runs only one iteration."""
        score = make_score(7.0)
        feedback = ScriptFeedback(weaknesses=[], missing_angles=[], improvement_suggestions=[])

        eval_mock = AsyncMock(return_value=(feedback, score))

        with (
            patch("flows.coordinator.run_research", new=AsyncMock(return_value=MOCK_BRIEF)),
            patch("flows.coordinator.run_outline", new=AsyncMock(return_value=MOCK_OUTLINE)),
            patch("flows.coordinator.run_script", new=AsyncMock(return_value=MOCK_SCRIPT)),
            patch("flows.coordinator.run_evaluator", new=eval_mock),
            patch("flows.coordinator.run_voice", new=AsyncMock(return_value=MOCK_NARRATION)),
            patch("flows.coordinator.run_clips", new=AsyncMock(return_value=MOCK_CLIPS)),
        ):
            result = await run(topic="Test", max_iterations=1)

        assert eval_mock.call_count == 1
        assert result.score.overall_score == 7.0

    @pytest.mark.asyncio
    async def test_max_iterations_3_runs_three_iterations(self):
        """Test that max_iterations=3 runs exactly three iterations."""
        scores = [make_score(6.0), make_score(7.0), make_score(8.0)]
        feedback = ScriptFeedback(weaknesses=[], missing_angles=[], improvement_suggestions=[])

        scripts = [MOCK_SCRIPT, MOCK_SCRIPT_V2, MOCK_SCRIPT_V3]

        with (
            patch("flows.coordinator.run_research", new=AsyncMock(return_value=MOCK_BRIEF)),
            patch("flows.coordinator.run_outline", new=AsyncMock(return_value=MOCK_OUTLINE)),
            patch("flows.coordinator.run_script", new=AsyncMock(side_effect=scripts)),
            patch("flows.coordinator.run_evaluator", new=AsyncMock(side_effect=[
                (feedback, scores[0]), (feedback, scores[1]), (feedback, scores[2])
            ])) as eval_mock,
            patch("flows.coordinator.run_voice", new=AsyncMock(return_value=MOCK_NARRATION)),
            patch("flows.coordinator.run_clips", new=AsyncMock(return_value=MOCK_CLIPS)),
        ):
            result = await run(topic="Test", max_iterations=3)

        assert eval_mock.call_count == 3
        # Should select best script (score 8.0)
        assert result.score.overall_score == 8.0


class TestImprovementThreshold:
    """Integration tests for --improvement-threshold flag."""

    @pytest.mark.asyncio
    async def test_low_improvement_triggers_early_stop(self):
        """Test that improvement below threshold stops early."""
        # Improvement: 6.0 -> 6.1 = 0.1 (below threshold 0.2)
        scores = [make_score(6.0), make_score(6.1)]
        feedback = ScriptFeedback(weaknesses=[], missing_angles=[], improvement_suggestions=[])

        with (
            patch("flows.coordinator.run_research", new=AsyncMock(return_value=MOCK_BRIEF)),
            patch("flows.coordinator.run_outline", new=AsyncMock(return_value=MOCK_OUTLINE)),
            patch("flows.coordinator.run_script", new=AsyncMock(side_effect=[MOCK_SCRIPT, MOCK_SCRIPT_V2])),
            patch("flows.coordinator.run_evaluator", new=AsyncMock(side_effect=[
                (feedback, scores[0]), (feedback, scores[1])
            ])) as eval_mock,
            patch("flows.coordinator.run_voice", new=AsyncMock(return_value=MOCK_NARRATION)),
            patch("flows.coordinator.run_clips", new=AsyncMock(return_value=MOCK_CLIPS)),
        ):
            result = await run(topic="Test", max_iterations=3, improvement_threshold=0.2)

        # Should stop after 2 iterations
        assert eval_mock.call_count == 2

    @pytest.mark.asyncio
    async def test_high_improvement_continues_iteration(self):
        """Test that improvement above threshold continues iteration."""
        # Improvement: 6.0 -> 7.5 = 1.5 (above threshold 0.2)
        scores = [make_score(6.0), make_score(7.5), make_score(7.6)]
        feedback = ScriptFeedback(weaknesses=[], missing_angles=[], improvement_suggestions=[])

        with (
            patch("flows.coordinator.run_research", new=AsyncMock(return_value=MOCK_BRIEF)),
            patch("flows.coordinator.run_outline", new=AsyncMock(return_value=MOCK_OUTLINE)),
            patch("flows.coordinator.run_script", new=AsyncMock(side_effect=[MOCK_SCRIPT, MOCK_SCRIPT_V2, MOCK_SCRIPT_V3])),
            patch("flows.coordinator.run_evaluator", new=AsyncMock(side_effect=[
                (feedback, scores[0]), (feedback, scores[1]), (feedback, scores[2])
            ])) as eval_mock,
            patch("flows.coordinator.run_voice", new=AsyncMock(return_value=MOCK_NARRATION)),
            patch("flows.coordinator.run_clips", new=AsyncMock(return_value=MOCK_CLIPS)),
        ):
            result = await run(topic="Test", max_iterations=3, improvement_threshold=0.2)

        # Should run all 3 iterations (improvement 0.1 on last iteration but we can't break after last)
        assert eval_mock.call_count == 3


class TestNoRewrite:
    """Integration tests for --no-rewrite flag."""

    @pytest.mark.asyncio
    async def test_no_rewrite_forces_single_iteration(self):
        """Test that --no-rewrite (max_iterations=1) forces single iteration."""
        score = make_score(7.0)
        feedback = ScriptFeedback(weaknesses=[], missing_angles=[], improvement_suggestions=[])

        eval_mock = AsyncMock(return_value=(feedback, score))

        with (
            patch("flows.coordinator.run_research", new=AsyncMock(return_value=MOCK_BRIEF)),
            patch("flows.coordinator.run_outline", new=AsyncMock(return_value=MOCK_OUTLINE)),
            patch("flows.coordinator.run_script", new=AsyncMock(return_value=MOCK_SCRIPT)),
            patch("flows.coordinator.run_evaluator", new=eval_mock),
            patch("flows.coordinator.run_voice", new=AsyncMock(return_value=MOCK_NARRATION)),
            patch("flows.coordinator.run_clips", new=AsyncMock(return_value=MOCK_CLIPS)),
        ):
            # Simulating --no-rewrite behavior
            result = await run(topic="Test", max_iterations=1)

        assert eval_mock.call_count == 1


class TestBestScriptSelection:
    """Integration tests for best script selection."""

    @pytest.mark.asyncio
    async def test_best_script_by_overall_score_selected(self):
        """Test that script with highest overall_score is returned."""
        # Scores: 6.0, 8.5, 7.0 - should select second script
        scores = [make_score(6.0), make_score(8.5), make_score(7.0)]
        feedback = ScriptFeedback(weaknesses=[], missing_angles=[], improvement_suggestions=[])

        scripts = [MOCK_SCRIPT, MOCK_SCRIPT_V2, MOCK_SCRIPT_V3]

        with (
            patch("flows.coordinator.run_research", new=AsyncMock(return_value=MOCK_BRIEF)),
            patch("flows.coordinator.run_outline", new=AsyncMock(return_value=MOCK_OUTLINE)),
            patch("flows.coordinator.run_script", new=AsyncMock(side_effect=scripts)),
            patch("flows.coordinator.run_evaluator", new=AsyncMock(side_effect=[
                (feedback, scores[0]), (feedback, scores[1]), (feedback, scores[2])
            ])),
            patch("flows.coordinator.run_voice", new=AsyncMock(return_value=MOCK_NARRATION)),
            patch("flows.coordinator.run_clips", new=AsyncMock(return_value=MOCK_CLIPS)),
        ):
            result = await run(topic="Test", max_iterations=3)

        assert result.score.overall_score == 8.5
        assert result.script is MOCK_SCRIPT_V2

    @pytest.mark.asyncio
    async def test_voice_uses_best_script(self):
        """Test that voice agent uses best script, not last script."""
        # Best script is first one (9.0)
        scores = [make_score(9.0), make_score(6.0)]
        feedback = ScriptFeedback(weaknesses=[], missing_angles=[], improvement_suggestions=[])

        scripts = [MOCK_SCRIPT, MOCK_SCRIPT_V2]

        voice_mock = AsyncMock(return_value=MOCK_NARRATION)

        with (
            patch("flows.coordinator.run_research", new=AsyncMock(return_value=MOCK_BRIEF)),
            patch("flows.coordinator.run_outline", new=AsyncMock(return_value=MOCK_OUTLINE)),
            patch("flows.coordinator.run_script", new=AsyncMock(side_effect=scripts)),
            patch("flows.coordinator.run_evaluator", new=AsyncMock(side_effect=[
                (feedback, scores[0]), (feedback, scores[1])
            ])),
            patch("flows.coordinator.run_voice", new=voice_mock),
            patch("flows.coordinator.run_clips", new=AsyncMock(return_value=MOCK_CLIPS)),
        ):
            await run(topic="Test", max_iterations=2)

        # Voice should use first script (best score)
        assert voice_mock.call_count == 1
        assert voice_mock.call_args.kwargs["script"] is MOCK_SCRIPT


class TestArtifactSaving:
    """Integration tests for artifact saving with iterations."""

    @pytest.mark.asyncio
    async def test_iteration_artifacts_saved(self, tmp_path):
        """Test that per-iteration artifacts are saved."""
        scores = [make_score(6.0), make_score(7.0)]
        feedback = ScriptFeedback(weaknesses=[], missing_angles=[], improvement_suggestions=[])

        scripts = [MOCK_SCRIPT, MOCK_SCRIPT_V2]

        run_dir = str(tmp_path / "test_run")

        with (
            patch("flows.coordinator.run_research", new=AsyncMock(return_value=MOCK_BRIEF)),
            patch("flows.coordinator.run_outline", new=AsyncMock(return_value=MOCK_OUTLINE)),
            patch("flows.coordinator.run_script", new=AsyncMock(side_effect=scripts)),
            patch("flows.coordinator.run_evaluator", new=AsyncMock(side_effect=[
                (feedback, scores[0]), (feedback, scores[1])
            ])),
            patch("flows.coordinator.run_voice", new=AsyncMock(return_value=MOCK_NARRATION)),
            patch("flows.coordinator.run_clips", new=AsyncMock(return_value=MOCK_CLIPS)),
            patch("flows.coordinator.create_run_dir", return_value=run_dir),
        ):
            import os
            os.makedirs(run_dir, exist_ok=True)
            result = await run(topic="Test", max_iterations=2, save_run=True, run_id="test_run")

        # Check that best_script is saved
        best_script_path = Path(run_dir) / "best_script.txt"
        assert best_script_path.exists()


class TestCLIIntegration:
    """Tests for CLI flag integration with main.py."""

    @pytest.fixture
    def mock_engine_result(self):
        """Create a mock EngineResult for testing."""
        from flows.coordinator import EngineResult
        return EngineResult(
            brief=MOCK_BRIEF,
            outline=MOCK_OUTLINE,
            script=MOCK_SCRIPT,
            narration=MOCK_NARRATION,
            clips=MOCK_CLIPS,
            run_id="test-run",
        )

    def test_max_iterations_passed_to_coordinator(self, mock_engine_result):
        """Test that --max-iterations is passed through to coordinator."""
        from main import main as main_func

        async def mock_run(*args, **kwargs):
            return mock_engine_result

        with patch("sys.argv", ["main.py", "--topic", "Test", "--max-iterations", "3"]):
            with patch("main.run", new=mock_run):
                with patch("builtins.print"):  # Suppress output
                    main_func()

    def test_improvement_threshold_passed_to_coordinator(self, mock_engine_result):
        """Test that --improvement-threshold is passed through."""
        from main import main as main_func

        captured_kwargs = {}

        async def mock_run(*args, **kwargs):
            captured_kwargs.update(kwargs)
            return mock_engine_result

        with patch("sys.argv", ["main.py", "--topic", "Test", "--improvement-threshold", "0.5"]):
            with patch("main.run", new=mock_run):
                with patch("builtins.print"):  # Suppress output
                    main_func()

        assert captured_kwargs.get("improvement_threshold") == 0.5

    def test_no_rewrite_sets_max_iterations_to_1(self, mock_engine_result):
        """Test that --no-rewrite forces max_iterations=1."""
        from main import main as main_func

        captured_kwargs = {}

        async def mock_run(*args, **kwargs):
            captured_kwargs.update(kwargs)
            return mock_engine_result

        with patch("sys.argv", ["main.py", "--topic", "Test", "--no-rewrite", "--max-iterations", "5"]):
            with patch("main.run", new=mock_run):
                with patch("builtins.print"):  # Suppress output
                    main_func()

        # --no-rewrite should override max_iterations
        assert captured_kwargs.get("max_iterations") == 1
