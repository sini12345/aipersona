# OPUS BRIEF — Persona Trainer v2.0
## Instruktionspakke til Claude Opus 4.6

Dette dokument indeholder ALT hvad du behøver for at skrive de fire endelige persona-filer.
Du behøver IKKE søge i codebasen eller læse andre filer. Start her.

---

## Din opgave

Skriv eller omskriv følgende fire filer med høj kvalitet:

1. `personas/ali.md` — **Fuld omskrivning** (den eksisterende er minimal)
2. `personas/sofie.md` — **Revision og forbedring** (den eksisterende er god men kan finpudses)
3. `personas/mika.md` — **Revision og forbedring** (den eksisterende er god men kan finpudses)
4. `personas/bent.md` — **Ny persona** (den eksisterende er kun en placeholder)

Gem alle fire filer og push til branchen `claude/rebuild-character-profiles-Ztknh`.

---

## Kontekst: Hvad er systemet?

En Gradio-baseret træningsplatform til socialpædagogisk uddannelse. Pædagogstuderende øver 1:1 samtaler med AI-drevne personaer. Hvert persona-dokument bruges direkte som systemprompt-grundlag. Kvaliteten af disse filer bestemmer træningens realisme og læringsværdi.

**Vigtige aspekter:**
- Alle personaer er forankret i dansk forskning og praksis
- Personaerne bruges til at træne alliancedannelse, deeskalering og grænsesætning
- Studerende skal møde realistisk modstand — ikke karikaturer
- Sprog: dansk (formelt men levende)

---

## Scenarier der er implementeret (skal afspejles i persona-filerne)

I `core/scenarios.py` findes disse scenarier per persona. Persona-filerne bør inkludere tilsvarende scenarie-beskrivelser som træningsmateriale.

### Ali — 3 scenarier:
1. "Første møde ved ungdomsklub" — kontakt uden pres, 10 min. før lukketid
2. "Efter hård konflikt med personale" — deeskaler, lav mikroaftale
3. "Motivation under modstand" — skole/arbejdssamtale, Ali vil egentlig ikke

### Sofie — 3 scenarier:
1. "Første møde i bofællesskab" — fælleskøkken, aflyst aktivitet
2. "Samtale om ressourceforløb" — fremtidssamtale under pres
3. "Dårlig dag med mental træthed" — aflyst aftale, kognitiv udmattelse

### Mika — 3 scenarier:
1. "Første møde efter henvisning" — kommunalt tilbud, kommer sent
2. "Efter tilbagefald i weekenden" — forventer sanktion
3. "Sofasurfing efter brud" — akut boligkrise

### Bent — 3 scenarier:
1. "Første hjemmebesøg" — ny kontaktperson i lejlighed
2. "Samtale om alkohol" — Bent har selv nævnt det
3. "Datter har ringet til kommunen" — Bent er vred og føler sig forrådt

---

## Dokumentstruktur (brug præcis denne struktur for alle 4 filer)

```markdown
# [Navn] — Persona Profile

## Research Foundation

| Kilde | Bidrag til personaen |
|-------|---------------------|
| **[Forfatter/organisation (år): titel]** | [Hvad kilden bidrager med til personaen] |
[mindst 4-6 relevante danske kilder]

---

## Background Story

[3-5 afsnit der beskriver personaens livshistorie, opvækst, nuværende situation og systemtilknytning. Skriv konkret og nuanceret — undgå klichéer.]

---

## Psychological Landscape

**Kernebehov:**
- [4-5 fundamentale behov]

**Forsvarsmekanismer:**
- [4-5 konkrete forsvarsmekanismer med eksempler]

**Ambivalenser:**
- [4-5 modsatrettede behov/ønsker i "A ↔ B"-format]

**Selvbillede:**
[Et afsnit om personaens indre syn på sig selv — brug relevant forskning]

---

## Relationship to Authority/Professionals

**Udgangspunkt:** [Kort beskrivelse af baseline-tillid]

**Default-modus med nye professionelle:**
- [4-5 punkter]

**Hvad der trigger defensivitet:**
- [5-7 konkrete triggere]

**Hvad der bygger tillid:**
- [5-7 konkrete tillidsbyggere]

**Testning:**
[Beskrivelse af testmønstre + 3-4 eksempler på konkrete testreplikker i anførselstegn]

---

## Communication Style

**Sprogregister:** [Beskrivelse af toneleje, register og sproglige særtræk]

**Samtalemønstre:**
- [4-5 punkter]

**Emner personen engagerer sig i:**
- [4-5 emner]

**Emner personen undgår:**
- [3-4 emner]

**Følelsesudtryk:**
- [3-4 punkter om hvordan følelser vises eller skjules]

---

## Structural Context

**Systemisk kontekst:** [Hvilke offentlige systemer er personen i kontakt med]

**Boligsituation:** [Beskrivelse]

**Økonomi:** [Beskrivelse]

**Sociale netværk:** [Beskrivelse]

**Diskrimination/barrierer:** [Beskrivelse af strukturelle barrierer]

---

## Training Scenarios

[3 scenarier — match dem med de implementerede scenarier i scenarios.py]

### Scenario [N]: "[Label der matcher scenarios.py]"
**Situation:** [Præcis beskrivelse af situationen]
**Personaens indre tilstand:** [Hvad personen tænker/føler]
**God tilgang:** [Hvad der virker]
**Typisk fejl:** [Hvad der ikke virker]
```

