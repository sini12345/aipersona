"""
Ali Træningssystem - HuggingFace Spaces Gradio Interface
Pædagogstuderende kan øve samtaler med Ali, en 19-årig fra Tingbjerg/Nørrebro
"""

import os
import gradio as gr
from ali_hybrid import AliPersona


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def check_api_key() -> bool:
    """Kontrollerer om ANTHROPIC_API_KEY er sat som miljøvariabel."""
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def create_ali_instance(model: str, extended_thinking: bool):
    """
    Opretter en ny AliPersona instans.
    Returnerer None hvis API key mangler.
    """
    if not check_api_key():
        return None
    return AliPersona(model=model, extended_thinking=extended_thinking)


def format_stats(ali) -> str:
    """
    Formaterer session statistik til visning i Gradio.
    Returnerer en dansk-sproget Markdown streng.
    """
    if ali is None:
        return "_Ingen aktiv session._"

    interactions = ali.session_stats.get("interactions", [])
    if not interactions:
        return "_Ingen interaktioner endnu._"

    cost = ali.estimate_cost()
    stats = ali.get_session_stats()

    lines = [
        "### Session Statistik",
        f"**Model:** {cost['model'].upper()}",
        f"**Extended thinking:** {'TIL' if cost['extended_thinking'] else 'FRA'}",
        f"**Antal beskeder:** {len(interactions)}",
        f"**Tokens i alt:** {cost['total_tokens']:,}",
        f"&nbsp;&nbsp;- Input: {cost['input_tokens']:,}",
        f"&nbsp;&nbsp;- Output: {cost['output_tokens']:,}",
        f"**Estimeret pris:** {cost['cost_dkk']} DKK ({cost['cost_usd']} USD)",
        f"**Varighed:** {int(stats['duration_seconds'])} sek.",
    ]
    if stats.get("avg_tokens_per_interaction"):
        lines.append(
            f"**Gns. tokens/besked:** {int(stats['avg_tokens_per_interaction']):,}"
        )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Core chat handler
# ---------------------------------------------------------------------------

def respond(user_message, chat_history, ali_state, show_thinking):
    """
    Behandler en brugerbesked og returnerer opdateret tilstand.

    Returns:
        chat_history:  Opdateret liste til gr.Chatbot
        thinking_text: Ali's tankeproces (tom streng hvis ikke valgt)
        stats_text:    Opdateret statistik Markdown
    """
    if ali_state is None:
        error_msg = (
            "FEJL: ANTHROPIC_API_KEY er ikke konfigureret. "
            "Kontakt administratoren af dette Space."
        )
        chat_history = chat_history + [[user_message, error_msg]]
        return chat_history, "", "_API nøgle mangler._"

    if not user_message.strip():
        return chat_history, "", format_stats(ali_state)

    result = ali_state.chat(user_message.strip())

    if result.get("error"):
        ali_response = f"[FEJL: {result['error']}]"
        thinking_text = ""
    else:
        ali_response = result.get("response", "")
        raw_thinking = result.get("thinking") or ""
        thinking_text = raw_thinking if show_thinking else ""

    chat_history = chat_history + [[user_message, ali_response]]
    stats_text = format_stats(ali_state)

    return chat_history, thinking_text, stats_text


# ---------------------------------------------------------------------------
# Settings change / session reset
# ---------------------------------------------------------------------------

MODEL_MAP = {
    "Sonnet 4.5 (hurtig, anbefalet)": "sonnet",
    "Opus 4.5 (bedste kvalitet)": "opus",
}


def reset_session(model_choice, thinking_on):
    """
    Opretter en ny AliPersona og nulstiller chat historik.
    Kaldes ved model-/thinking-ændring eller "Ny Session"-knap.

    Returns:
        chat_history, ali_state, stats_text, thinking_text
    """
    model_key = MODEL_MAP.get(model_choice, "sonnet")
    new_ali = create_ali_instance(model_key, thinking_on)

    if new_ali is None:
        stats_text = (
            "**FEJL:** `ANTHROPIC_API_KEY` mangler. "
            "Sæt den som HuggingFace Secret i Space-indstillingerne."
        )
    else:
        stats_text = "_Ny session startet. Ingen interaktioner endnu._"

    return [], new_ali, stats_text, ""


def trigger_analysis(ali_state):
    """
    Kører analyze_student_approach() — ekstra API-kald, kun på brugerens anmodning.
    """
    if ali_state is None:
        return "FEJL: Ingen aktiv session."

    interactions = ali_state.session_stats.get("interactions", [])
    if not interactions:
        return "Der er ingen interaktioner at analysere endnu. Skriv til Ali først."

    return ali_state.analyze_student_approach()


# ---------------------------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------------------------

NO_API_KEY_WARNING = """\
> **ADVARSEL:** `ANTHROPIC_API_KEY` er ikke konfigureret som HuggingFace Secret.
> Applikationen kan ikke kommunikere med Ali uden en gyldig API-nøgle.
> Gå til **Settings → Variables and secrets** og tilføj nøglen.
"""

