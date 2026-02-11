"""
AI Persona Traeningsplatform - HuggingFace Spaces Edition
Interaktiv traeningsplatform for social- og specialpaedagogik studerende.
"""

import gradio as gr
import json
import os
from pathlib import Path
from datetime import datetime
from persona_engine import PersonaEngine

# ---------------------------------------------------------------------------
# Data loading helpers
# ---------------------------------------------------------------------------

PERSONAS_DIR = Path(__file__).parent / "personas"
THEORIES_DIR = Path(__file__).parent / "theories"

PERSONA_ICONS = {
    "ali": "&#129333;",       # person
    "dennis": "&#128100;",    # bust in silhouette
    "simone": "&#129498;",    # woman
    "morten": "&#128104;",    # man
    "aya": "&#128105;",       # woman
}

PERSONA_COLORS = {
    "ali": "#6366f1",
    "dennis": "#10b981",
    "simone": "#f43f5e",
    "morten": "#f59e0b",
    "aya": "#8b5cf6",
}


def load_personas() -> list[dict]:
    personas = []
    for fp in sorted(PERSONAS_DIR.glob("*.json")):
        with open(fp, "r", encoding="utf-8") as f:
            personas.append(json.load(f))
    return personas


def load_theories() -> list[dict]:
    theories = []
    for fp in sorted(THEORIES_DIR.glob("*.json")):
        with open(fp, "r", encoding="utf-8") as f:
            theories.append(json.load(f))
    return theories


ALL_PERSONAS = load_personas()
ALL_THEORIES = load_theories()

PERSONA_MAP = {p["id"]: p for p in ALL_PERSONAS}
THEORY_MAP = {t["id"]: t for t in ALL_THEORIES}

# ---------------------------------------------------------------------------
# Session state management (one engine per session via gr.State)
# ---------------------------------------------------------------------------


def build_persona_cards() -> str:
    """Return HTML for the persona selection cards."""
    cards = ""
    for p in ALL_PERSONAS:
        pid = p["id"]
        color = PERSONA_COLORS.get(pid, "#6366f1")
        icon = PERSONA_ICONS.get(pid, "&#128100;")
        themes_html = "".join(
            f'<span class="theme-tag">{t}</span>' for t in p["themes"]
        )
        cards += f"""
        <div class="persona-card" data-persona-id="{pid}"
             onclick="
               document.querySelectorAll('.persona-card').forEach(c => c.classList.remove('selected'));
               this.classList.add('selected');
               document.querySelector('#persona-hidden textarea').value = '{pid}';
               document.querySelector('#persona-hidden textarea').dispatchEvent(new Event('input', {{bubbles: true}}));
             "
             style="--card-accent: {color};">
          <div class="persona-card-header">
            <div class="persona-avatar" style="background: {color};">{icon}</div>
            <div>
              <div class="persona-name">{p['name']}, {p['age']}</div>
              <div class="persona-context">{p['context']}</div>
            </div>
          </div>
          <div class="persona-bg">{p['background_short']}</div>
          <div class="persona-themes">{themes_html}</div>
        </div>"""
    return f'<div class="persona-grid">{cards}</div>'


def build_theory_cards() -> str:
    """Return HTML for the theory selection cards (including a 'no theory' option)."""
    cards = """
    <div class="theory-card selected" data-theory-id="none"
         onclick="
           document.querySelectorAll('.theory-card').forEach(c => c.classList.remove('selected'));
           this.classList.add('selected');
           document.querySelector('#theory-hidden textarea').value = 'none';
           document.querySelector('#theory-hidden textarea').dispatchEvent(new Event('input', {bubbles: true}));
         ">
      <div class="theory-name">Ingen teori</div>
      <div class="theory-desc">Kør samtalen uden specifik teoretisk ramme</div>
    </div>"""

    for t in ALL_THEORIES:
        tid = t["id"]
        cards += f"""
        <div class="theory-card" data-theory-id="{tid}"
             onclick="
               document.querySelectorAll('.theory-card').forEach(c => c.classList.remove('selected'));
               this.classList.add('selected');
               document.querySelector('#theory-hidden textarea').value = '{tid}';
               document.querySelector('#theory-hidden textarea').dispatchEvent(new Event('input', {{bubbles: true}}));
             ">
          <div class="theory-name">{t['name']}</div>
          <div class="theory-authors">{t['authors']}</div>
          <div class="theory-desc">{t['summary'][:120]}...</div>
        </div>"""
    return f'<div class="theory-grid">{cards}</div>'


