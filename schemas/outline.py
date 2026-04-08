from dataclasses import dataclass, field


@dataclass
class OutlineSection:
    title: str
    argument: str


@dataclass
class CommentaryOutline:
    hook: str = ""
    thesis: str = ""
    sections: list[OutlineSection] = field(default_factory=list)
    emotional_progression: str = ""
    closing_idea: str = ""
