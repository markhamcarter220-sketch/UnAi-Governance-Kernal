"""
Governance Invariants

The six formal invariants that prevent authority accumulation:
- AIT-1: Authority Invariance
- BG-1: Boundary Governance
- GI-1: Gauge Invariance
- MAP-1: Meaning-Authority Pairing
- CMP-1: Consequence-Memory Pairing
- EXP-1: Experience-Authority Coupling
"""

from typing import Dict, Any
from abc import ABC, abstractmethod


class Invariant(ABC):
    """Base class for all governance invariants."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def check(self, state: Dict[str, Any]) -> bool:
        """
        Check if invariant holds for given state.

        Args:
            state: Boolean state variables from encoder

        Returns:
            True if invariant holds, False if violated
        """
        pass

    @abstractmethod
    def explain_violation(
        self,
        context: Dict[str, Any],
        action: Dict[str, Any],
    ) -> str:
        """
        Explain why the invariant was violated.

        Args:
            context: Original context
            action: Proposed action

        Returns:
            Human-readable explanation
        """
        pass


class AIT1_Invariant(Invariant):
    """
    AIT-1: Authority Invariance

    Capability does not grant authority.

    A system's ability to perform an action (capability) is explicitly
    separated from its permission to perform that action (authority).

    Violation example:
        - System has `execute_trade` capability
        - System has `advisory` authority level
        - System attempts `binding_decision`
        → BLOCKED: Capability ≠ Authority
    """

    def __init__(self):
        super().__init__(
            name='AIT-1',
            description='Authority Invariance - capability does not grant authority'
        )

    def check(self, state: Dict[str, Any]) -> bool:
        """
        Check if action's required authority ≤ system's granted authority.
        """
        system_authority = state.get('authority_level', 'none')
        required_authority = state.get('requires_authority', 'none')

        # Authority hierarchy
        authority_levels = {
            'none': 0,
            'advisory': 1,
            'binding': 2,
            'autonomous': 3,
        }

        granted = authority_levels.get(system_authority, 0)
        required = authority_levels.get(required_authority, 0)

        # Invariant holds if granted >= required
        return granted >= required

    def explain_violation(self, context: Dict[str, Any], action: Dict[str, Any]) -> str:
        system_auth = context.get('authority_level', 'none')
        required_auth = action.get('requires_authority', 'unknown')

        return (
            f"System has '{system_auth}' authority but action requires "
            f"'{required_auth}' authority. Capability to execute does not "
            f"grant authority to execute."
        )


class BG1_Invariant(Invariant):
    """
    BG-1: Boundary Governance

    Only humans can bind reality.

    Actions that create binding commitments or irreversible consequences
    require human authority.

    Violation example:
        - AI system attempts to sign legal contract
        - No human in the authority chain
        → BLOCKED: Only humans can bind reality
    """

    def __init__(self):
        super().__init__(
            name='BG-1',
            description='Boundary Governance - only humans can bind reality'
        )

    def check(self, state: Dict[str, Any]) -> bool:
        """
        Check if binding actions have human authority.
        """
        is_binding = state.get('is_binding_action', False)
        has_human_authority = state.get('human_in_authority_chain', False)

        # If action is binding, must have human authority
        if is_binding:
            return has_human_authority

        return True

    def explain_violation(self, context: Dict[str, Any], action: Dict[str, Any]) -> str:
        return (
            "Action creates binding commitment or irreversible consequence, "
            "but no human authority is present. Only humans can bind reality."
        )


class GI1_Invariant(Invariant):
    """
    GI-1: Gauge Invariance

    Optimization cannot change constraint meaning.

    Hard constraints (safety, rights, physics) cannot be reinterpreted
    or optimized away, regardless of optimization pressure.

    Violation example:
        - Hard constraint: "No hazmat through residential"
        - Optimization finds faster route through residential
        - System attempts to reinterpret constraint
        → BLOCKED: Constraints are invariant under optimization
    """

    def __init__(self):
        super().__init__(
            name='GI-1',
            description='Gauge Invariance - optimization preserves constraints'
        )

    def check(self, state: Dict[str, Any]) -> bool:
        """
        Check if action violates hard constraints.
        """
        hard_constraints = state.get('hard_constraints', [])
        violated_constraints = state.get('violated_constraints', [])

        # No hard constraint may be violated
        return len(set(hard_constraints) & set(violated_constraints)) == 0

    def explain_violation(self, context: Dict[str, Any], action: Dict[str, Any]) -> str:
        violated = context.get('violated_constraints', [])
        return (
            f"Action violates hard constraints: {violated}. "
            f"These constraints are invariant under optimization and "
            f"cannot be reinterpreted or traded off."
        )


class MAP1_Invariant(Invariant):
    """
    MAP-1: Meaning-Authority Pairing

    Meaning collapse requires authority.

    When multiple interpretations exist (superposition of meaning),
    collapsing to a specific interpretation requires appropriate authority.

    Violation example:
        - Ambiguous policy clause
        - AI interprets in way that benefits itself
        - No authority to make that interpretation
        → BLOCKED: Meaning collapse requires authority
    """

    def __init__(self):
        super().__init__(
            name='MAP-1',
            description='Meaning-Authority Pairing - meaning collapse needs authority'
        )

    def check(self, state: Dict[str, Any]) -> bool:
        """
        Check if interpretation decisions have proper authority.
        """
        makes_interpretation = state.get('makes_interpretation', False)
        has_interpretation_authority = state.get('interpretation_authority', False)

        if makes_interpretation:
            return has_interpretation_authority

        return True

    def explain_violation(self, context: Dict[str, Any], action: Dict[str, Any]) -> str:
        return (
            "Action requires interpreting ambiguous meaning or policy, "
            "but lacks authority to make that interpretation. Meaning "
            "collapse requires explicit authority."
        )


class CMP1_Invariant(Invariant):
    """
    CMP-1: Consequence-Memory Pairing

    Decisions trace to consequence-bearers.

    Every decision must be traceable to an entity that bears the
    consequences of that decision.

    Violation example:
        - AI makes investment decision
        - No traceable consequence-bearer
        - Responsibility is diffused
        → BLOCKED: Decision must trace to consequence-bearer
    """

    def __init__(self):
        super().__init__(
            name='CMP-1',
            description='Consequence-Memory Pairing - decisions trace to bearers'
        )

    def check(self, state: Dict[str, Any]) -> bool:
        """
        Check if decision has traceable consequence-bearer.
        """
        makes_decision = state.get('makes_decision', False)
        has_consequence_bearer = state.get('consequence_bearer') is not None

        if makes_decision:
            return has_consequence_bearer

        return True

    def explain_violation(self, context: Dict[str, Any], action: Dict[str, Any]) -> str:
        return (
            "Action makes a consequential decision but no consequence-bearer "
            "is identified. Every decision must trace to an entity that bears "
            "the consequences."
        )


class EXP1_Invariant(Invariant):
    """
    EXP-1: Experience-Authority Coupling

    Those who experience consequences hold authority.

    Authority over decisions should reside with those who will experience
    the consequences of those decisions.

    Violation example:
        - Policy affects Group A
        - Group B makes the decision
        - Group A has no input or override
        → BLOCKED: Those who experience must have authority
    """

    def __init__(self):
        super().__init__(
            name='EXP-1',
            description='Experience-Authority Coupling - experiencers hold authority'
        )

    def check(self, state: Dict[str, Any]) -> bool:
        """
        Check if those affected have authority.
        """
        affects_group = state.get('affects_group')
        decision_maker = state.get('decision_maker')

        # If action affects a group, that group must be the decision maker
        # or must have delegated authority
        if affects_group and decision_maker:
            return (
                affects_group == decision_maker or
                state.get('delegated_authority_from_affected', False)
            )

        return True

    def explain_violation(self, context: Dict[str, Any], action: Dict[str, Any]) -> str:
        affects = context.get('affects_group', 'unknown')
        decider = context.get('decision_maker', 'unknown')

        return (
            f"Action affects '{affects}' but decision is made by '{decider}'. "
            f"Those who experience consequences must hold or delegate authority "
            f"for decisions affecting them."
        )
