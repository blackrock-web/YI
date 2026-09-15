"""
MY AI - Reminder Management Subsystem
Handles time-based reminders, triggering checks, and notifications.
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from app.memory.database import DatabaseManager
from app.config import config

@dataclass
class Reminder:
    id: str
    user_id: str
    message: str
    remind_at: str
    task_id: Optional[str] = None
    is_triggered: bool = False
    created_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "message": self.message,
            "remind_at": self.remind_at,
            "task_id": self.task_id,
            "is_triggered": self.is_triggered,
            "created_at": self.created_at
        }

class ReminderManager:
    def __init__(self, db: Optional[DatabaseManager] = None, user_id: Optional[str] = None):
        self.db = db or DatabaseManager.get_instance()
        self.user_id = user_id or config.default_user_id

    def create_reminder(self, message: str, remind_at: str, task_id: Optional[str] = None) -> Reminder:
        rem_id = str(uuid.uuid4())
        with self.db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO reminders (id, user_id, task_id, message, remind_at, is_triggered)
                VALUES (?, ?, ?, ?, ?, 0)
                """,
                (rem_id, self.user_id, task_id, message.strip(), remind_at)
            )
        return Reminder(
            id=rem_id,
            user_id=self.user_id,
            message=message.strip(),
            remind_at=remind_at,
            task_id=task_id,
            is_triggered=False
        )

    def list_active_reminders(self) -> List[Reminder]:
        rows = self.db.fetchall(
            """
            SELECT * FROM reminders 
            WHERE user_id = ? AND is_triggered = 0
            ORDER BY remind_at ASC
            """,
            (self.user_id,)
        )
        return [
            Reminder(
                id=r["id"],
                user_id=r["user_id"],
                message=r["message"],
                remind_at=r["remind_at"],
                task_id=r["task_id"],
                is_triggered=bool(r["is_triggered"]),
                created_at=r["created_at"]
            )
            for r in rows
        ]

    def dismiss_reminder(self, reminder_id: str) -> bool:
        with self.db.transaction() as conn:
            cur = conn.execute(
                "UPDATE reminders SET is_triggered = 1 WHERE id = ? AND user_id = ?",
                (reminder_id, self.user_id)
            )
            return cur.rowcount > 0

    def delete_reminder(self, reminder_id: str) -> bool:
        with self.db.transaction() as conn:
            cur = conn.execute("DELETE FROM reminders WHERE id = ? AND user_id = ?", (reminder_id, self.user_id))
            return cur.rowcount > 0
