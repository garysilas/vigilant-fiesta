import argparse
import asyncio
import json
import os

from dotenv import load_dotenv

from flows.coordinator import run
from tools.run_artifacts import load_json, _get_runs_dir


def _print_section(title: str, content: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    print(content)


def _print_clip(index: int, clip) -> None:
    print(f"\n{'-'*60}")
    print(f"  Clip {index + 1}")
    print(f"{'-'*60}")
    print(f"HOOK: {clip.hook}\n")
    print(f"BODY: {clip.body}\n")
    print(f"CLOSING: {clip.closing}")


def _inspect_run(run_id: str) -> None:
    """Inspect a previous run and display summary."""
    run_dir = os.path.join(_get_runs_dir(), run_id)

    if not os.path.exists(run_dir):
        print(f"Error: Run '{run_id}' not found.")
        return

    metadata_path = os.path.join(run_dir, "metadata.json")
    if not os.path.exists(metadata_path):
        print(f"Error: Metadata not found for run '{run_id}'.")
        return

    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    print(f"\n{'='*60}")
    print(f"  RUN INSPECTION: {run_id}")
    print(f"{'='*60}")
    print(f"Topic: {metadata.get('topic', 'N/A')}")
    print(f"Angle: {metadata.get('angle', 'N/A')}")
    print(f"Audience: {metadata.get('audience', 'N/A')}")
    print(f"Version: {metadata.get('version', 'N/A')}")

    config = metadata.get('config', {})
    print(f"Tone: {config.get('tone', 'N/A')}")
    print(f"Style: {config.get('style', 'N/A')}")

    # Check for scores
    scores_files = [f for f in os.listdir(run_dir) if f.startswith('scores_')]
    if scores_files:
        print(f"\nIterations: {len(scores_files)}")
        for sf in sorted(scores_files):
            with open(os.path.join(run_dir, sf), "r", encoding="utf-8") as f:
                scores = json.load(f)
            iter_num = sf.replace('scores_', '').replace('.json', '')
            print(f"  {iter_num}: overall={scores.get('overall_score', 'N/A')}")
    else:
        print("\nIterations: 1 (no scoring yet)")

    # Show best script path
    script_path = os.path.join(run_dir, "script_v1.txt")
    if os.path.exists(script_path):
        print(f"\nScript: {script_path}")

    print(f"\nFull run directory: {run_dir}")


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Content Engine - generate scripts from a topic")
    parser.add_argument("--topic", default=None, help="Topic to generate a script about")
    parser.add_argument("--angle", default=None, help="Optional angle or framing")
    parser.add_argument("--audience", default=None, help="Optional target audience")
    parser.add_argument("--red-lines", default=None, help="Optional things to avoid")
    parser.add_argument("--must-hits", default=None, help="Optional required talking points")
    parser.add_argument("--tone", default=None, help="Optional tone (e.g. serious, conversational)")
    parser.add_argument("--style", default=None, help="Optional style (e.g. documentary, editorial)")
    parser.add_argument(
        "--output_mode",
        default="all",
        choices=["draft", "narration", "clips", "all"],
        help="Output mode: draft (script only), narration (narration only), clips (clips only), all (everything)"
    )
    # Sprint 5 CLI flags
    parser.add_argument(
        "--save-run",
        type=lambda x: x.lower() in ('true', '1', 'yes'),
        default=True,
        help="Enable/disable run artifact saving (default: true)"
    )
    parser.add_argument("--run-id", default=None, help="Optional custom run ID (else auto-generate)")
    parser.add_argument("--max-iterations", type=int, default=1, help="Max rewrite iterations (default: 1)")
    parser.add_argument("--improvement-threshold", type=float, default=0.2, help="Stop if improvement below threshold (default: 0.2)")
    parser.add_argument("--no-rewrite", action="store_true", help="Skip rewrite pass entirely")
    parser.add_argument("--export", default=None, choices=["json", "txt", "all"], help="Export output format")
    parser.add_argument("--inspect-run", default=None, help="Inspect a previous run by ID")
    args = parser.parse_args()

    # Handle inspect-run mode
    if args.inspect_run:
        _inspect_run(args.inspect_run)
        return

    # Validate topic is provided for generation mode
    if not args.topic:
        parser.error("--topic is required (unless using --inspect-run)")

    print(f"[content-engine] Running pipeline for topic: {args.topic}")
    if args.run_id:
        print(f"[content-engine] Run ID: {args.run_id}")
    if args.save_run:
        print(f"[content-engine] Run artifacts will be saved")
    else:
        print(f"[content-engine] Run artifacts disabled")

    # Handle --no-rewrite flag (forces single iteration)
    max_iterations = 1 if args.no_rewrite else args.max_iterations

    result = asyncio.run(run(
        topic=args.topic,
        angle=args.angle,
        audience=args.audience,
        red_lines=args.red_lines,
        must_hits=args.must_hits,
        tone=args.tone,
        style=args.style,
        run_id=args.run_id,
        save_run=args.save_run,
        max_iterations=max_iterations,
        improvement_threshold=args.improvement_threshold,
    ))

    if args.output_mode in ("draft", "all"):
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

    if args.output_mode in ("narration", "all"):
        _print_section("NARRATION SCRIPT", result.narration.text)

    if args.output_mode in ("clips", "all"):
        print(f"\n{'='*60}")
        print(f"  SHORT-FORM CLIPS ({len(result.clips)} clips)")
        print(f"{'='*60}")
        for i, clip in enumerate(result.clips):
            _print_clip(i, clip)

    # Handle --export flag
    if args.export:
        export_results(result, args.export, args.run_id or result.run_id)


def export_results(result, export_format: str, run_id: str | None) -> None:
    """Export results to file(s)."""
    from pathlib import Path

    export_dir = Path("exports")
    export_dir.mkdir(exist_ok=True)

    base_name = run_id or "output"

    if export_format in ("txt", "all"):
        txt_path = export_dir / f"{base_name}.txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(f"Script:\n{result.script.full_text()}\n\n")
            f.write(f"Narration:\n{result.narration.text}\n")
        print(f"\n[content-engine] Exported to {txt_path}")

    if export_format in ("json", "all"):
        import json
        from dataclasses import asdict

        json_path = export_dir / f"{base_name}.json"
        data = {
            "script": {
                "opening": result.script.opening,
                "body": result.script.body,
                "closing": result.script.closing,
                "full_text": result.script.full_text(),
            },
            "narration": {"text": result.narration.text},
            "clips": [asdict(c) for c in result.clips],
            "run_id": result.run_id,
        }
        if result.score:
            data["score"] = asdict(result.score)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"[content-engine] Exported to {json_path}")


if __name__ == "__main__":
    main()
