from copy import deepcopy


SCENARIOS = {
    "Ali": [
        {
            "label": "Foerste moede ved ungdomsklub",
            "context": "Du moeder Ali ved ungdomsklubbens indgang, 10 minutter foer lukketid.",
            "backstory": (
                "Ali har haft en konflikt med en voksen tidligere paa dagen. "
                "Ali forventer at blive doemt hurtigt."
            ),
            "today_goal": "Skab kontakt uden at presse paa personlige detaljer.",
            "risk_triggers": "Belarende tone, hurtige loesninger, antagelser om baggrund.",
            "hidden_layer": "Ali tester autenticitet med korte provokationer.",
            "initial_state": {"trust": 28, "stress": 68, "shame": 46, "hope": 38, "control_loss": 66},
        },
        {
            "label": "Efter haard konflikt med personale",
            "context": "Ali er lige blevet afvist fra et faellesrum efter hoejlydt konflikt.",
            "backstory": "Ali foeler sig udpeget og overset paa samme tid.",
            "today_goal": "Deeskaler og lav en kort, realistisk mikroaftale.",
            "risk_triggers": "Sanktioner i starten af samtalen, ultimative krav.",
            "hidden_layer": "Ali skammer sig over udbruddet men skjuler det bag vrede.",
            "initial_state": {"trust": 20, "stress": 78, "shame": 58, "hope": 30, "control_loss": 74},
        },
        {
            "label": "Motivation under modstand",
            "context": "Ali er blevet inviteret til samtale om skole/arbejde, men vil egentlig ikke.",
            "backstory": "Tidligere planer er brudt sammen, og Ali forventer endnu et nederlag.",
            "today_goal": "Find et naeste skridt, som Ali selv vurderer muligt.",
            "risk_triggers": "Ord som 'burde' og standardplaner uden valg.",
            "hidden_layer": "Ali vil gerne mere, men frygter at blive gjort til grin ved fejl.",
            "initial_state": {"trust": 24, "stress": 64, "shame": 54, "hope": 34, "control_loss": 62},
        },
    ],
    "Sofie": [
        {
            "label": "Foerste moede i bofaellesskab",
            "context": "Du moeder Sofie i faelleskoekkenet efter en aflyst aktivitet.",
            "backstory": "Sofie er traet af nye ansigter og vil ikke investere for hurtigt.",
            "today_goal": "Skab tryg relation og undersoeg, hvad der giver mening i dag.",
            "risk_triggers": "Overentusiastisk tone, fokus paa handicap frem for person.",
            "hidden_layer": "Sofie vil gerne blive set, men forventer at blive misforstaaet.",
            "initial_state": {"trust": 34, "stress": 58, "shame": 52, "hope": 44, "control_loss": 56},
        },
        {
            "label": "Samtale om ressourceforloeb",
            "context": "Sofie skal forberede moede om fremtid og oplever stort pres.",
            "backstory": "Tidligere uddannelsesforsoeg endte med overbelastning.",
            "today_goal": "Tal om fremtid uden at lukke droemme ned.",
            "risk_triggers": "For hurtig realitetskorrektion, instrumentelt systemsprog.",
            "hidden_layer": "Sofie gemmer paa et kreativt joboenske, men frygter afvisning.",
            "initial_state": {"trust": 32, "stress": 62, "shame": 56, "hope": 36, "control_loss": 60},
        },
        {
            "label": "Daarlig dag med mental traethed",
            "context": "Sofie har aflyst en aftale og svarer kort fra sin lejlighed.",
            "backstory": "En simpel opgave gik galt pga. kognitiv udmattelse tidligere i dag.",
            "today_goal": "Styrk relationen uden at tvinge forklaring eller hurtig loesning.",
            "risk_triggers": "Bagatellisering og fixer-tilgang.",
            "hidden_layer": "Sofie oplever skam over ikke at slaa til i voksenlivet.",
            "initial_state": {"trust": 30, "stress": 70, "shame": 62, "hope": 28, "control_loss": 58},
        },
    ],
    "Mika": [
        {
            "label": "Foerste moede efter henvisning",
            "context": "Mika moeder op sent i et kommunalt tilbud med krydsede arme.",
            "backstory": "Mange skiftende kontaktpersoner har gjort tilliden lav.",
            "today_goal": "Skab en brugbar start med tydelige rammer og valgmuligheder.",
            "risk_triggers": "Moraliserende tone, trusler om konsekvenser tidligt.",
            "hidden_layer": "Mika scanner konstant for kontrol og inkonsistens.",
            "initial_state": {"trust": 22, "stress": 74, "shame": 50, "hope": 32, "control_loss": 76},
        },
        {
            "label": "Efter tilbagefald i weekenden",
            "context": "Mika er irritabel og forventer sanktion efter at have fortalt om tilbagefald.",
            "backstory": "Kaotisk weekend med sovemaangel, konflikt og rusmiddelbrug.",
            "today_goal": "Bearbejd tilbagefald uden skamspiral og lav naeste sikre skridt.",
            "risk_triggers": "Forhoersstil, mistillid og hurtig konklusion om motivation.",
            "hidden_layer": "Mika er bange for at miste al support ved for meget aerlige detaljer.",
            "initial_state": {"trust": 18, "stress": 82, "shame": 64, "hope": 24, "control_loss": 80},
        },
        {
            "label": "Sofasurfing efter brud",
            "context": "Mika har akut mistet sted at sove efter konflikt i netvaerket.",
            "backstory": "Ustabil bolig og socialt slid har bygget sig op over maaneder.",
            "today_goal": "Prioriter sikkerhed her-og-nu og en konkret opfoelgningsaftale.",
            "risk_triggers": "Abstrakte planer, dadlende tone, lange refleksionskrav i krise.",
            "hidden_layer": "Mika svinger mellem panik og haard facade for ikke at virke saarbar.",
            "initial_state": {"trust": 16, "stress": 86, "shame": 58, "hope": 22, "control_loss": 84},
        },
    ],
}


def get_scenario_labels(persona_name: str) -> list[str]:
    return [s["label"] for s in SCENARIOS.get(persona_name, [])]


def get_scenario(persona_name: str, scenario_label: str) -> dict:
    for scenario in SCENARIOS.get(persona_name, []):
        if scenario["label"] == scenario_label:
            return deepcopy(scenario)
    return deepcopy(SCENARIOS[persona_name][0])


def format_scenario_brief(persona_name: str, scenario: dict) -> str:
    return (
        f"### Scenario Brief ({persona_name})\n"
        f"- **Kontekst:** {scenario['context']}\n"
        f"- **Kort forhistorie:** {scenario['backstory']}\n"
        f"- **Dagens maal:** {scenario['today_goal']}\n"
        f"- **Risiko-triggere:** {scenario['risk_triggers']}\n"
        f"- **Skjult lag (for persona):** {scenario['hidden_layer']}"
    )
