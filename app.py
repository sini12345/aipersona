import os
from datetime import datetime

import anthropic
import gradio as gr

from core.feedback_engine import build_end_feedback
from core.logger import save_session_log
from core.prompt_builder import build_system_prompt, load_persona_markdown
from core.scenarios import format_scenario_brief, get_scenario, get_scenario_labels
from core.state_engine import PersonaState, update_state_from_turn


PERSONA_FILES = {
    "Ali": "personas/ali.md",
    "Sofie": "personas/sofie.md",
    "Mika": "personas/mika.md",
}

LEARNING_GOALS = [
    "Alliance",
    "Deeskalering",
    "Graensesaetning",
]


def _build_client() -> anthropic.Anthropic:
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise ValueError("Missing ANTHROPIC_API_KEY. Add it in HF Space Secrets or local .env.")
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


def start_session(persona_name: str, scenario_label: str, learning_goal: str, difficulty: int):
    persona_text = load_persona_markdown(PERSONA_FILES[persona_name])
    selected_label = scenario_label or _default_scenario_label(persona_name)
    scenario = get_scenario(persona_name, selected_label)

    state = PersonaState()
    state.difficulty = difficulty
    initial_state = scenario.get("initial_state", {})
    for key, value in initial_state.items():
        if hasattr(state, key):
            setattr(state, key, value)
    state.clamp()

    brief = format_scenario_brief(persona_name, scenario)

    session = {
        "id": datetime.utcnow().strftime("%Y%m%d_%H%M%S"),
        "persona_name": persona_name,
        "scenario_label": selected_label,
        "scenario_brief": brief,
        "scenario_hidden_layer": scenario.get("hidden_layer", ""),
        "learning_goal": learning_goal,
        "difficulty": difficulty,
        "persona_text": persona_text,
        "turns": [],
        "state_history": [state.to_dict()],
        "started_at": datetime.utcnow().isoformat(),
    }

    status = (
        "Session started | "
        f"Persona: {persona_name} | "
        f"Scenario: {selected_label} | "
        f"Goal: {learning_goal} | "
        f"Difficulty: {difficulty}"
    )
    return session, [], status, state.to_panel_text(), brief


def chat_turn(user_text: str, session: dict, chat_history: list):
    if not session:
        return "Start en session foerst.", session, chat_history, "Session not started.", ""

    if not user_text.strip():
        return "", session, chat_history, "Tom besked ignoreret.", ""

    try:
        client = _build_client()
    except Exception as e:
        return "", session, chat_history, f"Config error: {e}", ""

    current_state = PersonaState.from_dict(session["state_history"][-1])
    system_prompt = build_system_prompt(
        persona_name=session["persona_name"],
        persona_markdown=session["persona_text"],
        learning_goal=session["learning_goal"],
        difficulty=session["difficulty"],
        scenario_brief=session.get("scenario_brief", ""),
        scenario_hidden_layer=session.get("scenario_hidden_layer", ""),
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
        updated = update_state_from_turn(current_state, user_text, ai_text, session["learning_goal"])
        session["state_history"].append(updated.to_dict())

        chat_history = chat_history + [
            {"role": "user", "content": user_text},
            {"role": "assistant", "content": ai_text},
        ]
        status = f"Turns: {len(session['turns']) // 2}"
        return "", session, chat_history, status, updated.to_panel_text()
    except Exception as e:
        return "", session, chat_history, f"API error: {e}", current_state.to_panel_text()


def end_session(session: dict):
    if not session:
        return "No active session.", ""

    session["ended_at"] = datetime.utcnow().isoformat()
    path = save_session_log(session)
    feedback = build_end_feedback(
        turns=session["turns"],
        learning_goal=session["learning_goal"],
        state_history=session["state_history"],
    )
    return feedback, f"Saved log: {path}"


def build_ui():
    with gr.Blocks(title="Persona Trainer v1.5") as demo:
        gr.Markdown("# Persona Trainer v1.5 (Gradio + Anthropic)")

        with gr.Row():
            persona = gr.Dropdown(choices=list(PERSONA_FILES.keys()), value="Ali", label="Persona")
            scenario = gr.Dropdown(
                choices=get_scenario_labels("Ali"),
                value=_default_scenario_label("Ali"),
                label="Scenario",
            )
            learning_goal = gr.Dropdown(choices=LEARNING_GOALS, value="Alliance", label="Laeringsmaal")
            difficulty = gr.Slider(1, 3, value=2, step=1, label="Svaerhedsgrad")

        scenario_brief = gr.Markdown(
            value=format_scenario_brief("Ali", get_scenario("Ali", _default_scenario_label("Ali")))
        )

        start_btn = gr.Button("Start Session")

        chatbot = gr.Chatbot(type="messages", height=420, label="Samtale")
        user_input = gr.Textbox(label="Din besked", placeholder="Skriv til personaen...")

        with gr.Row():
            send_btn = gr.Button("Send")
            end_btn = gr.Button("Afslut + Feedback")

        status = gr.Textbox(label="Status", interactive=False)
        state_panel = gr.Textbox(label="Persona State", lines=6, interactive=False)
        feedback = gr.Textbox(label="Slutfeedback", lines=8, interactive=False)

        session_state = gr.State(value={})

        start_btn.click(
            fn=start_session,
            inputs=[persona, scenario, learning_goal, difficulty],
            outputs=[session_state, chatbot, status, state_panel, scenario_brief],
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
            outputs=[user_input, session_state, chatbot, status, state_panel],
        )

        user_input.submit(
            fn=chat_turn,
            inputs=[user_input, session_state, chatbot],
            outputs=[user_input, session_state, chatbot, status, state_panel],
        )

        end_btn.click(
            fn=end_session,
            inputs=[session_state],
            outputs=[feedback, status],
        )

    return demo


if __name__ == "__main__":
    app = build_ui()
    app.launch(server_name="0.0.0.0", server_port=7860)
