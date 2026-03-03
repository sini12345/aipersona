import os
from datetime import datetime
from pathlib import Path

import anthropic
import gradio as gr

from core.feedback_engine import build_end_feedback
from core.logger import save_session_log
from core.prompt_builder import build_system_prompt, load_persona_markdown
from core.scenarios import format_scenario_brief, get_scenario, get_scenario_labels
from core.state_engine import PersonaState, update_state_from_turn
from core.twist_cards import TWIST_TRIGGER_TURNS, get_twist_card


def _load_persona_files() -> dict[str, str]:
    persona_files: dict[str, str] = {}
    for path in sorted(Path("personas").glob("*_system_prompt.md")):
        name = path.stem.replace("_system_prompt", "").split("_")[0].capitalize()
        persona_files[name] = path.as_posix()
    return persona_files


PERSONA_FILES = _load_persona_files()
DEFAULT_PERSONA = "Ali" if "Ali" in PERSONA_FILES else (next(iter(PERSONA_FILES), ""))

LEARNING_GOALS = [
    "Alliance",
    "Deeskalering",
    "Grænsesætning",
]


def _build_client() -> anthropic.Anthropic:
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise ValueError("Mangler ANTHROPIC_API_KEY. Tilføj den i HF Space Secrets eller lokal .env.")
    return anthropic.Anthropic(api_key=api_key)


def _messages_for_api(turns: list[dict]) -> list[dict]:
    msgs = []
    for t in turns:
        role = "assistant" if t["role"] == "assistant" else "user"
        msgs.append({"role": role, "content": t["content"]})
    return msgs


def _default_scenario_label(persona_name: str) -> str:
    labels = get_scenario_labels(persona_name)
    return labels[0] if labels else ""


def _format_state_panel(state: PersonaState, blind_mode: bool, reveal: bool = False) -> str:
    if blind_mode and not reveal:
        return "Blind mode aktiv: state vises først ved session-afslutning."
    return state.to_panel_text()


def _round_status(session: dict) -> str:
    if not session:
        return "Ingen aktiv session."
    if not session.get("speed_round_enabled", False):
        return f"Normal mode | Ture: {session.get('turn_count', 0)}"
    max_turns = session.get("speed_round_max_turns", 6)
    turn_count = session.get("turn_count", 0)
    return f"Speed round: {turn_count}/{max_turns} ture"


def refresh_scenarios(persona_name: str):
    labels = get_scenario_labels(persona_name)
    selected = labels[0] if labels else ""
    scenario = get_scenario(persona_name, selected)
    brief = format_scenario_brief(persona_name, scenario)
    return gr.Dropdown(choices=labels, value=selected), brief


def refresh_scenario_brief(persona_name: str, scenario_label: str):
    selected_label = scenario_label or _default_scenario_label(persona_name)
    scenario = get_scenario(persona_name, selected_label)
    return format_scenario_brief(persona_name, scenario)


def start_session(
    persona_name: str,
    scenario_label: str,
    learning_goal: str,
    difficulty: int,
    twist_enabled: bool,
    blind_mode: bool,
    speed_round_enabled: bool,
    speed_round_max_turns: int,
):
    if not PERSONA_FILES:
        raise ValueError("Ingen persona-filer fundet i ./personas")
    selected_persona = persona_name if persona_name in PERSONA_FILES else DEFAULT_PERSONA
    persona_text = load_persona_markdown(PERSONA_FILES[selected_persona])
    selected_label = scenario_label or _default_scenario_label(selected_persona)
    scenario = get_scenario(selected_persona, selected_label)

    state = PersonaState()
    state.difficulty = difficulty
    initial_state = scenario.get("initial_state", {})
    for key, value in initial_state.items():
        if hasattr(state, key):
            setattr(state, key, value)
    state.clamp()

    brief = format_scenario_brief(selected_persona, scenario)

    session = {
        "id": datetime.utcnow().strftime("%Y%m%d_%H%M%S"),
        "persona_name": selected_persona,
        "scenario_label": selected_label,
        "scenario_brief": brief,
        "scenario_hidden_layer": scenario.get("hidden_layer", ""),
        "scenario_state_modifiers": scenario.get("state_modifiers", {}),
        "learning_goal": learning_goal,
        "difficulty": difficulty,
        "persona_text": persona_text,
        "turns": [],
        "state_history": [state.to_dict()],
        "started_at": datetime.utcnow().isoformat(),
        "twist_enabled": bool(twist_enabled),
        "blind_mode": bool(blind_mode),
        "speed_round_enabled": bool(speed_round_enabled),
        "speed_round_max_turns": int(speed_round_max_turns),
        "turn_count": 0,
        "fired_twist_turns": [],
        "twist_history": [],
        "active_twist": "Ingen aktiv twist endnu.",
    }

    status = (
        "Session startet | "
        f"Persona: {selected_persona} | "
        f"Scenarie: {selected_label} | "
        f"Læringsmål: {learning_goal} | "
        f"Sværhedsgrad: {difficulty}"
    )

    return (
        session,
        [],
        status,
        _format_state_panel(state, blind_mode=bool(blind_mode), reveal=False),
        brief,
        f"Twist: {session['active_twist']}",
        _round_status(session),
    )


