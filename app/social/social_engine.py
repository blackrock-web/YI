"""
MY AI - Social Intelligence Engine
Multi-speaker conversational dynamics, turn-taking modeling, addressivity detection,
and conversational etiquette (determining when MY AI is addressed vs when other people are talking).
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum

class SocialContext(str, Enum):
    ONE_ON_ONE = "ONE_ON_ONE"
    GROUP_MEETING = "GROUP_MEETING"
    BACKGROUND_CHATTER = "BACKGROUND_CHATTER"

@dataclass
class SpeakerTurn:
    speaker_id: str
    text: str
    is_user: bool = True
    confidence: float = 1.0

class SocialIntelligenceEngine:
    AI_NAMES = {"my ai", "assistant", "ai", "aura"}

    def __init__(self, bot_name: str = "MY AI"):
        self.bot_name = bot_name.lower()
        self.turns: List[SpeakerTurn] = []

    def is_directly_addressed(self, utterance: str) -> bool:
        """Determines whether utterance is directed at the assistant."""
        clean = utterance.lower().strip()
        # Direct wake word or question
        for name in self.AI_NAMES:
            if clean.startswith(name) or f", {name}" in clean or clean.endswith(name):
                return True
        # Starts with imperative action or assistant question
        if clean.startswith(("can you", "could you", "please", "what time", "what is my", "remind me", "plan my")):
            return True
        return False

    def should_intervene(self, utterance: str, current_speaker: str, context: SocialContext) -> Tuple[bool, str]:
        """
        Determines if MY AI should speak, remain silent, or acknowledge quietly.
        In multi-party settings, remains respectfully quiet unless explicitly summoned.
        """
        if context == SocialContext.ONE_ON_ONE:
            return True, "One-on-one dialogue: active response."

        # Group meeting / background context
        if self.is_directly_addressed(utterance):
            return True, "Directly addressed in group setting."

        return False, "Multi-party conversation detected: remaining quiet to avoid interrupting."
