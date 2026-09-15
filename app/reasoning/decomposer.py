"""
MY AI - Task & Goal Decomposer
Deterministic hierarchical task decomposition: decomposes high-level goals into actionable,
sequential subtasks with estimated durations and dependencies.
Zero LLM required: uses structured domain templates and rule-based decomposition trees.
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class SubTaskPlan:
    step_number: int
    title: str
    description: str
    estimated_duration_min: int
    category: str

class TaskDecomposer:
    # Domain-specific decomposition heuristics
    DECOMPOSITION_RECIPES = {
        "learn": [
            ("Research core concepts and documentation", 45, "learning"),
            ("Set up development / practice environment", 30, "setup"),
            ("Build a hands-on hello-world prototype", 60, "practice"),
            ("Complete practice exercises and self-review", 45, "review")
        ],
        "build": [
            ("Define architecture specifications and constraints", 60, "planning"),
            ("Implement core modules and state management", 120, "development"),
            ("Write automated unit and integration tests", 60, "testing"),
            ("Document features and verify stability", 30, "documentation")
        ],
        "trip": [
            ("Book transport and accommodations", 45, "travel"),
            ("Create daily itinerary and map points of interest", 60, "planning"),
            ("Pack essentials, documents, and devices", 45, "preparation"),
            ("Confirm bookings and departure schedule", 15, "logistics")
        ],
        "interview": [
            ("Review company background and role requirements", 30, "research"),
            ("Practice core technical questions and system design", 90, "practice"),
            ("Prepare behavioral stories and STAR responses", 45, "preparation"),
            ("Prepare thoughtful questions for the interviewer", 20, "preparation")
        ]
    }

    @classmethod
    def decompose(cls, goal_title: str) -> List[SubTaskPlan]:
        clean_goal = goal_title.lower()
        selected_recipe = None

        for keyword, recipe in cls.DECOMPOSITION_RECIPES.items():
            if keyword in clean_goal:
                selected_recipe = recipe
                break

        # Fallback generic plan
        if not selected_recipe:
            selected_recipe = [
                ("Clarify requirements and define scope", 30, "planning"),
                ("Execute primary implementation or action", 60, "execution"),
                ("Review results and verify completion", 30, "review")
            ]

        plans = []
        for i, (title, dur, cat) in enumerate(selected_recipe, start=1):
            plans.append(SubTaskPlan(
                step_number=i,
                title=f"Step {i}: {title}",
                description=f"Action item for goal: '{goal_title}'",
                estimated_duration_min=dur,
                category=cat
            ))
        return plans
