import json
import shutil
from pathlib import Path
from unittest.mock import patch

import pytest

from schemas.research import ResearchBrief, Source
from tools.knowledge_store import (
    KNOWLEDGE_DIR,
    _slugify,
    load_relevant_knowledge,
    save_research_brief,
)

MOCK_BRIEF = ResearchBrief(
    key_facts=["fact1", "fact2"],
    key_tensions=["tension1"],
    relevant_examples=["example1"],
    caveats=["caveat1"],
    source_notes=["source1"],
    sources=[Source(title="Article A", url="https://example.com/a", summary="Summary A")],
)


@pytest.fixture
def tmp_knowledge_dir(tmp_path):
    knowledge_dir = tmp_path / "knowledge"
    knowledge_dir.mkdir()
    with patch("tools.knowledge_store.KNOWLEDGE_DIR", knowledge_dir):
        yield knowledge_dir


def test_slugify_basic():
    assert _slugify("Hello World") == "hello_world"


def test_slugify_special_chars():
    assert _slugify("AI & Machine Learning!") == "ai_machine_learning"


def test_slugify_truncates():
    long_text = "a " * 100
    result = _slugify(long_text)
    assert len(result) <= 80


def test_save_research_brief_creates_file(tmp_knowledge_dir):
    path = save_research_brief(MOCK_BRIEF, "Test Topic")
    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["topic"] == "Test Topic"
    assert data["brief"]["key_facts"] == ["fact1", "fact2"]
    assert len(data["brief"]["sources"]) == 1
    assert data["brief"]["sources"][0]["title"] == "Article A"


def test_save_research_brief_filename(tmp_knowledge_dir):
    path = save_research_brief(MOCK_BRIEF, "AI in 2026")
    assert path.name == "ai_in_2026.json"


def test_save_research_brief_overwrites(tmp_knowledge_dir):
    save_research_brief(MOCK_BRIEF, "Same Topic")
    updated_brief = ResearchBrief(key_facts=["updated_fact"])
    save_research_brief(updated_brief, "Same Topic")
    path = tmp_knowledge_dir / "same_topic.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["brief"]["key_facts"] == ["updated_fact"]


def test_load_relevant_knowledge_empty(tmp_knowledge_dir):
    results = load_relevant_knowledge("Nonexistent topic xyz")
    assert results == []


def test_load_relevant_knowledge_matches(tmp_knowledge_dir):
    save_research_brief(MOCK_BRIEF, "AI trends")
    results = load_relevant_knowledge("AI research")
    assert len(results) == 1
    assert results[0].key_facts == ["fact1", "fact2"]
    assert len(results[0].sources) == 1
    assert isinstance(results[0].sources[0], Source)


def test_load_relevant_knowledge_no_match(tmp_knowledge_dir):
    save_research_brief(MOCK_BRIEF, "AI trends")
    results = load_relevant_knowledge("cooking recipes")
    assert results == []


def test_load_relevant_knowledge_multiple_matches(tmp_knowledge_dir):
    save_research_brief(MOCK_BRIEF, "AI trends 2026")
    brief2 = ResearchBrief(key_facts=["other_fact"])
    save_research_brief(brief2, "AI safety")
    results = load_relevant_knowledge("AI developments")
    assert len(results) == 2


def test_load_relevant_knowledge_missing_dir(tmp_path):
    missing_dir = tmp_path / "nonexistent"
    with patch("tools.knowledge_store.KNOWLEDGE_DIR", missing_dir):
        results = load_relevant_knowledge("anything")
    assert results == []


def test_load_relevant_knowledge_corrupt_file(tmp_knowledge_dir):
    bad_file = tmp_knowledge_dir / "bad.json"
    bad_file.write_text("not valid json", encoding="utf-8")
    results = load_relevant_knowledge("bad")
    assert results == []


def test_roundtrip(tmp_knowledge_dir):
    save_research_brief(MOCK_BRIEF, "roundtrip test")
    results = load_relevant_knowledge("roundtrip")
    assert len(results) == 1
    loaded = results[0]
    assert loaded.key_facts == MOCK_BRIEF.key_facts
    assert loaded.key_tensions == MOCK_BRIEF.key_tensions
    assert loaded.relevant_examples == MOCK_BRIEF.relevant_examples
    assert loaded.caveats == MOCK_BRIEF.caveats
    assert loaded.source_notes == MOCK_BRIEF.source_notes
    assert len(loaded.sources) == len(MOCK_BRIEF.sources)
    assert loaded.sources[0].title == MOCK_BRIEF.sources[0].title
    assert loaded.sources[0].url == MOCK_BRIEF.sources[0].url
    assert loaded.sources[0].summary == MOCK_BRIEF.sources[0].summary


def test_roundtrip_source_scoring(tmp_knowledge_dir):
    scored_source = Source(
        title="Scored", url="https://scored.com", summary="S",
        credibility_score=0.92, recency="2025", bias_flag="none",
    )
    brief = ResearchBrief(key_facts=["f1"], sources=[scored_source])
    save_research_brief(brief, "scoring roundtrip")
    results = load_relevant_knowledge("scoring")
    assert len(results) == 1
    loaded_src = results[0].sources[0]
    assert loaded_src.credibility_score == 0.92
    assert loaded_src.recency == "2025"
    assert loaded_src.bias_flag == "none"
