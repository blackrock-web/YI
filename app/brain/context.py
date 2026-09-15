"""
MY AI - Conversation Context
Maintains active conversation state, topic continuity, pending confirmations, and entity references.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime

@dataclass
class Turn:
    role: str   # "user" | "assistant"
    text: str
    intent: Optional[str] = None
    entities: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

@dataclass
class PendingAction:
    action_name: str
    target: str
    params: Dict[str, Any] = field(default_factory=dict)
    confirmation_token: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

class ConversationContext:
    def __init__(self, max_history: int = 20):
        self.max_history = max_history
        self.history: List[Turn] = []
        self.active_topic: Optional[str] = None
        self.last_entity_mentioned: Dict[str, str] = {}  # e.g. {"PERSON": "Rahul", "APPLICATION": "Terminal"}
        self.pending_action: Optional[PendingAction] = None
        self.session_data: Dict[str, Any] = {}

    def add_turn(self, role: str, text: str, intent: Optional[str] = None, entities: Optional[Dict[str, Any]] = None) -> Turn:
        turn = Turn(role=role, text=text, intent=intent, entities=entities or {})
        self.history.append(turn)
        if len(self.history) > self.max_history:
            self.history.pop(0)

        # Update last entity mentioned for reference resolution
        if entities:
            for ent_type, val in entities.items():
                if isinstance(val, str) and val.strip():
                    self.last_entity_mentioned[ent_type] = val.strip()

        return turn

    def set_active_topic(self, topic: str) -> None:
        self.active_topic = topic

    def get_last_turn(self, role: Optional[str] = None) -> Optional[Turn]:
        for turn in reversed(self.history):
            if role is None or turn.role == role:
                return turn
        return None

    def resolve_reference(self, pronoun: str) -> Optional[Tuple[str, str]]:
        """
        Resolves pronouns ('he', 'she', 'they', 'it') to most recently mentioned entity.
        Returns (entity_type, entity_value) or None.
        """
        pronoun_lower = pronoun.lower()
        if pronoun_lower in ("he", "him", "his", "she", "her", "they"):
            person = self.last_entity_mentioned.get("PERSON")
            if person:
                return ("PERSON", person)
        elif pronoun_lower in ("it", "this", "that"):
            # Could be application, task, or place
            for candidate in ["APPLICATION", "TASK", "EVENT", "PLACE"]:
                val = self.last_entity_mentioned.get(candidate)
                if val:
                    return (candidate, val)
        return None

    def set_pending_action(self, action: PendingAction) -> None:
        self.pending_action = action

    def clear_pending_action(self) -> Optional[PendingAction]:
        action = self.pending_action
        self.pending_action = None
        return action

    def has_pending_action(self) -> bool:
        return self.pending_action is not None
