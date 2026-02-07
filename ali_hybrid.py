"""
Ali - Hybrid AI Persona Training System
Support for både Opus 4.5 og Sonnet 4.5 med extended thinking toggle
"""

import anthropic
import os
from datetime import datetime
import json
from typing import Optional, Literal

class AliPersona:
    def __init__(
        self, 
        api_key: Optional[str] = None,
        model: Literal["opus", "sonnet"] = "sonnet",
        extended_thinking: bool = True
    ):
        """
        Initialiserer Ali persona med valgfri model og extended thinking
        
        Args:
            api_key: Anthropic API key (eller brug ANTHROPIC_API_KEY env var)
            model: "opus" for bedste kvalitet, "sonnet" for hurtigere/billigere
            extended_thinking: True = Ali tænker før hun svarer (anbefalet)
        """
        self.client = anthropic.Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
        self.extended_thinking = extended_thinking
        
        # Model mapping
        self.models = {
            "opus": "claude-opus-4-5-20251101",
            "sonnet": "claude-sonnet-4-5-20250929"
        }
        self.current_model = self.models[model]
        self.model_name = model
        
        self.conversation_history = []
        self.session_stats = {
            "model": model,
            "extended_thinking": extended_thinking,
            "total_tokens": 0,
            "total_thinking_tokens": 0,
            "interactions": [],
            "start_time": datetime.now().isoformat()
        }
        
        # Ali's persona
        self.persona_prompt = """Du er Ali, en 19-årig pige fra Tingbjerg/Nørrebro i København.

BAGGRUND:
- Vokset op i et belastet miljø med manglende tillid til voksne/autoriteter
- Har oplevet svigt fra personer der burde beskytte dig
- Har let ved at blive defensiv når folk prøver at "hjælpe"
- Masker sårbarhed med attitude og distance
- Taler ofte i korte sætninger, bruger slang fra området

KOMMUNIKATIONSSTIL:
- Starter ofte lukket af og skeptisk
- Tester folk for at se om de er ægte
- Bruger ironi og sarkasme som forsvar
- Kan åbne op hvis du mærker æghed og respekt (ikke nødvendigvis sympati)
- Hader når folk taler ned til dig eller antager ting

VIGTIGE NUANCER:
- Du er IKKE bare "sur" - du beskytter dig selv
- Du har drømme og håb, men tør ikke vise dem til hvem som helst
- Du kan skelne mellem folk der vil hjælpe fordi de SKAL og folk der rent faktisk ser dig
- Authenticity betyder alt - du gennemskuer bullshit med det samme

EKSEMPEL PÅ DIN TALE:
- "Hvad vil du?" (ikke "Hvordan kan jeg hjælpe dig?")
- "Jamen, okay..." (skeptisk, ikke overbevist)
- "Alle siger det jo..." (når nogen lover noget)
- Bruger "seriøst?", "altså", "hvad fanden"

VIGTIG INSTRUKTION:
Tag dig tid til at tænke over den studerendes tilgang. Reagér autentisk baseret på:
- Om de lyder scriptede eller ægte
- Om de respekterer dine grænser
- Om de lytter eller bare kører deres program
- Om de ser dig som person eller "case"
"""

    def chat(self, student_message: str, thinking_budget: int = 10000) -> dict:
        """
        Sender besked til Ali
        
        Args:
            student_message: Besked fra pædagogstuderende
            thinking_budget: Antal tokens til extended thinking (kun hvis enabled)
            
        Returns:
            dict med Ali's svar, tanker (hvis enabled), og metadata
        """
        # Tilføj til historik
        self.conversation_history.append({
            "role": "user",
            "content": student_message
        })
        
        # Opret messages array
        messages = [
            {
                "role": "user",
                "content": self.persona_prompt + "\n\nStuderende siger: " + student_message
            }
        ] + self.conversation_history[1:]
        
        try:
            # Byg API call baseret på extended thinking setting
            api_params = {
                "model": self.current_model,
                "max_tokens": 16000,
                "messages": messages
            }
            
            # Tilføj thinking kun hvis enabled
            if self.extended_thinking:
                api_params["thinking"] = {
                    "type": "enabled",
                    "budget_tokens": thinking_budget
                }
            
            response = self.client.messages.create(**api_params)
            
            # Udtræk thinking og response
            thinking_content = ""
            response_text = ""
            
            for block in response.content:
                if block.type == "thinking":
                    thinking_content = block.thinking
                elif block.type == "text":
                    response_text = block.text
            
            # Gem Ali's svar i historik
            self.conversation_history.append({
                "role": "assistant",
                "content": response_text
            })
            
            # Opdater stats
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            
            self.session_stats["total_tokens"] += input_tokens + output_tokens
            
            # Log interaktion
            interaction = {
                "timestamp": datetime.now().isoformat(),
                "student_message": student_message,
                "ali_response": response_text,
                "tokens": {
                    "input": input_tokens,
                    "output": output_tokens,
                    "total": input_tokens + output_tokens
                }
            }
            
            if self.extended_thinking:
                interaction["ali_thinking"] = thinking_content
                # Thinking tokens er inkluderet i input_tokens
            
            self.session_stats["interactions"].append(interaction)
            
            return {
                "response": response_text,
                "thinking": thinking_content if self.extended_thinking else None,
                "metadata": {
                    "model": self.model_name,
                    "extended_thinking": self.extended_thinking,
                    "tokens": response.usage.model_dump(),
                    "interaction_number": len(self.session_stats["interactions"])
                }
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "response": "Fejl i kommunikation med Ali",
                "thinking": None
            }
    
    def get_session_stats(self) -> dict:
        """Returnerer statistik om sessionen"""
        duration = (datetime.now() - datetime.fromisoformat(self.session_stats["start_time"])).total_seconds()
        
        return {
            **self.session_stats,
            "duration_seconds": duration,
            "avg_tokens_per_interaction": (
                self.session_stats["total_tokens"] / len(self.session_stats["interactions"])
                if self.session_stats["interactions"] else 0
            )
        }
    
    def save_session(self, filename: Optional[str] = None) -> str:
        """Gemmer session data til fil"""
        if filename is None:
            model_prefix = self.model_name
            thinking_suffix = "_thinking" if self.extended_thinking else ""
            filename = f"ali_session_{model_prefix}{thinking_suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        stats = self.get_session_stats()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        return filename
    
    def analyze_student_approach(self) -> str:
        """Analyserer den studerendes kommunikationsstrategi"""
        if len(self.session_stats["interactions"]) == 0:
            return "Ingen interaktioner endnu"
        
        analysis_prompt = f"""
Baseret på følgende interaktioner mellem en pædagogstuderende og Ali, 
analyser den studerendes kommunikationsstrategi:

{json.dumps(self.session_stats["interactions"], ensure_ascii=False, indent=2)}

Vurder:
1. Autenticitet - lyder de scriptede eller ægte?
2. Respekt for grænser - presser de for hårdt?
3. Lytning - bygger de videre på Ali's svar?
4. Tilgang - ser de Ali som person eller "case"?

Giv konstruktiv feedback på hvad der fungerede og hvad der kunne forbedres.
"""
        
        try:
            response = self.client.messages.create(
                model=self.current_model,
                max_tokens=4000,
                messages=[{
                    "role": "user",
                    "content": analysis_prompt
                }]
            )
            
            return response.content[0].text
            
        except Exception as e:
            return f"Fejl i analyse: {str(e)}"
    
    def estimate_cost(self) -> dict:
        """Estimerer omkostninger for sessionen i DKK"""
        # Priser per 1M tokens (cirka, Anthropic pricing)
        pricing = {
            "opus": {
                "input": 15.0,  # USD per 1M input tokens
                "output": 75.0   # USD per 1M output tokens
            },
            "sonnet": {
                "input": 3.0,
                "output": 15.0
            }
        }
        
        usd_to_dkk = 7.0  # Cirka vekselkurs
        
        total_input = sum(i["tokens"]["input"] for i in self.session_stats["interactions"])
        total_output = sum(i["tokens"]["output"] for i in self.session_stats["interactions"])
        
        model_pricing = pricing[self.model_name]
        
        cost_input_usd = (total_input / 1_000_000) * model_pricing["input"]
        cost_output_usd = (total_output / 1_000_000) * model_pricing["output"]
        total_cost_usd = cost_input_usd + cost_output_usd
        total_cost_dkk = total_cost_usd * usd_to_dkk
        
        return {
            "total_tokens": total_input + total_output,
            "input_tokens": total_input,
            "output_tokens": total_output,
            "cost_usd": round(total_cost_usd, 4),
            "cost_dkk": round(total_cost_dkk, 2),
            "model": self.model_name,
            "extended_thinking": self.extended_thinking
        }


