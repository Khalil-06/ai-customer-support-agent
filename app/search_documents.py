from sqlalchemy import text

from .database import SessionLocal
from .embeddings import get_embedding_model


def search_documents(question: str, company_id: int, limit: int = 5):

    # Generate 384-dimensional question embedding
    embedding_model = get_embedding_model()
    question_embedding = embedding_model.encode(question).tolist()
    # Convert embedding to pgvector format
    embedding_string = "[" + ",".join(
        str(value) for value in question_embedding
    ) + "]"

    db = SessionLocal()

    try:
        query = text("""
            SELECT
                document_name,
                chunk_text,
                embedding <=> CAST(:embedding AS vector) AS distance
            FROM document_chunks
            WHERE company_id = :company_id
              AND embedding IS NOT NULL
            ORDER BY embedding <=> CAST(:embedding AS vector)
            LIMIT :limit
        """)

        result = db.execute(
            query,
            {
                "embedding": embedding_string,
                "company_id": company_id,
                "limit": limit
            }
        )

        return result.fetchall()

    finally:
        db.close()