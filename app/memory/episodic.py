"""
MY AI - Episodic Memory
Tracks experiential events, past interactions, episodic timelines, and conversation snapshots.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from app.memory.database import DatabaseManager
from app.config import config

class EpisodicMemory:
    def __init__(self, db: Optional[DatabaseManager] = None, user_id: Optional[str] = None):
        self.db = db or DatabaseManager.get_instance()
        self.user_id = user_id or config.default_user_id

    def record_episode(
        self,
        event_name: str,
        description: str,
        emotional_state: Optional[str] = None,
        importance: int = 5,
        entities: Optional[Dict[str, Any]] = None
    ) -> str:
        episode_id = str(uuid.uuid4())
        # Store in emotional_events or memories as type 'experience'
        with self.db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO memories (id, user_id, memory_type, key, value, importance, source)
                VALUES (?, ?, 'experience', ?, ?, ?, 'episodic_tracker')
                """,
                (episode_id, self.user_id, event_name, description, importance)
            )
            if emotional_state:
                conn.execute(
                    """
                    INSERT INTO emotional_events (id, user_id, emotion, trigger_text, notes)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (str(uuid.uuid4()), self.user_id, emotional_state, event_name, description)
                )
        return episode_id

    def get_recent_episodes(self, limit: int = 10) -> List[Dict[str, Any]]:
        rows = self.db.fetchall(
            """
            SELECT * FROM memories WHERE user_id = ? AND memory_type = 'experience'
            ORDER BY created_at DESC LIMIT ?
            """,
            (self.user_id, limit)
        )
        return [dict(r) for r in rows]
