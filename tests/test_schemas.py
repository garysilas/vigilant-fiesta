from schemas.research import ResearchBrief, Source
from schemas.outline import CommentaryOutline, OutlineSection
from schemas.script import FinalScript


def test_research_brief_defaults():
    brief = ResearchBrief()
    assert brief.key_facts == []
    assert brief.key_tensions == []
    assert brief.relevant_examples == []
    assert brief.caveats == []
    assert brief.source_notes == []
    assert brief.sources == []


def test_source_fields():
    source = Source(title="Article A", url="https://example.com", summary="A summary")
    assert source.title == "Article A"
    assert source.url == "https://example.com"
    assert source.summary == "A summary"


def test_research_brief_with_sources():
    source = Source(title="Article A", url="https://example.com", summary="A summary")
    brief = ResearchBrief(sources=[source])
    assert len(brief.sources) == 1
    assert brief.sources[0].title == "Article A"


def test_research_brief_populated():
    brief = ResearchBrief(
        key_facts=["fact1"],
        key_tensions=["tension1"],
        relevant_examples=["example1"],
        caveats=["caveat1"],
        source_notes=["source1"],
    )
    assert len(brief.key_facts) == 1
    assert brief.key_facts[0] == "fact1"


def test_commentary_outline_defaults():
    outline = CommentaryOutline()
    assert outline.hook == ""
    assert outline.thesis == ""
    assert outline.sections == []
    assert outline.emotional_progression == ""
    assert outline.closing_idea == ""


def test_commentary_outline_with_sections():
    section = OutlineSection(title="Act 1", argument="Setup the problem")
    outline = CommentaryOutline(
        hook="Did you know...",
        thesis="Young men face structural disadvantages",
        sections=[section],
        emotional_progression="curiosity → tension → resolution",
        closing_idea="systemic change is needed",
    )
    assert len(outline.sections) == 1
    assert outline.sections[0].title == "Act 1"


def test_final_script_full_text():
    script = FinalScript(opening="Hello.", body="Middle part.", closing="Goodbye.")
    assert script.full_text() == "Hello.\n\nMiddle part.\n\nGoodbye."


def test_final_script_full_text_partial():
    script = FinalScript(opening="Hello.", body="", closing="Goodbye.")
    assert script.full_text() == "Hello.\n\nGoodbye."


def test_final_script_defaults():
    script = FinalScript()
    assert script.full_text() == ""
