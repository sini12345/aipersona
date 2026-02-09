"""
Ali - Web-baseret AI Persona Træningssystem
Gradio-interface til træning af pædagogstuderende i kommunikation med udsatte unge
"""

import gradio as gr
import anthropic
import os
from datetime import datetime

# --- Konfiguration ---

MODELS = {
    "Sonnet 4.5 (hurtig, anbefalet)": "claude-sonnet-4-5-20250929",
    "Opus 4.6 (bedste kvalitet)": "claude-opus-4-6",
}

MODEL_PRICING = {
    "claude-sonnet-4-5-20250929": {"input": 3.0, "output": 15.0, "name": "Sonnet 4.5"},
    "claude-opus-4-6": {"input": 15.0, "output": 75.0, "name": "Opus 4.6"},
}

USD_TO_DKK = 7.0

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


# --- Session tracking ---

session_data = {
    "start_time": None,
    "interactions": [],
    "total_input_tokens": 0,
    "total_output_tokens": 0,
}


def reset_session():
    session_data["start_time"] = datetime.now()
    session_data["interactions"] = []
    session_data["total_input_tokens"] = 0
    session_data["total_output_tokens"] = 0


def get_stats_text(model_name):
    if not session_data["interactions"]:
        return "Ingen beskeder endnu."

    model_id = MODELS.get(model_name, "")
    pricing = MODEL_PRICING.get(model_id, {"input": 3.0, "output": 15.0, "name": "?"})

    total_in = session_data["total_input_tokens"]
    total_out = session_data["total_output_tokens"]
    total = total_in + total_out
    num = len(session_data["interactions"])

    cost_usd = (total_in / 1_000_000) * pricing["input"] + (total_out / 1_000_000) * pricing["output"]
    cost_dkk = cost_usd * USD_TO_DKK

    duration = (datetime.now() - session_data["start_time"]).total_seconds() if session_data["start_time"] else 0
    minutes = int(duration // 60)
    seconds = int(duration % 60)

    return f"""### Session-statistik

| | |
|---|---|
| **Beskeder** | {num} udvekslinger |
| **Varighed** | {minutes}m {seconds}s |
| **Model** | {pricing['name']} |
| **Tokens brugt** | {total:,} ({total_in:,} input + {total_out:,} output) |
| **Estimeret pris** | {cost_dkk:.2f} DKK ({cost_usd:.4f} USD) |
"""


# --- API helper ---

def get_client(api_key_override=""):
    api_key = (api_key_override or "").strip() or os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return None
    return anthropic.Anthropic(api_key=api_key)


# --- Chat-funktion ---

def respond(message, history, model_name, thinking_enabled, api_key_override):
    """Sender besked til Ali med streaming"""
    client = get_client(api_key_override)
    if client is None:
        yield "Mangler API-nøgle. Indtast din Anthropic API-nøgle under 'Indstillinger', eller sæt ANTHROPIC_API_KEY som miljøvariabel."
        return

    if session_data["start_time"] is None:
        reset_session()

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

        # Opdater session stats efter komplet svar
        final = stream.get_final_message()
        input_tokens = final.usage.input_tokens
        output_tokens = final.usage.output_tokens
        session_data["total_input_tokens"] += input_tokens
        session_data["total_output_tokens"] += output_tokens
        session_data["interactions"].append({
            "timestamp": datetime.now().isoformat(),
            "student": message,
            "ali": response_text,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        })

    except anthropic.AuthenticationError:
        yield "Ugyldig API-nøgle. Tjek at din nøgle er korrekt."
    except anthropic.RateLimitError:
        yield "Rate limit nået. Vent et øjeblik og prøv igen."
    except Exception as e:
        yield f"Fejl: {str(e)}"


# --- Analyse-funktion ---

def analyze_conversation(history, model_name, api_key_override):
    """Analyserer den studerendes kommunikationsstrategi"""
    client = get_client(api_key_override)
    if client is None:
        return "Mangler API-nøgle."

    if not history:
        return "Ingen samtale at analysere endnu. Start en samtale med Ali først."

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

CSS = """
.main-title {
    text-align: center;
    margin-bottom: 0.5em;
}
.scenario-box {
    background: linear-gradient(135deg, #667eea22, #764ba222);
    border: 1px solid #667eea44;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 1em;
}
.info-box {
    background: #f0f9ff;
    border: 1px solid #bae6fd;
    border-radius: 8px;
    padding: 16px;
}
.cost-table {
    background: #fefce8;
    border: 1px solid #fde68a;
    border-radius: 8px;
    padding: 16px;
}
"""

with gr.Blocks(title="Ali - Træningssystem", css=CSS) as demo:

    # Header
    gr.Markdown(
        "# Ali - Træningssystem for pædagogstuderende",
        elem_classes=["main-title"],
    )
    gr.Markdown(
        "*Et AI-baseret træningsværktøj hvor du øver dig i at kommunikere med udsatte unge.*"
    )

    with gr.Tabs():

        # === TAB 1: Samtale ===
        with gr.Tab("Samtale med Ali"):

            gr.Markdown(
                """<div class="scenario-box">

**Scenario:** Du møder Ali for første gang på et ungdomscenter.
Ali står ved vinduet og kigger ud. Han har ikke set dig endnu.

*Skriv til Ali som om du var en pædagogstuderende der møder ham for første gang.*

</div>""")

            with gr.Row():
                with gr.Column(scale=3):
                    chatbot = gr.Chatbot(
                        height=480,
                        placeholder="Skriv din første besked til Ali nedenfor...",
                        show_label=False,
                    )
                    with gr.Row():
                        msg = gr.Textbox(
                            placeholder="Skriv til Ali...",
                            label="Din besked",
                            scale=4,
                            container=False,
                        )
                        send_btn = gr.Button("Send", variant="primary", scale=1)

                    with gr.Row():
                        clear_btn = gr.Button("Ny samtale", variant="secondary", size="sm")

                with gr.Column(scale=1):
                    model_dropdown = gr.Dropdown(
                        choices=list(MODELS.keys()),
                        value="Sonnet 4.5 (hurtig, anbefalet)",
                        label="AI Model",
                    )
                    thinking_checkbox = gr.Checkbox(
                        value=True,
                        label="Extended Thinking",
                        info="Ali tænker grundigere (anbefalet)",
                    )
                    api_key_input = gr.Textbox(
                        type="password",
                        label="API-nøgle",
                        placeholder="sk-ant-...",
                        info="Valgfri hvis sat som miljøvariabel",
                    )

                    gr.Markdown("---")
                    stats_display = gr.Markdown("Ingen beskeder endnu.")
                    refresh_stats_btn = gr.Button("Opdater statistik", size="sm")

            # Chat-logik
            def user_send(message, history):
                if not message.strip():
                    return "", history
                history = history + [{"role": "user", "content": message}]
                return "", history

            def bot_respond(history, model_name, thinking_enabled, api_key):
                if not history:
                    return history
                last_msg = history[-1]["content"]
                past = history[:-1]
                history = history + [{"role": "assistant", "content": ""}]
                for text in respond(last_msg, past, model_name, thinking_enabled, api_key):
                    history[-1]["content"] = text
                    yield history

            def clear_chat():
                reset_session()
                return [], "Ingen beskeder endnu."

            # Send ved Enter eller klik
            msg.submit(
                user_send, [msg, chatbot], [msg, chatbot]
            ).then(
                bot_respond, [chatbot, model_dropdown, thinking_checkbox, api_key_input], chatbot
            )

            send_btn.click(
                user_send, [msg, chatbot], [msg, chatbot]
            ).then(
                bot_respond, [chatbot, model_dropdown, thinking_checkbox, api_key_input], chatbot
            )

            clear_btn.click(clear_chat, outputs=[chatbot, stats_display])

            refresh_stats_btn.click(
                get_stats_text, inputs=[model_dropdown], outputs=[stats_display]
            )

        # === TAB 2: Feedback ===
        with gr.Tab("Feedback og analyse"):
            gr.Markdown("""### Få feedback på din kommunikation

Når du har haft en samtale med Ali, kan du få en AI-analyse af din kommunikationsstrategi.

Analysen vurderer dig på fire dimensioner:
- **Autenticitet** - lyder du scriptet eller ægte?
- **Respekt for grænser** - presser du for hårdt?
- **Lytning** - bygger du videre på Ali's svar?
- **Tilgang** - ser du Ali som person eller "case"?
""")
            analyze_btn = gr.Button(
                "Analysér min kommunikation",
                variant="primary",
                size="lg",
            )
            analysis_output = gr.Markdown()

            analyze_btn.click(
                analyze_conversation,
                inputs=[chatbot, model_dropdown, api_key_input],
                outputs=analysis_output,
            )

        # === TAB 3: Prisguide ===
        with gr.Tab("Prisguide"):
            gr.Markdown("""### Prissammenligning for en typisk session

Estimater baseret på en 15-minutters session med ca. 10 udvekslinger.

| Konfiguration | Tokens/session | Pris (DKK) | Pris (USD) |
|---|---|---|---|
| **Sonnet 4.5 + Thinking** | ~12.000 | ~0,25 DKK | ~$0,036 |
| **Sonnet 4.5 uden Thinking** | ~8.000 | ~0,18 DKK | ~$0,025 |
| **Opus 4.6 + Thinking** | ~12.000 | ~1,26 DKK | ~$0,180 |

---

### Anbefaling

| Situation | Anbefalet model |
|---|---|
| Daglig træning med studerende | **Sonnet 4.5 + Thinking** |
| Stram budgetramme | Sonnet 4.5 uden Thinking |
| Vigtige demonstrationer / research | Opus 4.6 + Thinking |

**Sonnet 4.5 med Extended Thinking er det bedste valg for de fleste.**
God kvalitet, hurtige svar og meget billigt.

Med et budget på $50 (~350 DKK) kan du køre **ca. 1.400 sessioner** med Sonnet.
""")

        # === TAB 4: Vejledning ===
        with gr.Tab("Vejledning"):
            gr.Markdown("""### Sådan bruger du Ali-træningssystemet

**Formål:**
Du træner i at kommunikere med en ung person i en udsat position.
Ali er 19 år, fra Tingbjerg/Nørrebro, og har oplevet svigt fra voksne og autoriteter.
Han er skeptisk, defensiv og tester om du er ægte.

---

**Tips til god kommunikation med Ali:**

1. **Vær ægte** - Ali gennemskuer det med det samme hvis du kører en script
2. **Respektér hans grænser** - Pres ikke. Hvis han ikke vil snakke, så acceptér det
3. **Lyt aktivt** - Byg videre på det han faktisk siger, ikke det du tror han burde sige
4. **Se personen** - Ali er ikke en "case" eller et "projekt". Han er et menneske
5. **Tål stilhed** - Det er OK at der er pauser. Ikke alt behøver at blive fyldt ud

---

**Hvad du IKKE skal gøre:**

- Sige "Jeg forstår hvordan du har det" (det gør du ikke, og han ved det)
- Stille for mange spørgsmål i træk (det føles som et forhør)
- Bruge fagsprog eller pædagogiske floskler
- Prøve at "redde" ham eller "løse" hans problemer
- Antage ting om hans liv

---

**Sådan bruger du feedback-funktionen:**

1. Hav en samtale med Ali (mindst 3-5 beskeder)
2. Gå til "Feedback og analyse"-fanen
3. Klik "Analysér min kommunikation"
4. Læs feedbacken og prøv igen med en ny samtale
""")

    # Footer
    gr.Markdown(
        "<center><small>Ali Træningssystem | Bygget til pædagogstuderende | "
        "API-forbrug faktureres via Anthropic</small></center>"
    )

if __name__ == "__main__":
    demo.launch()
