"""
MY AI - Safe Filesystem Tool
Sandboxed filesystem operations with path traversal protection and safety tiers.
"""
from pathlib import Path
from typing import List, Dict, Any, Optional
import os
import shutil
from app.actions.permissions import PermissionManager, PermissionTier
from app.config import config
from app.logging_config import logger

class FilesystemAction:
    def __init__(self, sandbox_root: Optional[Path] = None, permissions: Optional[PermissionManager] = None):
        self.sandbox_root = sandbox_root or config.data_dir
        self.sandbox_root.mkdir(parents=True, exist_ok=True)
        self.permissions = permissions or PermissionManager()

    def _resolve_safe_path(self, relative_path: str) -> Path:
        """Enforces sandboxing: prevents path traversal (../) outside sandbox_root."""
        clean_rel = relative_path.lstrip("/\\")
        target = (self.sandbox_root / clean_rel).resolve()
        sandbox_resolved = self.sandbox_root.resolve()
        
        # Verify target is inside sandbox_root
        if not str(target).startswith(str(sandbox_resolved)):
            raise PermissionError(f"Access denied: path '{relative_path}' attempts to escape sandbox.")
        return target

    def list_files(self, subfolder: str = "") -> Dict[str, Any]:
        """SAFE tier: list files inside sandboxed folder."""
        allowed, _, err = self.permissions.evaluate_action(
            action_type="LIST_FILES",
            tier=PermissionTier.SAFE,
            description=f"List files in {subfolder or 'root'}",
            payload={"subfolder": subfolder}
        )
        if not allowed:
            return {"success": False, "error": err}
            
        target = self._resolve_safe_path(subfolder)
        if not target.exists():
            return {"success": False, "error": f"Folder '{subfolder}' does not exist"}
            
        items = []
        for entry in target.iterdir():
            items.append({
                "name": entry.name,
                "is_dir": entry.is_dir(),
                "size_bytes": entry.stat().st_size if entry.is_file() else 0
            })
        return {"success": True, "path": str(target), "items": items}

    def search_files(self, query: str, subfolder: str = "") -> Dict[str, Any]:
        """SAFE tier: search file names matching query."""
        target = self._resolve_safe_path(subfolder)
        if not target.exists():
            return {"success": False, "error": "Search root does not exist"}
            
        matches = []
        for root, dirs, files in os.walk(str(target)):
            for f in files:
                if query.lower() in f.lower():
                    matches.append(str(Path(root, f).relative_to(self.sandbox_root)))
                    
        return {"success": True, "query": query, "matches": matches}

    def create_folder(self, folder_path: str, confirmed: bool = False) -> Dict[str, Any]:
        """CONFIRMATION_REQUIRED tier: modifying filesystem."""
        allowed, req_id, reason = self.permissions.evaluate_action(
            action_type="CREATE_FOLDER",
            tier=PermissionTier.CONFIRMATION_REQUIRED,
            description=f"Create folder '{folder_path}'",
            payload={"folder_path": folder_path},
            user_confirmed=confirmed
        )
        if not allowed:
            return {"success": False, "confirmation_required": True, "request_id": req_id, "message": reason}

        target = self._resolve_safe_path(folder_path)
        target.mkdir(parents=True, exist_ok=True)
        return {"success": True, "created_path": str(target)}
