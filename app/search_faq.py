from sqlalchemy import text

from .database import SessionLocal


def search_faq(question: str, company_id: int):
    db = SessionLocal()

    try:
        result = db.execute(
            text("""
                SELECT
                    question,
                    answer
                FROM faqs
                WHERE company_id = :company_id
                  AND (
                      question ILIKE :q1
                      OR answer ILIKE :q1
                  )
                LIMIT 5
            """),
            {
                "company_id": company_id,
                "q1": f"%{question}%"
            }
        )

        return result.fetchall()

    finally:
        db.close()


if __name__ == "__main__":
    results = search_faq(
        "How can I return a product?",
        company_id=1
    )

    for row in results:
        print("\nQuestion:", row.question)
        print("Answer:", row.answer)