"""
Tests for Phase 5 (Tasks) & Phase 6 (Planner)
Verifies task creation, completion, priorities, and deterministic daily scheduling engine.
"""
import unittest
import tempfile
from pathlib import Path
from app.memory.database import DatabaseManager
from app.planner.tasks import TaskManager, Priority, TaskStatus
from app.planner.calendar import CalendarManager
from app.planner.reminders import ReminderManager
from app.planner.daily_planner import DailyPlanner

class TestTaskAndPlanner(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_planner.db"
        self.db = DatabaseManager(self.db_path)
        self.task_manager = TaskManager(self.db, user_id="test_plan_user")
        self.calendar_manager = CalendarManager(self.db, user_id="test_plan_user")
        self.reminder_manager = ReminderManager(self.db, user_id="test_plan_user")
        self.planner = DailyPlanner(self.task_manager, self.calendar_manager)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_task_lifecycle(self):
        # Create task
        task = self.task_manager.create_task(
            title="Study Python for MY AI",
            priority=Priority.HIGH,
            category="learning",
            estimated_duration_min=60
        )
        self.assertIsNotNone(task.id)
        self.assertEqual(task.status, TaskStatus.PENDING)
        self.assertEqual(task.priority, Priority.HIGH)

        # Edit task
        updated = self.task_manager.edit_task(task.id, priority=Priority.URGENT)
        self.assertEqual(updated.priority, Priority.URGENT)

        # Complete task
        completed = self.task_manager.complete_task(task.id)
        self.assertEqual(completed.status, TaskStatus.COMPLETED)
        self.assertIsNotNone(completed.completed_at)

    def test_reminders(self):
        rem = self.reminder_manager.create_reminder("Check morning schedule", "2026-09-15 08:30:00")
        active = self.reminder_manager.list_active_reminders()
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0].message, "Check morning schedule")

        self.reminder_manager.dismiss_reminder(rem.id)
        active_after = self.reminder_manager.list_active_reminders()
        self.assertEqual(len(active_after), 0)

    def test_deterministic_daily_planner(self):
        # Create tasks
        self.task_manager.create_task(title="Project Architecture", priority=Priority.URGENT, estimated_duration_min=90)
        self.task_manager.create_task(title="Python Code Review", priority=Priority.HIGH, estimated_duration_min=60)
        self.task_manager.create_task(title="Gym Workout", priority=Priority.MEDIUM, estimated_duration_min=45)

        # Create calendar meeting at 15:00 - 16:00
        self.calendar_manager.create_event(
            title="Team Sync Meeting",
            start_time="2026-09-15T15:00",
            end_time="2026-09-15T16:00"
        )

        schedule = self.planner.plan_day("2026-09-15")
        self.assertGreater(len(schedule), 3)

        # Verify slots exist and are ordered
        times = [s.start_time for s in schedule]
        self.assertEqual(times, sorted(times))

        # Verify Lunch is included
        titles = [s.title for s in schedule]
        self.assertTrue(any("Lunch" in t for t in titles))
        self.assertTrue(any("Team Sync Meeting" in t for t in titles))
        self.assertTrue(any("Project Architecture" in t for t in titles))

if __name__ == "__main__":
    unittest.main()