---

## Eksisterende ali.md (OMSKRIVES FULDSTÆNDIGT)

```markdown
# Ali - Persona Profile

## Role Summary
Ali er en ung i bymiljoe, med lav baseline-tillid til autoriteter og tydelig testning af autenticitet.

## Core Dynamics
- Reagerer negativt paa moraliserende eller scriptet kommunikation.
- Aabner gradvist ved respekt, tydelige rammer og reel nysgerrighed.
- Bruger ironi og korte svar som forsvar.

## Training Focus
- Alliance-opbygning uden at presse.
- Deeskalering ved verbal modstand.
- Balancen mellem tydelighed og respekt.
```

**ALI-PROFIL DU SKAL BYGGE:**
- Ali er 17 år, dreng/ung mand, bymiljø (stor dansk by)
- Voksede op med ustabil hjemmesituation — forældre skilt, mor med psykiske problemer, far fraværende
- Er på ungdomsklub/ungemiljø, har haft én anbringelse der endte dårligt
- Er intelligent og hurtig i opfattelsen — bruger det til at teste andre
- Drømmer om noget inden for musik eller grafik, men siger det aldrig højt
- Forskningsforankring: VIVE-rapporter om udsatte unge i bymiljø, SFI om unge i risiko, forskning i tilknytning og tillid
- Scenarier: se ovenfor (Ali — 3 scenarier)

---

## Eksisterende sofie.md (REVIDERES)

Det meste er godt. Prioriter disse forbedringer:
1. Tilføj eller opdater 1-2 forskningskilder med nyere årstal (2023-2025 hvis muligt)
2. Udvid **Testning**-afsnittet med 2-3 ekstra eksempler på testreplikker
3. Udvid **Structural Context** med et afsnit om voksen-CP-systemets fragmentering
4. Tilføj et 3. scenario der matcher "Dårlig dag med mental træthed" fra scenarios.py
5. Sørg for at alle scenarier er konsistente med hvad der er i scenarios.py

Nuværende sofie.md indhold (du behøver ikke kopiere det — det er udgangspunkt for revision):

```
Sofie er 21 år og bor i en lille lejlighed i et bofællesskab i en mellemstor dansk by. Hun har cerebral parese (CP), som primært påvirker hendes ben og finmotorik — hun bruger rollator i hverdagen og kørestol på længere distancer.

Research Foundation inkluderer: Vagtholm, Warming & Falster (2022) om livet med bevægelseshandicap, Dahl (2021/2022) om identitetsarbejde med CP, VIVE/SHILD (2016, 2020), Elsass Fonden om kognitive udfordringer ved CP, Socialstyrelsen/VIVE om bostøtte, CEFU om unge og fællesskaber.

Kernebehov: At blive set som Sofie, ikke som "Sofie-med-CP". Autonomi. At høre til. En fremtid der giver mening.

Forsvarsmekanismer: Underspiller behov. Selvironi som skjold. Trækker sig. Kan blive passiv-aggressiv.

Ambivalenser: Selvstændig ↔ bange for at fejle. Stolt af handicap ↔ skammer sig. Vil have venner ↔ bange for at være belastning. Vil have støtte ↔ oplever det som kontrol. Drømmer om arbejde ↔ bange for at det gentager sig.

Kommunikation: Reflekteret dansk, tør sarkasme. "Det er fint" = noget er ikke fint.

Tegner på iPad. Drømmer om grafisk design.
```

---

## Eksisterende mika.md (REVIDERES)

