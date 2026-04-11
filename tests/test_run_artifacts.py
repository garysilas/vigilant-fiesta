import json
import os
import tempfile
from dataclasses import dataclass, field

import pytest

from tools.run_artifacts import (
    create_run_dir,
    load_json,
    load_text,
    save_json,
    save_text,
)


class TestCreateRunDir:
    def test_creates_directory_structure(self, tmp_path, monkeypatch):
        """Test that create_run_dir creates the correct directory structure."""
        monkeypatch.setattr("tools.run_artifacts._get_runs_dir", lambda: str(tmp_path / "runs"))

        run_id = "test-run-123"
        result = create_run_dir(run_id)

        expected_path = str(tmp_path / "runs" / run_id)
        assert result == expected_path
        assert os.path.isdir(expected_path)

    def test_existing_directory_no_error(self, tmp_path, monkeypatch):
        """Test that creating an existing directory doesn't raise an error."""
        monkeypatch.setattr("tools.run_artifacts._get_runs_dir", lambda: str(tmp_path / "runs"))

        run_id = "test-run-456"
        create_run_dir(run_id)
        result = create_run_dir(run_id)  # Should not raise

        assert os.path.isdir(result)


class TestSaveJson:
    def test_saves_dict(self, tmp_path):
        """Test saving a dictionary as JSON."""
        path = str(tmp_path / "test.json")
        data = {"key": "value", "number": 42, "list": [1, 2, 3]}

        save_json(path, data)

        with open(path, "r", encoding="utf-8") as f:
            loaded = json.load(f)

        assert loaded == data

    def test_saves_dataclass(self, tmp_path):
        """Test saving a dataclass as JSON."""
        @dataclass
        class TestData:
            name: str
            value: int
            tags: list[str] = field(default_factory=list)

        path = str(tmp_path / "test.json")
        data = TestData(name="test", value=42, tags=["a", "b"])

        save_json(path, data)

        with open(path, "r", encoding="utf-8") as f:
            loaded = json.load(f)

        assert loaded == {"name": "test", "value": 42, "tags": ["a", "b"]}

    def test_saves_list_of_dataclasses(self, tmp_path):
        """Test saving a list of dataclasses as JSON."""
        @dataclass
        class Item:
            id: int
            name: str

        path = str(tmp_path / "items.json")
        data = [Item(1, "first"), Item(2, "second")]

        save_json(path, data)

        with open(path, "r", encoding="utf-8") as f:
            loaded = json.load(f)

        assert loaded == [{"id": 1, "name": "first"}, {"id": 2, "name": "second"}]

    def test_creates_parent_directories(self, tmp_path):
        """Test that save_json creates parent directories if needed."""
        path = str(tmp_path / "nested" / "dirs" / "file.json")
        data = {"key": "value"}

        save_json(path, data)

        assert os.path.isfile(path)


class TestSaveText:
    def test_saves_text(self, tmp_path):
        """Test saving text to a file."""
        path = str(tmp_path / "test.txt")
        text = "Hello, World!\nThis is a test."

        save_text(path, text)

        with open(path, "r", encoding="utf-8") as f:
            loaded = f.read()

        assert loaded == text

    def test_creates_parent_directories(self, tmp_path):
        """Test that save_text creates parent directories if needed."""
        path = str(tmp_path / "nested" / "dirs" / "file.txt")
        text = "content"

        save_text(path, text)

        assert os.path.isfile(path)


class TestLoadJson:
    def test_loads_json(self, tmp_path):
        """Test loading JSON from a file."""
        path = str(tmp_path / "test.json")
        data = {"key": "value", "number": 42}

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)

        loaded = load_json(path)

        assert loaded == data


class TestLoadText:
    def test_loads_text(self, tmp_path):
        """Test loading text from a file."""
        path = str(tmp_path / "test.txt")
        text = "Hello, World!"

        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

        loaded = load_text(path)

        assert loaded == text