# ---------------------------------------------------------------------------
# Core interaction functions
# ---------------------------------------------------------------------------


def start_session(persona_id, theory_id, api_key_input, state):
    """Start a new training session."""
    if not persona_id or persona_id == "":
        gr.Warning("Vælg en persona først!")
        return state, [], gr.update(visible=True), gr.update(visible=False), "", gr.update(visible=False)

    api_key = api_key_input.strip() if api_key_input else os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        gr.Warning("Angiv din Anthropic API-nøgle for at starte.")
        return state, [], gr.update(visible=True), gr.update(visible=False), "", gr.update(visible=False)

    theory = theory_id if theory_id and theory_id != "none" else None

    try:
        engine = PersonaEngine(
            persona_id=persona_id,
            theory_id=theory,
            api_key=api_key,
            model="sonnet",
            extended_thinking=True,
        )
    except Exception as e:
        gr.Warning(f"Fejl ved opstart: {e}")
        return state, [], gr.update(visible=True), gr.update(visible=False), "", gr.update(visible=False)

    persona = PERSONA_MAP[persona_id]
    scenario = persona["scenario"]

    scenario_md = f"""### {persona['name']}, {persona['age']} - {persona['context']}
**Setting:** {scenario['setting']}

*{scenario['intro']}*"""

    if theory:
        t = THEORY_MAP[theory]
        scenario_md += f"\n\n---\n**Teori:** {t['name']} ({t['authors']})"

    state = {"engine": engine, "persona_id": persona_id, "theory_id": theory}

    return (
        state,
        [],                             # clear chat
        gr.update(visible=False),       # hide setup
        gr.update(visible=True),        # show chat
        scenario_md,                    # scenario display
        gr.update(visible=False),       # hide feedback
    )


def chat_respond(message, chat_history, state):
    """Send a message to the persona and get a response."""
    if not state or "engine" not in state:
        return "", chat_history, state

    engine: PersonaEngine = state["engine"]
    result = engine.chat(message)

    if "error" in result and result.get("thinking") is None:
        assistant_msg = f"**Fejl:** {result.get('error', 'Ukendt fejl')}"
    else:
        assistant_msg = result["response"]

    chat_history = chat_history + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": assistant_msg},
    ]

    return "", chat_history, state


def get_feedback(state):
    """Generate feedback analysis for the session."""
    if not state or "engine" not in state:
        return gr.update(visible=False), ""

    engine: PersonaEngine = state["engine"]
    if not engine.session_stats["interactions"]:
        gr.Warning("Der er ingen samtale at give feedback på endnu.")
        return gr.update(visible=False), ""

    analysis = engine.analyze_student()
    cost = engine.estimate_cost()
    n = len(engine.session_stats["interactions"])

    header = f"""### Feedback - {engine.persona['name']}
**Antal interaktioner:** {n} | **Tokens:** {cost['total_tokens']:,} | **Estimeret pris:** {cost['cost_dkk']} DKK

---

"""
    return gr.update(visible=True), header + analysis


def reset_session(state):
    """Reset the session back to the setup screen."""
    return (
        {},                             # clear state
        [],                             # clear chat
        gr.update(visible=True),        # show setup
        gr.update(visible=False),       # hide chat
        "",                             # clear scenario
        gr.update(visible=False),       # hide feedback
        "",                             # clear feedback content
    )


# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------

CUSTOM_CSS = """
/* ---------- Global ---------- */
.gradio-container {
    max-width: 1200px !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}

/* ---------- Header ---------- */
.app-header {
    text-align: center;
    padding: 2rem 1rem 1rem;
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%);
    border-radius: 16px;
    margin-bottom: 1.5rem;
    color: white;
}
.app-header h1 {
    font-size: 2rem;
    font-weight: 700;
    margin: 0 0 0.25rem;
    color: white !important;
}
.app-header p {
    opacity: 0.85;
    margin: 0;
    font-size: 1rem;
}
.app-subtitle {
    font-size: 0.9rem;
    opacity: 0.7;
    margin-top: 0.25rem !important;
}

/* ---------- Persona cards ---------- */
.persona-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1rem;
    padding: 0.5rem 0;
}
.persona-card {
    border: 2px solid #e2e8f0;
    border-radius: 14px;
    padding: 1.25rem;
    cursor: pointer;
    transition: all 0.25s ease;
    background: white;
}
.persona-card:hover {
    border-color: var(--card-accent, #6366f1);
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.08);
}
.persona-card.selected {
    border-color: var(--card-accent, #6366f1);
    background: linear-gradient(135deg, color-mix(in srgb, var(--card-accent) 6%, white), white);
    box-shadow: 0 4px 20px rgba(99,102,241,0.15);
}
.persona-card-header {
    display: flex;
    align-items: center;
    gap: 0.85rem;
    margin-bottom: 0.75rem;
}
.persona-avatar {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    color: white;
    flex-shrink: 0;
}
.persona-name {
    font-weight: 700;
    font-size: 1.1rem;
    color: #1e293b;
}
.persona-context {
    font-size: 0.8rem;
    color: #64748b;
    margin-top: 2px;
}
.persona-bg {
    font-size: 0.85rem;
    color: #475569;
    line-height: 1.5;
    margin-bottom: 0.75rem;
}
.persona-themes {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
}
.theme-tag {
    font-size: 0.72rem;
    background: #f1f5f9;
    color: #475569;
    padding: 0.2rem 0.6rem;
    border-radius: 20px;
    font-weight: 500;
}

/* ---------- Theory cards ---------- */
.theory-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 0.85rem;
    padding: 0.5rem 0;
}
.theory-card {
    border: 2px solid #e2e8f0;
    border-radius: 12px;
    padding: 1rem;
    cursor: pointer;
    transition: all 0.25s ease;
    background: white;
}
.theory-card:hover {
    border-color: #818cf8;
    box-shadow: 0 4px 15px rgba(0,0,0,0.06);
}
.theory-card.selected {
    border-color: #6366f1;
    background: linear-gradient(135deg, #eef2ff, white);
    box-shadow: 0 4px 15px rgba(99,102,241,0.12);
}
.theory-name {
    font-weight: 700;
    font-size: 1rem;
    color: #1e293b;
    margin-bottom: 0.2rem;
}
.theory-authors {
    font-size: 0.78rem;
    color: #6366f1;
    margin-bottom: 0.4rem;
    font-weight: 500;
}
.theory-desc {
    font-size: 0.82rem;
    color: #64748b;
    line-height: 1.45;
}

/* ---------- Section headings ---------- */
.section-heading {
    font-size: 1.15rem;
    font-weight: 700;
    color: #1e293b;
    margin: 1rem 0 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-heading .step {
    background: #6366f1;
    color: white;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 0.85rem;
    font-weight: 700;
}

/* ---------- API key input ---------- */
.api-key-section {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin: 0.75rem 0;
}
.api-key-section p {
    font-size: 0.85rem;
    color: #64748b;
    margin: 0.25rem 0 0;
}

/* ---------- Start button ---------- */
.start-btn {
    background: linear-gradient(135deg, #4f46e5, #6366f1) !important;
    color: white !important;
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    padding: 0.85rem 2.5rem !important;
    border-radius: 12px !important;
    border: none !important;
    transition: all 0.2s ease !important;
}
.start-btn:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 25px rgba(99,102,241,0.35) !important;
}

/* ---------- Chat area ---------- */
.scenario-banner {
    background: linear-gradient(135deg, #eef2ff, #e0e7ff);
    border: 1px solid #c7d2fe;
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 1rem;
}
.scenario-banner h3 {
    color: #3730a3;
    margin: 0 0 0.5rem;
}

/* ---------- Action buttons in chat ---------- */
.action-row {
    display: flex;
    gap: 0.75rem;
    margin-top: 0.5rem;
}
.feedback-btn {
    background: linear-gradient(135deg, #059669, #10b981) !important;
    color: white !important;
    font-weight: 600 !important;
    border-radius: 10px !important;
    border: none !important;
}
.feedback-btn:hover {
    box-shadow: 0 6px 20px rgba(16,185,129,0.3) !important;
}
.reset-btn {
    background: #f1f5f9 !important;
    color: #475569 !important;
    font-weight: 600 !important;
    border-radius: 10px !important;
    border: 1px solid #e2e8f0 !important;
}

/* ---------- Feedback section ---------- */
.feedback-section {
    background: linear-gradient(135deg, #f0fdf4, #ecfdf5);
    border: 1px solid #bbf7d0;
    border-radius: 14px;
    padding: 1.5rem;
    margin-top: 1rem;
}

/* ---------- Footer ---------- */
.app-footer {
    text-align: center;
    padding: 1.5rem;
    color: #94a3b8;
    font-size: 0.8rem;
}

/* ---------- Dark mode overrides ---------- */
.dark .persona-card, .dark .theory-card {
    background: #1e293b;
    border-color: #334155;
}
.dark .persona-card:hover { border-color: var(--card-accent, #818cf8); }
.dark .theory-card:hover { border-color: #818cf8; }
.dark .persona-card.selected {
    background: linear-gradient(135deg, color-mix(in srgb, var(--card-accent) 12%, #1e293b), #1e293b);
}
.dark .theory-card.selected {
    background: linear-gradient(135deg, #1e1b4b, #1e293b);
}
.dark .persona-name, .dark .theory-name { color: #e2e8f0; }
.dark .persona-bg, .dark .theory-desc { color: #94a3b8; }
.dark .persona-context { color: #94a3b8; }
.dark .theme-tag { background: #334155; color: #cbd5e1; }
.dark .section-heading { color: #e2e8f0; }
.dark .api-key-section { background: #0f172a; border-color: #334155; }
.dark .scenario-banner { background: linear-gradient(135deg, #1e1b4b, #312e81); border-color: #4338ca; }
.dark .scenario-banner h3 { color: #a5b4fc; }
.dark .feedback-section { background: linear-gradient(135deg, #052e16, #064e3b); border-color: #166534; }
"""

