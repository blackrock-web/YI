"""
MY AI - Logical Reasoning Engine
Forward-chaining inference engine over known facts, rules, and constraints.
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Set

@dataclass
class Rule:
    name: str
    premises: List[str]  # e.g. ["user_is_tired", "time_is_late"]
    conclusion: str      # e.g. "recommend_sleep"

class ReasoningEngine:
    def __init__(self, rules: Optional[List[Rule]] = None):
        self.rules = rules or self._default_rules()

    def _default_rules(self) -> List[Rule]:
        return [
            Rule(
                name="Suggest rest when tired late at night",
                premises=["user_tired", "is_night"],
                conclusion="suggest_winding_down"
            ),
            Rule(
                name="Suggest focus block for urgent high-priority tasks",
                premises=["has_urgent_task", "working_hours"],
                conclusion="schedule_focus_block"
            ),
            Rule(
                name="Suggest hydration/break during long study sessions",
                premises=["working_over_2_hours"],
                conclusion="suggest_hydration_break"
            )
        ]

    def infer(self, facts: Set[str]) -> List[str]:
        """Forward-chaining inference: applies rules until no new conclusions are drawn."""
        known = set(facts)
        new_inferences: List[str] = []
        changed = True

        while changed:
            changed = False
            for rule in self.rules:
                if rule.conclusion not in known and all(p in known for p in rule.premises):
                    known.add(rule.conclusion)
                    new_inferences.append(rule.conclusion)
                    changed = True

        return new_inferences
