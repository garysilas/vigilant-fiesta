import json
import os
import re
from dataclasses import asdict
from pathlib import Path

from schemas.research import ResearchBrief, Source
from tools.logger import log

KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "data" / "knowledge"


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[\s_-]+", "_", text)[:80]


def save_research_brief(brief: ResearchBrief, topic: str) -> Path:
    KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{_slugify(topic)}.json"
    path = KNOWLEDGE_DIR / filename
    data = {
        "topic": topic,
        "brief": asdict(brief),
    }
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    log("knowledge_store", "saved", filename=path.name, topic=topic)
    return path


def load_relevant_knowledge(topic: str) -> list[ResearchBrief]:
    if not KNOWLEDGE_DIR.exists():
        return []

    topic_lower = topic.lower()
    topic_words = set(topic_lower.split())
    results: list[ResearchBrief] = []

    for file in sorted(KNOWLEDGE_DIR.glob("*.json")):
        try:
            data = json.loads(file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        stored_topic = data.get("topic", "")
        stored_words = set(stored_topic.lower().split())
        if not topic_words & stored_words:
            continue

        brief_data = data.get("brief", {})
        sources = [
            Source(
                title=s.get("title", ""),
                url=s.get("url", ""),
                summary=s.get("summary", ""),
                credibility_score=float(s.get("credibility_score", 0.0)),
                recency=s.get("recency", ""),
                bias_flag=s.get("bias_flag", ""),
            )
            for s in brief_data.get("sources", [])
        ]
        results.append(
            ResearchBrief(
                key_facts=brief_data.get("key_facts", []),
                key_tensions=brief_data.get("key_tensions", []),
                relevant_examples=brief_data.get("relevant_examples", []),
                caveats=brief_data.get("caveats", []),
                source_notes=brief_data.get("source_notes", []),
                sources=sources,
            )
        )

    if results:
        log("knowledge_store", "loaded", count=len(results), topic=topic)
    return results
