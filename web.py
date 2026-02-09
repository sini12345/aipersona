"""
Flask Web Server: Persona Træningsplatform
Kør med: python web.py
Demo-mode (uden API key): python web.py --demo
Åbn: http://localhost:5000
"""

import os
import sys
import json
import random
from flask import Flask, render_template, request, jsonify
from persona_engine import PersonaEngine
from pathlib import Path

app = Flask(__name__)

# Store active engines per session (simple in-memory store)
engines: dict[str, PersonaEngine] = {}

# Demo mode flag
DEMO_MODE = "--demo" in sys.argv or not os.environ.get("ANTHROPIC_API_KEY")

# Pre-scripted demo responses per persona
DEMO_RESPONSES = {
    "ali": [
        {"response": "Hvad vil du?", "thinking": "Den studerende prøver at starte en samtale. Jeg kender dem ikke. Jeg har set mange pædagoger komme og gå. Lad mig se om de er ægte eller bare kører deres program."},
        {"response": "Jamen, okay... Du er ny her, eller hvad?", "thinking": "De virker ikke helt som de andre. Men jeg stoler ikke på det endnu. Alle starter pænt. Lad mig teste dem lidt."},
        {"response": "Alle siger det jo. At de vil hjælpe. Og så smutter de igen efter tre måneder.", "thinking": "De siger de vil hjælpe. Det har jeg hørt før. Min gamle kontaktperson sagde det samme. Og den før det. Lad mig se om de bliver defensive nu."},
        {"response": "... du er sgu lidt anderledes end de andre.", "thinking": "De pressede ikke. De blev ikke fornærmede. Måske... men jeg holder stadig lidt igen. Det er for tidligt at slippe garden."},
        {"response": "Jeg ved det ikke. Nogle gange tænker jeg bare... hvad er pointen, du ved?", "thinking": "De lytter faktisk. De prøver ikke at fixe mig. Det føles... okay. Måske kan jeg sige lidt mere."},
    ],
    "dennis": [
        {"response": "Det er IKKE fair. Jeg handler altid om tirsdagen.", "thinking": "Min indkøbsdag er ændret uden at nogen spurgte mig. Det er MIN tirsdag. Jeg har handlet om tirsdagen i to år."},
        {"response": "... ved ikke...", "thinking": "De spørger hvordan jeg har det. Det er svært at sige. Jeg er sur og ked af det på samme tid. Ordene sidder fast."},
        {"response": "Tina siger også I ikke må bestemme det. Det er MINE penge.", "thinking": "Tina forstår mig. Hun siger personalet ikke bare kan bestemme over mig. Jeg vil gerne have at den her pædagog også forstår det."},
        {"response": "*Dennis tripper med foden* Kan du ikke bare... sige til de andre?", "thinking": "Måske kan denne pædagog hjælpe mig. De lytter i hvert fald. Men jeg er bange for at de bare siger det er reglerne."},
        {"response": "Okay... men kun hvis det stadig er MINE penge. Og jeg bestemmer hvad jeg køber.", "thinking": "De respekterer at det er min beslutning. Det føles bedre. Jeg er stadig lidt urolig, men ikke så sur mere."},
    ],
    "simone": [
        {"response": "Hvad laver du overhovedet her? Det hjælper jo ikke alligevel.", "thinking": "Jeg har ikke sovet. Lejligheden er rodet. Jeg gider ikke den her samtale i dag. Lad mig se om de bliver bange."},
        {"response": "Ja, du siger det... Det sagde den forrige også. Og hende før det.", "thinking": "De prøver at være forstående. Men det kender jeg. Alle starter med at være søde. Lad mig se hvad der sker når jeg presser."},
        {"response": "Nej, men DU er jo så professionel. Du har sikkert læst alt om folk som mig.", "thinking": "Jeg provokerer dem. Jeg ved det godt. Men jeg skal vide om de kan holde til mig. Eller om de også smutter."},
        {"response": "*Simone trækker ærmerne ned over hænderne* ... undskyld. Jeg mente det ikke.", "thinking": "De blev ikke vrede. De blev ikke bange. De blev bare... rolige. Det overrasker mig. Jeg føler mig pludselig flov over min egen opførsel."},
        {"response": "Tror du... tror du jeg bliver normal nogen sinde?", "thinking": "Jeg turde spørge. Det er sjældent. Der er noget ved den her person der gør at jeg tør. De dømmer mig ikke."},
    ],
    "morten": [
        {"response": "Hvad fanden kigger du på?", "thinking": "Mælken er væltet overalt. Jeg kan ikke engang lave morgenmad selv mere. Og nu står der en og ser det. Det er ydmygende."},
        {"response": "*Morten knytter hænderne* Jeg KUNNE jo godt det der før! For helvede...", "thinking": "Jeg var tømrer i 18 år. Jeg byggede huse. Og nu kan jeg ikke hælde mælk op. Frustrationen er overvældende."},
        {"response": "Lad mig nu bare selv...", "thinking": "Jeg vil ikke have hjælp. Hjælp betyder at jeg ikke kan selv. Men... det kan jeg heller ikke. Det gør det hele værre."},
        {"response": "*Morten kigger ud af vinduet* Da jeg var tømrer, der kunne jeg... alt.", "thinking": "Jeg tænker på dengang. Da jeg var mig. Nu ved jeg ikke hvem jeg er. Mathias så mig bygge ting. Nu ser han mig spilde mælk."},
        {"response": "... det er fint. *Det er ikke fint*", "thinking": "De tilbød at hjælpe uden at gøre det til en stor ting. Det var... okay. Men sorgen sidder stadig. Det går ikke væk."},
    ],
    "aya": [
        {"response": "*Aya tager ikke høretelefonerne af. Hun har ikke hørt dig.*", "thinking": "Jeg har høretelefonerne på og studerer. Hvis nogen vil tale med mig, skal de sørge for at jeg ved de er der. Bare at begynde at tale virker ikke."},
        {"response": "Kl. 17:30 i stedet for 18:00. Det er 30 minutter tidligere. Hvorfor?", "thinking": "En ændring. Jeg har brug for at forstå den præcist. Hvornår er det, og hvorfor er det ændret? Hvis jeg ikke forstår det, kan jeg ikke forholde mig til det."},
        {"response": "Det stod ikke på ugeskemaet. Ugeskemaet siger pasta kl. 18.", "thinking": "Ugeskemaet er min reference. Hvis ugeskemaet siger én ting og virkeligheden er en anden, er det ugeskemaet der er forkert. Det skal opdateres."},
        {"response": "Fisk. Hvad slags fisk? Jeg spiser ikke fisk med skind. Teksturen er ubehagelig.", "thinking": "Fisk er ikke bare fisk. Der er mange slags. Nogle har skind og det føles forfærdeligt i munden. Jeg har brug for specifik information."},
        {"response": "Kan du skrive det ned? Så opdaterer jeg mit skema. Og jeg laver min egen mad hvis det er fisk med skind.", "thinking": "Hvis de skriver det ned, kan jeg forholde mig til det. Og hvis jeg kan lave min egen mad som alternativ, har jeg en løsning. Det sænker min stress."},
    ],
}

