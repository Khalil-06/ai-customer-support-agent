from sentence_transformers import SentenceTransformer
from sqlalchemy import text

from .database import SessionLocal


model = SentenceTransformer("all-MiniLM-L6-v2")


def search_documents(question: str, company_id: int):
    embedding = model.encode(question).tolist()

    db = SessionLocal()

    try:
        result = db.execute(
            text("""
                SELECT
                    document_name,
                    chunk_text,
                    embedding <=> CAST(:embedding AS vector) AS distance
                FROM document_chunks
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
    question = "How many days do I have to return a product?"

    results = search_documents(question, company_id=1)

    for row in results:
        print("\nDocument:", row.document_name)
        print("Content:", row.chunk_text)
        print("Distance:", row.distance)