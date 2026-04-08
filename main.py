import argparse
import asyncio

from dotenv import load_dotenv

from flows.coordinator import run


def _print_section(title: str, content: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    print(content)


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Content Engine - generate scripts from a topic")
    parser.add_argument("--topic", required=True, help="Topic to generate a script about")
    parser.add_argument("--angle", default=None, help="Optional angle or framing")
    parser.add_argument("--audience", default=None, help="Optional target audience")
    parser.add_argument("--red-lines", default=None, help="Optional things to avoid")
    parser.add_argument("--must-hits", default=None, help="Optional required talking points")
    args = parser.parse_args()

    print(f"[content-engine] Running pipeline for topic: {args.topic}")

    result = asyncio.run(run(
        topic=args.topic,
        angle=args.angle,
        audience=args.audience,
        red_lines=args.red_lines,
        must_hits=args.must_hits,
    ))

    brief = result.brief
    _print_section("RESEARCH BRIEF", (
        f"Key facts:\n" + "\n".join(f"  - {f}" for f in brief.key_facts) +
        f"\n\nKey tensions:\n" + "\n".join(f"  - {t}" for t in brief.key_tensions) +
        f"\n\nRelevant examples:\n" + "\n".join(f"  - {e}" for e in brief.relevant_examples) +
        f"\n\nCaveats:\n" + "\n".join(f"  - {c}" for c in brief.caveats) +
        f"\n\nSource notes:\n" + "\n".join(f"  - {s}" for s in brief.source_notes)
    ))

    outline = result.outline
    sections_text = "\n".join(f"  {i+1}. {s.title}: {s.argument}" for i, s in enumerate(outline.sections))
    _print_section("COMMENTARY OUTLINE", (
        f"Hook: {outline.hook}\n"
        f"Thesis: {outline.thesis}\n\n"
        f"Sections:\n{sections_text}\n\n"
        f"Emotional progression: {outline.emotional_progression}\n"
        f"Closing idea: {outline.closing_idea}"
    ))

    _print_section("FINAL SCRIPT", result.script.full_text())


if __name__ == "__main__":
    main()
