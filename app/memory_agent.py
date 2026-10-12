from .memory import get_conversation_history
from .ai import client


def generate_memory_response(conversation_id: int, message: str):
    history = get_conversation_history(conversation_id)

    conversation_text = ""

    for item in history:
        conversation_text += (
            f"{item['sender']}: {item['message']}\n"
        )

    prompt = f"""
You are an AI customer support agent.

Previous conversation:
{conversation_text}

New customer message:
{message}

Use the previous conversation to understand context.

Rules:
- Be friendly and concise.
- Do not invent information.
- If information is unavailable, say so.
- Remember what the customer previously said.
"""

    response = client.models.generate_content(
        model="gemini-flash-lite-latest",
        contents=prompt
    )

    return response.text


if __name__ == "__main__":
    answer = generate_memory_response(
        conversation_id=1,
        message="Can you tell me more about that?"
    )

    print("\nAI ANSWER:")
    print(answer)