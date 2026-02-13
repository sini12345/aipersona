# Project Context

## Purpose
Bygge en AI-baseret traeningsprototype til socialpaedagogiske 1:1 samtaler med empirisk forankrede personaer.

## Current Product
- Platform: Gradio i Hugging Face Space, syncet via GitHub (`sini12345/aipersona`).
- App entrypoint: `app.py`.
- Model API: Anthropic (`ANTHROPIC_API_KEY` i HF Secrets).
- Personaer: `Ali`, `Sofie`, `Mika`.

## Pedagogical Design
- Studerende vaelger persona, scenario, laeringsmaal og svaerhedsgrad.
- Samtalen koeres som realistisk rollespil med relationel dynamik.
- Indre state spores: `trust`, `stress`, `skam`, `haab`, `kontroltab`.
- Slutfeedback giver kort refleksion over styrker og forbedringspunkter.

## What Is Implemented (v1.5)
- Multi-persona chat.
- Scenario Brief-panel foer start:
  - kontekst
  - kort forhistorie
  - dagens maal
  - risiko-triggere
  - skjult lag
- Scenario-baseret state-init.
- Samtalelogging til `data/logs/*.json`.
- Bugfix: Scenario Brief opdaterer nu ved scenarieskift i dropdown.

## Core Files
- `app.py` - UI, sessionflow, API-kald.
- `core/scenarios.py` - scenariedata + brief-formattering.
- `core/prompt_builder.py` - systemprompt med scenario/state.
- `core/state_engine.py` - state-model og opdateringslogik.
- `core/feedback_engine.py` - slutfeedback.
- `core/logger.py` - sessionslog.

## Deployment
- Branch: `main`
- Remote: `origin -> https://github.com/sini12345/aipersona.git`
- HF Space forventes at redeploye automatisk ved push til `main`.

## Next Priorities
1. Event-kort midt i samtalen.
2. Persona-specifikke svaerhedsprofiler.
3. Mikro-feedback hver 3.-4. tur.
4. Underviser-view/rapportering i senere fase.
