from dataclasses import dataclass


@dataclass
class PersonaState:
    trust: int = 35
    stress: int = 60
    shame: int = 50
    hope: int = 40
    control_loss: int = 60
    difficulty: int = 2

    def clamp(self):
        for attr in ["trust", "stress", "shame", "hope", "control_loss"]:
            value = getattr(self, attr)
            setattr(self, attr, max(0, min(100, value)))

    def to_dict(self) -> dict:
        return {
            "trust": self.trust,
            "stress": self.stress,
            "shame": self.shame,
            "hope": self.hope,
            "control_loss": self.control_loss,
            "difficulty": self.difficulty,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

    def to_panel_text(self) -> str:
        return (
            f"Trust: {self.trust}\n"
            f"Stress: {self.stress}\n"
            f"Skam: {self.shame}\n"
            f"Håb: {self.hope}\n"
            f"Kontroltab: {self.control_loss}"
        )


def update_state_from_turn(state: PersonaState, user_text: str, ai_text: str, learning_goal: str) -> PersonaState:
    s = PersonaState.from_dict(state.to_dict())
    text = user_text.lower()

    validating_words = ["forstår", "giver mening", "hører", "tak", "valgmulighed", "hvad tænker du"]
    pressure_words = ["skal", "burde", "konsekvens", "sanktion", "nu gør du"]

    if any(w in text for w in validating_words):
        s.trust += 4
        s.hope += 3
        s.stress -= 3
        s.control_loss -= 3

    if any(w in text for w in pressure_words):
        s.trust -= 5
        s.stress += 5
        s.shame += 3
        s.control_loss += 4

    if learning_goal == "Deeskalering" and "rolig" in text:
        s.stress -= 2
        s.trust += 2

    if learning_goal == "Grænsesætning" and "ramme" in text:
        s.control_loss -= 2

    # Difficulty shifts baseline resistance.
    s.stress += max(0, s.difficulty - 2)
    s.control_loss += max(0, s.difficulty - 2)

    s.clamp()
    return s
