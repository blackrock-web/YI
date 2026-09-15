"""
MY AI - System Configuration
Local-first, private personal AI assistant configuration.
"""
from dataclasses import dataclass, field
import os
from pathlib import Path
from typing import List, Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_DIR = DATA_DIR / "database"
LOCAL_MODELS_DIR = DATA_DIR / "local_models"
AUDIT_DIR = DATA_DIR / "audit"

@dataclass
class SafetyConfig:
    local_first_strict: bool = True
    allow_external_network: bool = False
    require_confirmation_for_actions: bool = True
    audit_logging_enabled: bool = True
    safe_file_extensions: List[str] = field(default_factory=lambda: [".txt", ".md", ".json", ".csv", ".log"])
    allowed_sandboxed_directories: List[str] = field(default_factory=lambda: [str(DATA_DIR)])

@dataclass
class PersonalityConfig:
    warmth: float = 0.8          # 0.0 - 1.0
    humor: float = 0.4           # 0.0 - 1.0
    curiosity: float = 0.7       # 0.0 - 1.0
    seriousness: float = 0.6     # 0.0 - 1.0
    formality: float = 0.4       # 0.0 - 1.0
    assertiveness: float = 0.5   # 0.0 - 1.0
    patience: float = 0.9        # 0.0 - 1.0

@dataclass
class PlannerConfig:
    work_start_hour: int = 9
    work_end_hour: int = 18
    default_break_minutes: int = 30
    default_task_duration_minutes: int = 45

@dataclass
class Config:
    app_name: str = "MY AI"
    version: str = "0.1.0"
    base_dir: Path = BASE_DIR
    data_dir: Path = DATA_DIR
    db_path: Path = DATABASE_DIR / "my_ai.db"
    models_dir: Path = LOCAL_MODELS_DIR
    audit_log_path: Path = AUDIT_DIR / "audit_log.jsonl"
    
    safety: SafetyConfig = field(default_factory=SafetyConfig)
    personality: PersonalityConfig = field(default_factory=PersonalityConfig)
    planner: PlannerConfig = field(default_factory=PlannerConfig)
    
    default_user_name: str = "User"
    default_user_id: str = "local_user_1"
    
    def ensure_directories(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)

# Global default configuration instance
config = Config()
config.ensure_directories()
