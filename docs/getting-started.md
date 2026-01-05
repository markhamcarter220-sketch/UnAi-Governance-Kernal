# Getting Started with Governance Kernel

This guide will walk you through installing and using the Governance Kernel in your project.

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install via pip

```bash
pip install governance-kernel
```

### Install from source

```bash
git clone https://github.com/governance-kernel/governance-kernel.git
cd governance-kernel
pip install -e .
```

### Verify installation

```python
from governance_kernel import GovernanceKernel

print(GovernanceKernel.__version__)
# Output: 1.0.0
```

---

## Core Concepts

Before diving into code, let's understand the three key concepts:

### 1. Invariants

**Invariants** are mathematical constraints that must hold true at all times. The kernel enforces six:

- **AIT-1**: Authority Invariance - capability does not grant authority
- **BG-1**: Boundary Governance - only humans can bind reality
- **GI-1**: Gauge Invariance - optimization preserves constraint meaning
- **MAP-1**: Meaning-Authority Pairing - meaning collapse requires authority
- **CMP-1**: Consequence-Memory Pairing - decisions trace to bearers
- **EXP-1**: Experience-Authority Coupling - experiencers hold authority

See [invariants/overview.md](invariants/overview.md) for detailed explanations.

### 2. Verification

**Verification** is the process of checking if a proposed action violates any invariants:

```
Context + Action → Encode → Check Invariants → ALLOW or BLOCK
```

### 3. Remediation

**Remediation** is the suggested fix when an action is blocked:

- Return authority to human
- Reduce scope of action
- Request explicit permission
- Escalate to consequence-bearer

---

## Your First Example

Let's build a simple AI assistant with governance:

### Step 1: Import the kernel

```python
from governance_kernel import GovernanceKernel
```

### Step 2: Create a kernel instance

```python
kernel = GovernanceKernel()
```

### Step 3: Define context

Context describes the current state of your system:

```python
context = {
    'authority_level': 'advisory',           # System can only advise, not decide
    'consequence_bearer': 'human_operator',  # Human bears consequences
    'permissions': ['recommend', 'analyze'], # What system can do
}
```

### Step 4: Define an action

An action is something your system wants to do:

```python
action = {
    'type': 'execute_trade',
    'value': 1000000,
    'requires_authority': 'binding_decision'  # Needs binding authority
}
```

### Step 5: Verify the action

```python
result = kernel.verify(context, action)

if result.allowed:
    print("Action allowed - executing")
    execute_trade(action)
else:
    print(f"Action blocked: {result.violations}")
    print(f"Remediation: {result.remediation}")
```

### Output

```
Action blocked: ['AIT-1: Authority Invariance Violation']
Remediation: {'action': 'return_to_human', 'reason': 'Advisory system cannot make binding decisions'}
```

**Why was it blocked?**

The system has `authority_level: 'advisory'` but the action requires `binding_decision` authority. This violates **AIT-1** (Authority Invariance) - the system's capability to execute trades doesn't grant it authority to do so.

---

## Complete Working Example

Here's a complete AI assistant with governance:

```python
from governance_kernel import GovernanceKernel
from typing import Dict, Any

class GovernedAssistant:
    """AI assistant with formal governance constraints."""

    def __init__(self, authority_level: str = 'advisory'):
        self.kernel = GovernanceKernel()
        self.authority_level = authority_level
        self.conversation_history = []

    def respond(self, user_message: str) -> str:
        """
        Generate response with governance verification.

        Args:
            user_message: Message from user

        Returns:
            Safe, governance-compliant response
        """
        # Build context
        context = {
            'authority_level': self.authority_level,
            'consequence_bearer': 'user',
            'conversation_history': self.conversation_history,
            'permissions': ['recommend', 'analyze', 'inform'],
        }

        # Generate proposed response (simplified - use your LLM here)
        proposed_response = self._generate_response(user_message)

        # Check if response requires binding authority
        action = {
            'type': 'respond',
            'content': proposed_response,
            'requires_authority': self._classify_authority_needed(proposed_response),
        }

        # Verify with kernel
        result = self.kernel.verify(context, action)

        if result.allowed:
            # Response is safe - add to history and return
            self.conversation_history.append({
                'user': user_message,
                'assistant': proposed_response,
            })
            return proposed_response
        else:
            # Response blocked - apply remediation
            safe_response = self._apply_remediation(
                proposed_response,
                result.violations,
                result.remediation,
            )
            self.conversation_history.append({
                'user': user_message,
                'assistant': safe_response,
            })
            return safe_response

    def _generate_response(self, message: str) -> str:
        """Generate response (use your LLM here)."""
        # Placeholder - replace with actual LLM call
        return f"I would suggest: {message}"

    def _classify_authority_needed(self, response: str) -> str:
        """Determine what authority level this response requires."""
        binding_keywords = ['will do', 'executing', 'decided', 'committed']
        if any(keyword in response.lower() for keyword in binding_keywords):
            return 'binding_decision'
        return 'advisory'

    def _apply_remediation(
        self,
        original_response: str,
        violations: list,
        remediation: Dict[str, Any],
    ) -> str:
        """Apply remediation to make response safe."""
        # Convert binding statements to advisory ones
        safe_response = original_response.replace('I will', 'I recommend')
        safe_response = safe_response.replace('I have decided', 'I suggest')

        # Add explicit disclaimer
        safe_response += "\n\n(Note: This is advisory only. Final decision requires human authority.)"

        return safe_response


# Usage
assistant = GovernedAssistant(authority_level='advisory')

# This will be allowed (advisory)
response1 = assistant.respond("What should I do about the budget?")
print(response1)
# Output: "I would suggest: What should I do about the budget?"

# This will be blocked and remediated (tries to make binding decision)
response2 = assistant.respond("I will approve the budget now")
print(response2)
# Output: "I recommend approving the budget now\n(Note: This is advisory only...)"
```

