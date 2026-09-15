"""
MY AI - Safe Action Permission System
Enforces safety tiers (SAFE, CONFIRMATION_REQUIRED, RESTRICTED) and audit logging.
"""
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Callable, Tuple
import json
import uuid
from datetime import datetime
from app.config import config
from app.logging_config import logger

class PermissionTier(str, Enum):
    SAFE = "SAFE"                                   # Read-only or completely safe local inspection
    CONFIRMATION_REQUIRED = "CONFIRMATION_REQUIRED" # State modifications or external app launching
    RESTRICTED = "RESTRICTED"                       # Dangerous operations (deletions, arbitrary root shell)

@dataclass
class ActionRequest:
    id: str
    action_type: str
    tier: PermissionTier
    description: str
    payload: Dict[str, Any]
    approved: bool = False
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

class PermissionManager:
    def __init__(self, auto_approve_safe: bool = True):
        self.auto_approve_safe = auto_approve_safe
        self.pending_confirmations: Dict[str, ActionRequest] = {}
        self.audit_log_path = config.audit_log_path
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)

    def log_audit(self, action_type: str, tier: PermissionTier, status: str, details: Dict[str, Any]) -> None:
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action_type": action_type,
            "tier": tier.value,
            "status": status,
            "details": details
        }
        try:
            with open(self.audit_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.error(f"Failed writing audit log: {e}")

    def evaluate_action(
        self,
        action_type: str,
        tier: PermissionTier,
        description: str,
        payload: Dict[str, Any],
        user_confirmed: bool = False
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Returns (is_allowed, request_id, rejection_or_prompt_reason)
        """
        req_id = str(uuid.uuid4())
        
        # 1. RESTRICTED actions are blocked or strictly gated
        if tier == PermissionTier.RESTRICTED:
            self.log_audit(action_type, tier, "BLOCKED_RESTRICTED", payload)
            return False, None, f"Action '{action_type}' is RESTRICTED for user privacy and security."

        # 2. SAFE actions
        if tier == PermissionTier.SAFE:
            self.log_audit(action_type, tier, "AUTO_ALLOWED", payload)
            return True, None, None

        # 3. CONFIRMATION_REQUIRED
        if user_confirmed:
            self.log_audit(action_type, tier, "USER_CONFIRMED", payload)
            return True, None, None
            
        # Store pending confirmation
        req = ActionRequest(
            id=req_id,
            action_type=action_type,
            tier=tier,
            description=description,
            payload=payload,
            approved=False
        )
        self.pending_confirmations[req_id] = req
        self.log_audit(action_type, tier, "AWAITING_CONFIRMATION", payload)
        prompt_msg = f"Confirmation required: Do you want to allow '{description}'? (Reference ID: {req_id[:8]})"
        return False, req_id, prompt_msg

    def confirm_action(self, req_id: str) -> bool:
        if req_id in self.pending_confirmations:
            req = self.pending_confirmations.pop(req_id)
            req.approved = True
            self.log_audit(req.action_type, req.tier, "CONFIRMED_MANUALLY", req.payload)
            return True
        return False
