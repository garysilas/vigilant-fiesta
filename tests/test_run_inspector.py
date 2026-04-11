"""Tests for run inspector functionality"""

import json
import os
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

from main import _inspect_run, main


class TestInspectRunCLI:
    """Tests for --inspect-run CLI flag parsing."""

    def test_cli_parses_inspect_run_flag(self):
        """Test that --inspect-run flag is parsed correctly."""
        with patch("sys.argv", ["main.py", "--inspect-run", "test_run_123"]):
            with patch("main._inspect_run") as mock_inspect:
                main()
                mock_inspect.assert_called_once_with("test_run_123")

    def test_inspect_run_skips_topic_validation(self):
        """Test that --inspect-run mode skips --topic requirement."""
        with patch("sys.argv", ["main.py", "--inspect-run", "abc123"]):
            with patch("main._inspect_run") as mock_inspect:
                main()
                mock_inspect.assert_called_once_with("abc123")


class TestInspectRunValidRun:
    """Tests for _inspect_run with valid run_id."""

    def test_inspect_valid_run_prints_summary(self, tmp_path):
        """Test that valid run displays correct summary."""
        # Create mock run directory structure
        run_dir = tmp_path / "abc123"
        run_dir.mkdir()

        metadata = {
            "run_id": "abc123",
            "topic": "Test Topic",
            "angle": "Test Angle",
            "audience": "Test Audience",
            "version": "v5",
            "config": {
                "tone": "serious",
                "style": "documentary",
            },
        }
        metadata_path = run_dir / "metadata.json"
        metadata_path.write_text(json.dumps(metadata), encoding="utf-8")

        with patch("main._get_runs_dir", return_value=str(tmp_path)):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                _inspect_run("abc123")
                output = mock_stdout.getvalue()

        assert "RUN INSPECTION: abc123" in output
        assert "Topic: Test Topic" in output
        assert "Angle: Test Angle" in output
        assert "Audience: Test Audience" in output
        assert "Tone: serious" in output
        assert "Style: documentary" in output

    def test_inspect_run_with_scores(self, tmp_path):
        """Test that run with scores displays iterations."""
        run_dir = tmp_path / "run456"
        run_dir.mkdir()

        metadata = {
            "run_id": "run456",
            "topic": "AI Safety",
            "version": "v5",
            "config": {},
        }
        (run_dir / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")

        # Create score files
        scores1 = {"overall_score": 6.5, "clarity_score": 7.0}
        scores2 = {"overall_score": 8.2, "clarity_score": 8.5}
        (run_dir / "scores_v1.json").write_text(json.dumps(scores1), encoding="utf-8")
        (run_dir / "scores_v2.json").write_text(json.dumps(scores2), encoding="utf-8")

        with patch("main._get_runs_dir", return_value=str(tmp_path)):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                _inspect_run("run456")
                output = mock_stdout.getvalue()

        assert "Iterations: 2" in output
        assert "v1: overall=6.5" in output
        assert "v2: overall=8.2" in output

    def test_inspect_run_shows_script_path(self, tmp_path):
        """Test that script path is shown if script exists."""
        run_dir = tmp_path / "run789"
        run_dir.mkdir()

        metadata = {"run_id": "run789", "topic": "Test", "version": "v5", "config": {}}
        (run_dir / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
        (run_dir / "script_v1.txt").write_text("Test script content", encoding="utf-8")

        with patch("main._get_runs_dir", return_value=str(tmp_path)):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                _inspect_run("run789")
                output = mock_stdout.getvalue()

        assert "Script:" in output
        assert "script_v1.txt" in output


class TestInspectRunInvalidRun:
    """Tests for _inspect_run with invalid run_id."""

    def test_inspect_nonexistent_run_prints_error(self, tmp_path):
        """Test that non-existent run prints error message."""
        with patch("main._get_runs_dir", return_value=str(tmp_path)):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                _inspect_run("nonexistent")
                output = mock_stdout.getvalue()

        assert "Error: Run 'nonexistent' not found" in output

    def test_inspect_run_missing_metadata_prints_error(self, tmp_path):
        """Test that run without metadata prints error."""
        run_dir = tmp_path / "no_metadata"
        run_dir.mkdir()

        with patch("main._get_runs_dir", return_value=str(tmp_path)):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                _inspect_run("no_metadata")
                output = mock_stdout.getvalue()

        assert "Error: Metadata not found" in output


class TestInspectRunMetadata:
    """Tests for loading and displaying run metadata."""

    def test_inspect_run_handles_missing_optional_fields(self, tmp_path):
        """Test that missing optional fields show as N/A."""
        run_dir = tmp_path / "minimal"
        run_dir.mkdir()

        metadata = {
            "run_id": "minimal",
            "topic": "Minimal Topic",
            "version": "v5",
            "config": {},  # No tone or style
        }
        (run_dir / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")

        with patch("main._get_runs_dir", return_value=str(tmp_path)):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                _inspect_run("minimal")
                output = mock_stdout.getvalue()

        assert "Tone: N/A" in output
        assert "Style: N/A" in output
        assert "Topic: Minimal Topic" in output

    def test_inspect_run_shows_full_directory_path(self, tmp_path):
        """Test that full run directory path is displayed."""
        run_dir = tmp_path / "fullpath"
        run_dir.mkdir()

        metadata = {"run_id": "fullpath", "topic": "Test", "version": "v5", "config": {}}
        (run_dir / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")

        with patch("main._get_runs_dir", return_value=str(tmp_path)):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                _inspect_run("fullpath")
                output = mock_stdout.getvalue()

        assert f"Full run directory: {run_dir}" in output


class TestInspectRunArtifacts:
    """Tests for loading and displaying run artifacts."""

    def test_inspect_run_without_scores_shows_single_iteration(self, tmp_path):
        """Test that run without score files shows as single iteration."""
        run_dir = tmp_path / "no_scores"
        run_dir.mkdir()

        metadata = {"run_id": "no_scores", "topic": "Test", "version": "v5", "config": {}}
        (run_dir / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")

        with patch("main._get_runs_dir", return_value=str(tmp_path)):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                _inspect_run("no_scores")
                output = mock_stdout.getvalue()

        assert "Iterations: 1 (no scoring yet)" in output

    def test_inspect_run_with_multiple_score_versions(self, tmp_path):
        """Test handling multiple score version files."""
        run_dir = tmp_path / "multi"
        run_dir.mkdir()

        metadata = {"run_id": "multi", "topic": "Test", "version": "v5", "config": {}}
        (run_dir / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")

        # Create multiple score files
        for i in range(1, 4):
            scores = {"overall_score": 5.0 + i, "clarity_score": 6.0 + i}
            (run_dir / f"scores_v{i}.json").write_text(json.dumps(scores), encoding="utf-8")

        with patch("main._get_runs_dir", return_value=str(tmp_path)):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                _inspect_run("multi")
                output = mock_stdout.getvalue()

        assert "Iterations: 3" in output
        assert "v1: overall=6.0" in output
        assert "v2: overall=7.0" in output
        assert "v3: overall=8.0" in output
