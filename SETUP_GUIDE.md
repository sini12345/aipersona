# Ali Trainer - Setup Guide

## 🚀 Hurtig Start med Færdige Executables

### For Studerende (Nemmest)

1. **Download den rigtige fil:**
   - Windows: `Ali-Trainer.exe`
   - Mac: `Ali-Trainer.app`

2. **Første gang (kun Windows):**
   - Windows Defender kan advare - klik "Mere info" → "Kør alligevel"
   - Dette er normalt for programmer der ikke er "signerede"

3. **Kør programmet:**
   - Dobbeltklik på filen
   - Indtast Anthropic API key når programmet starter
   - Vælg model og thinking mode
   - Begynd at chatte med Ali!

### API Key

Du skal bruge en Anthropic API key. Få én her: https://console.anthropic.com/

**To muligheder:**

**A) Studerende bruger egen key (mest sikkert):**
- Hver studerende opretter gratis Anthropic konto
- Får $5 gratis credit til at starte med
- Indtaster deres egen key når programmet starter

**B) Delt key (nemmere, men mindre sikkert):**
- Du opretter én API key
- Giver den til alle studerende
- ⚠️ Du betaler for alt forbrug
- ⚠️ Nogen kan misbruge key

---

## 🛠 For Udviklere

### Lokal Udvikling (Python)

```bash
# 1. Klon repository
git clone https://github.com/DIT-BRUGERNAVN/ali-trainer.git
cd ali-trainer

# 2. Installer dependencies
pip install -r requirements.txt

# 3. Sæt API key
export ANTHROPIC_API_KEY="din-key-her"

# 4. Kør
python ali_hybrid.py
```

### Byg Executable Lokalt

**Windows:**
```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name Ali-Trainer ali_hybrid.py
# → Finder Ali-Trainer.exe i dist/ mappen
```

**Mac:**
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name Ali-Trainer ali_hybrid.py
# → Finder Ali-Trainer.app i dist/ mappen
```

### Automatisk Byggning via GitHub Actions

Når du pusher til `main` branch, bygger GitHub automatisk både .exe og .app:

1. Gå til repository på GitHub
2. Klik "Actions" tab
3. Se build status
4. Download færdige filer under "Artifacts"

Eller vent på automatisk release under "Releases"

---

## 📁 Fil Struktur

```
ali-trainer/
├── ali_hybrid.py              # Hoved-program (hybrid version)
├── test_comparison.py         # Sammenligning af modeller
├── requirements.txt           # Python dependencies
├── README.md                  # Dokumentation
├── SETUP_GUIDE.md            # Denne fil
└── .github/
    └── workflows/
        └── build.yml          # GitHub Actions config
```

---

## 🎓 For Undervisere

### Session Data

Ali gemmer automatisk session data når studerende afslutter:

```
ali_session_sonnet_thinking_20250207_143022.json
```

Filen indeholder:
- Alle beskeder frem og tilbage
- Ali's tankeproces (hvis thinking er enabled)
- Tokens brugt
- Timestamps

Du kan bruge dette til:
- Evaluering af studerendes kommunikation
- Feedback
- Research
- Forbedring af Ali persona

### Omkostninger

**Typisk 15-min træningssession:**

| Konfiguration | Estimeret pris |
|--------------|----------------|
| Sonnet + Thinking | 2-3 DKK |
| Sonnet Basic | 0.5-1 DKK |
| Opus + Thinking | 15-20 DKK |

**Anbefaling:** Start med Sonnet + Thinking

### Tilpasning af Ali

Rediger `persona_prompt` i `ali_hybrid.py` for at:
- Ændre Ali's baggrund
- Tilføje specifikke triggere
- Justere kommunikationsstil
- Skabe andre personas

---

## 🔧 Troubleshooting

### "pyinstaller: command not found"
```bash
pip install pyinstaller
# eller
pip3 install pyinstaller
```

### Windows Defender blokerer .exe
Dette er normalt. To løsninger:
1. Klik "Mere info" → "Kør alligevel"
2. Tilføj undtagelse i Windows Defender

### Mac "kan ikke åbne app fra uidentificeret udvikler"
```bash
# Højreklik på Ali-Trainer.app → Vælg "Åbn"
# Eller i terminal:
xattr -cr Ali-Trainer.app
```

### API key virker ikke
- Check at key starter med `sk-ant-`
- Verificer på https://console.anthropic.com/
- Tjek om du har credit tilbage

### Program crasher
- Tjek internet forbindelse
- Verificer API key
- Se error log (gemmes samme sted som programmet)

---

## 📞 Support

Spørgsmål? Kontakt Simon eller opret et issue på GitHub.

---

## 🔐 Sikkerhed

**VIGTIG:** Gem aldrig API keys i koden!

✅ Brug environment variables
✅ Lad brugere indtaste deres egen key
❌ Hard-code ikke keys i source code
❌ Commit ikke keys til GitHub
