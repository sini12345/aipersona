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


def _count_matches(text: str, words: list[str]) -> int:
    return sum(1 for w in words if w in text)


def update_state_from_turn(state: PersonaState, user_text: str, ai_text: str, learning_goal: str) -> PersonaState:
    s = PersonaState.from_dict(state.to_dict())
    text = user_text.lower()

    # --- Validating language (builds trust, reduces stress) ---
    validating_words = [
        "forstår", "giver mening", "hører dig", "tak", "valgmulighed",
        "hvad tænker du", "fortæl mig", "det lyder", "jeg kan godt se",
        "det er okay", "i dit tempo", "du bestemmer", "hvad vil du",
        "hvordan oplever du", "det giver mening",
    ]
    val_hits = _count_matches(text, validating_words)
    if val_hits:
        boost = min(val_hits, 3)  # cap at 3 to avoid runaway gains
        s.trust += 3 * boost
        s.hope += 2 * boost
        s.stress -= 2 * boost
        s.shame -= 1 * boost
        s.control_loss -= 2 * boost

    # --- Pressure language (erodes trust, raises stress/shame) ---
    pressure_words = [
        "skal", "burde", "konsekvens", "sanktion", "nu gør du",
        "du må ikke", "det duer ikke", "tag dig sammen", "det er din skyld",
        "hvorfor gjorde du", "det var forkert", "du skulle have",
    ]
    press_hits = _count_matches(text, pressure_words)
    if press_hits:
        penalty = min(press_hits, 3)
        s.trust -= 4 * penalty
        s.stress += 4 * penalty
        s.shame += 3 * penalty
        s.hope -= 2 * penalty
        s.control_loss += 3 * penalty

    # --- Curiosity / open questions (builds hope and trust) ---
    curiosity_words = [
        "hvad synes du", "kan du fortælle", "hvordan har du det",
        "hvad er vigtigt", "hvad drømmer du", "hvad kunne hjælpe",
    ]
    if any(w in text for w in curiosity_words):
        s.hope += 3
        s.trust += 2
        s.shame -= 2

    # --- Normalising language (reduces shame) ---
    normalising_words = [
        "det er helt normalt", "mange oplever", "det kan ske for alle",
        "der er ingen der dømmer", "det er forståeligt",
    ]
    if any(w in text for w in normalising_words):
        s.shame -= 4
        s.hope += 2
        s.stress -= 1

    # --- Learning-goal-specific bonuses ---
    if learning_goal == "Deeskalering":
        calming = ["rolig", "ro på", "lad os tage den langsomt", "trække vejret", "pause"]
        if any(w in text for w in calming):
            s.stress -= 3
            s.trust += 2
            s.control_loss -= 2

    if learning_goal == "Grænsesætning":
        framing = ["ramme", "aftale", "grænse", "vi aftaler", "tydeligt"]
        if any(w in text for w in framing):
            s.control_loss -= 3
            s.trust += 1

    if learning_goal == "Alliance":
        alliance = ["sammen", "vi to", "fælles", "med dig", "ved din side"]
        if any(w in text for w in alliance):
            s.trust += 3
            s.hope += 2
            s.stress -= 1

    # Difficulty shifts baseline resistance.
    s.stress += max(0, s.difficulty - 2)
    s.control_loss += max(0, s.difficulty - 2)

    s.clamp()
    return s