def chat_turn(user_text: str, session: dict, chat_history: list):
    if not session:
        return "Start en session først.", session, chat_history, "Session ikke startet.", "", "Twist: -", "Ingen aktiv session."

    blind_mode = bool(session.get("blind_mode", False))

    if not user_text.strip():
        current_state = PersonaState.from_dict(session["state_history"][-1])
        return (
            "",
            session,
            chat_history,
            "Tom besked ignoreret.",
            _format_state_panel(current_state, blind_mode=blind_mode, reveal=False),
            f"Twist: {session.get('active_twist', '-')}",
            _round_status(session),
        )

    if session.get("speed_round_enabled", False):
        max_turns = session.get("speed_round_max_turns", 6)
        if session.get("turn_count", 0) >= max_turns:
            current_state = PersonaState.from_dict(session["state_history"][-1])
            return (
                "",
                session,
                chat_history,
                "Speed round er færdig. Klik 'Afslut + Feedback'.",
                _format_state_panel(current_state, blind_mode=blind_mode, reveal=False),
                f"Twist: {session.get('active_twist', '-')}",
                _round_status(session),
            )

    try:
        client = _build_client()
    except Exception as e:
        return "", session, chat_history, f"Konfigurationsfejl: {e}", "", "Twist: -", _round_status(session)

    current_state = PersonaState.from_dict(session["state_history"][-1])
    system_prompt = build_system_prompt(
        persona_name=session["persona_name"],
        persona_markdown=session["persona_text"],
        learning_goal=session["learning_goal"],
        difficulty=session["difficulty"],
        scenario_brief=session.get("scenario_brief", ""),
        scenario_hidden_layer=session.get("scenario_hidden_layer", ""),
        active_twist=session.get("active_twist", "Ingen aktiv twist endnu."),
        state=current_state,
    )

    session["turns"].append({"role": "user", "content": user_text})

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=500,
            system=system_prompt,
            messages=_messages_for_api(session["turns"]),
        )

        ai_text = ""
        for block in response.content:
            if block.type == "text":
                ai_text += block.text

        session["turns"].append({"role": "assistant", "content": ai_text})
        updated = update_state_from_turn(
            current_state,
            user_text,
            ai_text,
            session["learning_goal"],
            scenario_modifiers=session.get("scenario_state_modifiers", {}),
        )

        session["turn_count"] = session.get("turn_count", 0) + 1
        turn_number = session["turn_count"]

        twist_status = f"Twist: {session.get('active_twist', 'Ingen aktiv twist endnu.')}"
        if session.get("twist_enabled", False):
            if turn_number in TWIST_TRIGGER_TURNS and turn_number not in session.get("fired_twist_turns", []):
                twist = get_twist_card(session["persona_name"], turn_number)
                session["active_twist"] = twist
                session.setdefault("fired_twist_turns", []).append(turn_number)
                session.setdefault("twist_history", []).append({"turn": turn_number, "card": twist})

                # Light event impact so twist has gameplay consequence.
                updated.stress += 4
                updated.control_loss += 3
                updated.trust -= 2
                updated.clamp()

                twist_status = f"Twist (tur {turn_number}): {twist}"

        session["state_history"].append(updated.to_dict())

        chat_history = chat_history + [
            {"role": "user", "content": user_text},
            {"role": "assistant", "content": ai_text},
        ]

        status = f"Ture: {session['turn_count']}"
        if session.get("speed_round_enabled", False):
            max_turns = session.get("speed_round_max_turns", 6)
            if session["turn_count"] >= max_turns:
                status += " | Speed round færdig - klik 'Afslut + Feedback'."

        return (
            "",
            session,
            chat_history,
            status,
            _format_state_panel(updated, blind_mode=blind_mode, reveal=False),
            twist_status,
            _round_status(session),
        )
    except Exception as e:
        return (
            "",
            session,
            chat_history,
            f"API-fejl: {e}",
            _format_state_panel(current_state, blind_mode=blind_mode, reveal=False),
            f"Twist: {session.get('active_twist', '-')}",
            _round_status(session),
        )


def end_session(session: dict):
    if not session:
        return "Ingen aktiv session.", "", "", "Ingen aktiv session."

    session["ended_at"] = datetime.utcnow().isoformat()
    path = save_session_log(session)

    feedback = build_end_feedback(
        turns=session["turns"],
        learning_goal=session["learning_goal"],
        state_history=session["state_history"],
    )

    twist_history = session.get("twist_history", [])
    if twist_history:
        lines = ["", "Twists i sessionen:"]
        for t in twist_history:
            lines.append(f"- Tur {t['turn']}: {t['card']}")
        feedback += "\n" + "\n".join(lines)

    final_state = PersonaState.from_dict(session["state_history"][-1])
    final_state_text = _format_state_panel(final_state, blind_mode=False, reveal=True)

    status = f"Log gemt: {path}"
    if session.get("speed_round_enabled", False):
        status += f" | Speed round færdig: {session.get('turn_count', 0)}/{session.get('speed_round_max_turns', 6)}"

    return feedback, status, final_state_text, _round_status(session)


