"""
Governance Kernel - Universal Framework for Authority Preservation

A domain-independent framework for preventing authority accumulation in AI and
complex systems through formal invariant enforcement.

Example:
    >>> from governance_kernel import GovernanceKernel
    >>> kernel = GovernanceKernel()
    >>> result = kernel.verify(context, action)
    >>> if result.allowed:
    ...     execute(action)
    ... else:
    ...     handle_violation(result.violations)
"""

__version__ = '1.0.0'
__author__ = 'Mark Carter'
__license__ = 'Apache 2.0'

from .core.kernel import GovernanceKernel, VerificationResult, verify

__all__ = [
    'GovernanceKernel',
    'VerificationResult',
    'verify',
]
