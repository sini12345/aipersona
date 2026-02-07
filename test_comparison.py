"""
Sammenligning af forskellige Ali konfigurationer
Viser forskelle mellem Opus/Sonnet og thinking on/off
"""

from ali_hybrid import AliPersona
import os

def compare_configurations():
    """
    Tester samme samtale med forskellige konfigurationer
    """
    
    # Test besked fra studerende
    test_messages = [
        "Hej Ali, jeg hedder Simon og jeg er her for at hjælpe dig. Vil du fortælle mig hvordan du har det?",
        "Hey. Må jeg sidde her?"
    ]
    
    configs = [
        {"model": "sonnet", "extended_thinking": True, "name": "Sonnet + Thinking"},
        {"model": "sonnet", "extended_thinking": False, "name": "Sonnet (kun svar)"},
        {"model": "opus", "extended_thinking": True, "name": "Opus + Thinking"},
    ]
    
    print("=== SAMMENLIGNING AF ALI KONFIGURATIONER ===\n")
    print("Tester samme besked med forskellige settings...\n")
    
    for msg_idx, message in enumerate(test_messages, 1):
        print(f"\n{'='*70}")
        print(f"TEST BESKED {msg_idx}: \"{message}\"")
        print(f"{'='*70}\n")
        
        for config in configs:
            print(f"\n--- {config['name']} ---")
            
            ali = AliPersona(
                model=config['model'],
                extended_thinking=config['extended_thinking']
            )
            
            result = ali.chat(message)
            
            if "error" in result:
                print(f"FEJL: {result['error']}")
                continue
            
            # Vis thinking hvis tilgængeligt
            if result['thinking']:
                print(f"\nTankeproces (første 250 chars):")
                print(result['thinking'][:250] + "...")
            
            # Vis svar
            print(f"\nAli's svar:")
            print(f'"{result["response"]}"')
            
            # Vis tokens
            tokens = result['metadata']['tokens']
            print(f"\nTokens: {tokens['input_tokens']} input + {tokens['output_tokens']} output = {tokens['input_tokens'] + tokens['output_tokens']} total")
            
            # Estimeret kostnad
            cost = ali.estimate_cost()
            print(f"Omkostning: ~{cost['cost_dkk']} DKK")
            
            print()
    
    print("\n" + "="*70)
    print("KONKLUSION:")
    print("="*70)
    print("""
Sonnet + Thinking:
  ✓ Bedste balance mellem kvalitet og pris
  ✓ God til at skelne autentisk vs scriptet kommunikation
  ✓ Anbefalet til studerende-træning

Sonnet (uden thinking):
  ✓ Billigst og hurtigst
  ✓ Stadig god kvalitet
  ⚠ Mindre nuanceret - mere forudsigelige svar
  → Brug hvis budget/hastighed er kritisk

Opus + Thinking:
  ✓ Absolut bedste kvalitet
  ✓ Mest realistisk og subtil persona
  ✗ 10x dyrere end Sonnet
  → Brug til demonstrationer og research
    """)


def cost_comparison():
    """
    Viser prissammenligning for en typisk træningssession
    """
    print("\n=== PRISSAMMENLIGNING - TYPISK 15-MIN SESSION ===\n")
    
    # Antag 10 udvekslinger i en session
    scenarios = {
        "Sonnet + Thinking": {"model": "sonnet", "thinking": True, "exchanges": 10},
        "Sonnet Basic": {"model": "sonnet", "thinking": False, "exchanges": 10},
        "Opus + Thinking": {"model": "opus", "thinking": True, "exchanges": 10},
    }
    
    # Gennemsnitlige tokens (rough estimates)
    avg_tokens = {
        ("sonnet", True): {"input": 1000, "output": 200},  # Thinking inkluderet i input
        ("sonnet", False): {"input": 600, "output": 200},
        ("opus", True): {"input": 1000, "output": 200},
    }
    
    # Priser per 1M tokens
    pricing = {
        "opus": {"input": 15.0, "output": 75.0},
        "sonnet": {"input": 3.0, "output": 15.0}
    }
    
    usd_to_dkk = 7.0
    
    print(f"{'Konfiguration':<25} {'Tokens/session':<18} {'Pris (DKK)':<15} {'Pris (USD)'}")
    print("-" * 75)
    
    for name, scenario in scenarios.items():
        model = scenario["model"]
        thinking = scenario["thinking"]
        exchanges = scenario["exchanges"]
        
        tokens = avg_tokens[(model, thinking)]
        total_tokens = (tokens["input"] + tokens["output"]) * exchanges
        
        price = pricing[model]
        input_cost = (tokens["input"] * exchanges / 1_000_000) * price["input"]
        output_cost = (tokens["output"] * exchanges / 1_000_000) * price["output"]
        total_cost_usd = input_cost + output_cost
        total_cost_dkk = total_cost_usd * usd_to_dkk
        
        print(f"{name:<25} {total_tokens:>6,} tokens      {total_cost_dkk:>6.2f} DKK    ${total_cost_usd:>5.3f}")
    
    print("\n💡 Anbefaling:")
    print("   - Brug Sonnet + Thinking til daglig træning (bedste balance)")
    print("   - Brug Opus til special cases (vigtige demos, research)")
    print("   - Disable thinking hvis budget er meget tight")


if __name__ == "__main__":
    # Check API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("⚠️  Sæt ANTHROPIC_API_KEY environment variable først")
        print("   Eller kør: export ANTHROPIC_API_KEY='din-key-her'")
    else:
        compare_configurations()
        cost_comparison()
