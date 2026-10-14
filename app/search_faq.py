from sentence_transformers import SentenceTransformer
from sqlalchemy import text
from .database import SessionLocal

model = SentenceTransformer("all-MiniLM-L6-v2")


def search_faq(question: str, company_id: int):
    embedding = model.encode(question).tolist()

    db = SessionLocal()

    try:
        result = db.execute(
            text("""
                SELECT
                    question,
                    answer,
                    embedding <=> CAST(:embedding AS vector) AS distance
                FROM faqs
                WHERE embedding IS NOT NULL
                  AND company_id = :company_id
                ORDER BY embedding <=> CAST(:embedding AS vector)
                LIMIT 3
            """),
            {
                "embedding": str(embedding),
                "company_id": company_id
            }
        )

        return result.fetchall()

    finally:
        db.close()


if __name__ == "__main__":
    question = "When will my package arrive?"

    results = search_faq(question, company_id=1)
    for row in results:
        print("\nQuestion:", row.question)
        print("Answer:", row.answer)
        print("Distance:", row.distance)