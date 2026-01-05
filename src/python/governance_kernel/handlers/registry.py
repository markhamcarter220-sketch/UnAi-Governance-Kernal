"""
Handler Registry

Manages violation handlers for each invariant.

When an invariant is violated, the appropriate handler determines
the remediation strategy.
"""

from typing import Dict, List, Any, Optional


class HandlerRegistry:
    """
    Registry of violation handlers for each invariant.

    Each invariant has a corresponding handler that determines how to
    remediate violations.
    """

    def __init__(self):
        # Map from invariant name to handler function
        self.handlers = {
            'AIT-1': self._handle_ait1,
            'BG-1': self._handle_bg1,
            'GI-1': self._handle_gi1,
            'MAP-1': self._handle_map1,
            'CMP-1': self._handle_cmp1,
            'EXP-1': self._handle_exp1,
        }

    def handle(
        self,
        violations: List[str],
        context: Dict[str, Any],
        action: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Determine remediation for violations.

        Args:
            violations: List of violated invariant names
            context: Original context
            action: Proposed action

        Returns:
            Remediation strategy
        """
        if not violations:
            return {'action': 'allow'}

        # If multiple violations, prioritize most severe
        primary_violation = self._prioritize_violations(violations)

        # Get appropriate handler
        handler = self.handlers.get(primary_violation, self._handle_default)

        # Generate remediation
        return handler(context, action, violations)

    def _prioritize_violations(self, violations: List[str]) -> str:
        """
        Prioritize which violation to handle first.

        Priority order (most to least severe):
        1. BG-1 (binding authority)
        2. GI-1 (hard constraints)
        3. CMP-1 (consequence tracing)
        4. AIT-1 (authority mismatch)
        5. EXP-1 (affected party authority)
        6. MAP-1 (interpretation authority)
        """
        priority_order = ['BG-1', 'GI-1', 'CMP-1', 'AIT-1', 'EXP-1', 'MAP-1']

        for invariant in priority_order:
            if invariant in violations:
                return invariant

        return violations[0]

    def _handle_ait1(
        self,
        context: Dict[str, Any],
        action: Dict[str, Any],
        violations: List[str],
    ) -> Dict[str, Any]:
        """
        Handle AIT-1 (Authority Invariance) violation.

        Remediation: Return decision to appropriate authority level.
        """
        system_auth = context.get('authority_level', 'none')
        required_auth = action.get('requires_authority', 'unknown')

        return {
            'action': 'return_to_authority',
            'reason': f'Action requires {required_auth} authority, system has {system_auth}',
            'required_authority_level': required_auth,
            'current_authority_level': system_auth,
            'suggested_action': 'Escalate to appropriate authority level',
        }

    def _handle_bg1(
        self,
        context: Dict[str, Any],
        action: Dict[str, Any],
        violations: List[str],
    ) -> Dict[str, Any]:
        """
        Handle BG-1 (Boundary Governance) violation.

        Remediation: Require human authority for binding actions.
        """
        return {
            'action': 'require_human_authority',
            'reason': 'Binding action requires human in authority chain',
            'suggested_action': 'Obtain explicit human authorization before proceeding',
            'binding_action_type': action.get('type'),
        }

    def _handle_gi1(
        self,
        context: Dict[str, Any],
        action: Dict[str, Any],
        violations: List[str],
    ) -> Dict[str, Any]:
        """
        Handle GI-1 (Gauge Invariance) violation.

        Remediation: Respect hard constraints, cannot be optimized away.
        """
        violated_constraints = context.get('violated_constraints', [])

        return {
            'action': 'respect_hard_constraints',
            'reason': 'Action violates hard constraints that cannot be optimized away',
            'violated_constraints': violated_constraints,
            'suggested_action': 'Find alternative that satisfies all constraints',
        }

    def _handle_map1(
        self,
        context: Dict[str, Any],
        action: Dict[str, Any],
        violations: List[str],
    ) -> Dict[str, Any]:
        """
        Handle MAP-1 (Meaning-Authority Pairing) violation.

        Remediation: Obtain authority for interpretation.
        """
        return {
            'action': 'obtain_interpretation_authority',
            'reason': 'Interpreting ambiguous meaning requires explicit authority',
            'suggested_action': 'Escalate interpretation to authorized decision-maker',
        }

    def _handle_cmp1(
        self,
        context: Dict[str, Any],
        action: Dict[str, Any],
        violations: List[str],
    ) -> Dict[str, Any]:
        """
        Handle CMP-1 (Consequence-Memory Pairing) violation.

        Remediation: Identify consequence-bearer.
        """
        return {
            'action': 'identify_consequence_bearer',
            'reason': 'Decision must trace to entity that bears consequences',
            'suggested_action': 'Explicitly identify who bears consequences of this decision',
        }

    def _handle_exp1(
        self,
        context: Dict[str, Any],
        action: Dict[str, Any],
        violations: List[str],
    ) -> Dict[str, Any]:
        """
        Handle EXP-1 (Experience-Authority Coupling) violation.

        Remediation: Give authority to affected parties.
        """
        affects = context.get('affects_group', 'unknown')

        return {
            'action': 'delegate_to_affected',
            'reason': 'Those who experience consequences must hold authority',
            'affected_group': affects,
            'suggested_action': f'Obtain authorization from {affects}',
        }

    def _handle_default(
        self,
        context: Dict[str, Any],
        action: Dict[str, Any],
        violations: List[str],
    ) -> Dict[str, Any]:
        """
        Default handler for unknown violations.
        """
        return {
            'action': 'block',
            'reason': f'Unknown invariant violations: {violations}',
            'suggested_action': 'Review governance requirements',
        }
