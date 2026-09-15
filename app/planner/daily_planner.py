"""
MY AI - Deterministic Daily Planner
Algorithmic constraint satisfaction & interval scheduling engine for optimal day planning.
Zero LLM: Pure deterministic optimization.
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.planner.tasks import Task, TaskManager, TaskStatus, Priority
from app.planner.calendar import CalendarEvent, CalendarManager
from app.config import config
from app.logging_config import logger

@dataclass
class ScheduleSlot:
    start_time: str   # "HH:MM"
    end_time: str     # "HH:MM"
    title: str
    slot_type: str    # "TASK", "EVENT", "BREAK", "LUNCH"
    item_id: Optional[str] = None
    priority: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "title": self.title,
            "slot_type": self.slot_type,
            "item_id": self.item_id,
            "priority": self.priority
        }

class DailyPlanner:
    def __init__(
        self,
        task_manager: Optional[TaskManager] = None,
        calendar_manager: Optional[CalendarManager] = None
    ):
        self.task_manager = task_manager or TaskManager()
        self.calendar_manager = calendar_manager or CalendarManager()

    @staticmethod
    def _time_to_minutes(time_str: str) -> int:
        parts = time_str.split(":")
        return int(parts[0]) * 60 + int(parts[1])

    @staticmethod
    def _minutes_to_time(minutes: int) -> str:
        h = (minutes // 60) % 24
        m = minutes % 60
        return f"{h:02d}:{m:02d}"

    def plan_day(
        self,
        date_str: Optional[str] = None,
        work_start_hour: int = 9,
        work_end_hour: int = 18,
        lunch_hour: int = 13,
        lunch_duration_min: int = 60
    ) -> List[ScheduleSlot]:
        """
        Deterministic interval scheduling algorithm:
        1. Reserve immutable calendar events (meetings, fixed appointments).
        2. Reserve lunch break and rest intervals.
        3. Sort pending tasks by (Priority descending: URGENT > HIGH > MEDIUM > LOW, then shortest duration / earliest deadline).
        4. Fit tasks into available open interval slots.
        """
        target_date = date_str or datetime.now().strftime("%Y-%m-%d")
        
        # 1. Gather Calendar Events for the day
        events = self.calendar_manager.list_events_for_day(target_date)
        
        # 2. Gather Pending Tasks
        tasks = self.task_manager.list_tasks(status=TaskStatus.PENDING)
        
        # Day bounds in minutes from midnight
        start_min = work_start_hour * 60
        end_min = work_end_hour * 60
        
        # Occupied intervals: list of (start_min, end_min, ScheduleSlot)
        occupied: List[tuple] = []
        
        # Insert calendar events
        for ev in events:
            try:
                # Expecting format 'YYYY-MM-DDTHH:MM' or 'HH:MM'
                ev_start = ev.start_time.split("T")[-1][:5]
                ev_end = ev.end_time.split("T")[-1][:5]
                s_m = self._time_to_minutes(ev_start)
                e_m = self._time_to_minutes(ev_end)
                slot = ScheduleSlot(
                    start_time=ev_start,
                    end_time=ev_end,
                    title=ev.title,
                    slot_type="EVENT",
                    item_id=ev.id,
                    priority="HIGH"
                )
                occupied.append((s_m, e_m, slot))
            except Exception:
                continue

        # Insert Lunch break
        lunch_start_min = lunch_hour * 60
        lunch_end_min = lunch_start_min + lunch_duration_min
        occupied.append((
            lunch_start_min,
            lunch_end_min,
            ScheduleSlot(
                start_time=self._minutes_to_time(lunch_start_min),
                end_time=self._minutes_to_time(lunch_end_min),
                title="Lunch & Rest",
                slot_type="LUNCH"
            )
        ))

        # Sort occupied intervals by start time
        occupied.sort(key=lambda x: x[0])
        
        # Find free intervals between start_min and end_min
        free_intervals: List[tuple] = []
        curr_ptr = start_min
        for o_start, o_end, _ in occupied:
            if o_start > curr_ptr:
                free_intervals.append((curr_ptr, min(o_start, end_min)))
            curr_ptr = max(curr_ptr, o_end)
            if curr_ptr >= end_min:
                break
        if curr_ptr < end_min:
            free_intervals.append((curr_ptr, end_min))

        # 3. Sort tasks by priority and deadline
        priority_weights = {
            Priority.URGENT: 4,
            Priority.HIGH: 3,
            Priority.MEDIUM: 2,
            Priority.LOW: 1
        }
        sorted_tasks = sorted(
            tasks,
            key=lambda t: (priority_weights.get(t.priority, 2), -(t.estimated_duration_min or 45)),
            reverse=True
        )

        # 4. Greedy Packing into free intervals with 10-minute micro-breaks between tasks
        task_slots: List[tuple] = []
        remaining_tasks = list(sorted_tasks)
        
        for f_start, f_end in free_intervals:
            slot_curr = f_start
            while remaining_tasks and slot_curr < f_end:
                available_time = f_end - slot_curr
                if available_time < 20: # Less than 20 mins free: take a short breather
                    task_slots.append((
                        slot_curr,
                        f_end,
                        ScheduleSlot(
                            start_time=self._minutes_to_time(slot_curr),
                            end_time=self._minutes_to_time(f_end),
                            title="Short Break",
                            slot_type="BREAK"
                        )
                    ))
                    break
                    
                # Find task that best fits or take highest priority task
                task_to_schedule = None
                for candidate in remaining_tasks:
                    dur = candidate.estimated_duration_min or 45
                    if dur <= available_time:
                        task_to_schedule = candidate
                        break
                if not task_to_schedule:
                    task_to_schedule = remaining_tasks[0]
                    dur = min(task_to_schedule.estimated_duration_min or 45, available_time)
                else:
                    dur = task_to_schedule.estimated_duration_min or 45

                dur = min(dur, available_time)
                end_t = slot_curr + dur
                task_slots.append((
                    slot_curr,
                    end_t,
                    ScheduleSlot(
                        start_time=self._minutes_to_time(slot_curr),
                        end_time=self._minutes_to_time(end_t),
                        title=task_to_schedule.title,
                        slot_type="TASK",
                        item_id=task_to_schedule.id,
                        priority=str(task_to_schedule.priority)
                    )
                ))
                remaining_tasks.remove(task_to_schedule)
                slot_curr = end_t
                
                # Add 10-minute breather if more than 20 minutes left in this block
                if f_end - slot_curr >= 25:
                    break_end = slot_curr + 10
                    task_slots.append((
                        slot_curr,
                        break_end,
                        ScheduleSlot(
                            start_time=self._minutes_to_time(slot_curr),
                            end_time=self._minutes_to_time(break_end),
                            title="Quick Break",
                            slot_type="BREAK"
                        )
                    ))
                    slot_curr = break_end

        # Combine all slots and sort by start time
        all_schedule = [s for _, _, s in (occupied + task_slots)]
        all_schedule.sort(key=lambda s: self._time_to_minutes(s.start_time))
        return all_schedule

    def format_schedule_text(self, slots: List[ScheduleSlot]) -> str:
        lines = ["📅 Daily Schedule Plan:"]
        for s in slots:
            indicator = "📌" if s.slot_type == "TASK" else ("🗓️" if s.slot_type == "EVENT" else "☕")
            lines.append(f"{s.start_time} - {s.end_time}  {indicator} {s.title}")
        return "\n".join(lines)