DEMO_FEEDBACK = """## Overordnet vurdering
Dette er en demo-session uden forbindelse til AI. I en rigtig session ville du få detaljeret, personlig feedback baseret på din samtale.

## Eksempel på feedback-format

### Persona-kriterier
Hvert kriterie scores 1-5 med konkrete eksempler fra din samtale.

### Teori-feedback (hvis valgt)
Din tilgang analyseres op mod den valgte teoris kernebegreber. Hvilke begreber var tydelige? Hvilke manglede?

### Forbedringsforslag
Et konkret, handlingsanvisende forslag til næste samtale.

---
*Start med en rigtig API-nøgle for at få ægte AI-genereret feedback.*"""


# Demo session storage
demo_sessions: dict[str, dict] = {}


@app.route("/")
def index():
    personas = PersonaEngine.list_personas()
    theories = PersonaEngine.list_theories()
    return render_template("index.html", personas=personas, theories=theories, demo_mode=DEMO_MODE)


@app.route("/api/start", methods=["POST"])
def start_session():
    data = request.json
    persona_id = data["persona_id"]
    theory_id = data.get("theory_id")

    if DEMO_MODE:
        session_id = f"demo_{persona_id}_{id(data)}"
        # Load persona info directly from JSON
        persona_path = PersonaEngine.PERSONAS_DIR / f"{persona_id}.json"
        with open(persona_path, "r", encoding="utf-8") as f:
            persona_data = json.load(f)

        theory_info = None
        if theory_id:
            theory_path = PersonaEngine.THEORIES_DIR / f"{theory_id}.json"
            with open(theory_path, "r", encoding="utf-8") as f:
                theory_data = json.load(f)
            theory_info = {
                "name": theory_data["name"],
                "authors": theory_data["authors"],
                "summary": theory_data["summary"],
            }

        demo_sessions[session_id] = {
            "persona_id": persona_id,
            "persona_name": persona_data["name"],
            "response_index": 0,
            "interaction_count": 0,
        }

        return jsonify({
            "session_id": session_id,
            "persona_name": persona_data["name"],
            "scenario": persona_data["scenario"],
            "theory": theory_info,
        })

    # Real mode
    model = data.get("model", "sonnet")
    thinking = data.get("extended_thinking", True)
    custom_text = data.get("custom_text")

    session_id = f"{persona_id}_{theory_id}_{id(data)}"

    engine = PersonaEngine(
        persona_id=persona_id,
        theory_id=theory_id if theory_id else None,
        custom_theory_text=custom_text if custom_text else None,
        model=model,
        extended_thinking=thinking,
    )
    engines[session_id] = engine

    scenario = engine.get_scenario()
    theory_info = None
    if engine.theory:
        theory_info = {
            "name": engine.theory["name"],
            "authors": engine.theory["authors"],
            "summary": engine.theory["summary"],
        }

    return jsonify({
        "session_id": session_id,
        "persona_name": engine.persona["name"],
        "scenario": scenario,
        "theory": theory_info,
    })


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    session_id = data["session_id"]
    message = data["message"]

    if DEMO_MODE:
        session = demo_sessions.get(session_id)
        if not session:
            return jsonify({"error": "Session ikke fundet"}), 404

        persona_id = session["persona_id"]
        responses = DEMO_RESPONSES.get(persona_id, DEMO_RESPONSES["ali"])
        idx = session["response_index"]

        if idx < len(responses):
            result = responses[idx]
            session["response_index"] = idx + 1
        else:
            # Cycle through last few responses if conversation continues
            result = random.choice(responses[2:])

        session["interaction_count"] += 1

        return jsonify({
            "response": result["response"],
            "thinking": result.get("thinking"),
            "metadata": {
                "model": "demo",
                "persona": persona_id,
                "interaction_number": session["interaction_count"],
            },
        })

    # Real mode
    engine = engines.get(session_id)
    if not engine:
        return jsonify({"error": "Session ikke fundet"}), 404

    result = engine.chat(message)
    return jsonify(result)


@app.route("/api/feedback", methods=["POST"])
def feedback():
    data = request.json
    session_id = data["session_id"]

    if DEMO_MODE:
        session = demo_sessions.get(session_id)
        return jsonify({
            "analysis": DEMO_FEEDBACK,
            "cost": {"total_tokens": 0, "cost_dkk": 0, "cost_usd": 0},
            "interactions": session["interaction_count"] if session else 0,
        })

    # Real mode
    engine = engines.get(session_id)
    if not engine:
        return jsonify({"error": "Session ikke fundet"}), 404

    analysis = engine.analyze_student()
    cost = engine.estimate_cost()

    return jsonify({
        "analysis": analysis,
        "cost": cost,
        "interactions": len(engine.session_stats["interactions"]),
    })


if __name__ == "__main__":
    mode = "DEMO (uden API key)" if DEMO_MODE else "LIVE (med API key)"
    print(f"\n  Persona Træningsplatform [{mode}]")
    print("  Åbn i browser: http://localhost:5000")
    if DEMO_MODE:
        print("  Tip: Sæt ANTHROPIC_API_KEY for rigtige AI-svar")
    print()
    app.run(debug=True, host="0.0.0.0", port=5000)
