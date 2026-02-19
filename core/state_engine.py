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
            f"Tillid:      {self.trust}/100\n"
            f"Stress:      {self.stress}/100\n"
            f"Skam:        {self.shame}/100\n"
            f"Håb:         {self.hope}/100\n"
            f"Kontroltab:  {self.control_loss}/100"
        )


# --- Ordlister ---

# Anerkendende og validerende sprog
_VALIDATING = [
    "forstår", "giver mening", "hører", "tak", "valgmulighed",
    "hvad tænker du", "hvad vil du", "hvad synes du", "det lyder svært",
    "det er din beslutning", "det er op til dig", "du bestemmer",
    "det kan godt være svært", "det giver mening", "jeg hører dig",
    "hvad er vigtigt for dig", "hvad vil det betyde", "fortæl mig mere",
    "jeg er nysgerrig", "hvad tænker du om",
]

# Åbne, nysgerrige spørgsmål (giver ekstra trust + hope)
_OPEN_QUESTIONS = [
    "hvad betyder", "hvad drømmer du", "hvad giver dig", "hvad handler det om",
    "hvad savner du", "hvad vil du helst", "hvad ville ændre", "hvad er dit",
    "hvad håber du", "fortæl mig", "kan du fortælle", "hvad har du",
]

# Konkrete mikroaftaler og valg (sænker kontroltab, øger håb)
_CONCRETE_STEPS = [
    "næste skridt", "mikroaftale", "aftale om", "vi aftaler", "en ting",
    "til næste gang", "hvad kan vi gøre", "hvad er muligt", "hvad virker",
    "vælg selv", "du vælger", "to muligheder", "tre muligheder",
]

# Pres, moralisering og krav
_PRESSURE = [
    "skal", "burde", "konsekvens", "sanktion", "nu gør du", "du er nødt til",
    "krav", "det forventes", "du mangler", "fravær", "du har ikke", "du skal møde",
    "regler siger", "lovgivningen kræver", "det er et krav", "ellers",
    "advarsel", "det kan betyde", "det koster",
]

# Bagatellisering (øger skam, sænker trust)
_MINIMIZING = [
    "det er ikke så slemt", "det er bare", "alle har det sådan", "det går nok",
    "du ser frisk ud", "du er ung", "det er en dårlig dag", "tag dig sammen",
    "prøv bare", "du skal ikke lade dig", "det er ikke noget",
]

# Persona-specifik modstandsvægtning ved pres
_PERSONA_PRESSURE_MULTIPLIER = {
    "Ali": 1.2,
    "Mika": 1.4,   # Mika er mest sensitiv over for pres og sanktioner
    "Sofie": 0.9,  # Sofie internaliserer — reagerer mere med skam end åben modstand
    "Bent": 1.1,   # Bent reagerer stærkt ved krænkelse af autonomi
}

# Persona-specifik bagatelliserings-vægtning
_PERSONA_MINIMIZING_MULTIPLIER = {
    "Ali": 1.0,
    "Mika": 1.2,
    "Sofie": 1.4,  # Sofie er særligt sensitiv over for bagatellisering af kognitive udfordringer
    "Bent": 1.1,
}


def update_state_from_turn(
    state: PersonaState,
    user_text: str,
    ai_text: str,
    learning_goal: str,
    persona_name: str = "Ali",
) -> PersonaState:
    s = PersonaState.from_dict(state.to_dict())
    text = user_text.lower()

    pressure_mult = _PERSONA_PRESSURE_MULTIPLIER.get(persona_name, 1.0)
    minimize_mult = _PERSONA_MINIMIZING_MULTIPLIER.get(persona_name, 1.0)

    # Validerende sprog
    if any(w in text for w in _VALIDATING):
        s.trust += 4
        s.hope += 3
        s.stress -= 3
        s.control_loss -= 3

    # Åbne, nysgerrige spørgsmål
    if any(w in text for w in _OPEN_QUESTIONS):
        s.trust += 3
        s.hope += 2
        s.shame -= 2

    # Konkrete næste skridt og mikroaftaler
    if any(w in text for w in _CONCRETE_STEPS):
        s.control_loss -= 4
        s.hope += 4
        s.stress -= 2

    # Pres og krav (persona-vægtet)
    if any(w in text for w in _PRESSURE):
        s.trust -= int(5 * pressure_mult)
        s.stress += int(5 * pressure_mult)
        s.shame += int(3 * pressure_mult)
        s.control_loss += int(4 * pressure_mult)

    # Bagatellisering (persona-vægtet)
    if any(w in text for w in _MINIMIZING):
        s.shame += int(4 * minimize_mult)
        s.trust -= int(3 * minimize_mult)
        s.hope -= 2

    # Læringsmål-specifikke effekter
    if learning_goal == "Deeskalering" and any(w in text for w in ["rolig", "stille", "pause", "tid"]):
        s.stress -= 3
        s.trust += 2

    if learning_goal == "Grænsesætning" and any(w in text for w in ["ramme", "aftale", "grænse", "tydelig"]):
        s.control_loss -= 3
        s.trust += 1

    if learning_goal == "Alliance" and any(w in text for w in ["sammen", "vi", "fælles", "samarbejde"]):
        s.trust += 2
        s.hope += 2

    # Sværhedsgradens baseline modstand
    s.stress += max(0, s.difficulty - 2)
    s.control_loss += max(0, s.difficulty - 2)

    s.clamp()
    return s