INTRO_TEXT = """\
# Ali Træningssystem

**Velkommen til Ali-træningssystemet.**

Ali er en 19-årig fra Tingbjerg/Nørrebro i København. Du er pædagogstuderende
og møder Ali for første gang på et ungdomscenter.

*Ali står ved vinduet og kigger ud. Hun har ikke set dig endnu.*

Vælg model og indstillinger nedenfor, og start samtalen.
"""


def build_interface() -> gr.Blocks:
    api_key_present = check_api_key()

    with gr.Blocks(
        title="Ali Træningssystem",
        theme=gr.themes.Soft(),
    ) as demo:

        ali_state = gr.State(value=None)

        gr.Markdown(INTRO_TEXT)

        if not api_key_present:
            gr.Markdown(NO_API_KEY_WARNING)

        # Settings row
        with gr.Row():
            model_dropdown = gr.Dropdown(
                choices=list(MODEL_MAP.keys()),
                value="Sonnet 4.5 (hurtig, anbefalet)",
                label="AI Model",
                info="Sonnet er hurtigere og billigere. Opus giver bedste kvalitet.",
                scale=2,
            )
            thinking_checkbox = gr.Checkbox(
                value=True,
                label="Extended Thinking",
                info="Ali tænker grundigt før hun svarer (anbefalet, men langsommere)",
                scale=1,
            )
            show_thinking_checkbox = gr.Checkbox(
                value=False,
                label="Vis tankeproces",
                info="Vis hvad Ali tænker internt (pædagogisk indsigt)",
                scale=1,
            )

        # Main layout
        with gr.Row():

            # Left: chat
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(
                    label="Samtale med Ali",
                    height=500,
                    show_copy_button=True,
                    bubble_full_width=False,
                )

                with gr.Row():
                    msg_input = gr.Textbox(
                        placeholder="Skriv din besked til Ali her...",
                        lines=2,
                        scale=4,
                        show_label=False,
                    )
                    send_btn = gr.Button("Send", variant="primary", scale=1)

                with gr.Accordion("Ali's tankeproces", open=False):
                    thinking_display = gr.Textbox(
                        label="Hvad Ali tænkte inden svaret",
                        lines=6,
                        interactive=False,
                        placeholder="(Ingen tankeproces at vise endnu — aktiver 'Vis tankeproces' ovenfor)",
                    )

            # Right: stats + actions
            with gr.Column(scale=1):
                stats_display = gr.Markdown(
                    value="_Ingen interaktioner endnu._",
                )

                gr.Markdown("---")

                new_session_btn = gr.Button("Ny Session", variant="secondary")
                gr.Markdown("_Nulstiller samtalen og starter forfra._")

                gr.Markdown("---")

                analyze_btn = gr.Button(
                    "Analyser min kommunikation", variant="secondary"
                )
                gr.Markdown(
                    "_Giver feedback på din kommunikationsstrategi "
                    "(bruger et ekstra API-kald)._"
                )

                analysis_display = gr.Textbox(
                    label="Feedback",
                    lines=10,
                    interactive=False,
                    placeholder="Klik 'Analyser' for at få feedback på din samtale.",
                )

        # Event wiring

        def on_load(model_choice, thinking_on):
            _, new_ali, stats, _ = reset_session(model_choice, thinking_on)
            return new_ali, stats

        demo.load(
            fn=on_load,
            inputs=[model_dropdown, thinking_checkbox],
            outputs=[ali_state, stats_display],
        )

        send_btn.click(
            fn=respond,
            inputs=[msg_input, chatbot, ali_state, show_thinking_checkbox],
            outputs=[chatbot, thinking_display, stats_display],
        ).then(fn=lambda: "", inputs=None, outputs=[msg_input])

        msg_input.submit(
            fn=respond,
            inputs=[msg_input, chatbot, ali_state, show_thinking_checkbox],
            outputs=[chatbot, thinking_display, stats_display],
        ).then(fn=lambda: "", inputs=None, outputs=[msg_input])

        model_dropdown.change(
            fn=reset_session,
            inputs=[model_dropdown, thinking_checkbox],
            outputs=[chatbot, ali_state, stats_display, thinking_display],
        )

        thinking_checkbox.change(
            fn=reset_session,
            inputs=[model_dropdown, thinking_checkbox],
            outputs=[chatbot, ali_state, stats_display, thinking_display],
        )

        new_session_btn.click(
            fn=reset_session,
            inputs=[model_dropdown, thinking_checkbox],
            outputs=[chatbot, ali_state, stats_display, thinking_display],
        )

        analyze_btn.click(
            fn=trigger_analysis,
            inputs=[ali_state],
            outputs=[analysis_display],
        )

    return demo


if __name__ == "__main__":
    interface = build_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
    )
