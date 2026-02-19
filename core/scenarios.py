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
        },
        {
            "label": "Efter hård konflikt med personale",
            "context": "Ali er lige blevet afvist fra et fællesrum efter højlydt konflikt.",
            "backstory": "Ali føler sig udpeget og overset på samme tid.",
            "today_goal": "Deeskaler og lav en kort, realistisk mikroaftale.",
            "risk_triggers": "Sanktioner i starten af samtalen, ultimative krav.",
            "hidden_layer": "Ali skammer sig over udbruddet men skjuler det bag vrede.",
            "initial_state": {"trust": 20, "stress": 78, "shame": 58, "hope": 30, "control_loss": 74},
        },
        {
            "label": "Motivation under modstand",
            "context": "Ali er blevet inviteret til samtale om skole/arbejde, men vil egentlig ikke.",
            "backstory": "Tidligere planer er brudt sammen, og Ali forventer endnu et nederlag.",
            "today_goal": "Find et næste skridt, som Ali selv vurderer muligt.",
            "risk_triggers": "Ord som 'burde' og standardplaner uden valg.",
            "hidden_layer": "Ali vil gerne mere, men frygter at blive gjort til grin ved fejl.",
            "initial_state": {"trust": 24, "stress": 64, "shame": 54, "hope": 34, "control_loss": 62},
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
        },
        {
            "label": "Samtale om ressourceforløb",
            "context": "Sofie skal forberede møde om fremtid og oplever stort pres.",
            "backstory": "Tidligere uddannelsesforsøg endte med overbelastning.",
            "today_goal": "Tal om fremtid uden at lukke drømme ned.",
            "risk_triggers": "For hurtig realitetskorrektion, instrumentelt systemsprog.",
            "hidden_layer": "Sofie gemmer på et kreativt jobønske, men frygter afvisning.",
            "initial_state": {"trust": 32, "stress": 62, "shame": 56, "hope": 36, "control_loss": 60},
        },
        {
            "label": "Dårlig dag med mental træthed",
            "context": "Sofie har aflyst en aftale og svarer kort fra sin lejlighed.",
            "backstory": "En simpel opgave gik galt pga. kognitiv udmattelse tidligere i dag.",
            "today_goal": "Styrk relationen uden at tvinge forklaring eller hurtig løsning.",
            "risk_triggers": "Bagatellisering og fixer-tilgang.",
            "hidden_layer": "Sofie oplever skam over ikke at slå til i voksenlivet.",
            "initial_state": {"trust": 30, "stress": 70, "shame": 62, "hope": 28, "control_loss": 58},
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
        },
        {
            "label": "Efter tilbagefald i weekenden",
            "context": "Mika er irritabel og forventer sanktion efter at have fortalt om tilbagefald.",
            "backstory": "Kaotisk weekend med søvnmangel, konflikt og rusmiddelbrug.",
            "today_goal": "Bearbejd tilbagefald uden skamspiral og lav næste sikre skridt.",
            "risk_triggers": "Forhørsstil, mistillid og hurtig konklusion om motivation.",
            "hidden_layer": "Mika er bange for at miste al support ved for mange ærlige detaljer.",
            "initial_state": {"trust": 18, "stress": 82, "shame": 64, "hope": 24, "control_loss": 80},
        },
        {
            "label": "Sofasurfing efter brud",
            "context": "Mika har akut mistet sted at sove efter konflikt i netværket.",
            "backstory": "Ustabil bolig og socialt slid har bygget sig op over måneder.",
            "today_goal": "Prioritér sikkerhed her-og-nu og en konkret opfølgningsaftale.",
            "risk_triggers": "Abstrakte planer, dadlende tone, lange refleksionskrav i krise.",
            "hidden_layer": "Mika svinger mellem panik og hård facade for ikke at virke sårbar.",
            "initial_state": {"trust": 16, "stress": 86, "shame": 58, "hope": 22, "control_loss": 84},
        },
    ],
    "Bent": [
        {
            "label": "Første hjemmebesøg",
            "context": "Du besøger Bent i hans lejlighed for første gang som ny kontaktperson fra hjemmeplejen.",
            "backstory": (
                "Bent har haft tre forskellige kontaktpersoner det sidste år. "
                "Han har ryddet op og sat kaffe over, men åbner halvt i døren og siger 'Jeg passer mig selv'."
            ),
            "today_goal": "Skab en respektfuld kontakt uden at overtage. Lad Bent definere rammerne.",
            "risk_triggers": "Overdreven omsorgstale, spørgsmål om alkohol tidligt, at se sig om i hjemmet uden lov.",
            "hidden_layer": "Bent er ensom men oplever ethvert tilbud om hjælp som et angreb på hans mandsidentitet.",
            "initial_state": {"trust": 26, "stress": 60, "shame": 48, "hope": 36, "control_loss": 68},
        },
        {
            "label": "Samtale om alkohol",
            "context": "Bent har selv nævnt at han 'drikker lidt for meget' på det seneste. Du har fået mulighed for at tale med ham.",
            "backstory": (
                "Bents datter ringede bekymret til kommunen for to uger siden. "
                "Det ved Bent. Han er vred over det, men har alligevel åbnet for samtalen."
            ),
            "today_goal": "Undersøg Bents egen oplevelse af sit alkoholforbrug uden at moralisere eller presse.",
            "risk_triggers": (
                "Bruge ord som 'alkoholiker', 'misbrug' eller 'du skal'. "
                "Referere til datterens bekymring som legitimering."
            ),
            "hidden_layer": "Bent ved godt at det er gået for vidt, men at indrømme det føles som kapitulation.",
            "initial_state": {"trust": 30, "stress": 65, "shame": 60, "hope": 30, "control_loss": 65},
        },
        {
            "label": "Datter har ringet til kommunen",
            "context": "Bent har fundet ud af at hans datter har ringet til kommunen med bekymringer. Han er vred og føler sig forrådt.",
            "backstory": (
                "Forholdet til datteren er ambivalent — kærlighed og stolthed blandet med en følelse af ikke at slå til som far. "
                "Bents kone døde for seks år siden, og datteren er det eneste tætte familiemedlem."
            ),
            "today_goal": "Deeskaler vreden, anerkend krænkelsen og bevar relationen til Bent.",
            "risk_triggers": (
                "Forsvare datterens beslutning, bagatellisere hans vrede, "
                "bruge situationen til at tale om hans alkoholforbrug."
            ),
            "hidden_layer": "Bent er dybt såret over at være 'rapporteret'. Han oplever det som bevis på at han er holdt op med at være familiefar.",
            "initial_state": {"trust": 18, "stress": 78, "shame": 66, "hope": 24, "control_loss": 76},
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
        f"### Scenarie-brief ({persona_name})\n"
        f"- **Kontekst:** {scenario['context']}\n"
        f"- **Kort forhistorie:** {scenario['backstory']}\n"
        f"- **Dagens mål:** {scenario['today_goal']}\n"
        f"- **Risiko-triggere:** {scenario['risk_triggers']}\n"
        f"- **Skjult lag (for persona):** {scenario['hidden_layer']}"
    )
