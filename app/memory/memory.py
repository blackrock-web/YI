"""
MY AI - Memory Management Subsystem
Handles structured episodic & semantic memories, preferences, importance, confidence, and conversation logging.
"""
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.memory.database import DatabaseManager
from app.memory.retrieval import MemoryRetriever
from app.config import config
from app.logging_config import logger

class MemoryManager:
    def __init__(self, db: Optional[DatabaseManager] = None, user_id: Optional[str] = None):
        self.db = db or DatabaseManager.get_instance()
        self.user_id = user_id or config.default_user_id
        self._ensure_user()

    def _ensure_user(self) -> None:
        with self.db.transaction() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO users (id, name) VALUES (?, ?)",
                (self.user_id, "User")
            )

    def store_memory(
        self,
        key: str,
        value: str,
        memory_type: str = "fact",
        importance: int = 5,
        confidence: float = 1.0,
        source: str = "user_statement"
    ) -> Dict[str, Any]:
        """
        Stores or updates a memory entry.
        If an entry with exact key and type exists for user, updates it.
        """
        clean_key = key.strip().lower().replace(" ", "_")
        mem_id = str(uuid.uuid4())
        
        # Check existing memory with same key
        existing = self.db.fetchone(
            "SELECT id, importance, value FROM memories WHERE user_id = ? AND key = ?",
            (self.user_id, clean_key)
        )
        
        with self.db.transaction() as conn:
            if existing:
                conn.execute(
                    """
                    UPDATE memories 
                    SET value = ?, memory_type = ?, importance = ?, confidence = ?, source = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (value.strip(), memory_type, importance, confidence, source, existing["id"])
                )
                mem_id = existing["id"]
            else:
                conn.execute(
                    """
                    INSERT INTO memories (id, user_id, memory_type, key, value, importance, confidence, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (mem_id, self.user_id, memory_type, clean_key, value.strip(), importance, confidence, source)
                )
                
        # Also store into preferences table if memory_type is preference
        if memory_type == "preference":
            pref_id = str(uuid.uuid4())
            with self.db.transaction() as conn:
                conn.execute(
                    """
                    INSERT INTO preferences (id, user_id, category, key, value)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(user_id, category, key) DO UPDATE SET value = excluded.value, updated_at = CURRENT_TIMESTAMP
                    """,
                    (pref_id, self.user_id, "general", clean_key, value.strip())
                )

        return {
            "id": mem_id,
            "key": clean_key,
            "value": value.strip(),
            "memory_type": memory_type,
            "importance": importance,
            "confidence": confidence,
            "source": source
        }

    def get_memory_by_key(self, key: str) -> Optional[Dict[str, Any]]:
        clean_key = key.strip().lower().replace(" ", "_")
        row = self.db.fetchone(
            "SELECT * FROM memories WHERE user_id = ? AND key = ?",
            (self.user_id, clean_key)
        )
        return dict(row) if row else None

    def search_memories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        rows = self.db.fetchall(
            "SELECT * FROM memories WHERE user_id = ? ORDER BY importance DESC, updated_at DESC",
            (self.user_id,)
        )
        all_mems = [dict(r) for r in rows]
        return MemoryRetriever.rank_memories(query, all_mems, limit=limit)

    def list_all_memories(self, memory_type: Optional[str] = None) -> List[Dict[str, Any]]:
        if memory_type:
            rows = self.db.fetchall(
                "SELECT * FROM memories WHERE user_id = ? AND memory_type = ? ORDER BY updated_at DESC",
                (self.user_id, memory_type)
            )
        else:
            rows = self.db.fetchall(
                "SELECT * FROM memories WHERE user_id = ? ORDER BY updated_at DESC",
                (self.user_id,)
            )
        return [dict(r) for r in rows]

    def delete_memory(self, memory_id_or_key: str) -> bool:
        with self.db.transaction() as conn:
            cursor = conn.execute(
                "DELETE FROM memories WHERE user_id = ? AND (id = ? OR key = ?)",
                (self.user_id, memory_id_or_key, memory_id_or_key.strip().lower().replace(" ", "_"))
            )
            return cursor.rowcount > 0

    # Conversation History
    def log_message(self, conversation_id: str, sender: str, content: str, intent: Optional[str] = None, emotion: Optional[str] = None) -> str:
        # Ensure conversation exists
        self.db.execute(
            "INSERT OR IGNORE INTO conversations (id, user_id, title) VALUES (?, ?, ?)",
            (conversation_id, self.user_id, f"Conversation {conversation_id[:8]}")
        )
        msg_id = str(uuid.uuid4())
        with self.db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO messages (id, conversation_id, sender, content, intent, emotion)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (msg_id, conversation_id, sender, content, intent, emotion)
            )
        return msg_id

    def get_conversation_history(self, conversation_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        rows = self.db.fetchall(
            """
            SELECT * FROM messages WHERE conversation_id = ? 
            ORDER BY timestamp ASC LIMIT ?
            """,
            (conversation_id, limit)
        )
        return [dict(r) for r in rows]
