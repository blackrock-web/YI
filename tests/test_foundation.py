"""
Tests for Phase 1: Foundation
Verifies configuration, directories, logging, and CLI interfaces.
"""
import unittest
import sys
from pathlib import Path
from app.config import Config, SafetyConfig, PersonalityConfig
from app.logging_config import setup_logger
from app.main import main

class TestFoundation(unittest.TestCase):
    def test_config_initialization(self):
        cfg = Config()
        self.assertEqual(cfg.app_name, "MY AI")
        self.assertEqual(cfg.version, "0.1.0")
        self.assertTrue(cfg.safety.local_first_strict)
        self.assertFalse(cfg.safety.allow_external_network)
        self.assertTrue(cfg.safety.require_confirmation_for_actions)

    def test_directory_creation(self):
        cfg = Config()
        cfg.ensure_directories()
        self.assertTrue(cfg.data_dir.exists())
        self.assertTrue(cfg.db_path.parent.exists())
        self.assertTrue(cfg.models_dir.exists())
        self.assertTrue(cfg.audit_log_path.parent.exists())

    def test_logging(self):
        log = setup_logger("test_logger")
        self.assertIsNotNone(log)
        self.assertTrue(hasattr(log, "info"))
        self.assertTrue(hasattr(log, "error"))

    def test_cli_status(self):
        exit_code = main(["--status"])
        self.assertEqual(exit_code, 0)

if __name__ == "__main__":
    unittest.main()
