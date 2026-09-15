"""
Tests for Phase 3: Local Memory
Verifies SQLite storage, memory CRUD, deterministic retrieval, importance, and conversation logging.
"""
import unittest
import tempfile
import os
from pathlib import Path
from app.memory.database import DatabaseManager
from app.memory.memory import MemoryManager

class TestLocalMemory(unittest.TestCase):
    def setUp(self):
        # Create a temporary SQLite database for clean isolated testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_memory.db"
        self.db = DatabaseManager(self.db_path)
        self.memory = MemoryManager(self.db, user_id="test_user")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_store_and_retrieve_preference(self):
        # Example from prompt:
        # User: "My favorite game is Minecraft."
        # type = preference, key = favorite_game, value = Minecraft
        stored = self.memory.store_memory(
            key="favorite_game",
            value="Minecraft",
            memory_type="preference",
            importance=8,
            confidence=1.0,
            source="user_statement"
        )
        self.assertEqual(stored["key"], "favorite_game")
        self.assertEqual(stored["value"], "Minecraft")
        self.assertEqual(stored["importance"], 8)

        # Later: User: "What is my favorite game?"
        results = self.memory.search_memories("What is my favorite game?")
        self.assertGreater(len(results), 0)
        top_match = results[0]
        self.assertEqual(top_match["key"], "favorite_game")
        self.assertEqual(top_match["value"], "Minecraft")
        self.assertGreater(top_match["_retrieval_score"], 20.0)

    def test_update_memory(self):
        self.memory.store_memory(key="pet_name", value="Shadow", memory_type="fact", importance=5)
        # Update
        updated = self.memory.store_memory(key="pet_name", value="Luna", memory_type="fact", importance=7)
        self.assertEqual(updated["value"], "Luna")
        
        mem = self.memory.get_memory_by_key("pet_name")
        self.assertEqual(mem["value"], "Luna")
        self.assertEqual(mem["importance"], 7)

    def test_delete_memory(self):
        self.memory.store_memory(key="temp_note", value="remember to buy milk")
        self.assertIsNotNone(self.memory.get_memory_by_key("temp_note"))
        
        deleted = self.memory.delete_memory("temp_note")
        self.assertTrue(deleted)
        self.assertIsNone(self.memory.get_memory_by_key("temp_note"))

    def test_conversation_history(self):
        conv_id = "conv_test_123"
        self.memory.log_message(conv_id, "user", "Hello there!", intent="GREETING")
        self.memory.log_message(conv_id, "assistant", "Hello! How can I help you today?", intent="GREETING")

        history = self.memory.get_conversation_history(conv_id)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["sender"], "user")
        self.assertEqual(history[1]["sender"], "assistant")

if __name__ == "__main__":
    unittest.main()
