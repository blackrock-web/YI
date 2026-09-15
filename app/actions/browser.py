"""
MY AI - Safe Browser Action Tool
Validates URLs to ensure safe schemes (http, https) and prevents file://, javascript:, or shell injection.
"""
from typing import Dict, Any, Optional
from urllib.parse import urlparse
from app.actions.permissions import PermissionManager, PermissionTier

class BrowserAction:
    def __init__(self, permissions: Optional[PermissionManager] = None):
        self.permissions = permissions or PermissionManager()

    def validate_url(self, url: str) -> bool:
        try:
            parsed = urlparse(url)
            return parsed.scheme in ("http", "https") and bool(parsed.netloc)
        except Exception:
            return False

    def launch_browser(self, url: str, confirmed: bool = False) -> Dict[str, Any]:
        """CONFIRMATION_REQUIRED tier: external network navigation."""
        if not self.validate_url(url):
            return {
                "success": False,
                "error": f"Invalid or unsafe URL scheme: '{url}'. Only http/https are allowed."
            }

        allowed, req_id, reason = self.permissions.evaluate_action(
            action_type="LAUNCH_BROWSER",
            tier=PermissionTier.CONFIRMATION_REQUIRED,
            description=f"Open web browser to '{url}'",
            payload={"url": url},
            user_confirmed=confirmed
        )
        if not allowed:
            return {
                "success": False,
                "confirmation_required": True,
                "request_id": req_id,
                "message": reason
            }

        return {
            "success": True,
            "url": url,
            "message": f"Browser launched for '{url}'"
        }
