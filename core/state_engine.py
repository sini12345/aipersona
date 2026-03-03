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


SIGNAL_PATTERNS = {
    "validation": ["forstår", "giver mening", "jeg hører dig", "tak", "det lyder svært", "kan godt se"],
    "pressure": ["skal", "burde", "konsekvens", "sanktion", "nu gør du", "du må"],
    "choice_language": ["vil du", "kan vi", "du kan vælge", "hvad tænker du", "hvad vil du helst"],
    "calm_language": ["rolig", "træk vejret", "en ting ad gangen", "tag det roligt", "vi tager det stille"],
    "boundary_language": ["ramme", "grænse", "aftale", "forventning", "tydeligt"],
    "structure_language": ["plan", "næste skridt", "først", "bagefter", "i dag gør vi"],
    "coercive_tone": ["ellers", "hvis ikke", "du skal bare", "ingen diskussion"],
}


LEARNING_GOAL_PROFILES = {
    "Alliance": {
        "validation": {"trust": 3, "stress": -2, "shame": -1, "hope": 2, "control_loss": -1},
        "choice_language": {"trust": 2, "stress": -1, "hope": 1, "control_loss": -1},
        "open_question": {"trust": 1, "stress": -1},
        "structure_language": {"trust": 1, "stress": -1},
        "pressure": {"trust": -4, "stress": 4, "shame": 2, "control_loss": 3},
        "coercive_tone": {"trust": -3, "stress": 3, "shame": 1, "control_loss": 2},
    },
    "Deeskalering": {
        "validation": {"trust": 2, "stress": -2, "shame": -1, "hope": 1, "control_loss": -1},
        "choice_language": {"trust": 1, "stress": -2, "hope": 1, "control_loss": -1},
        "open_question": {"trust": 1, "stress": -1},
        "calm_language": {"trust": 2, "stress": -4, "hope": 1, "control_loss": -2},
        "structure_language": {"trust": 1, "stress": -2, "control_loss": -1},
        "pressure": {"trust": -4, "stress": 5, "shame": 2, "control_loss": 4},
        "coercive_tone": {"trust": -4, "stress": 4, "shame": 2, "control_loss": 3},
    },
    "Grænsesætning": {
        "validation": {"trust": 2, "stress": -1, "hope": 1},
        "choice_language": {"trust": 1, "stress": -1, "control_loss": -1},
        "boundary_language": {"trust": 1, "stress": -1, "hope": 1, "control_loss": -3},
        "structure_language": {"trust": 1, "stress": -1, "control_loss": -1},
        "pressure": {"trust": -3, "stress": 3, "shame": 2, "control_loss": 3},
        "coercive_tone": {"trust": -3, "stress": 3, "shame": 1, "control_loss": 2},
    },
}


DELTA_CAPS = {
    "trust": 6,
    "stress": 8,
    "shame": 6,
    "hope": 6,
    "control_loss": 8,
}


SCENARIO_MODIFIER_KEYS = {
    "validation_boost_mult": {"validation"},
    "pressure_penalty_mult": {"pressure", "coercive_tone"},
    "deescalation_boost_mult": {"calm_language", "structure_language", "choice_language"},
    "boundary_boost_mult": {"boundary_language"},
}


def _extract_signals(user_text: str) -> dict[str, int]:
    text = user_text.lower().strip()
    signals: dict[str, int] = {}

    for signal, patterns in SIGNAL_PATTERNS.items():
        signals[signal] = sum(1 for pattern in patterns if pattern in text)

    question_starters = ("hvad", "hvordan", "hvilken", "hvilke", "hvorfor", "hvem")
    has_question_mark = "?" in text
    starts_open = any(text.startswith(starter) for starter in question_starters)
    signals["open_question"] = 1 if has_question_mark or starts_open else 0
    return signals


def _signal_multiplier(signal: str, modifiers: dict[str, float]) -> float:
    mult = 1.0
    for key, signal_set in SCENARIO_MODIFIER_KEYS.items():
        if signal not in signal_set:
            continue
        raw = modifiers.get(key, 1.0)
        try:
            value = float(raw)
        except (TypeError, ValueError):
            value = 1.0
        mult *= max(0.0, value)
    return mult


def _apply_profile_weights(
    deltas: dict[str, int],
    signals: dict[str, int],
    learning_goal: str,
    scenario_modifiers: dict[str, float] | None = None,
):
    modifiers = scenario_modifiers or {}
    profile = LEARNING_GOAL_PROFILES.get(learning_goal, LEARNING_GOAL_PROFILES["Alliance"])
    for signal, count in signals.items():
        if count <= 0:
            continue
        weight_map = profile.get(signal, {})
        mult = _signal_multiplier(signal, modifiers)
        for metric, weight in weight_map.items():
            deltas[metric] += round(weight * count * mult)


def _apply_ai_text_adjustments(deltas: dict[str, int], ai_text: str):
    words = ai_text.split()
    if len(words) >= 28:
        # Longer, more nuanced persona reply usually indicates increased openness.
        deltas["trust"] += 1
        deltas["hope"] += 1
        deltas["stress"] -= 1
    elif len(words) <= 5:
        # Very short replies often indicate shutdown or distrust.
        deltas["trust"] -= 1
        deltas["stress"] += 1


def _apply_difficulty_resistance(deltas: dict[str, int], difficulty: int):
    baseline = max(0, difficulty - 2)
    deltas["stress"] += baseline
    deltas["control_loss"] += baseline


def _clip_deltas(deltas: dict[str, int]) -> dict[str, int]:
    for metric, cap in DELTA_CAPS.items():
        deltas[metric] = max(-cap, min(cap, deltas[metric]))
    return deltas


def update_state_from_turn(
    state: PersonaState,
    user_text: str,
    ai_text: str,
    learning_goal: str,
    scenario_modifiers: dict[str, float] | None = None,
) -> PersonaState:
    s = PersonaState.from_dict(state.to_dict())
    deltas = {"trust": 0, "stress": 0, "shame": 0, "hope": 0, "control_loss": 0}

    signals = _extract_signals(user_text)
    _apply_profile_weights(deltas, signals, learning_goal, scenario_modifiers=scenario_modifiers)
    _apply_ai_text_adjustments(deltas, ai_text)
    _apply_difficulty_resistance(deltas, s.difficulty)
    deltas = _clip_deltas(deltas)

    s.trust += deltas["trust"]
    s.stress += deltas["stress"]
    s.shame += deltas["shame"]
    s.hope += deltas["hope"]
    s.control_loss += deltas["control_loss"]

    s.clamp()
    return s
