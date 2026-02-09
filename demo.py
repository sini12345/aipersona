"""
Interaktiv CLI-demo: Persona Træningsplatform
Med teori-valg til social- og specialpædagogisk uddannelse
"""

from persona_engine import PersonaEngine


def select_persona() -> str:
    """Lader brugeren vælge en persona."""
    personas = PersonaEngine.list_personas()

    print("=" * 65)
    print("  PERSONA TRÆNINGSPLATFORM")
    print("  Social- og specialpædagogisk samtale-simulation")
    print("=" * 65)
    print()
    print("Vælg hvem du vil tale med:\n")

    for i, p in enumerate(personas, 1):
        themes = ", ".join(p["themes"][:3])
        print(f"  {i}. {p['name']} ({p['age']} år) - {p['context']}")
        print(f"     {p['background_short']}")
        print(f"     Temaer: {themes}")
        print()

    while True:
        choice = input(f"Vælg persona (1-{len(personas)}): ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(personas):
                return personas[idx]["id"]
        except ValueError:
            pass
        print("Ugyldigt valg. Prøv igen.")


def select_theory() -> str | None:
    """Lader brugeren vælge en teori (valgfri)."""
    theories = PersonaEngine.list_theories()

    print()
    print("-" * 65)
    print("Vælg teoretisk ramme (feedbacken evaluerer dig ud fra teorien):\n")
    print(f"  0. Ingen teori (kun persona-feedback)")
    for i, t in enumerate(theories, 1):
        print(f"  {i}. {t['name']} ({t['authors']})")
        print(f"     {t['summary'][:80]}...")
        print()

    while True:
        choice = input(f"Vælg teori (0-{len(theories)}): ").strip()
        try:
            idx = int(choice)
            if idx == 0:
                return None
            if 1 <= idx <= len(theories):
                return theories[idx - 1]["id"]
        except ValueError:
            pass
        print("Ugyldigt valg. Prøv igen.")


def select_model() -> tuple[str, bool]:
    """Lader brugeren vælge model og thinking."""
    print("\nVælg AI-model:")
    print("  1. Sonnet (hurtig, god kvalitet - anbefalet)")
    print("  2. Opus  (langsom, bedste kvalitet)")
    choice = input("Valg (1/2): ").strip()
    model = "sonnet" if choice != "2" else "opus"

    print("\nExtended thinking (AI'en tænker før den svarer):")
    print("  1. Til  (mere nuancerede svar - anbefalet)")
    print("  2. Fra  (hurtigere og billigere)")
    t_choice = input("Valg (1/2): ").strip()
    thinking = t_choice != "2"

    return model, thinking


def run_session():
    """Kører en fuld træningssession."""
    persona_id = select_persona()
    theory_id = select_theory()
    model, thinking = select_model()

    engine = PersonaEngine(
        persona_id=persona_id,
        theory_id=theory_id,
        model=model,
        extended_thinking=thinking,
    )

    scenario = engine.get_scenario()
    persona = engine.persona

    print()
    print("=" * 65)
    print(f"  SAMTALE MED {persona['name'].upper()}")
    print(f"  {persona['context']}")
    if engine.theory:
        print(f"  Teori: {engine.theory['name']}")
    print(f"  Model: {model.upper()} | Thinking: {'TIL' if thinking else 'FRA'}")
    print("=" * 65)
    print()
    print(f"  Sted: {scenario['setting']}")
    print(f"  {scenario['intro']}")
    print()
    print("  Kommandoer: 'slut' = afslut | 'stats' = statistik | 'teori' = vis teori")
    print("-" * 65)
    print()

    while True:
        student_input = input("Du: ").strip()

        if not student_input:
            continue

        if student_input.lower() == "slut":
            break

        if student_input.lower() == "stats":
            cost = engine.estimate_cost()
            n = len(engine.session_stats["interactions"])
            print(f"\n  Interaktioner: {n}")
            print(f"  Tokens: {cost['total_tokens']:,}")
            print(f"  Pris: ~{cost['cost_dkk']} DKK\n")
            continue

        if student_input.lower() == "teori":
            summary = engine.get_theory_summary()
            if summary:
                print(f"\n  {summary}\n")
            else:
                print("\n  Ingen teori valgt.\n")
            continue

        if thinking:
            print(f"\n  [{persona['name']} tænker...]\n")

        result = engine.chat(student_input)

        if "error" in result:
            print(f"  FEJL: {result['error']}\n")
            continue

        if result["thinking"]:
            preview = result["thinking"][:300]
            dots = "..." if len(result["thinking"]) > 300 else ""
            print(f"  --- Tankeproces ---")
            print(f"  {preview}{dots}")
            print(f"  --- Slut ---\n")

        print(f"{persona['name']}: {result['response']}\n")

    # Session afsluttet
    print()
    print("=" * 65)
    print("  SESSION AFSLUTTET")
    print("=" * 65)

    if not engine.session_stats["interactions"]:
        print("\n  Ingen interaktioner at evaluere.\n")
        return

    # Gem session
    filename = engine.save_session()
    print(f"\n  Session gemt: {filename}")

    # Omkostning
    cost = engine.estimate_cost()
    print(f"  Pris: ~{cost['cost_dkk']} DKK ({cost['cost_usd']} USD)")
    print(f"  Tokens: {cost['total_tokens']:,}")

    # Feedback
    print()
    print("=" * 65)
    header = "  FEEDBACK PÅ DIN KOMMUNIKATION"
    if engine.theory:
        header += f" ({engine.theory['name'].upper()})"
    print(header)
    print("=" * 65)
    print()
    print("  Analyserer din samtale...\n")
    analysis = engine.analyze_student()
    print(analysis)
    print()


if __name__ == "__main__":
    run_session()
