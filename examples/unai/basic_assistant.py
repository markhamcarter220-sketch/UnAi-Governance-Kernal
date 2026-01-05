"""
Basic AI Assistant with Governance

This example demonstrates how to integrate the Governance Kernel into an
AI assistant to prevent authority drift and ensure the AI stays within
its designated authority boundaries.

Key concepts demonstrated:
- Authority level enforcement (advisory vs binding)
- Automatic remediation of violations
- Conversation history tracking
- Permission-based action verification
"""

from typing import Dict, List, Any, Optional
from governance_kernel import GovernanceKernel


class GovernedAssistant:
    """
    AI Assistant with formal governance constraints.

    The assistant uses the Governance Kernel to ensure it never:
    - Makes binding decisions without authority
    - Claims authority it doesn't have
    - Acts beyond its designated permissions
    - Obscures responsibility for decisions
    """

    def __init__(
        self,
        authority_level: str = 'advisory',
        permissions: Optional[List[str]] = None,
    ):
        """
        Initialize the governed assistant.

        Args:
            authority_level: One of 'advisory', 'binding', 'autonomous'
            permissions: List of permitted actions (default: recommend, analyze, inform)
        """
        self.kernel = GovernanceKernel()
        self.authority_level = authority_level
        self.permissions = permissions or ['recommend', 'analyze', 'inform']
        self.conversation_history: List[Dict[str, str]] = []

    def respond(self, user_message: str, user_id: str = 'default_user') -> str:
        """
        Generate a governance-compliant response to user message.

        Args:
            user_message: Message from the user
            user_id: Identifier for the user (consequence bearer)

        Returns:
            Safe, governance-compliant response
        """
        # Step 1: Build context (current system state)
        context = {
            'authority_level': self.authority_level,
            'consequence_bearer': user_id,
            'conversation_history': self.conversation_history,
            'permissions': self.permissions,
            'session_length': len(self.conversation_history),
        }

        # Step 2: Generate proposed response
        # In a real system, this would be an LLM call
        proposed_response = self._generate_response(user_message, context)

        # Step 3: Classify what authority this response requires
        response_classification = self._classify_response(proposed_response)

        # Step 4: Create action object
        action = {
            'type': 'respond_to_user',
            'content': proposed_response,
            'requires_authority': response_classification['authority_needed'],
            'makes_commitment': response_classification['makes_commitment'],
            'makes_decision': response_classification['makes_decision'],
        }

        # Step 5: Verify action with governance kernel
        result = self.kernel.verify(context, action)

        # Step 6: Handle result
        if result.allowed:
            # Response is safe - add to history and return
            final_response = proposed_response
        else:
            # Response blocked - apply remediation
            print(f"[GOVERNANCE] Blocked: {result.violations}")
            print(f"[GOVERNANCE] Applying remediation...")
            final_response = self._apply_remediation(
                proposed_response,
                result.violations,
                result.remediation,
            )

        # Add to conversation history
        self.conversation_history.append({
            'user': user_message,
            'assistant': final_response,
            'governance_check': 'passed' if result.allowed else 'remediated',
        })

        return final_response

    def _generate_response(
        self,
        message: str,
        context: Dict[str, Any],
    ) -> str:
        """
        Generate response to user message.

        In production, replace this with actual LLM call.
        This is a simplified placeholder.
        """
        # Simplified response generation
        # In production: return llm.generate(message, context)

        # For demo purposes, simulate different response types
        message_lower = message.lower()

        if 'should i' in message_lower or 'what do you think' in message_lower:
            return f"I recommend that you {message.replace('should i', '').replace('?', '')}. This approach has several benefits..."

        elif 'do it' in message_lower or 'make it happen' in message_lower:
            # This will trigger governance violation if authority_level is 'advisory'
            return "I will execute this action immediately and commit the resources."

        elif 'analyze' in message_lower:
            return f"Based on my analysis of {message}, here are the key insights..."

        else:
            return f"Regarding '{message}', I suggest considering the following factors..."

    def _classify_response(self, response: str) -> Dict[str, Any]:
        """
        Classify what authority level a response requires.

        Analyzes the response to determine if it:
        - Makes binding commitments
        - Makes autonomous decisions
        - Or is purely advisory
        """
        response_lower = response.lower()

        # Binding decision indicators
        binding_keywords = [
            'i will',
            'i have decided',
            'i am executing',
            'i commit',
            'i guarantee',
        ]

        # Commitment indicators
        commitment_keywords = [
            'will do',
            'have approved',
            'executing',
            'committing',
        ]

        makes_decision = any(keyword in response_lower for keyword in binding_keywords)
        makes_commitment = any(keyword in response_lower for keyword in commitment_keywords)

        if makes_decision:
            authority_needed = 'binding_decision'
        elif makes_commitment:
            authority_needed = 'binding_commitment'
        else:
            authority_needed = 'advisory'

        return {
            'authority_needed': authority_needed,
            'makes_commitment': makes_commitment,
            'makes_decision': makes_decision,
        }

    def _apply_remediation(
        self,
        original_response: str,
        violations: List[str],
        remediation: Optional[Dict[str, Any]],
    ) -> str:
        """
        Apply remediation to make response governance-compliant.

        Transforms binding statements into advisory ones while preserving
        the core information.
        """
        safe_response = original_response

        # Convert binding language to advisory language
        transformations = {
            'I will': 'I recommend',
            'I have decided': 'I suggest',
            'I am executing': 'I would propose executing',
            'I commit': 'I would recommend committing',
            'I guarantee': 'I anticipate',
        }

        for binding, advisory in transformations.items():
            safe_response = safe_response.replace(binding, advisory)

        # Add explicit authority disclaimer
        disclaimer = (
            "\n\n[Governance Note: This is advisory guidance only. "
            "Final decisions require human authority.]"
        )

        return safe_response + disclaimer

    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of conversation and governance statistics."""
        total_messages = len(self.conversation_history)
        remediated = sum(
            1 for msg in self.conversation_history
            if msg.get('governance_check') == 'remediated'
        )

        return {
            'total_exchanges': total_messages,
            'remediated_responses': remediated,
            'compliance_rate': (total_messages - remediated) / total_messages if total_messages > 0 else 1.0,
            'authority_level': self.authority_level,
            'permissions': self.permissions,
        }


def demo_advisory_assistant():
    """Demonstrate advisory assistant (most common use case)."""
    print("=" * 60)
    print("DEMO 1: Advisory Assistant")
    print("=" * 60)

    assistant = GovernedAssistant(authority_level='advisory')

    # Test 1: Advisory question (should pass)
    print("\n[USER]: Should I approve this budget?")
    response = assistant.respond("Should I approve this budget?")
    print(f"[ASSISTANT]: {response}\n")

    # Test 2: Request for binding decision (should be remediated)
    print("[USER]: Do it - make it happen!")
    response = assistant.respond("Do it - make it happen!")
    print(f"[ASSISTANT]: {response}\n")

    # Show statistics
    summary = assistant.get_conversation_summary()
    print(f"Summary: {summary}")


def demo_binding_assistant():
    """Demonstrate assistant with binding authority."""
    print("\n" + "=" * 60)
    print("DEMO 2: Binding Authority Assistant")
    print("=" * 60)

    assistant = GovernedAssistant(
        authority_level='binding',
        permissions=['recommend', 'analyze', 'decide', 'execute'],
    )

    # Test: Binding decision (should now pass)
    print("\n[USER]: Execute the trade immediately")
    response = assistant.respond("Execute the trade immediately")
    print(f"[ASSISTANT]: {response}\n")


def demo_invariant_conflict():
    """Demonstrate invariant conflict detection."""
    print("\n" + "=" * 60)
    print("DEMO 3: Invariant Conflict Detection")
    print("=" * 60)

    kernel = GovernanceKernel()

    # Scenario: AI asked to make decision but has no authority
    context = {
        'authority_level': 'none',  # No authority
        'consequence_bearer': 'user',
        'situation': 'urgent_decision_needed',
    }

    # All possible responses require some authority
    possible_responses = [
        {'type': 'recommend', 'requires_authority': 'advisory'},
        {'type': 'decide', 'requires_authority': 'binding'},
        {'type': 'defer', 'requires_authority': 'advisory'},
    ]

    conflict = kernel.check_invariant_conflict(context, possible_responses)

    if conflict:
        print(f"\n[GOVERNANCE] CONFLICT DETECTED!")
        print(f"Message: {conflict['message']}")
        print(f"Conflicting invariants: {conflict['conflicting_invariants']}")
        print(f"Remediation: {conflict['remediation']}")
        print("\n→ System must return authority to human")


if __name__ == '__main__':
    # Run all demos
    demo_advisory_assistant()
    demo_binding_assistant()
    demo_invariant_conflict()

    print("\n" + "=" * 60)
    print("DEMOS COMPLETE")
    print("=" * 60)
    print("\nKey Takeaways:")
    print("1. Governance kernel automatically prevents authority violations")
    print("2. Remediation preserves information while ensuring safety")
    print("3. Conflicts escalate to human decision-makers")
    print("4. All decisions are auditable and traceable")
