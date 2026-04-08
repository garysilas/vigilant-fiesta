from dataclasses import dataclass


@dataclass
class FinalScript:
    opening: str = ""
    body: str = ""
    closing: str = ""

    def full_text(self) -> str:
        return "\n\n".join(part for part in [self.opening, self.body, self.closing] if part)
