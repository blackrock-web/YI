"""
MY AI - Context Window & Long-Term Recall Subsystem
Assembles relevant conversational context, active goals, user profile, and deterministic episodic memory
into a bounded context budget for generation and dialogue comprehension.
"""
from typing import List, Dict, Any, Optional
from app.memory.memory import MemoryManager
from app.memory.profile import UserProfileManager
from app.planner.tasks import TaskManager, TaskStatus, Priority

class ContextRecallEngine:
    def __init__(
        self,
        memory: Optional[MemoryManager] = None,
        profile: Optional[UserProfileManager] = None,
        tasks: Optional[TaskManager] = None,
        max_context_tokens: int = 512
    ):
        self.memory = memory or MemoryManager()
        self.profile = profile or UserProfileManager()
        self.tasks = tasks or TaskManager()
        self.max_context_tokens = max_context_tokens

    def assemble_prompt_context(self, current_user_query: str, conversation_id: str) -> Dict[str, Any]:
        # 1. Retrieve most relevant long-term memories
        memories = self.memory.search_memories(current_user_query, limit=3)
        
        # 2. Retrieve active goals and preferences
        user_prefs = self.profile.get_preferences()
        user_goals = self.profile.list_goals()
        
        # 3. Retrieve urgent/pending tasks
        pending_tasks = self.tasks.list_tasks(status=TaskStatus.PENDING)
        urgent_tasks = [t for t in pending_tasks if (t.priority in (Priority.HIGH, Priority.URGENT) or getattr(t.priority, 'value', '') in ("HIGH", "URGENT"))][:3]

        # 4. Recent conversation turns
        recent_history = self.memory.get_conversation_history(conversation_id, limit=6)

        return {
            "query": current_user_query,
            "relevant_memories": [f"{m['key']}: {m['value']}" for m in memories],
            "preferences": user_prefs,
            "active_goals": [g.get("title", "") for g in user_goals][:3],
            "urgent_tasks": [t.title for t in urgent_tasks],
            "recent_turns": [
                {"role": m["sender"], "text": m["content"]}
                for m in recent_history
            ]
        }
