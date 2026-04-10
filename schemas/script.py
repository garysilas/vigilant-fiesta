from dataclasses import dataclass, field


@dataclass
class FinalScript:
    opening: str = ""
    body: str = ""
    closing: str = ""

    def full_text(self) -> str:
        return "\n\n".join(part for part in [self.opening, self.body, self.closing] if part)


@dataclass
class NarrationScript:
    text: str = ""


@dataclass
class Clip:
    hook: str = ""
    body: str = ""
    closing: str = ""


@dataclass
class ScriptFeedback:
    weaknesses: list[str] = field(default_factory=list)
    missing_angles: list[str] = field(default_factory=list)
    improvement_suggestions: list[str] = field(default_factory=list)
