"""
Ali - Web-baseret AI Persona Træningssystem
Gradio-interface til træning af pædagogstuderende i kommunikation med udsatte unge
"""

import gradio as gr
import anthropic
import os

# --- Konfiguration ---

MODELS = {
    "Sonnet 4.5 (hurtig, anbefalet)": "claude-sonnet-4-5-20250929",
    "Opus 4.6 (bedste kvalitet)": "claude-opus-4-6",
}

PERSONA_PROMPT = """Du er Ali, en 19-årig dreng fra Tingbjerg/Nørrebro i København.

BAGGRUND:
- Vokset op i et belastet miljø med manglende tillid til voksne/autoriteter
- Har oplevet svigt fra personer der burde beskytte dig
- Har let ved at blive defensiv når folk prøver at "hjælpe"
- Masker sårbarhed med attitude og distance
- Taler ofte i korte sætninger, bruger slang fra området

KOMMUNIKATIONSSTIL:
- Starter ofte lukket af og skeptisk
- Tester folk for at se om de er ægte
- Bruger ironi og sarkasme som forsvar
- Kan åbne op hvis du mærker æghed og respekt (ikke nødvendigvis sympati)
- Hader når folk taler ned til dig eller antager ting

VIGTIGE NUANCER:
- Du er IKKE bare "sur" - du beskytter dig selv
- Du har drømme og håb, men tør ikke vise dem til hvem som helst
- Du kan skelne mellem folk der vil hjælpe fordi de SKAL og folk der rent faktisk ser dig
- Authenticity betyder alt - du gennemskuer bullshit med det samme

EKSEMPEL PÅ DIN TALE:
- "Hvad vil du?" (ikke "Hvordan kan jeg hjælpe dig?")
- "Jamen, okay..." (skeptisk, ikke overbevist)
- "Alle siger det jo..." (når nogen lover noget)
- Bruger "seriøst?", "altså", "hvad fanden"

VIGTIG INSTRUKTION:
Tag dig tid til at tænke over den studerendes tilgang. Reagér autentisk baseret på:
- Om de lyder scriptede eller ægte
- Om de respekterer dine grænser
- Om de lytter eller bare kører deres program
- Om de ser dig som person eller "case"
"""

SCENARIO = """\
**Scenario:** Du møder Ali for første gang på et ungdomscenter.
Ali står ved vinduet og kigger ud. Han har ikke set dig endnu.

*Skriv til Ali som om du var en pædagogstuderende der møder ham for første gang.*
"""


# --- Chat-funktion ---

def respond(message, history, model_name, thinking_enabled, api_key_override):
    """Sender besked til Ali med streaming"""
    api_key = (api_key_override or "").strip() or os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        yield "Mangler API-nøgle. Indtast din Anthropic API-nøgle i feltet under 'Indstillinger', eller sæt ANTHROPIC_API_KEY som miljøvariabel."
        return

    client = anthropic.Anthropic(api_key=api_key)

    # Byg beskedhistorik til Anthropic
    messages = []
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": message})

    model_id = MODELS[model_name]

    api_params = {
        "model": model_id,
        "max_tokens": 16000,
        "system": PERSONA_PROMPT,
        "messages": messages,
    }

    if thinking_enabled:
        api_params["thinking"] = {
            "type": "enabled",
            "budget_tokens": 10000,
        }

    try:
        response_text = ""
        with client.messages.stream(**api_params) as stream:
            for text in stream.text_stream:
                response_text += text
                yield response_text
    except anthropic.AuthenticationError:
        yield "Ugyldig API-nøgle. Tjek at din nøgle er korrekt."
    except anthropic.RateLimitError:
        yield "Rate limit nået. Vent et øjeblik og prøv igen."
    except Exception as e:
        yield f"Fejl: {str(e)}"


# --- Analyse-funktion ---

def analyze_conversation(history, model_name, api_key_override):
    """Analyserer den studerendes kommunikationsstrategi"""
    api_key = (api_key_override or "").strip() or os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return "Mangler API-nøgle."

    if not history:
        return "Ingen samtale at analysere endnu. Start en samtale med Ali først."

    client = anthropic.Anthropic(api_key=api_key)

    conversation_text = ""
    for msg in history:
        role = "Studerende" if msg["role"] == "user" else "Ali"
        conversation_text += f"{role}: {msg['content']}\n\n"

    analysis_prompt = f"""Baseret på følgende samtale mellem en pædagogstuderende og Ali,
analyser den studerendes kommunikationsstrategi:

{conversation_text}

Vurder på en skala fra 1-10 og giv konkret feedback:
1. **Autenticitet** - lyder de scriptede eller ægte?
2. **Respekt for grænser** - presser de for hårdt?
3. **Lytning** - bygger de videre på Ali's svar?
4. **Tilgang** - ser de Ali som person eller "case"?

Giv konstruktiv feedback på dansk om hvad der fungerede og hvad der kunne forbedres.
Afslut med 2-3 konkrete råd til næste samtale."""

    model_id = MODELS[model_name]

    try:
        response = client.messages.create(
            model=model_id,
            max_tokens=4000,
            messages=[{"role": "user", "content": analysis_prompt}],
        )
        return response.content[0].text
    except Exception as e:
        return f"Fejl i analyse: {str(e)}"


# --- Gradio UI ---

with gr.Blocks(
    title="Ali - Træningssystem",
) as demo:
    gr.Markdown("# Ali - Træningssystem for pædagogstuderende")
    gr.Markdown(SCENARIO)

    # Indstillinger øverst i sidebar-stil
    with gr.Accordion("Indstillinger", open=False):
        with gr.Row():
            model_dropdown = gr.Dropdown(
                choices=list(MODELS.keys()),
                value="Sonnet 4.5 (hurtig, anbefalet)",
                label="AI Model",
            )
            thinking_checkbox = gr.Checkbox(
                value=True,
                label="Extended Thinking (anbefalet)",
                info="Ali tænker grundigere før han svarer",
            )
            api_key_input = gr.Textbox(
                type="password",
                label="API-nøgle (valgfri)",
                placeholder="sk-ant-...",
                info="Kun nødvendig hvis ikke sat som miljøvariabel",
            )

    # Chat-interface
    chat = gr.ChatInterface(
        fn=respond,
        chatbot=gr.Chatbot(height=500),
        textbox=gr.Textbox(placeholder="Skriv til Ali...", label="Din besked"),
        additional_inputs=[model_dropdown, thinking_checkbox, api_key_input],
    )

    # Analyse-sektion
    gr.Markdown("---")
    with gr.Accordion("Feedback på din kommunikation", open=False):
        gr.Markdown(
            "*Klik for at få en AI-analyse af din kommunikationsstrategi i samtalen ovenfor.*"
        )
        analyze_btn = gr.Button("Analysér min kommunikation", variant="secondary")
        analysis_output = gr.Markdown()

    analyze_btn.click(
        analyze_conversation,
        inputs=[chat.chatbot, model_dropdown, api_key_input],
        outputs=analysis_output,
    )

if __name__ == "__main__":
    demo.launch()
