"""
State Encoder

Encodes context + action into boolean state variables for invariant checking.

This is a critical component that transforms rich contextual information
into a normalized form that invariants can reason about.
"""

from typing import Dict, Any


class StateEncoder:
    """
    Encodes context and action into boolean state variables.

    The encoder extracts relevant features from context and action,
    normalizing them into a standard format that invariants can check.
    """

    def encode(
        self,
        context: Dict[str, Any],
        action: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Encode context + action into state variables.

        Args:
            context: Current system context
            action: Proposed action

        Returns:
            Dictionary of state variables for invariant checking
        """
        state = {}

        # Extract authority information (for AIT-1)
        state['authority_level'] = context.get('authority_level', 'none')
        state['requires_authority'] = action.get('requires_authority', 'none')

        # Extract binding/consequence information (for BG-1, CMP-1)
        state['is_binding_action'] = self._is_binding_action(action)
        state['human_in_authority_chain'] = self._has_human_authority(context)
        state['consequence_bearer'] = context.get('consequence_bearer')
        state['makes_decision'] = action.get('makes_decision', False)

        # Extract constraint information (for GI-1)
        state['hard_constraints'] = context.get('hard_constraints', [])
        state['violated_constraints'] = self._check_constraint_violations(context, action)

        # Extract interpretation information (for MAP-1)
        state['makes_interpretation'] = action.get('makes_interpretation', False)
        state['interpretation_authority'] = context.get('interpretation_authority', False)

        # Extract affected party information (for EXP-1)
        state['affects_group'] = action.get('affects_group') or context.get('affects_group')
        state['decision_maker'] = context.get('decision_maker')
        state['delegated_authority_from_affected'] = context.get(
            'delegated_authority_from_affected',
            False
        )

        return state

    def _is_binding_action(self, action: Dict[str, Any]) -> bool:
        """Determine if action creates binding commitment."""
        action_type = action.get('type', '')

        # Binding action indicators
        binding_types = [
            'execute',
            'commit',
            'sign',
            'approve',
            'transfer',
            'deploy',
        ]

        is_binding_type = any(bt in action_type.lower() for bt in binding_types)
        explicitly_binding = action.get('is_binding', False)

        return is_binding_type or explicitly_binding

    def _has_human_authority(self, context: Dict[str, Any]) -> bool:
        """Check if human is in authority chain."""
        # Check multiple ways human authority might be indicated
        has_human_bearer = context.get('consequence_bearer', '').startswith('human')
        has_human_decision_maker = context.get('decision_maker', '').startswith('human')
        explicit_human_auth = context.get('human_in_authority_chain', False)
        has_human_signature = context.get('human_signature') is not None

        return any([
            has_human_bearer,
            has_human_decision_maker,
            explicit_human_auth,
            has_human_signature,
        ])

    def _check_constraint_violations(
        self,
        context: Dict[str, Any],
        action: Dict[str, Any],
    ) -> list:
        """
        Check which hard constraints would be violated by action.

        This is a simplified implementation. In production, this would
        involve more sophisticated constraint checking.
        """
        violated = []

        # Check if action explicitly violates constraints
        if 'violates_constraints' in action:
            violated.extend(action['violates_constraints'])

        # Check specific constraint patterns
        hard_constraints = context.get('hard_constraints', [])

        for constraint in hard_constraints:
            if self._action_violates_constraint(action, constraint):
                violated.append(constraint)

        return violated

    def _action_violates_constraint(
        self,
        action: Dict[str, Any],
        constraint: str,
    ) -> bool:
        """
        Check if action violates a specific constraint.

        This is a simplified pattern matcher. In production, this would
        be more sophisticated (potentially using constraint solvers).
        """
        # Example: "no_residential_hazmat" constraint
        if constraint == 'no_residential_hazmat':
            return (
                action.get('passes_through_residential', False) and
                action.get('cargo_is_hazmat', False)
            )

        # Example: Time constraints
        if constraint.startswith('time_limit_'):
            limit = int(constraint.split('_')[-1])
            action_time = action.get('estimated_time_minutes', 0)
            return action_time > limit

        # Generic: check if action explicitly violates
        return action.get(f'violates_{constraint}', False)