def build_ui():
    with gr.Blocks(title="Persona Trainer v1.6") as demo:
        gr.Markdown("# Persona Trainer v1.6 (Gradio + Anthropic)")
        with gr.Accordion("Hjælp til valg", open=False):
            gr.Markdown(
                """
**Persona:** Hvem du træner samtale med. Vælg den profil, der passer til dit læringsfokus.

**Scenarie:** Den konkrete situation I mødes i. Scenariet styrer kontekst og starttilstand.

**Læringsmål:** Hvad du træner i denne session (`Alliance`, `Deeskalering`, `Grænsesætning`).

**Sværhedsgrad:** Hvor meget modstand du typisk møder. 1 = mild modstand, 3 = høj modstand.

**Twist-kort:** Indfører uventede hændelser under samtalen (typisk tur 3 og 6).

**Blind mode:** Skjuler persona-tilstand under samtalen. Tilstanden vises først ved afslutning/debrief.

**Speed round:** Gør samtalen kort og intensiv med et maksimum antal ture.
                """.strip()
            )

        with gr.Row():
            persona = gr.Dropdown(
                choices=list(PERSONA_FILES.keys()),
                value=DEFAULT_PERSONA,
                label="Persona",
                info="Vælg hvilken karakter du vil træne med.",
            )
            scenario = gr.Dropdown(
                choices=get_scenario_labels(DEFAULT_PERSONA),
                value=_default_scenario_label(DEFAULT_PERSONA),
                label="Scenarie",
                info="Vælg den konkrete situation for samtalen.",
            )
            learning_goal = gr.Dropdown(
                choices=LEARNING_GOALS,
                value="Alliance",
                label="Læringsmål",
                info="Vælg hvilket kommunikativt mål du vil fokusere på.",
            )
            difficulty = gr.Slider(
                1,
                3,
                value=2,
                step=1,
                label="Sværhedsgrad",
                info="1 = lav modstand, 3 = høj modstand.",
            )

        with gr.Row():
            twist_enabled = gr.Checkbox(
                value=True,
                label="Twist-kort",
                info="Slå til for uventede hændelser under samtalen.",
            )
            blind_mode = gr.Checkbox(
                value=False,
                label="Blind mode (skjuler tilstand under samtalen)",
                info="Du ser ikke trust/stress/skam/håb før debrief.",
            )
            speed_round_enabled = gr.Checkbox(
                value=False,
                label="Speed round (kort træning)",
                info="Afsluttes automatisk efter valgt antal ture.",
            )
            speed_round_max_turns = gr.Slider(
                4,
                12,
                value=6,
                step=1,
                label="Maks ture (speed)",
                info="Gælder kun når speed round er slået til.",
            )

        scenario_brief = gr.Markdown(
            value=format_scenario_brief(DEFAULT_PERSONA, get_scenario(DEFAULT_PERSONA, _default_scenario_label(DEFAULT_PERSONA)))
        )
        twist_panel = gr.Markdown(value="Twist: Ingen aktiv twist endnu.")

        start_btn = gr.Button("Start session")

        chatbot = gr.Chatbot(type="messages", height=420, label="Samtale")
        user_input = gr.Textbox(label="Din besked", placeholder="Skriv til personaen...")

        with gr.Row():
            send_btn = gr.Button("Send")
            end_btn = gr.Button("Afslut + Feedback")

        status = gr.Textbox(label="Status", interactive=False)
        round_status = gr.Textbox(label="Runde-status", interactive=False)
        state_panel = gr.Textbox(label="Persona-tilstand", lines=6, interactive=False)
        feedback = gr.Textbox(label="Slutfeedback", lines=10, interactive=False)

        session_state = gr.State(value={})

        start_btn.click(
            fn=start_session,
            inputs=[
                persona,
                scenario,
                learning_goal,
                difficulty,
                twist_enabled,
                blind_mode,
                speed_round_enabled,
                speed_round_max_turns,
            ],
            outputs=[session_state, chatbot, status, state_panel, scenario_brief, twist_panel, round_status],
        )

        persona.change(
            fn=refresh_scenarios,
            inputs=[persona],
            outputs=[scenario, scenario_brief],
        )

        scenario.change(
            fn=refresh_scenario_brief,
            inputs=[persona, scenario],
            outputs=[scenario_brief],
        )

        send_btn.click(
            fn=chat_turn,
            inputs=[user_input, session_state, chatbot],
            outputs=[user_input, session_state, chatbot, status, state_panel, twist_panel, round_status],
        )

        user_input.submit(
            fn=chat_turn,
            inputs=[user_input, session_state, chatbot],
            outputs=[user_input, session_state, chatbot, status, state_panel, twist_panel, round_status],
        )

        end_btn.click(
            fn=end_session,
            inputs=[session_state],
            outputs=[feedback, status, state_panel, round_status],
        )

    return demo


if __name__ == "__main__":
    app = build_ui()
    app.launch(server_name="0.0.0.0", server_port=7860)
