import re

from .escalation import escalate_to_human


ESCALATION_PHRASES = [
    "human agent",
    "human",
    "real person",
    "customer support agent",
    "connect me to an agent",
    "talk to an agent",
    "speak to an agent",
    "speak to a human",
    "talk to a human",
    "real agent",
]


def detect_escalation(message: str):
    message_lower = message.lower()

    for phrase in ESCALATION_PHRASES:
        if phrase in message_lower:
            return True

    return False


def handle_escalation(customer_id: int, message: str):
    if detect_escalation(message):
        return escalate_to_human(
            customer_id=customer_id,
            reason=message
        )

    return None


if __name__ == "__main__":
    message = "I want to speak to a human agent."

    result = handle_escalation(
        customer_id=3,
        message=message
    )

    if result:
        print("\nESCALATION DETECTED:")
        print(result)
    else:
        print("\nNo escalation required.")