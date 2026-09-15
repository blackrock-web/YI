"""
MY AI - Semantic Memory
Stores concepts, facts, taxonomies, and entity relationship graphs.
"""
from typing import List, Dict, Any, Optional
import uuid
from app.memory.database import DatabaseManager
from app.config import config

class SemanticMemory:
    def __init__(self, db: Optional[DatabaseManager] = None, user_id: Optional[str] = None):
        self.db = db or DatabaseManager.get_instance()
        self.user_id = user_id or config.default_user_id

    def store_concept(self, concept_key: str, definition: str, category: str = "general") -> str:
        concept_id = str(uuid.uuid4())
        clean_key = concept_key.strip().lower().replace(" ", "_")
        with self.db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO memories (id, user_id, memory_type, key, value, importance, source)
                VALUES (?, ?, 'concept', ?, ?, 6, 'semantic_network')
                ON CONFLICT(id) DO NOTHING
                """,
                (concept_id, self.user_id, clean_key, definition)
            )
        return concept_id

    def add_relationship(
        self,
        entity1_type: str,
        entity1_id: str,
        relation_type: str,
        entity2_type: str,
        entity2_id: str
    ) -> str:
        rel_id = str(uuid.uuid4())
        with self.db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO relationships (id, user_id, entity1_type, entity1_id, relation_type, entity2_type, entity2_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (rel_id, self.user_id, entity1_type, entity1_id, relation_type, entity2_type, entity2_id)
            )
        return rel_id

    def get_related_entities(self, entity_id: str) -> List[Dict[str, Any]]:
        rows = self.db.fetchall(
            """
            SELECT * FROM relationships 
            WHERE user_id = ? AND (entity1_id = ? OR entity2_id = ?)
            """,
            (self.user_id, entity_id, entity_id)
        )
        return [dict(r) for r in rows]
