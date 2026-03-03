from copy import deepcopy
from pathlib import Path
import re


BASE_SCENARIOS: dict[str, list[dict]] = {
    "Ali": [
        {
            "label": "Første møde ved ungdomsklub",
            "context": "Du møder Ali ved ungdomsklubbens indgang, 10 minutter før lukketid.",
            "backstory": (
                "Ali har haft en konflikt med en voksen tidligere på dagen. "
                "Ali forventer at blive dømt hurtigt."
            ),
            "today_goal": "Skab kontakt uden at presse på personlige detaljer.",
            "risk_triggers": "Belærende tone, hurtige løsninger, antagelser om baggrund.",
            "hidden_layer": "Ali tester autenticitet med korte provokationer.",
            "initial_state": {"trust": 28, "stress": 68, "shame": 46, "hope": 38, "control_loss": 66},
            "state_modifiers": {"pressure_penalty_mult": 1.1},
        },
        {
            "label": "Efter hård konflikt med personale",
            "context": "Ali er lige blevet afvist fra et fællesrum efter højlydt konflikt.",
            "backstory": "Ali føler sig udpeget og overset på samme tid.",
            "today_goal": "Deeskaler og lav en kort, realistisk mikroaftale.",
            "risk_triggers": "Sanktioner i starten af samtalen, ultimative krav.",
            "hidden_layer": "Ali skammer sig over udbruddet men skjuler det bag vrede.",
            "initial_state": {"trust": 20, "stress": 78, "shame": 58, "hope": 30, "control_loss": 74},
            "state_modifiers": {"pressure_penalty_mult": 1.25, "deescalation_boost_mult": 1.15},
        },
        {
            "label": "Motivation under modstand",
            "context": "Ali er blevet inviteret til samtale om skole/arbejde, men vil egentlig ikke.",
            "backstory": "Tidligere planer er brudt sammen, og Ali forventer endnu et nederlag.",
            "today_goal": "Find et næste skridt, som Ali selv vurderer muligt.",
            "risk_triggers": "Ord som 'burde' og standardplaner uden valg.",
            "hidden_layer": "Ali vil gerne mere, men frygter at blive gjort til grin ved fejl.",
            "initial_state": {"trust": 24, "stress": 64, "shame": 54, "hope": 34, "control_loss": 62},
            "state_modifiers": {"validation_boost_mult": 1.1, "pressure_penalty_mult": 1.15},
        },
    ],
    "Sofie": [
        {
            "label": "Første møde i bofællesskab",
            "context": "Du møder Sofie i fælleskøkkenet efter en aflyst aktivitet.",
            "backstory": "Sofie er træt af nye ansigter og vil ikke investere for hurtigt.",
            "today_goal": "Skab tryg relation og undersøg, hvad der giver mening i dag.",
            "risk_triggers": "Overentusiastisk tone, fokus på handicap frem for person.",
            "hidden_layer": "Sofie vil gerne blive set, men forventer at blive misforstået.",
            "initial_state": {"trust": 34, "stress": 58, "shame": 52, "hope": 44, "control_loss": 56},
            "state_modifiers": {"validation_boost_mult": 1.1},
        },
        {
            "label": "Samtale om ressourceforløb",
            "context": "Sofie skal forberede møde om fremtid og oplever stort pres.",
            "backstory": "Tidligere uddannelsesforsøg endte med overbelastning.",
            "today_goal": "Tal om fremtid uden at lukke drømme ned.",
            "risk_triggers": "For hurtig realitetskorrektion, instrumentelt systemsprog.",
            "hidden_layer": "Sofie gemmer på et kreativt jobønske, men frygter afvisning.",
            "initial_state": {"trust": 32, "stress": 62, "shame": 56, "hope": 36, "control_loss": 60},
            "state_modifiers": {"validation_boost_mult": 1.15, "pressure_penalty_mult": 1.1},
        },
        {
            "label": "Dårlig dag med mental træthed",
            "context": "Sofie har aflyst en aftale og svarer kort fra sin lejlighed.",
            "backstory": "En simpel opgave gik galt pga. kognitiv udmattelse tidligere i dag.",
            "today_goal": "Styrk relationen uden at tvinge forklaring eller hurtig løsning.",
            "risk_triggers": "Bagatellisering og fixer-tilgang.",
            "hidden_layer": "Sofie oplever skam over ikke at slå til i voksenlivet.",
            "initial_state": {"trust": 30, "stress": 70, "shame": 62, "hope": 28, "control_loss": 58},
            "state_modifiers": {"deescalation_boost_mult": 1.15, "pressure_penalty_mult": 1.2},
        },
    ],
    "Mika": [
        {
            "label": "Første møde efter henvisning",
            "context": "Mika møder op sent i et kommunalt tilbud med krydsede arme.",
            "backstory": "Mange skiftende kontaktpersoner har gjort tilliden lav.",
            "today_goal": "Skab en brugbar start med tydelige rammer og valgmuligheder.",
            "risk_triggers": "Moraliserende tone, trusler om konsekvenser tidligt.",
            "hidden_layer": "Mika scanner konstant for kontrol og inkonsistens.",
            "initial_state": {"trust": 22, "stress": 74, "shame": 50, "hope": 32, "control_loss": 76},
            "state_modifiers": {"pressure_penalty_mult": 1.2, "boundary_boost_mult": 1.1},
        },
        {
            "label": "Efter tilbagefald i weekenden",
            "context": "Mika er irritabel og forventer sanktion efter at have fortalt om tilbagefald.",
            "backstory": "Kaotisk weekend med søvnmangel, konflikt og rusmiddelbrug.",
            "today_goal": "Bearbejd tilbagefald uden skamspiral og lav næste sikre skridt.",
            "risk_triggers": "Forhørsstil, mistillid og hurtig konklusion om motivation.",
            "hidden_layer": "Mika er bange for at miste al support ved for mange ærlige detaljer.",
            "initial_state": {"trust": 18, "stress": 82, "shame": 64, "hope": 24, "control_loss": 80},
            "state_modifiers": {"pressure_penalty_mult": 1.3, "deescalation_boost_mult": 1.1},
        },
        {
            "label": "Sofasurfing efter brud",
            "context": "Mika har akut mistet sted at sove efter konflikt i netværket.",
            "backstory": "Ustabil bolig og socialt slid har bygget sig op over måneder.",
            "today_goal": "Prioritér sikkerhed her-og-nu og en konkret opfølgningsaftale.",
            "risk_triggers": "Abstrakte planer, dadlende tone, lange refleksionskrav i krise.",
            "hidden_layer": "Mika svinger mellem panik og hård facade for ikke at virke sårbar.",
            "initial_state": {"trust": 16, "stress": 86, "shame": 58, "hope": 22, "control_loss": 84},
            "state_modifiers": {"pressure_penalty_mult": 1.35, "deescalation_boost_mult": 1.2},
        },
    ],
}


