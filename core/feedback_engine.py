def build_end_feedback(turns: list[dict], learning_goal: str, state_history: list[dict]) -> str:
    user_turns = [t["content"] for t in turns if t["role"] == "user"]
    if not user_turns:
        return "Ingen samtale at evaluere endnu."

    start = state_history[0]
    end = state_history[-1]

    delta_trust = end["trust"] - start["trust"]
    delta_stress = end["stress"] - start["stress"]
    delta_shame = end["shame"] - start["shame"]
    delta_hope = end["hope"] - start["hope"]
    delta_control = end["control_loss"] - start["control_loss"]

    strengths: list[str] = []
    improvements: list[str] = []

    # --- Trust ---
    if delta_trust > 10:
        strengths.append("Du opbyggede markant tillid i samtalen — stærkt relationsarbejde.")
    elif delta_trust > 0:
        strengths.append("Du øgede tilliden i samtalen.")
    else:
        improvements.append("Arbejd med flere validerende formuleringer for at øge tillid.")

    # --- Stress ---
    if delta_stress < -10:
        strengths.append("Du reducerede stress betydeligt — effektiv deeskalering.")
    elif delta_stress < 0:
        strengths.append("Du reducerede belastning/stress over tid.")
    else:
        improvements.append("Prøv langsommere tempo og tydeligere struktur for at deeskalere.")

    # --- Shame ---
    if delta_shame < -5:
        strengths.append("Du mindskede skamfølelsen — god brug af normaliserende sprog.")
    elif delta_shame > 5:
        improvements.append("Vær opmærksom på formuleringer, der kan øge skam. Prøv at normalisere mere.")

    # --- Hope ---
    if delta_hope > 10:
        strengths.append("Du styrkede håbet markant — personaen så nye muligheder.")
    elif delta_hope > 0:
        strengths.append("Du nærede håbet i samtalen.")
    elif delta_hope < -5:
        improvements.append("Brug flere åbne spørgsmål om fremtid og ønsker for at styrke håb.")

    # --- Control loss ---
    if delta_control < -10:
        strengths.append("Du gav personaen en oplevelse af indflydelse — flot autonomi-støtte.")
    elif delta_control < 0:
        strengths.append("Du reducerede oplevelsen af kontroltab.")
    elif delta_control > 5:
        improvements.append("Giv flere valgmuligheder og inddrag personaen i beslutninger.")

    # Ensure minimum counts for output format.
    fallback_strengths = [
        "Du holdt samtalen i gang under modstand.",
        "Du var vedholdende og respektfuld i tonen.",
        "Du gennemførte sessionen med stabil kontakt.",
    ]
    fallback_improvements = [
        "Brug flere åbne spørgsmål med valgmuligheder.",
        "Næste skridt: gør dine mikroaftaler endnu mere konkrete.",
    ]

    while len(strengths) < 3:
        for fb in fallback_strengths:
            if fb not in strengths:
                strengths.append(fb)
                break
        else:
            break

    while len(improvements) < 2:
        for fb in fallback_improvements:
            if fb not in improvements:
                improvements.append(fb)
                break
        else:
            break

    # Build next-exercise suggestion based on learning goal.
    exercises = {
        "Alliance": "Start næste samtale med rammesætning + validering i de første 2-3 replikker.",
        "Deeskalering": "Øv dig i at spejle følelser og sænke tempoet med pauser de første 3 ture.",
        "Grænsesætning": "Øv dig i at sætte en tydelig ramme tidligt og derefter tilbyde et valg.",
    }
    next_exercise = exercises.get(learning_goal, exercises["Alliance"])

    # Format state deltas for transparency.
    delta_summary = (
        f"Tillid: {start['trust']} → {end['trust']} ({delta_trust:+d}) | "
        f"Stress: {start['stress']} → {end['stress']} ({delta_stress:+d}) | "
        f"Skam: {start['shame']} → {end['shame']} ({delta_shame:+d}) | "
        f"Håb: {start['hope']} → {end['hope']} ({delta_hope:+d}) | "
        f"Kontroltab: {start['control_loss']} → {end['control_loss']} ({delta_control:+d})"
    )

    return (
        f"Læringsmål: {learning_goal}\n\n"
        f"Tilstandsændring:\n{delta_summary}\n\n"
        f"3 styrker:\n"
        + "\n".join(f"{i+1}. {s}" for i, s in enumerate(strengths[:3]))
        + f"\n\n2 forbedringspunkter:\n"
        + "\n".join(f"{i+1}. {imp}" for i, imp in enumerate(improvements[:2]))
        + f"\n\n1 næste øvelse:\n"
        f"- {next_exercise}"
    )
