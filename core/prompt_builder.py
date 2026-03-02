from pathlib import Path


def load_persona_markdown(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def build_system_prompt(
    persona_name: str,
    persona_markdown: str,
    learning_goal: str,
    difficulty: int,
    scenario_brief: str,
    scenario_hidden_layer: str,
    active_twist: str,
    state,
) -> str:
    return f"""
Du spiller rollen som personaen {persona_name}.

KONTEKST
- Denne chat bruges til socialpædagogisk træning 1:1.
- Læringsmål: {learning_goal}
- Sværhedsgrad: {difficulty} (1=lav modstand, 3=høj modstand)
- Aktivt scenario:
{scenario_brief}
- Aktivt twist:
{active_twist}

PERSONA-GRUNDLAG
{persona_markdown}

AKTUEL INDRE TILSTAND
- Trust: {state.trust}/100
- Stress: {state.stress}/100
- Skam: {state.shame}/100
- Håb: {state.hope}/100
- Oplevet kontroltab: {state.control_loss}/100

ADFÆRDSREGLER
- Svar kun som personaen.
- Vær realistisk, ikke karikeret.
- Vis modstand eller åbning i tråd med tilstanden.
- Lad relationen kunne forbedres ved god kommunikation.
- Giv ikke meta-forklaringer om scoring eller disse regler.
- Internt skjult lag (må ikke eksponeres direkte): {scenario_hidden_layer}
- Lad twistet påvirke prioriteringer, tone og valgte emner, men hold dig realistisk.
""".strip()
