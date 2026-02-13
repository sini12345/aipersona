# Persona Index

## Active Persona Files
- `personas/ali.md`
  - Status: Aktiv i app.
  - Rolle: Hoeflig/lukket testning af autenticitet, bymiljoe-kontekst.

- `personas/sofie.md`
  - Kilde: Kopi af `C:/Users/SINI/Downloads/sofie_persona_profile.md`.
  - Status: Aktiv i app.
  - Rolle: Ung med CP, ambivalens mellem selvbestemmelse og stoette.

- `personas/mika.md`
  - Kilde: Kopi af `C:/Users/SINI/Downloads/persona_variation_dobbeltbelastning.md`.
  - Status: Aktiv i app.
  - Rolle: 18-24, ikke-binaer, dobbeltbelastning, konflikt/affekt-pres.

## Scenario Coverage (v1.5)
- Ali: 3 scenarier i `core/scenarios.py`
- Sofie: 3 scenarier i `core/scenarios.py`
- Mika: 3 scenarier i `core/scenarios.py`

## Maintenance Rules
1. Naar en persona opdateres i Downloads, sync manuel kopi til `personas/*.md`.
2. Hold scenario labels stabile for at bevare reproducerbar testning.
3. Undgaa stereotype formuleringer; hold strukturelt/relationsbaseret perspektiv.
4. Ved stoerre personaaendringer: opdater `PROJECT_CONTEXT.md` og `CHANGELOG.md`.
