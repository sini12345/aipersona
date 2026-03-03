from copy import deepcopy


SCENARIOS = {
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
