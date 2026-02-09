"""
PersonaEngine - Generisk AI Persona Træningsplatform
Understøtter multiple personaer og teori-baseret feedback
til social- og specialpædagogisk træning
"""

import anthropic
import os
import json
from datetime import datetime
from typing import Optional, Literal
from pathlib import Path


class PersonaEngine:
    """Generisk persona-engine med persona- og teori-valg."""

    PERSONAS_DIR = Path(__file__).parent / "personas"
    THEORIES_DIR = Path(__file__).parent / "theories"

    MODELS = {
        "opus": "claude-opus-4-5-20251101",
        "sonnet": "claude-sonnet-4-5-20250929",
    }

    def __init__(
        self,
        persona_id: str,
        theory_id: Optional[str] = None,
        custom_theory_text: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Literal["opus", "sonnet"] = "sonnet",
        extended_thinking: bool = True,
    ):
        self.client = anthropic.Anthropic(
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY")
        )
        self.extended_thinking = extended_thinking
        self.current_model = self.MODELS[model]
        self.model_name = model

        # Load persona
        self.persona = self._load_persona(persona_id)
        self.persona_id = persona_id

        # Load theory (optional)
        self.theory = None
        self.theory_id = theory_id
        if theory_id:
            self.theory = self._load_theory(theory_id)

        # Custom uploaded text (optional, supplements or replaces theory)
        self.custom_theory_text = custom_theory_text

        self.conversation_history = []
        self.session_stats = {
            "persona": persona_id,
            "persona_name": self.persona["name"],
            "theory": theory_id,
            "theory_name": self.theory["name"] if self.theory else None,
            "has_custom_text": custom_theory_text is not None,
            "model": model,
            "extended_thinking": extended_thinking,
            "total_tokens": 0,
            "interactions": [],
            "start_time": datetime.now().isoformat(),
        }

    def _load_persona(self, persona_id: str) -> dict:
        """Indlæser persona-definition fra JSON-fil."""
        filepath = self.PERSONAS_DIR / f"{persona_id}.json"
        if not filepath.exists():
            available = self.list_personas()
            ids = [p["id"] for p in available]
            raise FileNotFoundError(
                f"Persona '{persona_id}' ikke fundet. Tilgængelige: {ids}"
            )
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_theory(self, theory_id: str) -> dict:
        """Indlæser teori-definition fra JSON-fil."""
        filepath = self.THEORIES_DIR / f"{theory_id}.json"
        if not filepath.exists():
            available = self.list_theories()
            ids = [t["id"] for t in available]
            raise FileNotFoundError(
                f"Teori '{theory_id}' ikke fundet. Tilgængelige: {ids}"
            )
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    @classmethod
    def list_personas(cls) -> list[dict]:
        """Returnerer liste af tilgængelige personaer med metadata."""
        personas = []
        for filepath in sorted(cls.PERSONAS_DIR.glob("*.json")):
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                personas.append({
                    "id": data["id"],
                    "name": data["name"],
                    "age": data["age"],
                    "context": data["context"],
                    "background_short": data["background_short"],
                    "themes": data["themes"],
                })
        return personas

    @classmethod
    def list_theories(cls) -> list[dict]:
        """Returnerer liste af tilgængelige teorier med metadata."""
        theories = []
        for filepath in sorted(cls.THEORIES_DIR.glob("*.json")):
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                theories.append({
                    "id": data["id"],
                    "name": data["name"],
                    "authors": data["authors"],
                    "summary": data["summary"],
                })
        return theories

    def get_scenario(self) -> dict:
        """Returnerer scenariet for denne persona."""
        return self.persona["scenario"]

    def get_theory_summary(self) -> Optional[str]:
        """Returnerer en læsbar opsummering af valgt teori."""
        if not self.theory:
            return None

        concepts = "\n".join(
            f"  - {c['name']}: {c['definition']}"
            for c in self.theory["key_concepts"]
        )
        return (
            f"{self.theory['name']} ({self.theory['authors']})\n\n"
            f"{self.theory['summary']}\n\n"
            f"Kernebegreber:\n{concepts}"
        )

    def chat(self, student_message: str, thinking_budget: int = 10000) -> dict:
        """
        Sender besked til personaen.

        Args:
            student_message: Besked fra studerende
            thinking_budget: Tokens til extended thinking

        Returns:
            dict med svar, tanker, og metadata
        """
        self.conversation_history.append({
            "role": "user",
            "content": student_message,
        })

        # Build messages - persona prompt som system context i første besked
        if len(self.conversation_history) == 1:
            messages = [{
                "role": "user",
                "content": (
                    self.persona["system_prompt"]
                    + "\n\nDen studerende siger: "
                    + student_message
                ),
            }]
        else:
            messages = [
                {
                    "role": "user",
                    "content": (
                        self.persona["system_prompt"]
                        + "\n\nDen studerende siger: "
                        + self.conversation_history[0]["content"]
                    ),
                }
            ] + self.conversation_history[1:]

        try:
            api_params = {
                "model": self.current_model,
                "max_tokens": 16000,
                "messages": messages,
            }

            if self.extended_thinking:
                api_params["thinking"] = {
                    "type": "enabled",
                    "budget_tokens": thinking_budget,
                }

            response = self.client.messages.create(**api_params)

            thinking_content = ""
            response_text = ""

            for block in response.content:
                if block.type == "thinking":
                    thinking_content = block.thinking
                elif block.type == "text":
                    response_text = block.text

            self.conversation_history.append({
                "role": "assistant",
                "content": response_text,
            })

            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            self.session_stats["total_tokens"] += input_tokens + output_tokens

            interaction = {
                "timestamp": datetime.now().isoformat(),
                "student_message": student_message,
                "persona_response": response_text,
                "tokens": {
                    "input": input_tokens,
                    "output": output_tokens,
                    "total": input_tokens + output_tokens,
                },
            }

            if self.extended_thinking:
                interaction["persona_thinking"] = thinking_content

            self.session_stats["interactions"].append(interaction)

            return {
                "response": response_text,
                "thinking": thinking_content if self.extended_thinking else None,
                "metadata": {
                    "model": self.model_name,
                    "persona": self.persona_id,
                    "theory": self.theory_id,
                    "extended_thinking": self.extended_thinking,
                    "tokens": response.usage.model_dump(),
                    "interaction_number": len(self.session_stats["interactions"]),
                },
            }

        except Exception as e:
            return {
                "error": str(e),
                "response": f"Fejl i kommunikation med {self.persona['name']}",
                "thinking": None,
            }

    def _build_analysis_prompt(self) -> str:
        """Bygger analyse-prompt baseret på persona, teori og evt. uploadet tekst."""
        conversation_json = json.dumps(
            self.session_stats["interactions"], ensure_ascii=False, indent=2
        )

        # Base: persona-kriterier
        persona_criteria = "\n".join(
            f"- {c['name']}: {c['description']}"
            for c in self.persona["evaluation_criteria"]
        )

        # Teori-sektion
        theory_section = ""
        if self.theory:
            concepts = "\n".join(
                f"  - {c['name']}: {c['definition']}"
                for c in self.theory["key_concepts"]
            )
            eval_focus = "\n".join(
                f"  - {f}" for f in self.theory["evaluation_focus"]
            )
            theory_section = f"""

TEORETISK RAMME: {self.theory['name']} ({self.theory['authors']})
{self.theory['summary']}

Kernebegreber:
{concepts}

Evalueringsfokus ud fra teorien:
{eval_focus}
"""

        # Uploadet tekst
        custom_section = ""
        if self.custom_theory_text:
            custom_section = f"""

UPLOADET PENSUM-TEKST (brug som yderligere evalueringsgrundlag):
---
{self.custom_theory_text}
---
"""

        # Feedback-struktur afhænger af om teori er valgt
        if self.theory:
            feedback_structure = f"""Giv:
1. En kort overordnet vurdering (2-3 sætninger)

2. PERSONA-FEEDBACK - Evaluer ud fra disse kriterier:
{persona_criteria}
   For hvert kriterie: en score (1-5) og konkret feedback med eksempler fra samtalen

3. TEORI-FEEDBACK ({self.theory['name']}) - Evaluer den studerendes brug af teoriens begreber:
   - Hvilke begreber fra {self.theory['name']} var tydelige i den studerendes tilgang?
   - Hvilke begreber manglede eller blev misforstået?
   - Giv en samlet teori-score (1-5)
   - Konkrete eksempler fra samtalen koblet til teoriens begreber

4. Et konkret forbedringsforslag med reference til teorien"""
        else:
            feedback_structure = f"""Giv:
1. En kort overordnet vurdering (2-3 sætninger)
2. For hvert kriterie: en score (1-5) og konkret feedback med eksempler fra samtalen:
{persona_criteria}
3. Et konkret forbedringsforslag til næste gang"""

        return f"""Du er en erfaren underviser i social- og specialpædagogik.

En studerende har netop haft en træningssamtale med en simuleret borger/bruger:
- Persona: {self.persona['name']}, {self.persona['age']} år
- Kontekst: {self.persona['context']}
- Baggrund: {self.persona['background_short']}
{theory_section}{custom_section}
Samtalen:
{conversation_json}

{feedback_structure}

Vær konstruktiv, specifik og pædagogisk i din feedback. Brug eksempler fra samtalen.
Skriv på dansk."""

    def analyze_student(self) -> str:
        """Analyserer den studerendes kommunikation baseret på persona + teori."""
        if not self.session_stats["interactions"]:
            return "Ingen interaktioner endnu."

        try:
            response = self.client.messages.create(
                model=self.current_model,
                max_tokens=6000,
                messages=[{
                    "role": "user",
                    "content": self._build_analysis_prompt(),
                }],
            )
            return response.content[0].text
        except Exception as e:
            return f"Fejl i analyse: {e}"

    def estimate_cost(self) -> dict:
        """Estimerer omkostninger for sessionen."""
        pricing = {
            "opus": {"input": 15.0, "output": 75.0},
            "sonnet": {"input": 3.0, "output": 15.0},
        }
        usd_to_dkk = 7.0

        total_input = sum(
            i["tokens"]["input"] for i in self.session_stats["interactions"]
        )
        total_output = sum(
            i["tokens"]["output"] for i in self.session_stats["interactions"]
        )

        p = pricing[self.model_name]
        cost_usd = (total_input / 1_000_000) * p["input"] + (
            total_output / 1_000_000
        ) * p["output"]

        return {
            "total_tokens": total_input + total_output,
            "input_tokens": total_input,
            "output_tokens": total_output,
            "cost_usd": round(cost_usd, 4),
            "cost_dkk": round(cost_usd * usd_to_dkk, 2),
            "model": self.model_name,
        }

    def save_session(self, filename: Optional[str] = None) -> str:
        """Gemmer session til JSON-fil."""
        if filename is None:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            theory_part = f"_{self.theory_id}" if self.theory_id else ""
            filename = f"session_{self.persona_id}{theory_part}_{self.model_name}_{ts}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(
                {**self.session_stats, **self.estimate_cost()},
                f,
                ensure_ascii=False,
                indent=2,
            )
        return filename
