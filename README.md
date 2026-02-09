---
title: Ali - Træningssystem
emoji: 💬
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: "6.5.1"
python_version: "3.11"
app_file: app.py
pinned: false
---

# Ali - Træningssystem for pædagogstuderende

Et AI-baseret træningsværktøj hvor pædagogstuderende øver sig i at kommunikere med udsatte unge.

Ali er en simuleret 19-årig fra Tingbjerg/Nørrebro i København. Hun er skeptisk, defensiv og tester om du er ægte — præcis som mange unge i udsatte positioner gør i virkeligheden.

## Sådan bruger du det

1. Åbn appen i din browser
2. Skriv til Ali som om du møder hende for første gang
3. Få feedback på din kommunikationsstrategi via "Analysér"-knappen

## Opsætning

Sæt din Anthropic API-nøgle som miljøvariabel:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

Eller indtast den direkte i appen under "Indstillinger".

## Kør lokalt

```bash
pip install -r requirements.txt
python app.py
```
