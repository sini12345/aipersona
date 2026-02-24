"""
Genererer en standalone HTML-rapport over en afsluttet træningssession.
Rapporten kan åbnes i en browser og printes til PDF (Fil → Print → Gem som PDF).
"""
import html
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# Interne hjælpefunktioner
# ---------------------------------------------------------------------------

def _esc(text: str) -> str:
    """HTML-escape en tekststreng."""
    return html.escape(str(text or ""), quote=True)


def _delta_arrow(delta: int) -> str:
    if delta > 0:
        return f'<span class="up">▲ +{delta}</span>'
    if delta < 0:
        return f'<span class="down">▼ {delta}</span>'
    return '<span class="neutral">— 0</span>'


def _state_table(state_history: list[dict]) -> str:
    if not state_history:
        return "<p><em>Ingen tilstandsdata.</em></p>"

    labels = {
        "trust": "Tillid",
        "stress": "Stress",
        "shame": "Skam",
        "hope": "Håb",
        "control_loss": "Kontroltab",
    }
    start = state_history[0]
    end = state_history[-1]

    rows = ""
    for key, label in labels.items():
        s = start.get(key, 0)
        e = end.get(key, 0)
        delta = e - s
        rows += (
            f"<tr>"
            f"<td>{_esc(label)}</td>"
            f"<td>{s}</td>"
            f"<td>{e}</td>"
            f"<td>{_delta_arrow(delta)}</td>"
            f"</tr>\n"
        )

    return f"""<table class="state-table">
<thead>
  <tr><th>Dimension</th><th>Start</th><th>Slut</th><th>Ændring</th></tr>
</thead>
<tbody>
{rows}
</tbody>
</table>"""


def _transcript_html(turns: list[dict]) -> str:
    if not turns:
        return "<p><em>Ingen samtale registreret.</em></p>"

    blocks = ""
    for i, turn in enumerate(turns, 1):
        role = turn.get("role", "user")
        content = _esc(turn.get("content", ""))
        # Bevar linjeskift
        content = content.replace("\n", "<br>")

        if role == "user":
            label = "Studerende"
            css = "turn-user"
        else:
            label = "Persona"
            css = "turn-persona"

        blocks += f"""<div class="turn {css}">
  <div class="turn-header"><span class="turn-num">#{i//2 + i%2}</span> <strong>{label}</strong></div>
  <div class="turn-body">{content}</div>
</div>
"""
    return blocks


def _twist_section(twist_history: list[dict]) -> str:
    if not twist_history:
        return ""
    items = ""
    for t in twist_history:
        items += f"<li><strong>Tur {_esc(t['turn'])}:</strong> {_esc(t['card'])}</li>\n"
    return f"""<section>
<h2>Twist-hændelser</h2>
<ul class="twist-list">{items}</ul>
</section>"""


def _feedback_html(feedback_text: str) -> str:
    if not feedback_text or not feedback_text.strip():
        return "<p><em>Ingen feedback genereret.</em></p>"
    # Simpel konvertering: linjeskift → <br>, understøtter grundlæggende markdown bold
    lines = feedback_text.split("\n")
    result = []
    for line in lines:
        escaped = _esc(line)
        # Marker overskrifter (store bogstaver-linjer, fx "3 STYRKER")
        if line.strip().isupper() and len(line.strip()) > 2:
            result.append(f"<h3>{escaped}</h3>")
        else:
            result.append(escaped)
    return "<p>" + "<br>\n".join(result) + "</p>"


