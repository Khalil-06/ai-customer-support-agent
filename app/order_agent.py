import re

from .tools import get_order_status
from .ai import client


def answer_order_question(message: str):
    match = re.search(r"\b\d{4,}\b", message)

    if not match:
        return None

    order_id = int(match.group())

    order = get_order_status(order_id)

    if not order:
        return f"Sorry, I couldn't find order {order_id}."

    prompt = f"""
You are a customer support agent.

The customer asked:
{message}

Real order information from the database:
Order ID: {order["order_id"]}
Status: {order["status"]}

Answer the customer using ONLY this database information.
Do not invent any other order details.
Keep the answer short and friendly.
"""

    response = client.models.generate_content(
        model="gemini-flash-lite-latest",
        contents=prompt
    )

    return response.text


if __name__ == "__main__":
    question = "Where is my order 2002?"

    answer = answer_order_question(question)

    print("\nAI ANSWER:")
    print(answer)