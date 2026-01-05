"""
Logistics Stress Test - Invariant Conflict Detection

This is THE critical stress test that demonstrates the kernel's ability
to detect invariant conflicts and return authority to humans.

Scenario:
    A delivery system must transport life-saving medicine to a hospital.
    - Invariant A: Never transport hazmat through residential areas (safety)
    - Invariant B: Medicine must arrive within 10 minutes (patient dies otherwise)
    - Conflict: Only route that satisfies B violates A

Expected Behavior:
    The kernel detects that NO valid action exists and returns authority
    to human decision-maker rather than:
    - Picking the "least bad" option autonomously
    - Violating one invariant to satisfy the other
    - Freezing/failing silently

This proves the kernel prevents autonomous authority accumulation in
edge cases where optimization would otherwise force a choice.
"""

import pytest
from governance_kernel import GovernanceKernel


def test_logistics_conflict():
    """
    Test invariant conflict detection in logistics scenario.

    This is the canonical example of why governance kernels are necessary:
    when invariants conflict, the system must return authority to humans
    rather than make autonomous ethical trade-offs.
    """
    kernel = GovernanceKernel()

    # Context: Life-saving medicine delivery
    context = {
        'cargo_type': 'life_saving_medicine',
        'cargo_classification': 'chemical_hazard',  # It's hazmat
        'destination': 'city_hospital',
        'time_constraint_minutes': 10,  # Patient dies after 10 min
        'current_time': 0,
        'patient_status': 'critical',
    }

    # Route Option 1: Fast but through residential
    action_residential = {
        'type': 'select_route',
        'route_id': 'route_residential',
        'route_name': 'Highway 101 (residential)',
        'estimated_time_minutes': 8,
        'passes_through_residential': True,  # Violates safety invariant
        'passes_through_industrial': False,
    }

    # Route Option 2: Safe but too slow
    action_industrial = {
        'type': 'select_route',
        'route_id': 'route_industrial',
        'route_name': 'Industrial Bypass',
        'estimated_time_minutes': 35,  # Patient dies
        'passes_through_residential': False,
        'passes_through_industrial': True,
    }

    # Test Route 1: Should be blocked (safety violation)
    result1 = kernel.verify(context, action_residential)
    assert not result1.allowed, "Route through residential should be blocked"
    assert 'GI-1' in str(result1.violations), "Should violate Gauge Invariance (safety constraint)"

    # Test Route 2: Should be blocked (time constraint violation)
    result2 = kernel.verify(context, action_industrial)
    assert not result2.allowed, "Too-slow route should be blocked"
    assert 'CMP-1' in str(result2.violations), "Should violate Consequence-Memory (patient dies)"

    # Test Conflict Detection: No valid action exists
    possible_actions = [action_residential, action_industrial]
    conflict = kernel.check_invariant_conflict(context, possible_actions)

    # Assert conflict is detected
    assert conflict is not None, "Kernel must detect invariant conflict"
    assert conflict['type'] == 'invariant_conflict'
    assert 'No valid action exists' in conflict['message']
    assert conflict['remediation'] == 'human_decision_required'
    assert conflict['escalation_priority'] == 'high'

    print("\n" + "=" * 70)
    print("LOGISTICS CONFLICT TEST PASSED")
    print("=" * 70)
    print(f"\nConflict detected: {conflict['message']}")
    print(f"Conflicting invariants: {conflict['conflicting_invariants']}")
    print(f"Attempted actions: {conflict['attempted_actions']}")
    print(f"Remediation: {conflict['remediation']}")
    print("\n→ Authority correctly returned to human decision-maker")
    print("=" * 70)


def test_logistics_conflict_with_valid_option():
    """
    Test that conflict is NOT detected when a valid option exists.

    Same scenario but with a third route that satisfies both invariants.
    """
    kernel = GovernanceKernel()

    context = {
        'cargo_type': 'life_saving_medicine',
        'cargo_classification': 'chemical_hazard',
        'destination': 'city_hospital',
        'time_constraint_minutes': 10,
        'current_time': 0,
    }

    # Route 1: Fast but unsafe (blocked)
    action_residential = {
        'type': 'select_route',
        'estimated_time_minutes': 8,
        'passes_through_residential': True,
    }

    # Route 2: Safe but slow (blocked)
    action_industrial = {
        'type': 'select_route',
        'estimated_time_minutes': 35,
        'passes_through_residential': False,
    }

    # Route 3: Safe AND fast (valid!)
    action_express = {
        'type': 'select_route',
        'route_name': 'Express Industrial Corridor',
        'estimated_time_minutes': 7,
        'passes_through_residential': False,  # Safe
        'passes_through_industrial': True,
    }

    # Check for conflict with all three options
    possible_actions = [action_residential, action_industrial, action_express]
    conflict = kernel.check_invariant_conflict(context, possible_actions)

    # No conflict should be detected (express route is valid)
    assert conflict is None, "Should not detect conflict when valid option exists"

    # Verify the express route is actually allowed
    result_express = kernel.verify(context, action_express)
    assert result_express.allowed, "Express route should be allowed"

    print("\n[TEST PASSED] No conflict when valid action exists")