def _css() -> str:
    return """
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 13pt;
        line-height: 1.6;
        color: #1a1a1a;
        background: #fff;
        padding: 2cm 2.5cm;
        max-width: 900px;
        margin: 0 auto;
    }

    h1 { font-size: 22pt; color: #1a3a5c; margin-bottom: 0.3em; }
    h2 { font-size: 14pt; color: #1a3a5c; border-bottom: 2px solid #d0dce8;
         padding-bottom: 4px; margin: 1.8em 0 0.8em; }
    h3 { font-size: 12pt; font-weight: 700; margin: 1em 0 0.3em; color: #333; }

    .meta-table { border-collapse: collapse; width: 100%; margin: 1em 0 1.5em; }
    .meta-table td { padding: 5px 10px 5px 0; vertical-align: top; }
    .meta-table td:first-child { font-weight: 600; color: #555; width: 160px; }

    .state-table { border-collapse: collapse; width: 100%; margin: 0.5em 0; }
    .state-table th, .state-table td { border: 1px solid #cdd6df; padding: 6px 12px; text-align: left; }
    .state-table th { background: #eaf0f6; font-weight: 600; }
    .state-table tr:nth-child(even) { background: #f7fafc; }

    .up   { color: #1a7a3c; font-weight: 600; }
    .down { color: #b91c1c; font-weight: 600; }
    .neutral { color: #888; }

    .turn { border-radius: 6px; padding: 10px 14px; margin: 8px 0; page-break-inside: avoid; }
    .turn-user    { background: #eef4fb; border-left: 4px solid #3b7dd8; }
    .turn-persona { background: #f4f4f4; border-left: 4px solid #888; }
    .turn-header  { font-size: 10pt; color: #666; margin-bottom: 4px; }
    .turn-num     { display: inline-block; background: #d0dce8; border-radius: 3px;
                    padding: 0 5px; font-size: 9pt; margin-right: 4px; }
    .turn-body    { font-size: 12pt; }

    .twist-list { padding-left: 1.5em; }
    .twist-list li { margin: 0.4em 0; }

    .feedback-box { background: #fffbf0; border: 1px solid #e8d97a;
                    border-radius: 6px; padding: 14px 18px; margin-top: 0.5em; }

    footer { margin-top: 3em; font-size: 10pt; color: #aaa;
             border-top: 1px solid #eee; padding-top: 0.8em; }

    @media print {
        body { padding: 0; }
        .turn { page-break-inside: avoid; }
        h2 { page-break-after: avoid; }
    }
    """


# ---------------------------------------------------------------------------
# Offentlig funktion
# ---------------------------------------------------------------------------

def generate_html_report(session: dict, feedback_text: str, out_dir: str = "data/reports") -> str:
    """
    Genererer en HTML-rapport for den afsluttede session.

    Returnerer stien til den gemte fil.
    """
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    persona = session.get("persona_name", "Persona")
    scenario = session.get("scenario_label", "—")
    goal = session.get("learning_goal", "—")
    difficulty = session.get("difficulty", "—")
    started = session.get("started_at", "")
    ended = session.get("ended_at", "")
    turns = session.get("turns", [])
    state_history = session.get("state_history", [])
    twist_history = session.get("twist_history", [])
    blind_mode = "Ja" if session.get("blind_mode") else "Nej"
    speed_round = "Ja" if session.get("speed_round_enabled") else "Nej"
    turn_count = session.get("turn_count", 0)

    # Formatér datoer
    def fmt_dt(iso: str) -> str:
        try:
            return datetime.fromisoformat(iso).strftime("%d.%m.%Y %H:%M")
        except Exception:
            return iso or "—"

    generated_at = datetime.utcnow().strftime("%d.%m.%Y %H:%M")

    meta_rows = f"""
    <tr><td>Persona</td><td>{_esc(persona)}</td></tr>
    <tr><td>Scenarie</td><td>{_esc(scenario)}</td></tr>
    <tr><td>Læringsmål</td><td>{_esc(goal)}</td></tr>
    <tr><td>Sværhedsgrad</td><td>{_esc(difficulty)}</td></tr>
    <tr><td>Antal ture</td><td>{turn_count}</td></tr>
    <tr><td>Blind mode</td><td>{blind_mode}</td></tr>
    <tr><td>Speed round</td><td>{speed_round}</td></tr>
    <tr><td>Startet</td><td>{fmt_dt(started)}</td></tr>
    <tr><td>Afsluttet</td><td>{fmt_dt(ended)}</td></tr>
    """

    twist_html = _twist_section(twist_history)

    html_doc = f"""<!DOCTYPE html>
<html lang="da">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Samtalerapport — {_esc(persona)} — {_esc(scenario)}</title>
  <style>{_css()}</style>
</head>
<body>

<h1>Samtalerapport</h1>
<table class="meta-table">
{meta_rows}
</table>

<section>
<h2>Tilstandsudvikling</h2>
<p style="font-size:11pt;color:#666;margin-bottom:0.6em">
  Positiv ændring i Tillid og Håb — og fald i Stress, Skam og Kontroltab — indikerer god kontaktkvalitet.
</p>
{_state_table(state_history)}
</section>

<section>
<h2>Samtaletransskription</h2>
{_transcript_html(turns)}
</section>

{twist_html}

<section>
<h2>Feedback</h2>
<div class="feedback-box">
{_feedback_html(feedback_text)}
</div>
</section>

<footer>
  Genereret af Persona Trainer · {generated_at} UTC
  · Session-ID: {_esc(session.get('id', '—'))}
</footer>

</body>
</html>"""

    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"rapport_{persona.lower()}_{stamp}.html"
    filepath = Path(out_dir) / filename
    filepath.write_text(html_doc, encoding="utf-8")
    return str(filepath)
