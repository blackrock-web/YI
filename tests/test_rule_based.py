"""
Tests for Phase 2: Rule-Based Conversation
Verifies parser, tokenizer, intent matching, conversation context, and response engine.
"""
import unittest
from app.brain.parser import TextParser
from app.brain.tokenizer import Tokenizer
from app.brain.intents import IntentRegistry, Intent
from app.brain.context import ConversationContext
from app.brain.response_engine import ResponseEngine

class TestRuleBasedConversation(unittest.TestCase):
    def setUp(self):
        self.registry = IntentRegistry()
        self.response_engine = ResponseEngine(seed=42)
        self.context = ConversationContext()

    def test_parser_normalization(self):
        text = "I'm   testing, aren't you?"
        normalized = TextParser.normalize(text)
        self.assertEqual(normalized, "i am testing, are not you?")

    def test_tokenizer(self):
        tokenizer = Tokenizer()
        tokens = tokenizer.tokenize("Hello, my AI!")
        self.assertEqual(tokens, ["Hello", ",", "my", "AI", "!"])

    def test_greetings_and_farewells(self):
        res1 = self.registry.match("Hello there")
        self.assertEqual(res1.intent, Intent.GREETING)
        
        res2 = self.registry.match("Goodbye assistant")
        self.assertEqual(res2.intent, Intent.GOODBYE)

    def test_time_and_date(self):
        res_time = self.registry.match("What time is it?")
        self.assertEqual(res_time.intent, Intent.ASK_TIME)

        res_date = self.registry.match("What is today's date?")
        self.assertEqual(res_date.intent, Intent.ASK_DATE)

    def test_memory_intent_extraction(self):
        res = self.registry.match("My favorite game is Minecraft")
        self.assertEqual(res.intent, Intent.REMEMBER)
        self.assertEqual(res.extracted_params.get("key"), "favorite game")
        self.assertEqual(res.extracted_params.get("value"), "Minecraft")

        query_res = self.registry.match("What is my favorite game?")
        self.assertEqual(query_res.intent, Intent.SEARCH_MEMORY)
        self.assertEqual(query_res.extracted_params.get("query"), "favorite game")

    def test_task_intents(self):
        res_create = self.registry.match("create task: Study Python for ML")
        self.assertEqual(res_create.intent, Intent.CREATE_TASK)
        self.assertEqual(res_create.extracted_params.get("title"), "Study Python for ML")

        res_show = self.registry.match("show my tasks")
        self.assertEqual(res_show.intent, Intent.SHOW_TASKS)

    def test_emotion_intents(self):
        happy = self.registry.match("I am feeling very happy today!")
        self.assertEqual(happy.intent, Intent.USER_HAPPY)

        stressed = self.registry.match("I am so stressed")
        self.assertEqual(stressed.intent, Intent.USER_STRESSED)

    def test_context_history_and_pronoun_resolution(self):
        self.context.add_turn("user", "I talked to Rahul yesterday.", entities={"PERSON": "Rahul"})
        self.context.add_turn("assistant", "How was your conversation with Rahul?")
        resolved = self.context.resolve_reference("he")
        self.assertIsNotNone(resolved)
        self.assertEqual(resolved, ("PERSON", "Rahul"))

    def test_response_rendering(self):
        reply = self.response_engine.render(Intent.ASK_TIME)
        self.assertTrue(":" in reply)

if __name__ == "__main__":
    unittest.main()
