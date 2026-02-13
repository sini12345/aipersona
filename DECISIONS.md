# Decisions Log

## 2026-02-13 - Keep Gradio for now
- Decision: Fortsaet i Gradio frem for React/Next i tidlig fase.
- Why: Hurtigste iteration i HF Spaces, lav kompleksitet, eksisterende Ali-setup.

## 2026-02-13 - Build multi-persona v1
- Decision: Udvid fra Ali-only til `Ali`, `Sofie`, `Mika`.
- Why: Bedre didaktisk bredde og sammenlignelig traening pa tværs af profiler.

## 2026-02-13 - Add state model
- Decision: Track `trust`, `stress`, `skam`, `haab`, `kontroltab`.
- Why: Giver mere nuanceret traeningssignal end kun trust-meter.

## 2026-02-13 - Add scenario-first flow (v1.5)
- Decision: Scenario-vaelger + Scenario Brief foer sessionstart.
- Why: Giver bedre kontekst, mere realistiske oevemiljoer, lettere evaluering.

## 2026-02-13 - Scenario-based initialization
- Decision: Hvert scenario saetter startvaerdier for state.
- Why: Differentierer samtaleforlob og svaerhedsoplevelse mere autentisk.

## 2026-02-13 - Keep hidden layer internal
- Decision: Scenarioets "skjulte lag" sendes i systemprompt men skal ikke udstilles af personaen direkte.
- Why: Sikrer realistisk adfaerd uden metakommunikation.

## 2026-02-13 - Bugfix for scenario brief update
- Decision: Opdater brief ved `scenario.change`, ikke kun `persona.change`.
- Why: UI viste tidligere stale tekst ved scenarieskift.
