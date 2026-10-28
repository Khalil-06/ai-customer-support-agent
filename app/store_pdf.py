from sqlalchemy import text

from .database import SessionLocal
from .pdf_reader import extract_text_from_pdf
from .chunker import chunk_text


def store_pdf(file_path: str, document_name: str, company_id: int):
    text_content = extract_text_from_pdf(file_path)
    chunks = chunk_text(text_content)

    db = SessionLocal()

    try:
        for chunk in chunks:
            db.execute(
                text("""
                    INSERT INTO document_chunks
                    (document_name, chunk_text, company_id)
                    VALUES
                    (:document_name, :chunk_text, :company_id)
                """),
                {
                    "document_name": document_name,
                    "chunk_text": chunk,
                    "company_id": company_id
                }
            )

        db.commit()

        print(f"Stored {len(chunks)} chunks successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    store_pdf(
        "documents/company_faq.pdf",
        "company_faq.pdf",
        1
    )