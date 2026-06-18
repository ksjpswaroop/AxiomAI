"""
Planning Engine — STRIPS-style classical planning.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class STRIPSAction:
    """A STRIPS action: preconditions + effects."""
    name: str
    preconditions: list[str] = field(default_factory=list)
    add_effects: list[str] = field(default_factory=list)   # Facts added
    del_effects: list[str] = field(default_factory=list)    # Facts removed
    cost: int = 1

    def __str__(self) -> str:
        return f"{self.name}: requires {self.preconditions} → +{self.add_effects} -{self.del_effects}"


@dataclass
class Plan:
    """A generated action plan."""
    actions: list[STRIPSAction]
    state_sequence: list[set[str]]  # State after each action
    cost: int = 0
    found: bool = False
    failure_reason: Optional[str] = None


class PlanningEngine:
    """
    Classical planning using STRIPS formalism.

    Initial State → Actions → Goal State

    Uses BFS for completeness (finds shortest plans).
    """

    def __init__(self):
        self._actions: dict[str, STRIPSAction] = {}

    def add_action(self, action: STRIPSAction):
        self._actions[action.name] = action

    def plan(
        self,
        initial_state: set[str],
        goal: set[str],
        max_depth: int = 20,
    ) -> Plan:
        """
        Find a plan from initial state to goal using BFS.
        Returns Plan with actions + state sequence.
        """
        if goal.issubset(initial_state):
            return Plan(actions=[], state_sequence=[initial_state], found=True)

        from collections import deque
        queue = deque([(initial_state, [])])
        visited: set[frozenset] = {frozenset(initial_state)}
        step = 0

        while queue and step < max_depth:
            state, path = queue.popleft()
            step += 1

            for action in self._actions.values():
                # Check preconditions
                if not all(pre in state for pre in action.preconditions):
                    continue

                # Apply action effects
                new_state = (state - set(action.del_effects)) | set(action.add_effects)
                new_state_frozen = frozenset(new_state)

                if new_state_frozen in visited:
                    continue
                visited.add(new_state_frozen)

                new_path = path + [action]

                if goal.issubset(new_state):
                    return Plan(
                        actions=new_path,
                        state_sequence=[initial_state] + [
                            (state - set(a.del_effects)) | set(a.add_effects)
                            for a in new_path
                        ],
                        cost=sum(a.cost for a in new_path),
                        found=True,
                    )

                queue.append((new_state, new_path))

        return Plan(
            actions=[],
            state_sequence=[],
            found=False,
            failure_reason=f"No plan found within depth {max_depth}",
        )

    def validate_plan(self, plan: Plan, initial_state: set[str], goal: set[str]) -> bool:
        """Check if a plan actually achieves the goal."""
        state = set(initial_state)
        for action in plan.actions:
            if not all(pre in state for pre in action.preconditions):
                return False
            state = (state - set(action.del_effects)) | set(action.add_effects)
        return goal.issubset(state)
