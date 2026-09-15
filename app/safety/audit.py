"""
MY AI - Immutable Local Security Audit Logger
Maintains append-only audit trails of all security events, permission checks, and privacy verifications.
"""
from typing import Dict, Any, Optional
import json
from datetime import datetime
from app.config import config

class SecurityAuditLogger:
    def __init__(self, log_path=None):
        self.log_path = log_path or config.audit_log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log_event(self, event_type: str, severity: str, details: Dict[str, Any]) -> None:
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "severity": severity,
            "details": details
        }
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    def read_recent_events(self, limit: int = 50):
        if not self.log_path.exists():
            return []
        events = []
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        events.append(json.loads(line))
                    except Exception:
                        continue
        return events[-limit:]
