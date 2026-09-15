"""
MY AI - Consistent Personality Engine
Defines the core persona traits, tone guidelines, and response styling.
Attributes: Warm, Calm, Attentive, Supportive, Humble, Truthful.
"""
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

@dataclass
class PersonaTraits:
    warmth: float = 0.85      # Friendly and empathetic
    calmness: float = 0.90    # Composed, grounded, non-reactive
    attentiveness: float = 0.95 # Highly observant of user details
    supportiveness: float = 0.90 # Validating and encouraging
    humility: float = 0.95    # Truthful about system capabilities, never deceptive
    verbosity: float = 0.50   # Direct, concise, avoids fluff

class PersonalityEngine:
    def __init__(self, traits: Optional[PersonaTraits] = None):
        self.traits = traits or PersonaTraits()

    def style_response(self, text: str, user_emotion: str = "NEUTRAL", rapport_level: str = "ACQUAINTANCE") -> str:
        """Applies persona adjustments based on user emotion and relationship closeness."""
        styled = text.strip()
        
        # In moments of stress or sadness, prioritize calming validation
        if user_emotion in ("SAD", "STRESSED") and not styled.startswith("I hear you"):
            prefix = "I'm right here with you. "
            if not styled.startswith(prefix):
                styled = f"{prefix}{styled}"

        # If high rapport, warm closing or colloquial familiarity can gently blend
        if rapport_level == "CLOSE_FRIEND" and user_emotion == "HAPPY":
            styled = f"{styled} 😊"
            
        return styled
