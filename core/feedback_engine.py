def build_end_feedback(turns: list[dict], learning_goal: str, state_history: list[dict]) -> str:
    user_turns = [t["content"] for t in turns if t["role"] == "user"]
    if not user_turns:
        return "Ingen samtale at evaluere endnu."

    start = state_history[0]
    end = state_history[-1]

    delta_trust = end["trust"] - start["trust"]
    delta_stress = end["stress"] - start["stress"]

    strengths = []
    improvements = []

    if delta_trust > 0:
        strengths.append("Du oegede tillid i samtalen.")
    else:
        improvements.append("Arbejd med flere validerende formuleringer for at oege tillid.")

    if delta_stress < 0:
        strengths.append("Du reducerede belastning/stress over tid.")
    else:
        improvements.append("Proev langsommere tempo og tydeligere struktur for at deeskalere.")

    if not strengths:
        strengths.append("Du holdt samtalen i gang under modstand.")

    if not improvements:
        improvements.append("Nae ste skridt: goer dine mikroaftaler endnu mere konkrete.")

    return (
        f"Laeringsmaal: {learning_goal}\n\n"
        f"3 styrker:\n"
        f"1. {strengths[0]}\n"
        f"2. {strengths[1] if len(strengths) > 1 else 'Du var vedholdende og respektfuld i tonen.'}\n"
        f"3. Du gennemfoerte sessionen med stabil kontakt.\n\n"
        f"2 forbedringspunkter:\n"
        f"1. {improvements[0]}\n"
        f"2. {improvements[1] if len(improvements) > 1 else 'Brug flere aabne spoergsmaal med valgmuligheder.'}\n\n"
        f"1 naeste oevelse:\n"
        f"- Start naeste samtale med rammesaetning + validering i de foerste 2-3 replikker."
    )