def _persona_name_from_profile_path(path: Path) -> str:
    # Keep in sync with app.py's persona-name derivation.
    # Example: sara_eftervaern.md -> Sara
    stem = path.stem
    if stem.endswith("_system_prompt"):
        stem = stem[: -len("_system_prompt")]
    return stem.split("_")[0].capitalize()


def _initial_state_from_inner_state(inner_state: str) -> dict:
    text = (inner_state or "").lower()

    trust = 30
    stress = 65
    shame = 50
    hope = 35
    control_loss = 60

    if any(w in text for w in ["panik", "alarm", "krise", "overlevelse", "ingen sovested", "akut"]):
        trust -= 10
        stress += 20
        hope -= 10
        control_loss += 15

    if any(
        w in text
        for w in [
            "skam",
            "flov",
            "utilstrækkelig",
            "bange for fejl",
            "bange for at have lavet fejl",
        ]
    ):
        shame += 15
        trust -= 5
        stress += 5

    if any(w in text for w in ["vagt", "afvis", "klar til at afvise", "mistillid"]):
        trust -= 8
        control_loss += 8

    if any(w in text for w in ["træt", "flad", "lav energi", "udmattet"]):
        stress += 8
        hope -= 5

    def _clamp(v: int) -> int:
        return max(0, min(100, int(v)))

    return {
        "trust": _clamp(trust),
        "stress": _clamp(stress),
        "shame": _clamp(shame),
        "hope": _clamp(hope),
        "control_loss": _clamp(control_loss),
    }


def _state_modifiers_from_inner_state(inner_state: str) -> dict:
    text = (inner_state or "").lower()
    modifiers: dict[str, float] = {}

    # Default: a little extra sensitivity to pressure.
    modifiers["pressure_penalty_mult"] = 1.1

    if any(w in text for w in ["panik", "alarm", "krise", "overlevelse", "akut"]):
        modifiers["pressure_penalty_mult"] = max(modifiers.get("pressure_penalty_mult", 1.0), 1.3)
        modifiers["deescalation_boost_mult"] = 1.2

    if "skam" in text or "flov" in text:
        modifiers["validation_boost_mult"] = 1.15
        modifiers["pressure_penalty_mult"] = max(modifiers.get("pressure_penalty_mult", 1.0), 1.2)

    if any(w in text for w in ["selvbestemmelse", "voksen", "grænse", "ramme", "kontroltab"]):
        modifiers["boundary_boost_mult"] = 1.1

    return modifiers


