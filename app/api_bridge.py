"""
MY AI - Python API Bridge
Enables the Web UI / Desktop interface to communicate directly with all MY AI subsystems:
Brain, Memory, Planner, Emotion, Personality, Models, and Autonomous Companion.
"""
import sys
import json
from typing import Dict, Any
from app.brain.reasoning import AgentOrchestrator
from app.memory.memory import MemoryManager
from app.memory.profile import UserProfileManager
from app.planner.tasks import TaskManager, Priority, TaskStatus
from app.planner.calendar import CalendarManager
from app.planner.daily_planner import DailyPlanner
from app.planner.reminders import ReminderManager
from app.personality.relationship import RelationshipManager
from app.emotion.detector import EmotionDetector
from app.eval.benchmarks import BenchmarkSuite
from app.companion.autonomous_loop import AutonomousCompanion
from app.safety.privacy import PrivacyGuard

def handle_request(req: Dict[str, Any]) -> Dict[str, Any]:
    action = req.get("action", "")

    if action == "chat":
        text = req.get("text", "")
        orchestrator = AgentOrchestrator()
        response = orchestrator.process(text)
        return {
            "reply": response.text,
            "intent": response.matched_intent.value if response.matched_intent else "UNKNOWN",
            "confidence": response.confidence,
            "emotion": response.emotion,
            "valence": response.valence,
            "arousal": response.arousal,
            "action_result": response.action_result
        }

    elif action == "get_dashboard":
        tasks_mgr = TaskManager()
        all_tasks = [t.to_dict() for t in tasks_mgr.list_tasks()]
        rel_mgr = RelationshipManager()
        rel_state = rel_mgr.get_relationship_state()
        planner = DailyPlanner(tasks_mgr, CalendarManager())
        schedule = [s.to_dict() for s in planner.plan_day()]
        guard = PrivacyGuard()
        comp = guard.verify_offline_compliance()
        mem_mgr = MemoryManager()
        recent_mems = mem_mgr.search_memories("", limit=6)

        return {
            "tasks": all_tasks,
            "schedule": schedule,
            "relationship": {
                "level": rel_state.level.value,
                "rapport_score": round(rel_state.rapport_score, 2),
                "interactions_count": rel_state.interactions_count,
                "shared_memories_count": rel_state.shared_memories_count
            },
            "recent_memories": [
                {"key": m["key"], "value": m["value"]} for m in recent_mems
            ],
            "privacy": comp
        }

    elif action == "create_task":
        title = req.get("title", "New Task")
        pri_str = req.get("priority", "MEDIUM").upper()
        try:
            pri = Priority(pri_str)
        except Exception:
            pri = Priority.MEDIUM
        task = TaskManager().create_task(title=title, priority=pri)
        return {"success": True, "task": task.to_dict()}

    elif action == "complete_task":
        task_id = req.get("task_id", "")
        res = TaskManager().complete_task(task_id)
        return {"success": res}

    elif action == "run_benchmarks":
        suite = BenchmarkSuite()
        return suite.run_all_benchmarks()

    elif action == "tick_companion":
        comp = AutonomousCompanion()
        notifications = comp.tick_heartbeat()
        briefing = comp.generate_morning_briefing()
        return {
            "notifications": notifications,
            "morning_briefing": briefing
        }

    return {"error": f"Unknown action '{action}'"}

if __name__ == "__main__":
    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            print(json.dumps({"error": "Empty input"}))
            sys.exit(0)
        req_data = json.loads(raw_input)
        res_data = handle_request(req_data)
        print(json.dumps(res_data))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
