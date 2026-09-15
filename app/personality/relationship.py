"""
MY AI - Relationship & Context Model
Tracks cumulative interactions, rapport, familiarity, and trust dynamics with the user over time.
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum
from app.memory.database import DatabaseManager
from app.config import config

class RelationshipLevel(str, Enum):
    STRANGER = "STRANGER"              # 0 - 20
    ACQUAINTANCE = "ACQUAINTANCE"      # 21 - 50
    COMPANION = "COMPANION"            # 51 - 80
    CLOSE_CONFIDANT = "CLOSE_CONFIDANT" # 81 - 100

@dataclass
class RelationshipState:
    user_id: str
    rapport_score: float = 25.0
    interactions_count: int = 1
    shared_memories_count: int = 0
    level: RelationshipLevel = RelationshipLevel.ACQUAINTANCE

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "rapport_score": round(self.rapport_score, 1),
            "interactions_count": self.interactions_count,
            "shared_memories_count": self.shared_memories_count,
            "level": self.level.value
        }

class RelationshipManager:
    def __init__(self, db: Optional[DatabaseManager] = None, user_id: Optional[str] = None):
        self.db = db or DatabaseManager.get_instance()
        self.user_id = user_id or config.default_user_id

    def _calculate_level(self, score: float) -> RelationshipLevel:
        if score >= 80:
            return RelationshipLevel.CLOSE_CONFIDANT
        elif score >= 50:
            return RelationshipLevel.COMPANION
        elif score >= 20:
            return RelationshipLevel.ACQUAINTANCE
        return RelationshipLevel.STRANGER

    def get_relationship_state(self) -> RelationshipState:
        # Count messages for interactions count
        msg_row = self.db.fetchone(
            """
            SELECT COUNT(*) as cnt FROM messages m
            JOIN conversations c ON m.conversation_id = c.id
            WHERE c.user_id = ?
            """,
            (self.user_id,)
        )
        msg_count = msg_row["cnt"] if msg_row else 0

        # Count stored memories
        mem_row = self.db.fetchone(
            "SELECT COUNT(*) as cnt FROM memories WHERE user_id = ?",
            (self.user_id,)
        )
        mem_count = mem_row["cnt"] if mem_row else 0

        # Base rapport calculation: 25 + msg_count * 1.5 + mem_count * 3.0 (capped at 100)
        score = min(100.0, 25.0 + (msg_count * 1.5) + (mem_count * 3.0))
        level = self._calculate_level(score)

        return RelationshipState(
            user_id=self.user_id,
            rapport_score=score,
            interactions_count=msg_count,
            shared_memories_count=mem_count,
            level=level
        )
