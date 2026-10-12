import re

from .order_agent import answer_order_question
from .rag import generate_rag_response


def generate_chat_response(message: str):
    # Check whether the customer is asking about an order
    if re.search(r"\b(order|delivery|package|shipment)\b", message.lower()):
        order_response = answer_order_question(message)

        if order_response:
            return order_response

    # Otherwise use the RAG knowledge base
    return generate_rag_response(message)


if __name__ == "__main__":
    questions = [
        "Where is my order 2002?",
        "What is your return policy?"
    ]

    for question in questions:
        print("\nCustomer:", question)
        print("AI:", generate_chat_response(question))