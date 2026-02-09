"""
Flask Web Server: Persona Træningsplatform
Kør med: python web.py
Åbn: http://localhost:5000
"""

from flask import Flask, render_template, request, jsonify
from persona_engine import PersonaEngine

app = Flask(__name__)

# Store active engines per session (simple in-memory store)
engines: dict[str, PersonaEngine] = {}


@app.route("/")
def index():
    personas = PersonaEngine.list_personas()
    theories = PersonaEngine.list_theories()
    return render_template("index.html", personas=personas, theories=theories)


@app.route("/api/start", methods=["POST"])
def start_session():
    data = request.json
    persona_id = data["persona_id"]
    theory_id = data.get("theory_id")
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

    engine = engines.get(session_id)
    if not engine:
        return jsonify({"error": "Session ikke fundet"}), 404

    result = engine.chat(message)
    return jsonify(result)


@app.route("/api/feedback", methods=["POST"])
def feedback():
    data = request.json
    session_id = data["session_id"]

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
    print("\n  Persona Træningsplatform")
    print("  Åbn i browser: http://localhost:5000\n")
    app.run(debug=True, port=5000)
