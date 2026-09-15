"""
Tests for Phases 18-25:
Verifies Context Recall (P18), Tool Dispatch (P19), Visual Perception (P20), Social Intelligence (P21),
Evaluation Benchmarks (P23), INT8 Quantization (P24), and Autonomous Companion Heartbeat (P25).
"""
import unittest
import tempfile
import torch
from pathlib import Path
from app.memory.database import DatabaseManager
from app.memory.memory import MemoryManager
from app.planner.tasks import TaskManager, Priority
from app.brain.recall import ContextRecallEngine
from app.actions.dispatcher import ToolDispatcher
from app.vision.perception import LocalVisualPerception
from app.social.social_engine import SocialIntelligenceEngine, SocialContext
from app.eval.benchmarks import BenchmarkSuite
from app.models.transformer import DecoderTransformer, TransformerConfig
from app.models.quantization import ModelOptimizer
from app.companion.autonomous_loop import AutonomousCompanion
from app.planner.reminders import ReminderManager

class TestAdvancedPhases(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_adv.db"
        self.db = DatabaseManager(self.db_path)
        self.memory = MemoryManager(self.db, user_id="test_adv_user")
        self.tasks = TaskManager(self.db, user_id="test_adv_user")
        self.reminders = ReminderManager(self.db, user_id="test_adv_user")
        self.recall = ContextRecallEngine(memory=self.memory, tasks=self.tasks)
        self.dispatcher = ToolDispatcher(task_manager=self.tasks)
        self.social = SocialIntelligenceEngine()
        self.companion = AutonomousCompanion(reminder_manager=self.reminders, task_manager=self.tasks)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_context_recall(self):
        self.memory.store_memory(key="favorite_food", value="sushi")
        self.tasks.create_task(title="Finish project", priority=Priority.URGENT)

        context = self.recall.assemble_prompt_context("What should I eat?", conversation_id="conv_1")
        self.assertIn("query", context)
        self.assertTrue(len(context["relevant_memories"]) > 0)
        self.assertIn("Finish project", context["urgent_tasks"])

    def test_tool_dispatcher(self):
        # Create task via tool dispatcher
        res = self.dispatcher.dispatch("create_task", {"title": "Test Dispatcher Task", "priority": "HIGH"})
        self.assertTrue(res["success"])
        self.assertEqual(res["task"]["title"], "Test Dispatcher Task")

        # Query system info
        sys_res = self.dispatcher.dispatch("get_system_info", {})
        self.assertTrue(sys_res["success"])

    def test_visual_perception(self):
        # 10x10 dark image
        dark_pixels = bytes([20, 20, 20] * 100)
        dark_res = LocalVisualPerception.analyze_raw_rgb(dark_pixels, 10, 10)
        self.assertTrue(dark_res.is_dark_mode)

        # ASCII render
        ascii_art = LocalVisualPerception.render_ascii(dark_pixels, 10, 10, target_cols=5)
        self.assertIsInstance(ascii_art, str)
        self.assertGreater(len(ascii_art), 0)

    def test_social_intelligence(self):
        # Directly addressed
        self.assertTrue(self.social.is_directly_addressed("MY AI, what time is it?"))
        self.assertTrue(self.social.is_directly_addressed("Could you help me with this?"))
        self.assertFalse(self.social.is_directly_addressed("Hey John, let's grab coffee."))

        # Intervene policy in group meeting
        should_speak, reason = self.social.should_intervene(
            "Hey John, let's grab coffee.", "Speaker 1", SocialContext.GROUP_MEETING
        )
        self.assertFalse(should_speak)

    def test_evaluation_benchmarks(self):
        suite = BenchmarkSuite()
        results = suite.run_all_benchmarks()
        self.assertEqual(results["overall_status"], "ALL_BENCHMARKS_PASSED")
        self.assertEqual(results["intent_classification"]["passed"], results["intent_classification"]["total_tests"])

    def test_model_quantization(self):
        cfg = TransformerConfig(vocab_size=128, block_size=16, n_layer=1, n_head=1, n_embd=16)
        model = DecoderTransformer(cfg)
        size_before = ModelOptimizer.measure_model_size_mb(model)
        self.assertGreater(size_before, 0.0)

        quantized = ModelOptimizer.quantize_dynamic_int8(model)
        self.assertIsNotNone(quantized)

    def test_autonomous_companion(self):
        # Set past reminder
        self.reminders.create_reminder("Take a stretch break", "2020-01-01 00:00:00")
        notifications = self.companion.tick_heartbeat()
        self.assertTrue(any(n["type"] == "REMINDER" for n in notifications))

        briefing = self.companion.generate_morning_briefing()
        self.assertIn("Good morning", briefing)

if __name__ == "__main__":
    unittest.main()
