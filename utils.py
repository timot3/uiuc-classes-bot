from dataclasses import dataclass

@dataclass
class Course:
    subject: str
    number: str
    section: str = None

    def __str__(self) -> str:
        return f"{self.subject.upper()}{self.number}{self.section.upper() if self.section is not None else ''}"
    
    def __hash__(self) -> int:
        return hash(str(self))