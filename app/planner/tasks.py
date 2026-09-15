"""
MY AI - Task Management System
Handles structured tasks: creation, editing, status, priority, deadlines, duration, and categories.
"""
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from app.memory.database import DatabaseManager
from app.config import config
from app.logging_config import logger

class Priority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

@dataclass
class Task:
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    priority: Priority = Priority.MEDIUM
    category: str = "general"
    deadline: Optional[str] = None
    estimated_duration_min: int = 45
    status: TaskStatus = TaskStatus.PENDING
    is_recurring: bool = False
    recurrence_rule: Optional[str] = None
    completed_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "priority": str(self.priority),
            "category": self.category,
            "deadline": self.deadline,
            "estimated_duration_min": self.estimated_duration_min,
            "status": str(self.status),
            "is_recurring": self.is_recurring,
            "recurrence_rule": self.recurrence_rule,
            "completed_at": self.completed_at,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

class TaskManager:
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

    def create_task(
        self,
        title: str,
        description: Optional[str] = None,
        priority: Priority = Priority.MEDIUM,
        category: str = "general",
        deadline: Optional[str] = None,
        estimated_duration_min: int = 45,
        is_recurring: bool = False,
        recurrence_rule: Optional[str] = None
    ) -> Task:
        task_id = str(uuid.uuid4())
        priority_str = priority.value if isinstance(priority, Priority) else str(priority).upper()
        
        with self.db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO tasks (
                    id, user_id, title, description, priority, category,
                    deadline, estimated_duration_min, status, is_recurring, recurrence_rule
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'PENDING', ?, ?)
                """,
                (
                    task_id, self.user_id, title.strip(), description, priority_str,
                    category.lower(), deadline, estimated_duration_min, 1 if is_recurring else 0,
                    recurrence_rule
                )
            )
        return self.get_task(task_id) # type: ignore

    def get_task(self, task_id_or_title: str) -> Optional[Task]:
        row = self.db.fetchone(
            "SELECT * FROM tasks WHERE user_id = ? AND (id = ? OR LOWER(title) = ?)",
            (self.user_id, task_id_or_title, task_id_or_title.strip().lower())
        )
        if not row:
            return None
        return Task(
            id=row["id"],
            user_id=row["user_id"],
            title=row["title"],
            description=row["description"],
            priority=Priority(row["priority"]),
            category=row["category"],
            deadline=row["deadline"],
            estimated_duration_min=row["estimated_duration_min"],
            status=TaskStatus(row["status"]),
            is_recurring=bool(row["is_recurring"]),
            recurrence_rule=row["recurrence_rule"],
            completed_at=row["completed_at"],
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )

    def edit_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[Priority] = None,
        category: Optional[str] = None,
        deadline: Optional[str] = None,
        estimated_duration_min: Optional[int] = None
    ) -> Optional[Task]:
        task = self.get_task(task_id)
        if not task:
            return None
            
        new_title = title if title is not None else task.title
        new_desc = description if description is not None else task.description
        new_pri = (priority.value if isinstance(priority, Priority) else priority) if priority is not None else task.priority.value
        new_cat = category.lower() if category is not None else task.category
        new_dead = deadline if deadline is not None else task.deadline
        new_dur = estimated_duration_min if estimated_duration_min is not None else task.estimated_duration_min

        with self.db.transaction() as conn:
            conn.execute(
                """
                UPDATE tasks
                SET title = ?, description = ?, priority = ?, category = ?, deadline = ?,
                    estimated_duration_min = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND user_id = ?
                """,
                (new_title, new_desc, new_pri, new_cat, new_dead, new_dur, task.id, self.user_id)
            )
        return self.get_task(task.id)

    def complete_task(self, task_id_or_title: str) -> Optional[Task]:
        task = self.get_task(task_id_or_title)
        if not task:
            return None
        with self.db.transaction() as conn:
            conn.execute(
                """
                UPDATE tasks
                SET status = 'COMPLETED', completed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND user_id = ?
                """,
                (task.id, self.user_id)
            )
        return self.get_task(task.id)

    def delete_task(self, task_id_or_title: str) -> bool:
        task = self.get_task(task_id_or_title)
        if not task:
            return False
        with self.db.transaction() as conn:
            cur = conn.execute(
                "DELETE FROM tasks WHERE id = ? AND user_id = ?",
                (task.id, self.user_id)
            )
            return cur.rowcount > 0

    def list_tasks(self, status: Optional[TaskStatus] = None, category: Optional[str] = None) -> List[Task]:
        query = "SELECT * FROM tasks WHERE user_id = ?"
        params: List[Any] = [self.user_id]
        
        if status:
            query += " AND status = ?"
            params.append(status.value)
        if category:
            query += " AND category = ?"
            params.append(category.lower())
            
        query += " ORDER BY CASE priority WHEN 'URGENT' THEN 1 WHEN 'HIGH' THEN 2 WHEN 'MEDIUM' THEN 3 ELSE 4 END, deadline ASC"
        
        rows = self.db.fetchall(query, tuple(params))
        tasks: List[Task] = []
        for row in rows:
            tasks.append(Task(
                id=row["id"],
                user_id=row["user_id"],
                title=row["title"],
                description=row["description"],
                priority=Priority(row["priority"]),
                category=row["category"],
                deadline=row["deadline"],
                estimated_duration_min=row["estimated_duration_min"],
                status=TaskStatus(row["status"]),
                is_recurring=bool(row["is_recurring"]),
                recurrence_rule=row["recurrence_rule"],
                completed_at=row["completed_at"],
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            ))
        return tasks
