"""
MY AI - Personal User Profile Model
Local-first, privacy-respecting user profile tracking explicitly stated facts, preferences, routines, goals, and important people.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import json
import uuid
from app.memory.database import DatabaseManager
from app.config import config
from app.logging_config import logger

@dataclass
class Routine:
    name: str
    time_of_day: str  # e.g. "08:00"
    frequency: str    # "daily", "weekdays", "weekends"
    description: str = ""

@dataclass
class Goal:
    id: str
    title: str
    target_date: Optional[str] = None
    category: str = "personal"
    status: str = "active"  # "active", "completed", "paused"

@dataclass
class ImportantPerson:
    id: str
    name: str
    relationship: str  # "friend", "colleague", "family", "manager"
    nickname: Optional[str] = None
    notes: Optional[str] = None

class UserProfileManager:
    def __init__(self, db: Optional[DatabaseManager] = None, user_id: Optional[str] = None):
        self.db = db or DatabaseManager.get_instance()
        self.user_id = user_id or config.default_user_id
        self._ensure_user()

    def _ensure_user(self) -> None:
        with self.db.transaction() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO users (id, name) VALUES (?, ?)",
                (self.user_id, config.default_user_name)
            )

    # 1. Preferences
    def set_preference(self, category: str, key: str, value: str) -> None:
        clean_key = key.strip().lower().replace(" ", "_")
        pref_id = str(uuid.uuid4())
        with self.db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO preferences (id, user_id, category, key, value)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(user_id, category, key) DO UPDATE SET value = excluded.value, updated_at = CURRENT_TIMESTAMP
                """,
                (pref_id, self.user_id, category.lower(), clean_key, value.strip())
            )

    def get_preferences(self, category: Optional[str] = None) -> Dict[str, str]:
        if category:
            rows = self.db.fetchall(
                "SELECT key, value FROM preferences WHERE user_id = ? AND category = ?",
                (self.user_id, category.lower())
            )
        else:
            rows = self.db.fetchall(
                "SELECT key, value FROM preferences WHERE user_id = ?",
                (self.user_id,)
            )
        return {r["key"]: r["value"] for r in rows}

    # 2. Routines (Stored in memories table with type='routine')
    def add_routine(self, name: str, time_of_day: str, frequency: str = "daily", description: str = "") -> str:
        routine_data = json.dumps({
            "name": name,
            "time_of_day": time_of_day,
            "frequency": frequency,
            "description": description
        })
        mem_id = str(uuid.uuid4())
        with self.db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO memories (id, user_id, memory_type, key, value, importance, source)
                VALUES (?, ?, 'routine', ?, ?, 7, 'user_statement')
                """,
                (mem_id, self.user_id, name.lower(), routine_data)
            )
        return mem_id

    def list_routines(self) -> List[Dict[str, Any]]:
        rows = self.db.fetchall(
            "SELECT id, key, value FROM memories WHERE user_id = ? AND memory_type = 'routine'",
            (self.user_id,)
        )
        routines = []
        for r in rows:
            try:
                data = json.loads(r["value"])
                data["id"] = r["id"]
                routines.append(data)
            except Exception:
                routines.append({"id": r["id"], "name": r["key"], "description": r["value"]})
        return routines

    # 3. Goals (Stored in memories table with type='goal')
    def add_goal(self, title: str, category: str = "personal", target_date: Optional[str] = None) -> str:
        goal_id = str(uuid.uuid4())
        goal_data = json.dumps({
            "id": goal_id,
            "title": title,
            "category": category,
            "target_date": target_date,
            "status": "active"
        })
        with self.db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO memories (id, user_id, memory_type, key, value, importance, source)
                VALUES (?, ?, 'goal', ?, ?, 8, 'user_statement')
                """,
                (goal_id, self.user_id, title.lower(), goal_data)
            )
        return goal_id

    def list_goals(self) -> List[Dict[str, Any]]:
        rows = self.db.fetchall(
            "SELECT id, key, value FROM memories WHERE user_id = ? AND memory_type = 'goal'",
            (self.user_id,)
        )
        goals = []
        for r in rows:
            try:
                data = json.loads(r["value"])
                goals.append(data)
            except Exception:
                goals.append({"id": r["id"], "title": r["key"]})
        return goals

    # 4. Important People (Stored in people table)
    def add_person(self, name: str, relationship: str, nickname: Optional[str] = None, notes: Optional[str] = None) -> str:
        person_id = str(uuid.uuid4())
        with self.db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO people (id, user_id, name, relationship, nickname, notes, last_mentioned)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (person_id, self.user_id, name.strip(), relationship.strip(), nickname, notes)
            )
        return person_id

    def find_person(self, query: str) -> Optional[Dict[str, Any]]:
        q = query.strip().lower()
        row = self.db.fetchone(
            "SELECT * FROM people WHERE user_id = ? AND (LOWER(name) = ? OR LOWER(nickname) = ?)",
            (self.user_id, q, q)
        )
        return dict(row) if row else None

    def list_people(self) -> List[Dict[str, Any]]:
        rows = self.db.fetchall(
            "SELECT * FROM people WHERE user_id = ? ORDER BY last_mentioned DESC",
            (self.user_id,)
        )
        return [dict(r) for r in rows]

    # 5. Full Profile Overview
    def get_full_profile(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "preferences": self.get_preferences(),
            "routines": self.list_routines(),
            "goals": self.list_goals(),
            "people": self.list_people(),
        }
