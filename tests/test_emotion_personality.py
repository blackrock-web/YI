"""
Tests for Phase 10 (Emotion Engine) & Phase 11 (Personality & Relationship)
Verifies discrete emotion detection, valence/arousal circumplex mapping, persona consistency, and rapport evolution.
"""
import unittest
import tempfile
from pathlib import Path
from app.emotion.states import EmotionType, ConversationMode
from app.emotion.detector import EmotionDetector
from app.personality.personality import PersonalityEngine
from app.personality.relationship import RelationshipManager, RelationshipLevel
from app.memory.database import DatabaseManager
from app.memory.memory import MemoryManager

class TestEmotionAndPersonality(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_ep.db"
        self.db = DatabaseManager(self.db_path)
        self.detector = EmotionDetector()
        self.personality = PersonalityEngine()
        self.memory = MemoryManager(self.db, user_id="test_ep_user")
        self.relationship = RelationshipManager(self.db, user_id="test_ep_user")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_emotion_detection(self):
        # Happy
        state = self.detector.detect("I am so happy and excited today!")
        self.assertIn(state.primary_emotion, (EmotionType.HAPPY, EmotionType.EXCITED))
        self.assertGreater(state.valence, 0.5)

        # Sad
        sad_state = self.detector.detect("I am feeling very sad and down.")
        self.assertEqual(sad_state.primary_emotion, EmotionType.SAD)
        self.assertLess(sad_state.valence, 0.0)
        self.assertEqual(sad_state.conversation_mode, ConversationMode.VENTING)

        # Stressed
        stress_state = self.detector.detect("I am extremely stressed and overwhelmed with work.")
        self.assertEqual(stress_state.primary_emotion, EmotionType.STRESSED)
        self.assertGreater(stress_state.arousal, 0.5)

    def test_personality_styling(self):
        resp = self.personality.style_response("Take things one step at a time.", user_emotion="SAD")
        self.assertIn("I'm right here with you", resp)

    def test_relationship_growth(self):
        # Initial state
        initial = self.relationship.get_relationship_state()
        self.assertEqual(initial.interactions_count, 0)
        self.assertEqual(initial.level, RelationshipLevel.ACQUAINTANCE)

        # Add interactions & memories
        self.memory.store_memory(key="favorite_color", value="blue")
        self.memory.store_memory(key="hobby", value="piano")
        self.memory.log_message("c1", "user", "Hi")
        self.memory.log_message("c1", "assistant", "Hello")

        updated = self.relationship.get_relationship_state()
        self.assertEqual(updated.shared_memories_count, 2)
        self.assertEqual(updated.interactions_count, 2)
        self.assertGreater(updated.rapport_score, initial.rapport_score)

if __name__ == "__main__":
    unittest.main()