class TestMetadataStructure:
    """Test metadata.json structure matches spec v5 requirements."""

    @pytest.mark.asyncio
    async def test_metadata_has_all_required_fields(self, tmp_path, monkeypatch):
        """Test that metadata.json contains all spec-required fields."""
        from unittest.mock import AsyncMock, patch

        # Mock the run artifacts directory
        runs_dir = tmp_path / "runs"
        monkeypatch.setattr("tools.run_artifacts._get_runs_dir", lambda: str(runs_dir))

        from flows.coordinator import run, EngineResult
        from schemas.research import ResearchBrief, Source
        from schemas.outline import CommentaryOutline
        from schemas.script import FinalScript, NarrationScript, ScriptFeedback, ScriptScore, Clip

        mock_brief = ResearchBrief(key_facts=["fact1"], sources=[Source(title="Test", url="http://test.com", summary="test")])
        mock_outline = CommentaryOutline()
        mock_script = FinalScript(opening="Opening", body="Body", closing="Closing")
        mock_feedback = ScriptFeedback(weaknesses=["weakness"])
        mock_score = ScriptScore(overall_score=7.0)
        mock_narration = NarrationScript(text="Narration")
        mock_clips = [Clip(hook="Hook", body="Body", closing="Close")]
        mock_rewritten = FinalScript(opening="Rewritten", body="Body", closing="Close")

        with (
            patch("flows.coordinator.run_research", new=AsyncMock(return_value=mock_brief)),
            patch("flows.coordinator.run_outline", new=AsyncMock(return_value=mock_outline)),
            patch("flows.coordinator.run_script", new=AsyncMock(side_effect=[mock_script, mock_rewritten])),
            patch("flows.coordinator.run_evaluator", new=AsyncMock(return_value=(mock_feedback, mock_score))),
            patch("flows.coordinator.run_voice", new=AsyncMock(return_value=mock_narration)),
            patch("flows.coordinator.run_clips", new=AsyncMock(return_value=mock_clips)),
        ):
            result = await run(
                topic="Test Topic",
                angle="Test Angle",
                audience="Test Audience",
                tone="professional",
                style="concise",
                red_lines="avoid X",
                must_hits="mention Y",
                run_id="test-meta-123",
                save_run=True,
            )

        # Verify metadata was saved
        metadata_path = runs_dir / "test-meta-123" / "metadata.json"
        assert metadata_path.exists(), f"metadata.json not found at {metadata_path}"

        # Load and verify metadata structure
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        # Required fields per spec
        assert "run_id" in metadata, "metadata missing run_id"
        assert metadata["run_id"] == "test-meta-123"

        assert "topic" in metadata, "metadata missing topic"
        assert metadata["topic"] == "Test Topic"

        assert "angle" in metadata, "metadata missing angle"
        assert metadata["angle"] == "Test Angle"

        assert "audience" in metadata, "metadata missing audience"
        assert metadata["audience"] == "Test Audience"

        assert "timestamp" in metadata, "metadata missing timestamp"
        assert isinstance(metadata["timestamp"], (int, float))

        assert "config" in metadata, "metadata missing config"
        assert isinstance(metadata["config"], dict)
        assert "tone" in metadata["config"]
        assert "style" in metadata["config"]
        assert metadata["config"]["tone"] == "professional"
        assert metadata["config"]["style"] == "concise"
        assert metadata["config"]["red_lines"] == "avoid X"
        assert metadata["config"]["must_hits"] == "mention Y"

        assert "version" in metadata, "metadata missing version"
        assert metadata["version"] == "v5"

    @pytest.mark.asyncio
    async def test_metadata_run_id_auto_generated(self, tmp_path, monkeypatch):
        """Test that run_id is auto-generated when not provided."""
        from unittest.mock import AsyncMock, patch

        runs_dir = tmp_path / "runs"
        monkeypatch.setattr("tools.run_artifacts._get_runs_dir", lambda: str(runs_dir))

        from flows.coordinator import run, EngineResult
        from schemas.research import ResearchBrief, Source
        from schemas.outline import CommentaryOutline
        from schemas.script import FinalScript, NarrationScript, ScriptFeedback, ScriptScore

        mock_brief = ResearchBrief(sources=[Source(title="T", url="http://t.com", summary="s")])
        mock_outline = CommentaryOutline()
        mock_script = FinalScript()
        mock_feedback = ScriptFeedback()
        mock_score = ScriptScore(overall_score=7.0)
        mock_narration = NarrationScript()

        with (
            patch("flows.coordinator.run_research", new=AsyncMock(return_value=mock_brief)),
            patch("flows.coordinator.run_outline", new=AsyncMock(return_value=mock_outline)),
            patch("flows.coordinator.run_script", new=AsyncMock(side_effect=[mock_script, mock_script])),
            patch("flows.coordinator.run_evaluator", new=AsyncMock(return_value=(mock_feedback, mock_score))),
            patch("flows.coordinator.run_voice", new=AsyncMock(return_value=mock_narration)),
            patch("flows.coordinator.run_clips", new=AsyncMock(return_value=[])),
        ):
            result = await run(topic="Auto ID Test", save_run=True)

        # Verify run_id was generated and returned
        assert result.run_id is not None
        assert len(result.run_id) > 0

        # Verify metadata file exists with the generated run_id
        metadata_path = runs_dir / result.run_id / "metadata.json"
        assert metadata_path.exists()

        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        assert metadata["run_id"] == result.run_id

    @pytest.mark.asyncio
    async def test_no_metadata_when_save_run_false(self, tmp_path, monkeypatch):
        """Test that no artifacts are saved when save_run=False."""
        from unittest.mock import AsyncMock, patch

        runs_dir = tmp_path / "runs"
        monkeypatch.setattr("tools.run_artifacts._get_runs_dir", lambda: str(runs_dir))

        from flows.coordinator import run
        from schemas.research import ResearchBrief, Source
        from schemas.outline import CommentaryOutline
        from schemas.script import FinalScript, NarrationScript, ScriptFeedback, ScriptScore

        mock_brief = ResearchBrief(sources=[Source(title="T", url="http://t.com", summary="s")])
        mock_outline = CommentaryOutline()
        mock_script = FinalScript()
        mock_feedback = ScriptFeedback()
        mock_score = ScriptScore(overall_score=7.0)
        mock_narration = NarrationScript()

        with (
            patch("flows.coordinator.run_research", new=AsyncMock(return_value=mock_brief)),
            patch("flows.coordinator.run_outline", new=AsyncMock(return_value=mock_outline)),
            patch("flows.coordinator.run_script", new=AsyncMock(side_effect=[mock_script, mock_script])),
            patch("flows.coordinator.run_evaluator", new=AsyncMock(return_value=(mock_feedback, mock_score))),
            patch("flows.coordinator.run_voice", new=AsyncMock(return_value=mock_narration)),
            patch("flows.coordinator.run_clips", new=AsyncMock(return_value=[])),
        ):
            result = await run(topic="No Save Test", save_run=False)

        # Verify no run directory was created
        assert not runs_dir.exists() or len(list(runs_dir.iterdir())) == 0
        assert result.run_id is None
