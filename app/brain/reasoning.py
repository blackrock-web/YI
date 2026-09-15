"""
MY AI - Central Agent Orchestrator
Coordinates the Brain pipeline:
Input Text -> Emotion Detection -> Intent Resolution (Rules + Neural) -> Context & Memory Retrieval
-> Action Dispatch / Tool Execution -> Deterministic Response Generation -> Personality Styling -> Memory Logging.
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime
from app.brain.parser import TextParser
from app.brain.intents import IntentRegistry, Intent, IntentMatchResult
from app.brain.response_engine import ResponseEngine
from app.brain.context import ConversationContext
from app.emotion.detector import EmotionDetector
from app.personality.personality import PersonalityEngine
from app.memory.memory import MemoryManager
from app.memory.profile import UserProfileManager
from app.planner.tasks import TaskManager, Priority
from app.planner.daily_planner import DailyPlanner
from app.planner.calendar import CalendarManager
from app.actions.dispatcher import ToolDispatcher
from app.config import config

@dataclass
class AgentResponse:
    text: str
    matched_intent: Intent
    confidence: float
    emotion: str
    valence: float
    arousal: float
    action_result: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "intent": self.matched_intent.value if self.matched_intent else "UNKNOWN",
            "confidence": self.confidence,
            "emotion": self.emotion,
            "valence": self.valence,
            "arousal": self.arousal,
            "action_result": self.action_result
        }

class AgentOrchestrator:
    def __init__(self, user_id: Optional[str] = None):
        self.user_id = user_id or config.default_user_id
        self.parser = TextParser()
        self.intent_registry = IntentRegistry()
        self.response_engine = ResponseEngine()
        self.context = ConversationContext()
        self.emotion_detector = EmotionDetector()
        self.personality = PersonalityEngine()
        self.memory = MemoryManager(user_id=self.user_id)
        self.profile = UserProfileManager(user_id=self.user_id)
        self.tasks = TaskManager(user_id=self.user_id)
        self.calendar = CalendarManager(user_id=self.user_id)
        self.planner = DailyPlanner(self.tasks, self.calendar)
        self.dispatcher = ToolDispatcher(task_manager=self.tasks, calendar_manager=self.calendar)

    def process(self, raw_input: str, conversation_id: str = "default_cli") -> AgentResponse:
        cleaned_input = self.parser.normalize(raw_input)
        
        # 1. Detect emotion & affect
        emotion_state = self.emotion_detector.detect(raw_input)

        # 2. Match intent
        intent_match = self.intent_registry.match(raw_input)
        intent = intent_match.intent
        params = intent_match.extracted_params

        action_result = None

        # 3. Intent execution handling
        if intent == Intent.CREATE_TASK and "task" in params or "title" in params:
            title = params.get("task") or params.get("title", "Untitled Task")
            task = self.tasks.create_task(title=title)
            action_result = {"created_task": task.to_dict()}
            base_text = f"I've added '{title}' to your task list."

        elif intent == Intent.SHOW_TASKS:
            all_t = self.tasks.list_tasks()
            action_result = {"tasks": [t.to_dict() for t in all_t]}
            if not all_t:
                base_text = "Your task list is currently empty! Everything is up to date."
            else:
                task_lines = [f"• [{t.status.value}] {t.title} ({t.priority.value})" for t in all_t[:5]]
                base_text = "Here are your current tasks:\n" + "\n".join(task_lines)

        elif intent == Intent.SHOW_SCHEDULE:
            schedule = self.planner.plan_day()
            action_result = {"schedule": [s.to_dict() for s in schedule]}
            slots = [f"• {s.start_time} - {s.end_time}: {s.title}" for s in schedule[:4]]
            base_text = "Here is your plan for today:\n" + "\n".join(slots)

        elif intent == Intent.REMEMBER:
            key = params.get("key", "")
            val = params.get("value", "")
            if key and val:
                self.memory.store_memory(key=key, value=val, importance=7)
                base_text = f"Got it. I'll remember that {key} is {val}."
            else:
                base_text = "I've noted that down in your private local memory."

        elif intent == Intent.SEARCH_MEMORY:
            q = params.get("query", "")
            results = self.memory.search_memories(q, limit=2)
            if results:
                m = results[0]
                base_text = f"Based on what you told me earlier: {m['key']} is {m['value']}."
            else:
                base_text = f"I don't have any saved notes matching '{q}' yet."

        else:
            # Fallback to response engine templates
            context_vars = {
                "current_time": datetime.now().strftime("%I:%M %p"),
                "current_date": datetime.now().strftime("%A, %B %d, %Y")
            }
            base_text = self.response_engine.render(intent, context_vars)

        # 4. Style with personality based on emotion
        styled_text = self.personality.style_response(base_text, user_emotion=emotion_state.primary_emotion.value)

        # 5. Log interaction to local memory
        self.memory.log_message(conversation_id, "user", raw_input)
        self.memory.log_message(conversation_id, "assistant", styled_text)

        return AgentResponse(
            text=styled_text,
            matched_intent=intent,
            confidence=intent_match.confidence,
            emotion=emotion_state.primary_emotion.value,
            valence=emotion_state.valence,
            arousal=emotion_state.arousal,
            action_result=action_result
        )
