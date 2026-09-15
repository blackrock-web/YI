"""
MY AI - Long-Term Autonomous Companion Heartbeat
Runs proactive background monitoring:
- Checks upcoming reminders and triggers alert notifications
- Identifies approaching task deadlines
- Generates proactive morning greetings / daily schedule briefings
- Compassionate check-in following stressful episodes
Zero cloud dependencies.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.planner.reminders import ReminderManager
from app.planner.tasks import TaskManager, TaskStatus, Priority
from app.planner.daily_planner import DailyPlanner
from app.personality.personality import PersonalityEngine
from app.personality.relationship import RelationshipManager
from app.logging_config import logger

class AutonomousCompanion:
    def __init__(
        self,
        reminder_manager: Optional[ReminderManager] = None,
        task_manager: Optional[TaskManager] = None,
        relationship_manager: Optional[RelationshipManager] = None
    ):
        self.reminders = reminder_manager or ReminderManager()
        self.tasks = task_manager or TaskManager()
        self.relationship = relationship_manager or RelationshipManager()
        self.personality = PersonalityEngine()

    def tick_heartbeat(self) -> List[Dict[str, Any]]:
        """
        Executes an autonomous heartbeat check. Returns proactive notification messages.
        """
        notifications: List[Dict[str, Any]] = []

        # 1. Trigger pending reminders
        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        active_rems = self.reminders.list_active_reminders()
        for rem in active_rems:
            if rem.remind_at <= now_str:
                self.reminders.dismiss_reminder(rem.id)
                notifications.append({
                    "type": "REMINDER",
                    "title": "Reminder Alert",
                    "message": rem.message,
                    "timestamp": now_str
                })

        # 2. Check urgent pending tasks
        urgent_tasks = self.tasks.list_tasks(status=TaskStatus.PENDING)
        for t in urgent_tasks:
            if t.priority == Priority.URGENT:
                notifications.append({
                    "type": "URGENT_TASK",
                    "title": "Priority Task Focus",
                    "message": f"Remember your urgent task: '{t.title}'",
                    "task_id": t.id
                })
                break # Only alert highest urgent task per tick

        return notifications

    def generate_morning_briefing(self) -> str:
        """Constructs a supportive morning greeting and agenda briefing."""
        state = self.relationship.get_relationship_state()
        greeting = "Good morning!"
        if state.level.value in ("COMPANION", "CLOSE_CONFIDANT"):
            greeting = "Good morning! Ready for a productive and balanced day together?"

        pending = self.tasks.list_tasks(status=TaskStatus.PENDING)
        task_summary = f"You have {len(pending)} pending tasks on your agenda."
        return f"{greeting} {task_summary}"
