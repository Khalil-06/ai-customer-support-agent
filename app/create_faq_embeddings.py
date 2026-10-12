from sentence_transformers import SentenceTransformer
from sqlalchemy import text
from .database import SessionLocal

model = SentenceTransformer("all-MiniLM-L6-v2")


def create_embeddings():
    db = SessionLocal()

    try:
        rows = db.execute(
            text("SELECT id, question, answer FROM faqs")
        ).fetchall()

        for row in rows:
            embedding = model.encode(row.question).tolist()

            db.execute(
                text("""
                    UPDATE faqs
                    SET embedding = :embedding
                    WHERE id = :id
                """),
                {
                    "embedding": str(embedding),
                    "id": row.id
                }
            )

        db.commit()
        print(f"Embeddings created for {len(rows)} FAQs.")

    finally:
        db.close()


if __name__ == "__main__":
    create_embeddings()