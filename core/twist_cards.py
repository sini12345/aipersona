TWIST_TRIGGER_TURNS = [3, 6]

TWIST_CARDS = {
    "Ali": [
        "En ven skriver, at der er drama udenfor klubben nu. Personaen er split mellem at blive og smutte.",
        "Personaen har lige faaet en besked fra en voksen, de ikke stoler paa. Irritation stiger markant.",
        "En gammel konflikt bliver naevnt i rummet, og personaen forventer at blive gjort til problem.",
    ],
    "Sofie": [
        "Personaen modtager en besked om flyttet moede i kommunen. Oplevelsen af kontroltab stiger.",
        "En ven aflyser i sidste oeeblik. Personaen traekker sig og bliver mere kortfattet.",
        "Bostedspersonale banker paa midt i samtalen. Personaen bliver ekstra sensitiv over for tone.",
    ],
    "Mika": [
        "Personaen faar besked om mulig sanktion ved manglende fremmoede. Affekt og modstand stiger.",
        "En naer relation afviser overnatning i nat. Panik og vrede blandes.",
        "Personaen ser en besked fra tidligere kontaktperson, som genaktiverer mistillid til systemet.",
    ],
}


def get_twist_card(persona_name: str, turn_number: int) -> str:
    cards = TWIST_CARDS.get(persona_name, [])
    if not cards:
        return "Ingen twist-kort tilgaengelige."
    index = (turn_number // 3) % len(cards)
    return cards[index]
