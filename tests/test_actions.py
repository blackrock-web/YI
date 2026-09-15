"""
Tests for Phase 7: Computer Actions & Safe Permissions
Verifies safety tiers, confirmation gates, sandbox protection, and tool execution.
"""
import unittest
import tempfile
import os
from pathlib import Path
from app.actions.permissions import PermissionManager, PermissionTier
from app.actions.filesystem import FilesystemAction
from app.actions.browser import BrowserAction
from app.actions.system import SystemAction

class TestComputerActions(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.sandbox_path = Path(self.temp_dir.name) / "sandbox"
        self.sandbox_path.mkdir(parents=True, exist_ok=True)
        self.perm_manager = PermissionManager()
        self.fs_action = FilesystemAction(sandbox_root=self.sandbox_path, permissions=self.perm_manager)
        self.browser_action = BrowserAction(permissions=self.perm_manager)
        self.system_action = SystemAction(permissions=self.perm_manager)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_permission_tiers(self):
        # 1. Safe Action -> allowed immediately
        allowed, req_id, _ = self.perm_manager.evaluate_action(
            "TEST_SAFE", PermissionTier.SAFE, "Read safe config", {}
        )
        self.assertTrue(allowed)
        self.assertIsNone(req_id)

        # 2. Confirmation Required -> gated without confirm
        allowed, req_id, reason = self.perm_manager.evaluate_action(
            "TEST_CONFIRM", PermissionTier.CONFIRMATION_REQUIRED, "Create folder", {}
        )
        self.assertFalse(allowed)
        self.assertIsNotNone(req_id)
        self.assertIn("Confirmation required", reason)

        # Now confirm it manually
        confirmed = self.perm_manager.confirm_action(req_id)
        self.assertTrue(confirmed)

        # 3. Restricted Action -> permanently blocked
        allowed, _, reason = self.perm_manager.evaluate_action(
            "TEST_DANGEROUS", PermissionTier.RESTRICTED, "Format disk", {}
        )
        self.assertFalse(allowed)
        self.assertIn("RESTRICTED", reason)

    def test_sandboxed_filesystem(self):
        # List files in empty sandbox
        res = self.fs_action.list_files()
        self.assertTrue(res["success"])
        self.assertEqual(len(res["items"]), 0)

        # Try to create folder without confirmation -> requires confirmation
        unconfirmed = self.fs_action.create_folder("my_documents", confirmed=False)
        self.assertTrue(unconfirmed.get("confirmation_required"))

        # Create folder with confirmation -> succeeds
        confirmed = self.fs_action.create_folder("my_documents", confirmed=True)
        self.assertTrue(confirmed["success"])
        self.assertTrue((self.sandbox_path / "my_documents").exists())

        # Path traversal attack test -> MUST raise PermissionError
        with self.assertRaises(PermissionError):
            self.fs_action.list_files("../../etc")

    def test_browser_url_validation(self):
        self.assertTrue(self.browser_action.validate_url("https://google.com"))
        self.assertTrue(self.browser_action.validate_url("http://localhost:3000"))
        self.assertFalse(self.browser_action.validate_url("file:///etc/passwd"))
        self.assertFalse(self.browser_action.validate_url("javascript:alert(1)"))

        # Launch browser without confirm
        res = self.browser_action.launch_browser("https://python.org", confirmed=False)
        self.assertTrue(res.get("confirmation_required"))

        # Launch browser with confirm
        res_ok = self.browser_action.launch_browser("https://python.org", confirmed=True)
        self.assertTrue(res_ok["success"])

    def test_system_info(self):
        res = self.system_action.get_system_info()
        self.assertTrue(res["success"])
        self.assertIn("os", res)
        self.assertIn("python_version", res)
        self.assertGreater(res["cpu_cores"], 0)

if __name__ == "__main__":
    unittest.main()