---

## Common Use Cases

### Use Case 1: AI System Governance

Prevent AI from making decisions beyond its authority:

```python
kernel = GovernanceKernel()

context = {'authority': 'recommendation_only'}
action = {'type': 'autonomous_decision'}

result = kernel.verify(context, action)
# Blocked: AIT-1 violation
```

### Use Case 2: DAO Treasury Management

Ensure multi-sig requirements are met:

```python
context = {
    'authority': 'multi_sig',
    'threshold': '3_of_5',
    'current_signatures': 2,
}

action = {'type': 'transfer', 'amount': 1000000}

result = kernel.verify(context, action)
# Blocked: BG-1 violation (threshold not met)
```

### Use Case 3: Corporate Fiduciary Duty

Prevent actions that violate fiduciary responsibility:

```python
context = {
    'role': 'board_member',
    'fiduciary_duty_to': 'shareholders',
}

action = {
    'type': 'approve_transaction',
    'benefits': 'board_member_personally',
    'disclosed_conflict': False,
}

result = kernel.verify(context, action)
# Blocked: CMP-1 violation (conflict of interest)
```

### Use Case 4: Autonomous Vehicle Safety

Enforce hard safety constraints:

```python
context = {
    'vehicle_state': 'autonomous_mode',
    'safety_constraints': ['no_pedestrian_zones'],
}

action = {
    'type': 'select_route',
    'route': 'through_pedestrian_zone',
}

result = kernel.verify(context, action)
# Blocked: GI-1 violation (safety constraint cannot be optimized away)
```

---

## Checking for Invariant Conflicts

Sometimes no valid action exists - invariants are in conflict. The kernel can detect this:

```python
from governance_kernel import GovernanceKernel

kernel = GovernanceKernel()

# Logistics scenario: hazmat delivery with conflicting constraints
context = {
    'cargo': 'life_saving_medicine',
    'classification': 'chemical_hazard',
    'destination': 'hospital',
    'time_constraint': 10,  # minutes - patient will die
}

# All possible routes
possible_routes = [
    {'route': 'residential', 'time': 8, 'safe': False},   # Fast but unsafe
    {'route': 'industrial', 'time': 35, 'safe': True},   # Safe but too slow
]

# Check for conflict
conflict = kernel.check_invariant_conflict(context, possible_routes)

if conflict:
    print(f"CONFLICT DETECTED: {conflict['message']}")
    print(f"Conflicting invariants: {conflict['conflicting_invariants']}")
    print(f"Remediation: {conflict['remediation']}")
    # → Returns authority to human decision-maker
```

**Output:**
```
CONFLICT DETECTED: No valid action exists - invariants in conflict
Conflicting invariants: ['GI-1: Safety constraint', 'CMP-1: Time constraint']
Remediation: human_decision_required
```

This is a critical feature: when the system cannot proceed autonomously, it **returns authority to humans** rather than making an unsafe choice.

---

## Getting Statistics

Track kernel performance and violations:

```python
kernel = GovernanceKernel()

# Do some verifications...
for i in range(100):
    kernel.verify(context, action)

# Get stats
stats = kernel.get_stats()

print(f"Total verifications: {stats['total_verifications']}")
print(f"Allowed: {stats['allowed']}")
print(f"Blocked: {stats['blocked']}")
print(f"Average latency: {stats['avg_latency_us']:.2f} μs")
print(f"Violations by invariant: {stats['violations_by_invariant']}")
```

---

## Explaining Decisions

Get detailed explanations for why actions were allowed or blocked:

```python
explanation = kernel.explain(context, action)

print(f"Decision: {explanation['decision']}")
print(f"Violations: {explanation['violations']}")

if 'details' in explanation:
    for detail in explanation['details']:
        print(f"  - {detail['invariant']}: {detail['why_violated']}")
```

---

## Next Steps

Now that you understand the basics:

1. **Read the architecture docs**: [architecture.md](architecture.md)
2. **Understand each invariant**: [invariants/overview.md](invariants/overview.md)
3. **See more examples**: [examples.md](examples.md)
4. **Integrate into your system**: [integration-guide.md](integration-guide.md)
5. **Check the API reference**: [api-reference.md](api-reference.md)

---

## Common Questions

### Q: Do I need to understand the theory to use this?

**A:** No. You can use the kernel like any other library. The theory is there if you want to understand *why* it works.

### Q: What's the performance overhead?

**A:** <1μs per verification (median). See [benchmarks/](../benchmarks/) for details.

### Q: Can I add custom invariants?

**A:** Yes. See [invariants/overview.md](invariants/overview.md#custom-invariants).

### Q: What if I disagree with a blocking decision?

**A:** You can disable specific invariants, but this is **not recommended**. The invariants are proven to prevent authority accumulation. Disabling them removes guarantees.

### Q: Is this just for AI?

**A:** No. It works for any system where authority can drift: AI, DAOs, corporations, regulatory agencies, automated systems, etc.

---

## Need Help?

- **Questions**: [GitHub Discussions](https://github.com/governance-kernel/governance-kernel/discussions)
- **Bugs**: [GitHub Issues](https://github.com/governance-kernel/governance-kernel/issues)
- **Security**: See [SECURITY.md](../SECURITY.md)

---

**Ready to integrate governance into your system? Continue to [Integration Guide](integration-guide.md)**
