"""
MY AI - Calendar Subsystem
Local-first calendar events, scheduling constraints, and time block management.
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid
from app.memory.database import DatabaseManager
from app.config import config

@dataclass
class CalendarEvent:
    id: str
    user_id: str
    title: str
    start_time: str
    end_time: str
    description: Optional[str] = None
    location: Optional[str] = None
    is_recurring: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "description": self.description,
            "location": self.location,
            "is_recurring": self.is_recurring
        }

class CalendarManager:
    def __init__(self, db: Optional[DatabaseManager] = None, user_id: Optional[str] = None):
        self.db = db or DatabaseManager.get_instance()
        self.user_id = user_id or config.default_user_id

    def create_event(
        self,
        title: str,
        start_time: str,
        end_time: str,
        description: Optional[str] = None,
        location: Optional[str] = None
    ) -> CalendarEvent:
        event_id = str(uuid.uuid4())
        with self.db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO events (id, user_id, title, start_time, end_time, description, location)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (event_id, self.user_id, title.strip(), start_time, end_time, description, location)
            )
        return CalendarEvent(
            id=event_id,
            user_id=self.user_id,
            title=title.strip(),
            start_time=start_time,
            end_time=end_time,
            description=description,
            location=location
        )

    def list_events_for_day(self, day_date: str) -> List[CalendarEvent]:
        # day_date format: YYYY-MM-DD
        rows = self.db.fetchall(
            """
            SELECT * FROM events 
            WHERE user_id = ? AND start_time LIKE ? 
            ORDER BY start_time ASC
            """,
            (self.user_id, f"{day_date}%")
        )
        return [
            CalendarEvent(
                id=r["id"],
                user_id=r["user_id"],
                title=r["title"],
                start_time=r["start_time"],
                end_time=r["end_time"],
                description=r["description"],
                location=r["location"],
                is_recurring=bool(r["is_recurring"])
            )
            for r in rows
        ]

    def delete_event(self, event_id: str) -> bool:
        with self.db.transaction() as conn:
            cur = conn.execute("DELETE FROM events WHERE id = ? AND user_id = ?", (event_id, self.user_id))
            return cur.rowcount > 0
