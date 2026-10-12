from sentence_transformers import SentenceTransformer
from sqlalchemy import text

from .database import SessionLocal
from .pdf_reader import extract_text_from_pdf
from .chunker import chunk_text


model = SentenceTransformer("all-MiniLM-L6-v2")


def store_pdf(file_path: str, document_name: str):
    text_content = extract_text_from_pdf(file_path)
    chunks = chunk_text(text_content)

    db = SessionLocal()

    try:
        for chunk in chunks:
            embedding = model.encode(chunk).tolist()

            db.execute(
                text("""
                    INSERT INTO document_chunks
                    (document_name, chunk_text, embedding)
                    VALUES
                    (:document_name, :chunk_text,
                     CAST(:embedding AS vector))
                """),
                {
                    "document_name": document_name,
                    "chunk_text": chunk,
                    "embedding": str(embedding)
                }
            )

        db.commit()

        print(f"Stored {len(chunks)} chunks successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    store_pdf(
        "documents/company_faq.pdf",
        "company_faq.pdf"
    )