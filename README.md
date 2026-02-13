---
title: Aipersona
emoji: "🤖"
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: "5.48.0"
app_file: app.py
pinned: false
---

# Persona Trainer v1 (Gradio + Hugging Face + GitHub)

HF-ready prototype for socialpaedagogisk samtaletraening med flere personaer (`Ali`, `Sofie`, `Mika`).

## Features i v1
- Persona-vaelger
- Laeringsmaal-mode (`Alliance`, `Deeskalering`, `Graensesaetning`)
- Trust/state-panel (`trust`, `stress`, `skam`, `haab`, `kontroltab`)
- Samtalelogging til `data/logs/*.json`
- Kort slutfeedback efter session

## Projektstruktur
```text
app.py
core/
  prompt_builder.py
  state_engine.py
  feedback_engine.py
  logger.py
personas/
  ali.md
  sofie.md
  mika.md
data/logs/.gitkeep
requirements.txt
.env.example
```

## Lokal koersel
```bash
pip install -r requirements.txt
set ANTHROPIC_API_KEY=sk-ant-...   # Windows PowerShell: $env:ANTHROPIC_API_KEY="sk-ant-..."
python app.py
```

## Hugging Face Space setup (GitHub sync)
1. Opret repo paa GitHub og push disse filer.
2. Opret/brug en HF Space med `SDK: Gradio`.
3. Link Space til GitHub repo+branch i Space settings.
4. Tilfoej secret i HF Space:
   - `ANTHROPIC_API_KEY` = din key
5. Push til branch -> HF redeployer automatisk.

## Deployment note
- `app.py` er entrypoint for HF Gradio Space.
- Hvis du vil, kan du senere splitte prompt/state i mere avancerede engines uden at aendre UI-kontrakten.

## Naeste naturlige v1.5
- Event-kort midt i samtale
- Svaerhedsprofiler per persona
- Mikro-feedback hver 3-4 tur
