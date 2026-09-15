"""
MY AI - Local Knowledge Graph Subsystem
Stores entities (people, places, concepts, projects) and typed directional edges.
Zero external graph database required: runs directly with local graph traversal algorithms.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set
import json
from app.memory.database import DatabaseManager
from app.config import config

@dataclass
class KnowledgeNode:
    id: str
    entity_type: str  # "person", "place", "concept", "project", "topic"
    name: str
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass
class KnowledgeEdge:
    source_id: str
    target_id: str
    relation: str    # "friend_of", "works_on", "located_in", "interested_in", "part_of"
    weight: float = 1.0

class LocalKnowledgeGraph:
    def __init__(self, db: Optional[DatabaseManager] = None, user_id: Optional[str] = None):
        self.db = db or DatabaseManager.get_instance()
        self.user_id = user_id or config.default_user_id

    def add_entity(self, entity_id: str, entity_type: str, name: str, properties: Optional[Dict[str, Any]] = None) -> None:
        props_json = json.dumps(properties or {})
        with self.db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO memories (id, user_id, memory_type, key, value, importance, source)
                VALUES (?, ?, 'graph_node', ?, ?, 6, 'knowledge_graph')
                ON CONFLICT(id) DO UPDATE SET value = excluded.value, updated_at = CURRENT_TIMESTAMP
                """,
                (f"node_{entity_id}", self.user_id, f"{entity_type}:{name.lower()}", props_json)
            )

    def add_relation(self, source_id: str, relation: str, target_id: str) -> None:
        rel_id = f"edge_{source_id}_{relation}_{target_id}"
        with self.db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO relationships (id, user_id, entity1_type, entity1_id, relation_type, entity2_type, entity2_id)
                VALUES (?, ?, 'node', ?, ?, 'node', ?)
                ON CONFLICT(id) DO UPDATE SET relation_type = excluded.relation_type
                """,
                (rel_id, self.user_id, source_id, relation, target_id)
            )

    def get_neighbors(self, node_id: str) -> List[Dict[str, Any]]:
        """Traverses outward edges from a node."""
        rows = self.db.fetchall(
            """
            SELECT * FROM relationships 
            WHERE user_id = ? AND entity1_id = ?
            """,
            (self.user_id, node_id)
        )
        return [
            {
                "relation": r["relation_type"],
                "target_id": r["entity2_id"]
            }
            for r in rows
        ]

    def query_subgraph(self, start_node_id: str, max_depth: int = 2) -> Dict[str, Any]:
        """Breadth-first search traversal of local knowledge graph."""
        visited: Set[str] = {start_node_id}
        queue = [(start_node_id, 0)]
        edges = []

        while queue:
            curr_id, depth = queue.pop(0)
            if depth >= max_depth:
                continue

            neighbors = self.get_neighbors(curr_id)
            for n in neighbors:
                edges.append({
                    "from": curr_id,
                    "relation": n["relation"],
                    "to": n["target_id"]
                })
                if n["target_id"] not in visited:
                    visited.add(n["target_id"])
                    queue.append((n["target_id"], depth + 1))

        return {
            "root": start_node_id,
            "entities": list(visited),
            "edges": edges
        }