def _parse_training_scenarios(persona_name: str, markdown: str) -> list[dict]:
    lines = markdown.splitlines()

    start_idx = None
    for i, line in enumerate(lines):
        if line.strip() == "## Training Scenarios":
            start_idx = i + 1
            break

    if start_idx is None:
        return []

    end_idx = len(lines)
    for i in range(start_idx, len(lines)):
        if lines[i].startswith("## ") and lines[i].strip() != "## Training Scenarios":
            end_idx = i
            break

    block = lines[start_idx:end_idx]

    scenarios: list[dict] = []
    current: dict | None = None

    header_re = re.compile(r"^###\s*Scenario\s*\d+\s*:\s*(.*)$", re.IGNORECASE)
    # Accept both `**Situation:** text` and `**Situation**: text` styles.
    field_re = re.compile(r"^\*\*(.+?)\*\*\s*(?::\s*)?(.*)$")

    for raw in block:
        line = raw.strip()
        if not line:
            continue

        m = header_re.match(line)
        if m:
            if current:
                scenarios.append(current)
            title = m.group(1).strip().strip('"').strip()
            current = {
                "label": title or "Scenarie",
                "context": "",
                "backstory": "",
                "today_goal": "",
                "risk_triggers": "",
                "hidden_layer": "",
                "initial_state": {},
                "state_modifiers": {},
            }
            continue

        if not current:
            continue

        fm = field_re.match(line)
        if not fm:
            continue

        key = fm.group(1).strip().rstrip(":").lower()
        value = fm.group(2).strip()

        if "situation" in key:
            current["context"] = value
        elif "indre tilstand" in key:
            inner_state = value
            current["backstory"] = inner_state
            current["hidden_layer"] = (
                f"{persona_name} beskytter sig selv og tester, om du presser eller kan holde roen."
            )
            current["initial_state"] = _initial_state_from_inner_state(inner_state)
            current["state_modifiers"] = _state_modifiers_from_inner_state(inner_state)
        elif "god tilgang" in key:
            current["today_goal"] = value
        elif "typisk fejl" in key:
            current["risk_triggers"] = value

    if current:
        scenarios.append(current)

    cleaned: list[dict] = []
    for s in scenarios:
        if s.get("label") and s.get("context") and s.get("today_goal"):
            cleaned.append(s)
    return cleaned


def _load_profile_scenarios(personas_dir: str = "personas") -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for path in sorted(Path(personas_dir).glob("*.md")):
        if path.name.endswith("_system_prompt.md"):
            continue

        persona_name = _persona_name_from_profile_path(path)

        try:
            md = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            md = path.read_text(encoding="cp1252")

        scenarios = _parse_training_scenarios(persona_name, md)
        if scenarios:
            out[persona_name] = scenarios

    return out


def _build_scenarios() -> dict[str, list[dict]]:
    merged: dict[str, list[dict]] = {k: deepcopy(v) for k, v in BASE_SCENARIOS.items()}
    profile_scenarios = _load_profile_scenarios()

    for persona_name, scenarios in profile_scenarios.items():
        existing = merged.get(persona_name, [])
        existing_labels = {s.get("label") for s in existing}

        for s in scenarios:
            if s.get("label") in existing_labels:
                continue
            existing.append(s)

        if existing:
            merged[persona_name] = existing

    return merged


SCENARIOS = _build_scenarios()


def _default_scenario(persona_name: str) -> dict:
    return {
        "label": "Standard samtale",
        "context": f"Du møder {persona_name} i en almindelig opstartssamtale.",
        "backstory": f"{persona_name} er afventende og vurderer, om relationen virker tryg.",
        "today_goal": "Skab kontakt og afklar et realistisk næste skridt sammen.",
        "risk_triggers": "Hurtige konklusioner, pres og manglende valgmuligheder.",
        "hidden_layer": f"{persona_name} tester, om du er konsistent og respektfuld i tonen.",
        "initial_state": {"trust": 30, "stress": 60, "shame": 50, "hope": 40, "control_loss": 60},
        "state_modifiers": {"pressure_penalty_mult": 1.1},
    }


def get_scenario_labels(persona_name: str) -> list[str]:
    scenarios = SCENARIOS.get(persona_name, [])
    if scenarios:
        return [s["label"] for s in scenarios]
    return [_default_scenario(persona_name)["label"]]


def get_scenario(persona_name: str, scenario_label: str) -> dict:
    scenarios = SCENARIOS.get(persona_name, [])
    for scenario in scenarios:
        if scenario["label"] == scenario_label:
            return deepcopy(scenario)
    if scenarios:
        return deepcopy(scenarios[0])
    return deepcopy(_default_scenario(persona_name))


def format_scenario_brief(persona_name: str, scenario: dict) -> str:
    scenario = scenario or _default_scenario(persona_name)
    return (
        f"### Scenarie-brief ({persona_name})\n"
        f"- **Kontekst:** {scenario.get('context', '')}\n"
        f"- **Kort forhistorie:** {scenario.get('backstory', '')}\n"
        f"- **Dagens mål:** {scenario.get('today_goal', '')}\n"
        f"- **Risiko-triggere:** {scenario.get('risk_triggers', '')}\n"
        f"- **Skjult lag (for persona):** {scenario.get('hidden_layer', '')}"
    )
