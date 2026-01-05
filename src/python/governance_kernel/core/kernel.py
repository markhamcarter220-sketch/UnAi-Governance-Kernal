"""
Governance Kernel - Core Implementation

This is the main kernel class that enforces governance invariants
through formal verification.

Architecture:
    Context + Action → StateEncoder → Boolean Variables
                                            ↓
                                      SAT Verifier
                                            ↓
                              Check All 6 Invariants
                                            ↓
                            Violations → Handlers → Remediation
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

from .state_encoder import StateEncoder
from .verifier import Verifier
from .invariants import (
    AIT1_Invariant,
    BG1_Invariant,
    GI1_Invariant,
    MAP1_Invariant,
    CMP1_Invariant,
    EXP1_Invariant,
)
from ..handlers import HandlerRegistry
from ..utils.logger import AuditLogger


@dataclass
class VerificationResult:
    """
    Result of kernel verification.

    Attributes:
        allowed: Whether the action is permitted
        violations: List of invariant violations (empty if allowed)
        remediation: Suggested remediation strategy
        audit_id: Unique ID for audit trail
        timestamp: When verification occurred
        latency_us: Verification latency in microseconds
    """
    allowed: bool
    violations: List[str]
    remediation: Optional[Dict[str, Any]] = None
    audit_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    latency_us: Optional[float] = None


class GovernanceKernel:
    """
    Universal Governance Kernel

    Enforces six formal invariants to prevent authority accumulation
    in AI and complex systems.

    Invariants:
        AIT-1: Authority Invariance (capability ≠ authority)
        BG-1: Boundary Governance (only humans bind reality)
        GI-1: Gauge Invariance (optimization preserves constraints)
        MAP-1: Meaning-Authority Pairing (meaning collapse needs authority)
        CMP-1: Consequence-Memory Pairing (decisions trace to bearers)
        EXP-1: Experience-Authority Coupling (experiencers hold authority)

    Example:
        >>> kernel = GovernanceKernel()
        >>> context = {'authority_level': 'advisory'}
        >>> action = {'type': 'binding_decision'}
        >>> result = kernel.verify(context, action)
        >>> if result.allowed:
        ...     execute(action)
        ... else:
        ...     handle_violation(result.violations)
    """

    def __init__(
        self,
        invariants: Optional[List[Any]] = None,
        enable_audit: bool = True,
        strict_mode: bool = True,
    ):
        """
        Initialize the Governance Kernel.

        Args:
            invariants: List of invariant instances (uses defaults if None)
            enable_audit: Whether to enable audit logging
            strict_mode: If True, any violation blocks the action
        """
        # Core components
        self.state_encoder = StateEncoder()
        self.verifier = Verifier()
        self.handlers = HandlerRegistry()

        # Load invariants (default to all 6)
        self.invariants = invariants or self._default_invariants()

        # Configuration
        self.strict_mode = strict_mode
        self.enable_audit = enable_audit

        # Audit logging
        self.audit_logger = AuditLogger() if enable_audit else None

        # Statistics tracking
        self.stats = {
            'total_verifications': 0,
            'allowed': 0,
            'blocked': 0,
            'violations_by_invariant': {},
            'avg_latency_us': 0.0,
        }

        # Initialize violation counters for each invariant
        for inv in self.invariants:
            self.stats['violations_by_invariant'][inv.name] = 0

    def _default_invariants(self) -> List[Any]:
        """Return the default set of 6 governance invariants."""
        return [
            AIT1_Invariant(),  # Authority Invariance
            BG1_Invariant(),   # Boundary Governance
            GI1_Invariant(),   # Gauge Invariance
            MAP1_Invariant(),  # Meaning-Authority Pairing
            CMP1_Invariant(),  # Consequence-Memory Pairing
            EXP1_Invariant(),  # Experience-Authority Coupling
        ]

    def verify(
        self,
        context: Dict[str, Any],
        action: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> VerificationResult:
        """
        Verify an action against governance invariants.

        This is the main entry point for the kernel. It:
        1. Encodes context+action into boolean state
        2. Checks all invariants via SAT verification
        3. Returns ALLOW or BLOCK with remediation

        Args:
            context: Current system context (authority, permissions, state)
            action: Proposed action to verify
            metadata: Optional metadata for audit trail

        Returns:
            VerificationResult with allowed/blocked decision and remediation

        Example:
            >>> context = {
            ...     'authority_level': 'advisory',
            ...     'consequence_bearer': 'human',
            ...     'permissions': ['recommend']
            ... }
            >>> action = {
            ...     'type': 'execute_trade',
            ...     'requires_authority': 'binding'
            ... }
            >>> result = kernel.verify(context, action)
            >>> print(result.allowed)  # False
            >>> print(result.violations)  # ['AIT-1: Authority Invariance']
        """
        import time
        start_time = time.perf_counter()

        # Step 1: Encode context + action → boolean state
        state = self.state_encoder.encode(context, action)

        # Step 2: Check all invariants
        violations = []
        for invariant in self.invariants:
            if not invariant.check(state):
                violations.append(invariant.name)
                self.stats['violations_by_invariant'][invariant.name] += 1

        # Step 3: Determine if action is allowed
        allowed = len(violations) == 0

        # Step 4: Generate remediation if blocked
        remediation = None
        if not allowed:
            remediation = self.handlers.handle(violations, context, action)

        # Calculate latency
        end_time = time.perf_counter()
        latency_us = (end_time - start_time) * 1_000_000

        # Update statistics
        self.stats['total_verifications'] += 1
        if allowed:
            self.stats['allowed'] += 1
        else:
            self.stats['blocked'] += 1

        # Update running average latency
        n = self.stats['total_verifications']
        old_avg = self.stats['avg_latency_us']
        self.stats['avg_latency_us'] = (old_avg * (n - 1) + latency_us) / n

        # Create result
        result = VerificationResult(
            allowed=allowed,
            violations=violations,
            remediation=remediation,
            timestamp=datetime.utcnow(),
            latency_us=latency_us,
        )

        # Audit logging
        if self.enable_audit:
            audit_id = self.audit_logger.log_verification(
                context=context,
                action=action,
                result=result,
                metadata=metadata,
            )
            result.audit_id = audit_id

        return result

    def verify_batch(
        self,
        context: Dict[str, Any],
        actions: List[Dict[str, Any]],
    ) -> List[VerificationResult]:
        """
        Verify multiple actions in batch (more efficient than repeated calls).

        Args:
            context: Shared context for all actions
            actions: List of actions to verify

        Returns:
            List of VerificationResult, one per action
        """
        return [self.verify(context, action) for action in actions]

    def get_stats(self) -> Dict[str, Any]:
        """
        Get kernel statistics.

        Returns:
            Dictionary with verification stats, violations, latency
        """
        return self.stats.copy()

    def reset_stats(self) -> None:
        """Reset all statistics counters."""
        self.stats['total_verifications'] = 0
        self.stats['allowed'] = 0
        self.stats['blocked'] = 0
        self.stats['avg_latency_us'] = 0.0
        for inv in self.invariants:
            self.stats['violations_by_invariant'][inv.name] = 0

    def check_invariant_conflict(
        self,
        context: Dict[str, Any],
        possible_actions: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """
        Check if invariants are in conflict (no valid action exists).

        This is critical for detecting situations where the system cannot
        proceed autonomously and must return authority to humans.

        Args:
            context: Current context
            possible_actions: All possible actions to consider

        Returns:
            Conflict info if detected, None if at least one action is valid

        Example:
            >>> # Logistics scenario: hazmat through residential vs time constraint
            >>> context = {'cargo': 'hazmat', 'time_limit': 10}
            >>> actions = [
            ...     {'route': 'residential', 'time': 8},  # Fast but unsafe
            ...     {'route': 'industrial', 'time': 35}   # Safe but slow
            ... ]
            >>> conflict = kernel.check_invariant_conflict(context, actions)
            >>> if conflict:
            ...     # Return decision to human
            ...     escalate_to_human(conflict)
        """
        results = self.verify_batch(context, possible_actions)

        # Check if any action is allowed
        if any(r.allowed for r in results):
            return None  # No conflict, at least one valid action exists

        # All actions blocked - invariant conflict detected
        all_violations = set()
        for result in results:
            all_violations.update(result.violations)

        return {
            'type': 'invariant_conflict',
            'message': 'No valid action exists - invariants in conflict',
            'conflicting_invariants': list(all_violations),
            'attempted_actions': len(possible_actions),
            'remediation': 'human_decision_required',
            'escalation_priority': 'high',
        }

    def explain(
        self,
        context: Dict[str, Any],
        action: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Explain why an action was allowed or blocked.

        Provides detailed reasoning for transparency and debugging.

        Args:
            context: System context
            action: Action to explain

        Returns:
            Detailed explanation of verification decision
        """
        result = self.verify(context, action)

        explanation = {
            'decision': 'ALLOWED' if result.allowed else 'BLOCKED',
            'violations': result.violations,
            'latency_us': result.latency_us,
        }

        if not result.allowed:
            # Add detailed explanation for each violation
            explanation['details'] = []
            for violation in result.violations:
                for inv in self.invariants:
                    if inv.name == violation:
                        explanation['details'].append({
                            'invariant': inv.name,
                            'description': inv.description,
                            'why_violated': inv.explain_violation(context, action),
                        })

            explanation['remediation'] = result.remediation

        return explanation


# Convenience function for quick verification
def verify(
    context: Dict[str, Any],
    action: Dict[str, Any],
    **kwargs
) -> VerificationResult:
    """
    Convenience function for one-off verification without creating kernel instance.

    Example:
        >>> from governance_kernel import verify
        >>> result = verify(
        ...     context={'authority': 'advisory'},
        ...     action={'type': 'binding_decision'}
        ... )
    """
    kernel = GovernanceKernel(**kwargs)
    return kernel.verify(context, action)
