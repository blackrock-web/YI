"""
MY AI - Safe System Inspection Action Tool
Provides read-only local telemetry (CPU cores, OS, Python version, platform architecture).
Tier: SAFE
"""
import platform
import os
import sys
from typing import Dict, Any, Optional
from app.actions.permissions import PermissionManager, PermissionTier

class SystemAction:
    def __init__(self, permissions: Optional[PermissionManager] = None):
        self.permissions = permissions or PermissionManager()

    def get_system_info(self) -> Dict[str, Any]:
        """SAFE tier: basic non-sensitive environment telemetry."""
        allowed, _, err = self.permissions.evaluate_action(
            action_type="GET_SYSTEM_INFO",
            tier=PermissionTier.SAFE,
            description="Inspect system specs",
            payload={}
        )
        if not allowed:
            return {"success": False, "error": err}

        return {
            "success": True,
            "os": platform.system(),
            "os_release": platform.release(),
            "machine": platform.machine(),
            "python_version": sys.version.split()[0],
            "cpu_cores": os.cpu_count()
        }
