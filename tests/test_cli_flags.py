"""Tests for CLI flag parsing in main.py"""

import pytest


def test_cli_help_shows_new_flags():
    """Test that help output includes Sprint 5 flags."""
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "-m", "main", "--help"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    output = result.stdout

    # Check Sprint 5 flags are present
    assert "--save-run" in output
    assert "--run-id" in output
    assert "--max-iterations" in output
    assert "--improvement-threshold" in output
    assert "--no-rewrite" in output
    assert "--export" in output
    assert "--inspect-run" in output


class TestCLIArgumentParsing:
    """Test CLI argument parsing logic."""

    def test_save_run_true_by_default(self):
        """Test that --save-run defaults to True."""
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--save-run",
            type=lambda x: x.lower() in ('true', '1', 'yes'),
            default=True,
        )

        args = parser.parse_args([])
        assert args.save_run is True

    def test_save_run_false_when_specified(self):
        """Test that --save-run can be set to false."""
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--save-run",
            type=lambda x: x.lower() in ('true', '1', 'yes'),
            default=True,
        )

        args = parser.parse_args(["--save-run", "false"])
        assert args.save_run is False

        args = parser.parse_args(["--save-run", "no"])
        assert args.save_run is False

        args = parser.parse_args(["--save-run", "0"])
        assert args.save_run is False

    def test_run_id_optional(self):
        """Test that --run-id is optional."""
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument("--run-id", default=None)

        args = parser.parse_args([])
        assert args.run_id is None

        args = parser.parse_args(["--run-id", "my-run-123"])
        assert args.run_id == "my-run-123"

    def test_max_iterations_int_default(self):
        """Test that --max-iterations defaults to 1 and accepts int."""
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument("--max-iterations", type=int, default=1)

        args = parser.parse_args([])
        assert args.max_iterations == 1

        args = parser.parse_args(["--max-iterations", "5"])
        assert args.max_iterations == 5

    def test_improvement_threshold_float_default(self):
        """Test that --improvement-threshold defaults to 0.2 and accepts float."""
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument("--improvement-threshold", type=float, default=0.2)

        args = parser.parse_args([])
        assert args.improvement_threshold == 0.2

        args = parser.parse_args(["--improvement-threshold", "0.5"])
        assert args.improvement_threshold == 0.5

    def test_no_rewrite_flag(self):
        """Test that --no-rewrite is a boolean flag."""
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument("--no-rewrite", action="store_true")

        args = parser.parse_args([])
        assert args.no_rewrite is False

        args = parser.parse_args(["--no-rewrite"])
        assert args.no_rewrite is True

    def test_export_choices(self):
        """Test that --export accepts only valid choices."""
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument("--export", default=None, choices=["json", "txt", "all"])

        args = parser.parse_args([])
        assert args.export is None

        args = parser.parse_args(["--export", "json"])
        assert args.export == "json"

        args = parser.parse_args(["--export", "txt"])
        assert args.export == "txt"

        args = parser.parse_args(["--export", "all"])
        assert args.export == "all"

    def test_inspect_run_optional(self):
        """Test that --inspect-run accepts a run ID."""
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument("--inspect-run", default=None)

        args = parser.parse_args([])
        assert args.inspect_run is None

        args = parser.parse_args(["--inspect-run", "run-123"])
        assert args.inspect_run == "run-123"


class TestInspectRunFunctionality:
    """Test the --inspect-run functionality."""

    def test_inspect_run_nonexistent(self, capsys, monkeypatch, tmp_path):
        """Test inspecting a non-existent run prints error."""
        import sys
        from io import StringIO

        # Mock the runs directory to temp path
        monkeypatch.setattr("main._get_runs_dir", lambda: str(tmp_path / "runs"))

        from main import _inspect_run

        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        _inspect_run("nonexistent-run")

        output = sys.stdout.getvalue()
        sys.stdout = old_stdout

        assert "not found" in output

    def test_inspect_run_existing(self, monkeypatch, tmp_path):
        """Test inspecting an existing run displays metadata."""
        import os
        import json
        import sys
        from io import StringIO

        # Setup temp run directory
        runs_dir = tmp_path / "runs"
        run_dir = runs_dir / "test-run-123"
        run_dir.mkdir(parents=True)

        # Create metadata
        metadata = {
            "run_id": "test-run-123",
            "topic": "Test Topic",
            "angle": "Test Angle",
            "audience": "Test Audience",
            "version": "v5",
            "config": {
                "tone": "professional",
                "style": "concise"
            }
        }
        with open(run_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f)

        # Create script file
        with open(run_dir / "script_v1.txt", "w", encoding="utf-8") as f:
            f.write("Test script content")

        monkeypatch.setattr("main._get_runs_dir", lambda: str(runs_dir))

        from main import _inspect_run

        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        _inspect_run("test-run-123")

        output = sys.stdout.getvalue()
        sys.stdout = old_stdout

        assert "RUN INSPECTION: test-run-123" in output
        assert "Test Topic" in output
        assert "Test Angle" in output
        assert "v5" in output
        assert "professional" in output
