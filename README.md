# Content Engine

Generates long-form commentary scripts using the OpenAI Agents SDK.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
# Edit .env and set OPENAI_API_KEY
```

## Usage

```bash
python main.py --topic "Why young men are struggling financially"
python main.py --topic "Topic" --angle "Angle" --audience "Audience"
```

## Project structure

```
agents/     agent definitions (research, outline, script, coordinator)
tools/      tool functions used by agents
schemas/    typed output models
flows/      coordinator orchestration logic
tests/      pytest tests
```

## Run tests

```bash
pytest
```
