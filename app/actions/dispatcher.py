"""
MY AI - Tool Dispatcher & Execution Pipeline
Routes intent-driven tool invocations to safe local actuators with parameter validation and permission gates.
"""
from typing import Dict, Any, Optional
from app.actions.permissions import PermissionManager, PermissionTier
from app.actions.filesystem import FilesystemAction
from app.actions.applications import ApplicationsAction
from app.actions.browser import BrowserAction
from app.actions.system import SystemAction
from app.planner.tasks import TaskManager, Priority
from app.planner.calendar import CalendarManager
from app.planner.reminders import ReminderManager
from app.planner.daily_planner import DailyPlanner

class ToolDispatcher:
    def __init__(
        self,
        permissions: Optional[PermissionManager] = None,
        task_manager: Optional[TaskManager] = None,
        calendar_manager: Optional[CalendarManager] = None,
        reminder_manager: Optional[ReminderManager] = None
    ):
        self.permissions = permissions or PermissionManager()
        self.fs = FilesystemAction(permissions=self.permissions)
        self.apps = ApplicationsAction(permissions=self.permissions)
        self.browser = BrowserAction(permissions=self.permissions)
        self.system = SystemAction(permissions=self.permissions)
        self.tasks = task_manager or TaskManager()
        self.calendar = calendar_manager or CalendarManager()
        self.reminders = reminder_manager or ReminderManager()
        self.planner = DailyPlanner(self.tasks, self.calendar)

    def dispatch(self, tool_name: str, arguments: Dict[str, Any], confirmed: bool = False) -> Dict[str, Any]:
        """Executes tool by name with safety checks."""
        t_name = tool_name.lower().strip()

        if t_name == "create_task":
            title = arguments.get("title", "Untitled Task")
            pri_str = arguments.get("priority", "MEDIUM")
            try:
                pri = Priority(pri_str.upper())
            except Exception:
                pri = Priority.MEDIUM
            task = self.tasks.create_task(title=title, priority=pri)
            return {"success": True, "task": task.to_dict()}

        elif t_name == "list_tasks":
            tasks = self.tasks.list_tasks()
            return {"success": True, "tasks": [t.to_dict() for t in tasks]}

        elif t_name == "plan_day":
            date_str = arguments.get("date")
            schedule = self.planner.plan_day(date_str)
            return {"success": True, "schedule": [s.to_dict() for s in schedule]}

        elif t_name == "list_files":
            subfolder = arguments.get("subfolder", "")
            return self.fs.list_files(subfolder)

        elif t_name == "create_folder":
            folder_path = arguments.get("folder_path", "")
            return self.fs.create_folder(folder_path, confirmed=confirmed)

        elif t_name == "open_application":
            app_name = arguments.get("app_name", "")
            return self.apps.open_application(app_name, confirmed=confirmed)

        elif t_name == "launch_browser":
            url = arguments.get("url", "")
            return self.browser.launch_browser(url, confirmed=confirmed)

        elif t_name == "get_system_info":
            return self.system.get_system_info()

        return {"success": False, "error": f"Unknown tool: '{tool_name}'"}