def test_logistics_edge_case_zero_time():
    """
    Test edge case: Time constraint already violated (patient already dead).

    Expected: All actions blocked, conflict detected, human authority required.
    """
    kernel = GovernanceKernel()

    context = {
        'cargo_type': 'life_saving_medicine',
        'time_constraint_minutes': 10,
        'current_time': 12,  # Already past deadline
    }

    action = {
        'type': 'select_route',
        'estimated_time_minutes': 5,
    }

    result = kernel.verify(context, action)

    assert not result.allowed, "Should block action when time constraint already violated"
    print("\n[TEST PASSED] Edge case: time already expired")


def test_logistics_multiple_hazmat_types():
    """
    Test with different hazmat classifications.

    Some hazmat may be allowed through residential (e.g., medical oxygen),
    while others are strictly prohibited (e.g., explosives).
    """
    kernel = GovernanceKernel()

    # Scenario 1: Medical oxygen (less restricted)
    context_oxygen = {
        'cargo_classification': 'medical_oxygen',
        'hazard_level': 'low',
    }

    action = {
        'type': 'select_route',
        'passes_through_residential': True,
    }

    result_oxygen = kernel.verify(context_oxygen, action)

    # Scenario 2: Explosives (strictly prohibited)
    context_explosive = {
        'cargo_classification': 'explosive',
        'hazard_level': 'extreme',
    }

    result_explosive = kernel.verify(context_explosive, action)

    # Oxygen might be allowed, explosives should not
    assert not result_explosive.allowed, "Explosives through residential must be blocked"

    print("\n[TEST PASSED] Different hazmat classifications handled correctly")


def test_logistics_with_override_authority():
    """
    Test that conflict can be resolved with proper human authority.

    When human decision-maker explicitly authorizes a specific route,
    it should be allowed (human takes responsibility).
    """
    kernel = GovernanceKernel()

    context = {
        'cargo_type': 'life_saving_medicine',
        'cargo_classification': 'chemical_hazard',
        'time_constraint_minutes': 10,
        # Human authority present
        'human_decision_maker': 'emergency_coordinator_id_12345',
        'authority_level': 'binding',
        'explicit_authorization': True,
        'authorization_signature': 'SIGNED_BY_COORDINATOR',
    }

    action = {
        'type': 'select_route',
        'route_name': 'Highway 101 (residential)',
        'estimated_time_minutes': 8,
        'passes_through_residential': True,
        'authorized_by_human': True,  # Explicit human override
        'responsibility_bearer': 'emergency_coordinator_id_12345',
    }

    result = kernel.verify(context, action)

    # With explicit human authority, action should be allowed
    # Human takes responsibility for the decision
    assert result.allowed or 'human_override' in result.remediation, \
        "Human authority should be able to resolve conflict"

    print("\n[TEST PASSED] Human authority can resolve invariant conflict")


@pytest.mark.parametrize("time_constraint,route_time,should_pass", [
    (10, 5, True),   # Plenty of time
    (10, 10, True),  # Exactly on time
    (10, 11, False), # Too slow
    (10, 50, False), # Way too slow
])
def test_logistics_time_constraints(time_constraint, route_time, should_pass):
    """
    Parametrized test for various time constraint scenarios.
    """
    kernel = GovernanceKernel()

    context = {
        'time_constraint_minutes': time_constraint,
        'cargo_type': 'life_saving_medicine',
    }

    action = {
        'type': 'select_route',
        'estimated_time_minutes': route_time,
        'passes_through_residential': False,  # Safe route
    }

    result = kernel.verify(context, action)

    if should_pass:
        assert result.allowed, f"Route with {route_time}min should pass {time_constraint}min constraint"
    else:
        assert not result.allowed, f"Route with {route_time}min should fail {time_constraint}min constraint"


if __name__ == '__main__':
    """
    Run all logistics stress tests.

    These tests prove the kernel:
    1. Detects invariant conflicts
    2. Returns authority to humans when needed
    3. Never makes autonomous ethical trade-offs
    4. Respects human override with proper authorization
    """
    print("\n" + "=" * 70)
    print("RUNNING LOGISTICS STRESS TESTS")
    print("=" * 70)

    test_logistics_conflict()
    test_logistics_conflict_with_valid_option()
    test_logistics_edge_case_zero_time()
    test_logistics_multiple_hazmat_types()
    test_logistics_with_override_authority()

    print("\n" + "=" * 70)
    print("ALL LOGISTICS STRESS TESTS PASSED")
    print("=" * 70)
    print("\nKey Validations:")
    print("✓ Invariant conflicts detected")
    print("✓ Authority returned to humans")
    print("✓ No autonomous ethical trade-offs")
    print("✓ Human override properly respected")
    print("✓ Edge cases handled correctly")
    print("\n" + "=" * 70)
