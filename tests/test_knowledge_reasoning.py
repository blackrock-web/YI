"""
Tests for Phase 12 (Knowledge Base) & Phase 13 (Reasoning & Problem Solving)
Verifies local knowledge graph BFS, fact synthesis, task decomposition, and forward-chaining inference.
"""
import unittest
import tempfile
from pathlib import Path
from app.knowledge.graph import LocalKnowledgeGraph
from app.knowledge.facts import FactRepository
from app.reasoning.decomposer import TaskDecomposer
from app.reasoning.engine import ReasoningEngine, Rule
from app.memory.database import DatabaseManager
from app.memory.profile import UserProfileManager

class TestKnowledgeAndReasoning(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_kr.db"
        self.db = DatabaseManager(self.db_path)
        self.graph = LocalKnowledgeGraph(self.db, user_id="test_kr_user")
        self.profile = UserProfileManager(self.db, user_id="test_kr_user")
        self.facts = FactRepository(graph=self.graph, profile=self.profile)
        self.reasoning = ReasoningEngine()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_knowledge_graph_traversal(self):
        self.graph.add_entity("user", "person", "User")
        self.graph.add_entity("rahul", "person", "Rahul")
        self.graph.add_entity("chess", "hobby", "Chess")

        self.graph.add_relation("user", "friend_of", "rahul")
        self.graph.add_relation("rahul", "interested_in", "chess")

        subgraph = self.graph.query_subgraph("user", max_depth=2)
        self.assertIn("rahul", subgraph["entities"])
        self.assertIn("chess", subgraph["entities"])
        self.assertEqual(len(subgraph["edges"]), 2)

    def test_fact_repository(self):
        self.profile.add_person("Rahul", "friend", notes="Plays guitar and loves coding")
        summary = self.facts.get_entity_summary("Rahul")
        self.assertIsNotNone(summary)
        self.assertIn("Rahul is your friend", summary)

    def test_task_decomposition(self):
        plans = TaskDecomposer.decompose("Learn PyTorch deep learning")
        self.assertGreater(len(plans), 2)
        self.assertTrue(any("research" in p.title.lower() or "practice" in p.title.lower() for p in plans))

    def test_forward_chaining_reasoning(self):
        facts = {"user_tired", "is_night"}
        conclusions = self.reasoning.infer(facts)
        self.assertIn("suggest_winding_down", conclusions)

if __name__ == "__main__":
    unittest.main()
