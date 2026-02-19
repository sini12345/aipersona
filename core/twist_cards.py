TWIST_TRIGGER_TURNS = [3, 6]

TWIST_CARDS = {
    "Ali": [
        "En ven skriver, at der er drama udenfor klubben nu. Personaen er split mellem at blive og smutte.",
        "Personaen har lige fået en besked fra en voksen, de ikke stoler på. Irritation stiger markant.",
        "En gammel konflikt bliver nævnt i rummet, og personaen forventer at blive gjort til problem.",
    ],
    "Sofie": [
        "Personaen modtager en besked om flyttet møde i kommunen. Oplevelsen af kontroltab stiger.",
        "En ven aflyser i sidste øjeblik. Personaen trækker sig og bliver mere kortfattet.",
        "Bofællesskabspersonale banker på midt i samtalen. Personaen bliver ekstra sensitiv over for tone.",
    ],
    "Mika": [
        "Personaen får besked om mulig sanktion ved manglende fremmøde. Affekt og modstand stiger.",
        "En nær relation afviser overnatning i nat. Panik og vrede blandes.",
        "Personaen ser en besked fra tidligere kontaktperson, som genaktiverer mistillid til systemet.",
    ],
    "Bent": [
        "Bent finder et gammelt foto af sin kone under samtalen. Han bliver stille — en sjælden åbning for sårbarhed.",
        "Naboen banker hårdt på døren med brok om støj. Bent eskalerer og vil have samtalen til at stoppe.",
        "Bents datter ringer midt i samtalen. Han kigger på telefonen og siger 'Det tager jeg ikke'. Noget lukker i ham.",
    ],
}


def get_twist_card(persona_name: str, turn_number: int) -> str:
    cards = TWIST_CARDS.get(persona_name, [])
    if not cards:
        return "Ingen twist-kort tilgængelige."
    index = (turn_number // 3) % len(cards)
    return cards[index]
