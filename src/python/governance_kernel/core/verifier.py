"""
SAT-based Verifier

Verifies that state satisfies all invariants.

In production, this could use actual SAT solvers for complex verification.
This implementation uses direct boolean evaluation for efficiency.
"""

from typing import Dict, Any, List


class Verifier:
    """
    Verifies state against invariants.

    Uses boolean satisfiability checking to verify that the proposed
    state (context + action) satisfies all governance invariants.
    """

    def check(
        self,
        state: Dict[str, Any],
        invariants: List[Any],
    ) -> List[str]:
        """
        Check if state satisfies all invariants.

        Args:
            state: Boolean state variables
            invariants: List of invariant objects to check

        Returns:
            List of violated invariant names (empty if all pass)
        """
        violations = []

        for invariant in invariants:
            if not invariant.check(state):
                violations.append(invariant.name)

        return violations

    def check_single(
        self,
        state: Dict[str, Any],
        invariant: Any,
    ) -> bool:
        """
        Check if state satisfies a single invariant.

        Args:
            state: Boolean state variables
            invariant: Invariant to check

        Returns:
            True if invariant holds, False if violated
        """
        return invariant.check(state)
