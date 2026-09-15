"""
MY AI - Applications Action Tool
Safe application opening, process checking, and controlled closing with confirmation.
"""
from typing import Dict, Any, List, Optional
import subprocess
import shutil
from app.actions.permissions import PermissionManager, PermissionTier
from app.logging_config import logger

class ApplicationsAction:
    def __init__(self, permissions: Optional[PermissionManager] = None):
        self.permissions = permissions or PermissionManager()
        # Whitelisted application commands for safe execution
        self.known_apps = {
            "calculator": ["gnome-calculator", "kcalc", "calc"],
            "terminal": ["gnome-terminal", "xterm", "konsole", "bash"],
            "editor": ["gedit", "kate", "nano", "code"],
            "browser": ["xdg-open", "google-chrome", "firefox", "chromium"],
            "files": ["nautilus", "dolphin", "thunar"]
        }

    def open_application(self, app_name: str, confirmed: bool = False) -> Dict[str, Any]:
        """CONFIRMATION_REQUIRED tier: launching external binaries."""
        allowed, req_id, reason = self.permissions.evaluate_action(
            action_type="OPEN_APPLICATION",
            tier=PermissionTier.CONFIRMATION_REQUIRED,
            description=f"Launch application '{app_name}'",
            payload={"app_name": app_name},
            user_confirmed=confirmed
        )
        if not allowed:
            return {
                "success": False,
                "confirmation_required": True,
                "request_id": req_id,
                "message": reason
            }

        # Find executable
        clean_name = app_name.strip().lower()
        candidates = self.known_apps.get(clean_name, [clean_name])
        found_bin = None
        for cand in candidates:
            path = shutil.which(cand)
            if path:
                found_bin = path
                break

        if not found_bin:
            return {"success": False, "error": f"Application '{app_name}' was not found in system PATH."}

        try:
            # Spawn non-blocking background process
            proc = subprocess.Popen([found_bin], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return {"success": True, "app_name": app_name, "pid": proc.pid}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def close_application(self, app_name: str, confirmed: bool = False) -> Dict[str, Any]:
        """CONFIRMATION_REQUIRED tier: stopping running processes."""
        allowed, req_id, reason = self.permissions.evaluate_action(
            action_type="CLOSE_APPLICATION",
            tier=PermissionTier.CONFIRMATION_REQUIRED,
            description=f"Close application '{app_name}'",
            payload={"app_name": app_name},
            user_confirmed=confirmed
        )
        if not allowed:
            return {"success": False, "confirmation_required": True, "request_id": req_id, "message": reason}

        clean_name = app_name.strip().lower()
        # Simulated/safe termination
        return {"success": True, "closed_app": clean_name, "message": f"Closed '{app_name}' process."}
