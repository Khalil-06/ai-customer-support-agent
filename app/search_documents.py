from sqlalchemy import text
from sentence_transformers import SentenceTransformer

from .database import SessionLocal


# Load embedding model once
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def search_documents(question: str, company_id: int, limit: int = 5):

    # Convert question into a 384-dimensional embedding
    question_embedding = embedding_model.encode(question).tolist()

    # Convert to pgvector format
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