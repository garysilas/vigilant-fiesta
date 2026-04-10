from dataclasses import dataclass, field


@dataclass
class Source:
    title: str
    url: str
    summary: str
    credibility_score: float = 0.0
    recency: str = ""
    bias_flag: str = ""


@dataclass
class ResearchBrief:
    key_facts: list[str] = field(default_factory=list)
    key_tensions: list[str] = field(default_factory=list)
    relevant_examples: list[str] = field(default_factory=list)
    caveats: list[str] = field(default_factory=list)
    source_notes: list[str] = field(default_factory=list)
    sources: list[Source] = field(default_factory=list)