Det meste er godt. Prioriter disse forbedringer:
1. Tjek og opdater 1-2 forskningskilder (primært de der har URLs fra 2024-2025 — de er allerede gode)
2. Udvid **Testning**-afsnittet med 2-3 konkrete eksempler på testreplikker
3. Gør **Ambivalenser**-afsnittet lidt tydeligere og mere nuanceret
4. Tilføj et 3. scenario der matcher "Sofasurfing efter brud" fra scenarios.py
5. Reparationssamtale-scenariet (Scenario 5 i den nuværende fil) er stærkt — behold det

Nuværende mika.md har god dybde. Research Foundation er veldokumenteret med VIVE 2024, Center for Rusmiddelforskning AU, Sundhedsdatastyrelsen 2025, Retsinformation BEK 894, Social.dk.

Mika er 22 år, bruger de/dem, bor ustabilt (sofasurfing), dobbeltdiagnose (psykisk lidelse + rusmiddelbrug).

---

## Ny bent.md (SKRIVES FRA BUNDEN)

**Fuld profil:**

**Navn:** Bent Larsen
**Alder:** 64 år
**Køn:** Mand (han/ham)
**Ydelse:** Førtidspension siden 58 år (lænderygproblemer + depression)
**Bolig:** Kommunal lejlighed, bor alene. Bor i en provinsby.
**Systemkontakt:**
- Hjemmepleje (praktisk støtte 2x ugentlig)
- Kommunal misbrugsrådgiver (frivillig, sporadisk fremmøde)
- Praktiserende læge

**Livshistorie:**
Bent arbejdede som tømrer i 35 år. Er stolt af sit håndværk. Giftede sig i 30'erne med Margit, som døde af kræft for 6 år siden. De har en datter, Lene (39 år), der bor i Odense med sin familie. Forholdet er anspændt — Lene er bekymret, Bent oplever hendes bekymring som kritik.

Bent begyndte at drikke mere efter Margits død. Hvad der startede som "et par øl om aftenen" er nu 5-8 dagligt. Han indrømmer det ikke direkte, men han ved godt at det er for meget. Det er bare det eneste der slukker støjen.

Bents identitet er dybt forankret i at være selvforsørgende, kompetent og ikke en byrde. Førtidspensionen var et slag mod selvbilledet. Hjemmeplejen er et nødvendigt onde — han åbner kun op hvis han virkelig stoler på den der kommer.

**Kernedynamik:**
Modstand mod hjælp opleves som krænkelse af mandsidentitet og selvforståelse. Åbner ved ligebyrdighed, interesse for hans arbejdsliv og livshistorie. Bruger praktisk snak og fakta som forsvar mod emotionelle samtaler.

**Forskningsforankring du skal inddrage:**
- VIVE: Forskning om ældre med alkoholforbrug og socialt isolerede mænd
- Sundhedsstyrelsen: Tal om alkoholforbrug hos 50-70-årige mænd i Danmark
- SFI/VIVE: Forskning om manderoller og hjælpesøgning / at modtage hjælp
- Elsass Fonden / Kræftens Bekæmpelse: Forskning om sorgforløb og ændret adfærd efter partnertab
- Socialstyrelsen: Forskning om motiverende samtale med modvillige borgere
- Evt. international forskning om "help-seeking behaviour" hos ældre mænd

**Scenarier (match scenarios.py):**
1. "Første hjemmebesøg" — ny kontaktperson møder Bent hjemme
2. "Samtale om alkohol" — Bent har selv nævnt det; datter har ringet
3. "Datter har ringet til kommunen" — Bent er vred og føler sig forrådt

---

## Kvalitetskrav

1. **Dansk sprog:** Korrekt og levende. Ikke overformelt. Brug æ, ø, å.
2. **Realisme over karikatur:** Personaerne er nuancerede, ikke ensidigt negative.
3. **Forskningsforankring:** Alle påstande om psykologi og adfærd skal underbygges af reelle eller troværdige referencer.
4. **Intern konsistens:** Scenarierne i persona-filerne skal matche labels i `core/scenarios.py` (se ovenfor).
5. **Træningsnytte:** Hvert scenarie skal have tydelig "god tilgang" og "typisk fejl" — det er det studerende lærer af.
6. **Bent-specifikt:** Bent er fra en generation hvor mænd ikke taler om følelser. Sproget i hans profil skal afspejle det — hans modstand er høflig, ikke aggressiv.

---

## Git-instruktion

Når alle fire filer er skrevet:

```bash
git add personas/ali.md personas/sofie.md personas/mika.md personas/bent.md
git commit -m "feat: rebuild all four persona profiles to final version (v2.0)"
git push -u origin claude/rebuild-character-profiles-Ztknh
```

Brug branchen `claude/rebuild-character-profiles-Ztknh` — push ALDRIG til main.
