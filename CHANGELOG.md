# Changelog

## [Unreleased]
- Planlagt: Persona-specifikke svaerhedsprofiler.
- Planlagt: Mikro-feedback hver 3.-4. tur.
- Added: Ali persona udvidet til fuld research-baseret profil i `personas/ali.md`.
- Added: Ny system-prompt version for Ali i `personas/ali_system_prompt.md`.
- Added: Ny system-prompt version for Sofie i `personas/sofie_system_prompt.md`.
- Added: Ny system-prompt version for Mika i `personas/mika_system_prompt.md`.
- Changed: App-routing bruger nu system-prompt filer for alle personaer.

## [v1.6] - 2026-02-13
### Added
- Twist-kort feature med triggerpunkter (tur 3 og 6).
- Blind mode hvor state skjules indtil afslutning.
- Speed rounds med valgfrit max-turns loft.
- Nyt modul: `core/twist_cards.py`.

### Changed
- Prompten inkluderer nu aktivt twist-kort i personaens kontekst.

## [v1.5] - 2026-02-13
### Added
- Scenario-vaelger per persona.
- Scenario Brief-panel med kort forhistorie og traeningsramme.
- Scenario-baseret initial state.
- Nyt modul: `core/scenarios.py`.

### Fixed
- Scenario Brief opdaterer nu ved scenarieskift i dropdown.

## [v1.0] - 2026-02-13
### Added
- HF/GitHub-ready Gradio prototype.
- Multi-persona setup (`Ali`, `Sofie`, `Mika`).
- State-panel og simpel state-opdatering.
- Samtalelogging til `data/logs`.
- Slutfeedback efter session.