def interactive_demo():
    """
    Interaktiv demo med model- og thinking-valg
    """
    print("=== ALI TRÆNINGSSYSTEM - HYBRID VERSION ===\n")
    
    # Check API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        api_key = input("Indtast din Anthropic API key: ")
        os.environ["ANTHROPIC_API_KEY"] = api_key
    
    # Vælg model
    print("Vælg AI model:")
    print("1. Sonnet 4.5 (hurtig, billig, god kvalitet)")
    print("2. Opus 4.5 (langsom, dyr, bedste kvalitet)")
    model_choice = input("Valg (1/2): ").strip()
    model = "sonnet" if model_choice == "1" else "opus"
    
    # Vælg extended thinking
    print("\nVælg thinking mode:")
    print("1. Extended thinking ON (Ali tænker før hun svarer - anbefalet)")
    print("2. Extended thinking OFF (hurtigere, billigere)")
    thinking_choice = input("Valg (1/2): ").strip()
    extended_thinking = thinking_choice == "1"
    
    # Opret Ali
    ali = AliPersona(model=model, extended_thinking=extended_thinking)
    
    print(f"\n✓ Ali klar med {model.upper()} + thinking={'ON' if extended_thinking else 'OFF'}")
    print("\n[SCENARIO: Du møder Ali for første gang på et ungdomscenter]")
    print("Ali står ved vinduet og kigger ud. Hun har ikke set dig endnu.")
    print("\nSkriv 'quit' for at afslutte, 'stats' for statistik.\n")
    
    while True:
        student_input = input("Du siger: ").strip()
        
        if student_input.lower() == 'quit':
            break
        
        if student_input.lower() == 'stats':
            cost = ali.estimate_cost()
            print(f"\n📊 Session statistik:")
            print(f"   Model: {cost['model'].upper()}")
            print(f"   Extended thinking: {'ON' if cost['extended_thinking'] else 'OFF'}")
            print(f"   Tokens brugt: {cost['total_tokens']:,}")
            print(f"   Estimeret omkostning: {cost['cost_dkk']} DKK ({cost['cost_usd']} USD)")
            print()
            continue
        
        if not student_input:
            continue
        
        # Få Ali's svar
        if extended_thinking:
            print("\n[Ali tænker...]")
        
        result = ali.chat(student_input)
        
        if "error" in result:
            print(f"FEJL: {result['error']}")
            continue
        
        # Vis thinking hvis enabled
        if result["thinking"]:
            print(f"\n--- Ali's tankeproces: ---")
            thinking_preview = result["thinking"][:300]
            print(thinking_preview + ("..." if len(result["thinking"]) > 300 else ""))
            print("--- Slut ---\n")
        
        # Vis Ali's svar
        print(f"\nAli: {result['response']}\n")
    
    # Gem og vis stats
    filename = ali.save_session()
    print(f"\n💾 Session gemt til: {filename}")
    
    cost = ali.estimate_cost()
    print(f"\n💰 Final omkostning:")
    print(f"   {cost['cost_dkk']} DKK ({cost['cost_usd']} USD)")
    print(f"   {cost['total_tokens']:,} tokens total")
    
    # Analyser
    print("\n=== FEEDBACK PÅ DIN KOMMUNIKATION ===")
    analysis = ali.analyze_student_approach()
    print(analysis)
    
    return ali


if __name__ == "__main__":
    ali_session = interactive_demo()
