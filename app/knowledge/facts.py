"""
MY AI - Local Fact Repository
Manages curated, offline entity facts and question-answering over local structured data.
"""
from typing import Dict, Any, List, Optional
from app.knowledge.graph import LocalKnowledgeGraph
from app.memory.memory import MemoryManager
from app.memory.profile import UserProfileManager

class FactRepository:
    def __init__(
        self,
        graph: Optional[LocalKnowledgeGraph] = None,
        memory: Optional[MemoryManager] = None,
        profile: Optional[UserProfileManager] = None
    ):
        self.graph = graph or LocalKnowledgeGraph()
        self.memory = memory or MemoryManager()
        self.profile = profile or UserProfileManager()

    def get_entity_summary(self, entity_name: str) -> Optional[str]:
        clean_name = entity_name.strip()
        # 1. Check in important people
        person = self.profile.find_person(clean_name)
        if person:
            notes = f", notes: {person['notes']}" if person.get('notes') else ""
            return f"{person['name']} is your {person['relationship']}{notes}."

        # 2. Check in memories
        mems = self.memory.search_memories(clean_name, limit=2)
        if mems:
            facts = [f"{m['key'].replace('_', ' ')}: {m['value']}" for m in mems]
            return f"Information about {clean_name}: " + "; ".join(facts)

        return None
