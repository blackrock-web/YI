"""
Tests for Phase 4: Personal Profile
Verifies user profile modeling: preferences, routines, goals, and important people.
"""
import unittest
import tempfile
from pathlib import Path
from app.memory.database import DatabaseManager
from app.memory.profile import UserProfileManager

class TestPersonalProfile(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_profile.db"
        self.db = DatabaseManager(self.db_path)
        self.profile = UserProfileManager(self.db, user_id="test_profile_user")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_preferences(self):
        self.profile.set_preference("editor", "theme", "dark")
        self.profile.set_preference("food", "favorite_drink", "green tea")
        
        prefs = self.profile.get_preferences()
        self.assertEqual(prefs.get("theme"), "dark")
        self.assertEqual(prefs.get("favorite_drink"), "green tea")

    def test_routines(self):
        self.profile.add_routine("Morning Run", "07:00", "daily", "30 minutes around park")
        routines = self.profile.list_routines()
        self.assertEqual(len(routines), 1)
        self.assertEqual(routines[0]["name"], "Morning Run")
        self.assertEqual(routines[0]["time_of_day"], "07:00")

    def test_goals(self):
        self.profile.add_goal("Build MY AI", category="work", target_date="2026-12-31")
        goals = self.profile.list_goals()
        self.assertEqual(len(goals), 1)
        self.assertEqual(goals[0]["title"], "Build MY AI")

    def test_important_people(self):
        self.profile.add_person("Rahul", "friend", nickname="Rah", notes="Likes chess")
        person = self.profile.find_person("Rahul")
        self.assertIsNotNone(person)
        self.assertEqual(person["relationship"], "friend")
        self.assertEqual(person["nickname"], "Rah")

    def test_full_profile(self):
        self.profile.set_preference("general", "timezone", "UTC")
        full = self.profile.get_full_profile()
        self.assertIn("preferences", full)
        self.assertIn("routines", full)
        self.assertIn("goals", full)
        self.assertIn("people", full)

if __name__ == "__main__":
    unittest.main()
