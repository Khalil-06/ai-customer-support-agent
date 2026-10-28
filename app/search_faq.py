import re

from sqlalchemy import text

from .database import SessionLocal


STOP_WORDS = {
    "how", "many", "can", "i", "a", "an", "the",
    "do", "to", "is", "are", "what", "when", "where",
    "my", "me", "you", "your", "of", "for", "in", "on"
}


def search_faq(question: str):
    words = re.findall(r"\b[a-zA-Z]+\b", question.lower())

    keywords = [
        word
        for word in words
        if word not in STOP_WORDS and len(word) > 2
    ]

    if not keywords:
        return []

    db = SessionLocal()

    try:
        conditions = []
        params = {}

        for index, keyword in enumerate(keywords):
            key = f"keyword_{index}"

            conditions.append(
                f"(question ILIKE :{key} OR answer ILIKE :{key})"
            )

            params[key] = f"%{keyword}%"

        query = text(f"""
            SELECT
                question,
                answer
            FROM faqs
            WHERE {" OR ".join(conditions)}
            LIMIT 5
        """)

        result = db.execute(query, params)

        return result.fetchall()

    finally:
        db.close()


if __name__ == "__main__":
    results = search_faq("How many days can I return a product?")

    for row in results:
        print("\nQuestion:", row.question)
        print("Answer:", row.answer)