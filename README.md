# Content Engine v5

Generates long-form commentary scripts using the OpenAI Agents SDK. Version 5 features iterative optimization, run artifact tracking, and enhanced scoring.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
# Edit .env and set OPENAI_API_KEY and TAVILY_API_KEY
```

## Basic Usage

```bash
python main.py --topic "Why young men are struggling financially"
python main.py --topic "Topic" --angle "Angle" --audience "Audience"
```

## v5 Features

### Iterative Script Optimization

```bash
# Run up to 3 iterations, stopping early if improvement < 0.2
python main.py --topic "AI Safety" --max-iterations 3 --improvement-threshold 0.2

# Skip rewrite pass entirely
python main.py --topic "Quick Draft" --no-rewrite
```

### Run Artifact Tracking

```bash
# Save run with custom ID
python main.py --topic "Test" --run-id "my-run-001" --save-run

# Inspect a previous run
python main.py --inspect-run my-run-001
```

### Export Results

```bash
# Export to txt file
python main.py --topic "Test" --export txt

# Export to json with full metadata
python main.py --topic "Test" --export json

# Export both formats
python main.py --topic "Test" --export all
```

### Output Modes

```bash
# Show only the draft script
python main.py --topic "Test" --output_mode draft

# Show only narration-ready script
python main.py --topic "Test" --output_mode narration

# Show only short-form clips
python main.py --topic "Test" --output_mode clips
```

## Project Structure

```text
engine_agents/   agent definitions (research, outline, script, evaluator, voice, clips)
tools/           tool functions (web_search, knowledge_store, run_artifacts, logger, scoring)
schemas/         typed output models (ResearchBrief, CommentaryOutline, FinalScript, ScriptScore)
flows/           coordinator orchestration logic with iteration loop
tests/           pytest tests (148 passing)
```

## CLI Reference

| Flag | Description | Default |
| ------ | ----------- | ------- |
| `--topic` | Topic to generate script about | Required |
| `--angle` | Optional angle/framing | None |
| `--audience` | Target audience | None |
| `--tone` | Tone (serious, conversational) | None |
| `--style` | Style (documentary, editorial) | None |
| `--max-iterations` | Max rewrite iterations | 1 |
| `--improvement-threshold` | Stop if improvement below this | 0.2 |
| `--no-rewrite` | Skip rewrite pass | False |
| `--save-run` | Enable artifact saving | True |
| `--run-id` | Custom run ID | Auto-generated |
| `--inspect-run` | Inspect previous run by ID | None |
| `--export` | Export format (json/txt/all) | None |
| `--output_mode` | Output mode (draft/narration/clips/all) | all |

## Run Tests

```bash
pytest                    # Run all tests
pytest -v                 # Verbose output
pytest tests/test_final_integration.py  # Run integration tests only
```

## Iteration Loop

The coordinator now supports iterative script optimization:

1. **Initial script** is generated
2. **Evaluator** scores the script (clarity, argument, emotional impact, factual grounding)
3. **Script agent** rewrites with feedback
4. **Loop continues** up to `max_iterations`
5. **Early stopping** if improvement < `improvement_threshold`
6. **Best script** (by overall_score) is selected for voice/clips

Artifacts saved per iteration: `script_v{i}.txt`, `scores_v{i}.json`, `feedback_v{i}.json`