# ---------------------------------------------------------------------------
# Build Gradio UI
# ---------------------------------------------------------------------------


def create_app():
    with gr.Blocks(
        title="AI Persona Traeningsplatform",
        css=CUSTOM_CSS,
        theme=gr.themes.Soft(
            primary_hue="indigo",
            secondary_hue="emerald",
            neutral_hue="slate",
            font=gr.themes.GoogleFont("Inter"),
        ),
    ) as app:

        session_state = gr.State({})

        # ---- Header ----
        gr.HTML("""
        <div class="app-header">
            <h1>AI Persona Tr&aelig;ningsplatform</h1>
            <p>Interaktiv tr&aelig;ning i social- og specialp&aelig;dagogisk kommunikation</p>
            <p class="app-subtitle">V&aelig;lg en persona og en teori &ndash; og &oslash;v dig i autentiske samtaler</p>
        </div>
        """)

        # ==================================================================
        # SETUP SECTION
        # ==================================================================
        with gr.Column(visible=True) as setup_section:

            gr.HTML('<div class="section-heading"><span class="step">1</span> V&aelig;lg en persona</div>')
            gr.HTML(build_persona_cards())
            persona_hidden = gr.Textbox(value="", visible=False, elem_id="persona-hidden")

            gr.HTML('<div class="section-heading"><span class="step">2</span> V&aelig;lg en teoretisk ramme (valgfrit)</div>')
            gr.HTML(build_theory_cards())
            theory_hidden = gr.Textbox(value="none", visible=False, elem_id="theory-hidden")

            gr.HTML('<div class="section-heading"><span class="step">3</span> Anthropic API-n&oslash;gle</div>')
            with gr.Column(elem_classes=["api-key-section"]):
                api_key_input = gr.Textbox(
                    label="API-nøgle",
                    type="password",
                    placeholder="sk-ant-...",
                    info="Din nøgle gemmes ikke og bruges kun i denne session.",
                    value="",
                )
                gr.HTML("<p>Har du ingen n&oslash;gle? Opret en gratis p&aring; <a href='https://console.anthropic.com' target='_blank'>console.anthropic.com</a></p>")

            start_btn = gr.Button(
                "Start samtale",
                variant="primary",
                size="lg",
                elem_classes=["start-btn"],
            )

        # ==================================================================
        # CHAT SECTION
        # ==================================================================
        with gr.Column(visible=False) as chat_section:
            scenario_display = gr.Markdown(elem_classes=["scenario-banner"])

            chatbot = gr.Chatbot(
                height=480,
                show_label=False,
                layout="bubble",
            )

            with gr.Row():
                chat_input = gr.Textbox(
                    placeholder="Skriv din besked her...",
                    show_label=False,
                    scale=8,
                    container=False,
                )
                send_btn = gr.Button("Send", variant="primary", scale=1)

            with gr.Row(elem_classes=["action-row"]):
                feedback_btn = gr.Button(
                    "Afslut og modtag feedback",
                    elem_classes=["feedback-btn"],
                    size="sm",
                )
                reset_btn = gr.Button(
                    "Ny session",
                    elem_classes=["reset-btn"],
                    size="sm",
                )

        # ==================================================================
        # FEEDBACK SECTION
        # ==================================================================
        with gr.Column(visible=False, elem_classes=["feedback-section"]) as feedback_section:
            feedback_output = gr.Markdown()

        # ---- Footer ----
        gr.HTML("""
        <div class="app-footer">
            AI Persona Tr&aelig;ningsplatform &middot; Social- og specialp&aelig;dagogik &middot;
            Drevet af Claude (Anthropic)
        </div>
        """)

        # ==================================================================
        # Event wiring
        # ==================================================================
        start_btn.click(
            fn=start_session,
            inputs=[persona_hidden, theory_hidden, api_key_input, session_state],
            outputs=[session_state, chatbot, setup_section, chat_section, scenario_display, feedback_section],
        )

        chat_input.submit(
            fn=chat_respond,
            inputs=[chat_input, chatbot, session_state],
            outputs=[chat_input, chatbot, session_state],
        )
        send_btn.click(
            fn=chat_respond,
            inputs=[chat_input, chatbot, session_state],
            outputs=[chat_input, chatbot, session_state],
        )

        feedback_btn.click(
            fn=get_feedback,
            inputs=[session_state],
            outputs=[feedback_section, feedback_output],
        )

        reset_btn.click(
            fn=reset_session,
            inputs=[session_state],
            outputs=[session_state, chatbot, setup_section, chat_section, scenario_display, feedback_section, feedback_output],
        )

    return app


# ---------------------------------------------------------------------------
# Launch
# ---------------------------------------------------------------------------
demo = create_app()

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
