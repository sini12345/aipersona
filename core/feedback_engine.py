import os

import anthropic


def _format_transcript(turns: list[dict], max_chars: int = 3000) -> str:
    """Komprimér transskription til max_chars tegn for at spare tokens."""
    lines = []
    for t in turns:
        role = "Studerende" if t["role"] == "user" else "Persona"
        lines.append(f"{role}: {t['content']}")
    full = "\n".join(lines)
    if len(full) > max_chars:
        return full[-max_chars:]
    return full


def _compute_deltas(state_history: list[dict]) -> str:
    if len(state_history) < 2:
        return "Ingen state-ændringer (for kort session)."
    start = state_history[0]
    end = state_history[-1]
    lines = []
    labels = {
        "trust": "Tillid",
        "stress": "Stress",
        "shame": "Skam",
        "hope": "Håb",
        "control_loss": "Kontroltab",
    }
    for key, label in labels.items():
        delta = end.get(key, 0) - start.get(key, 0)
        sign = "+" if delta >= 0 else ""
        lines.append(f"{label}: {start[key]} → {end[key]} ({sign}{delta})")
    return "\n".join(lines)


def _ai_feedback(transcript: str, deltas: str, learning_goal: str) -> str:
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise ValueError("Mangler ANTHROPIC_API_KEY.")

    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""Du er supervisionssupervisor for pædagogstuderende. En studerende har gennemført en øvelsessamtale med en simuleret bruger.

Læringsmål for sessionen: {learning_goal}

Ændringer i brugerens indre tilstand (positiv ændring = god kommunikation):
{deltas}

Udskrift af samtalen:
{transcript}

Skriv kort, præcis feedback på dansk. Strukturér det sådan:

3 STYRKER
Nævn tre konkrete ting den studerende gjorde godt — med direkte reference til samtaleteksten.

2 FORBEDRINGSPUNKTER
Nævn to specifikke kommunikationsmønstre der bremste kontakten eller øgede modstand.

1 NÆSTE ØVELSE
Beskriv én konkret øvelse til næste session baseret på det svageste punkt.

Vær specifik og konstruktiv. Undgå generelle fraser. Hold det under 300 ord."""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=450,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def _rule_based_feedback(learning_goal: str, state_history: list[dict]) -> str:
    """Fallback hvis API-kald fejler."""
    start = state_history[0]
    end = state_history[-1]
    delta_trust = end["trust"] - start["trust"]
    delta_stress = end["stress"] - start["stress"]

    strengths = []
    improvements = []

    if delta_trust > 0:
        strengths.append("Du øgede tillid i samtalen.")
    else:
        improvements.append("Arbejd med flere validerende formuleringer for at øge tillid.")

    if delta_stress < 0:
        strengths.append("Du reducerede stress over tid.")
    else:
        improvements.append("Prøv langsommere tempo og tydeligere struktur for at deeskalere.")

    if not strengths:
        strengths.append("Du holdt samtalen i gang under modstand.")
    if not improvements:
        improvements.append("Næste skridt: gør dine mikroaftaler endnu mere konkrete.")

    return (
        f"Læringsmål: {learning_goal}\n\n"
        f"3 styrker:\n"
        f"1. {strengths[0]}\n"
        f"2. {strengths[1] if len(strengths) > 1 else 'Du var vedholdende og respektfuld i tonen.'}\n"
        f"3. Du gennemførte sessionen med stabil kontakt.\n\n"
        f"2 forbedringspunkter:\n"
        f"1. {improvements[0]}\n"
        f"2. {improvements[1] if len(improvements) > 1 else 'Brug flere åbne spørgsmål med valgmuligheder.'}\n\n"
        f"1 næste øvelse:\n"
        f"- Start næste samtale med rammesætning + validering i de første 2-3 replikker."
    )


def build_end_feedback(turns: list[dict], learning_goal: str, state_history: list[dict]) -> str:
    user_turns = [t for t in turns if t["role"] == "user"]
    if not user_turns:
        return "Ingen samtale at evaluere endnu."

    transcript = _format_transcript(turns)
    deltas = _compute_deltas(state_history)

    try:
        return _ai_feedback(transcript, deltas, learning_goal)
    except Exception as e:
        fallback = _rule_based_feedback(learning_goal, state_history)
        return f"{fallback}\n\n(AI-feedback utilgængelig: {e})"
