from .search_documents import search_documents
from .ai import client


def generate_rag_response(question: str) -> str:
    results = search_documents(question)

    context = ""

    for row in results:
        context += f"\n{row.chunk_text}\n"

    prompt = f"""
You are an AI customer support agent.

Answer the customer's question using ONLY the information
provided in the knowledge base below.

Knowledge Base:
{context}

Customer Question:
{question}

Rules:
- Do not invent information.
- If the answer is not available in the knowledge base,
  say that the information is not available.
- Keep the answer short and helpful.
"""

    response = client.models.generate_content(
        model="gemini-flash-lite-latest",
        contents=prompt
    )

    return response.text


if __name__ == "__main__":
    question = "How many days do I have to return a product?"

    answer = generate_rag_response(question)

    print("\nAI ANSWER:")
    print(answer)