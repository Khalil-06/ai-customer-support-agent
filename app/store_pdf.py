from sqlalchemy import text
from sentence_transformers import SentenceTransformer

from .database import SessionLocal
from .pdf_reader import extract_text_from_pdf
from .chunker import chunk_text


# Load embedding model once
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def store_pdf(file_path: str, document_name: str, company_id: int):
    text_content = extract_text_from_pdf(file_path)
    chunks = chunk_text(text_content)

    db = SessionLocal()

    try:
        for chunk in chunks:

            # Generate 384-dimensional embedding
            embedding = embedding_model.encode(chunk).tolist()

            # Convert embedding to pgvector format
            embedding_string = "[" + ",".join(
                str(value) for value in embedding
            ) + "]"

            db.execute(
                text("""
                    INSERT INTO document_chunks
                    (
                        document_name,
                        chunk_text,
                        embedding,
                        company_id
                    )
                    VALUES
                    (
                        :document_name,
                        :chunk_text,
                        CAST(:embedding AS vector),
                        :company_id
                    )
                """),
                {
                    "document_name": document_name,
                    "chunk_text": chunk,
                    "embedding": embedding_string,
                    "company_id": company_id
                }
            )

        db.commit()

        print(f"Stored {len(chunks)} chunks with embeddings successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    store_pdf(
        "documents/company_faq.pdf",
        "company_faq.pdf",
        1
    )