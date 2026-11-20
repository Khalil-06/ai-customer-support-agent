
from sqlalchemy import text
from sqlalchemy.orm import Session

from .database import SessionLocal
from .embeddings import get_embedding_model
from .pdf_reader import extract_text_from_pdf
from .chunker import chunk_text


def store_pdf(
    file_path: str,
    document_name: str,
    company_id: int,
    db: Session | None = None
):
    """
    Extract text, generate embeddings and store PDF chunks.

    If an existing database session is provided, the caller controls
    the transaction and must commit or rollback.

    If no session is provided, this function manages its own session.
    """

    # --------------------------------------------------
    # 1. Extract PDF text
    # --------------------------------------------------

    text_content = extract_text_from_pdf(file_path)

    if not text_content or not text_content.strip():
        raise ValueError("No readable text found in the PDF.")

    # --------------------------------------------------
    # 2. Split text into chunks
    # --------------------------------------------------

    chunks = chunk_text(text_content)

    if not chunks:
        raise ValueError("No readable text chunks found in the PDF.")

    # --------------------------------------------------
    # 3. Generate embeddings BEFORE modifying database
    # --------------------------------------------------

    embedding_model = get_embedding_model()

    prepared_chunks = []

    for chunk in chunks:

        embedding = embedding_model.encode(chunk).tolist()

        embedding_string = "[" + ",".join(
            str(value) for value in embedding
        ) + "]"

        prepared_chunks.append({
            "document_name": document_name,
            "chunk_text": chunk,
            "embedding": embedding_string,
            "company_id": company_id
        })

    # --------------------------------------------------
    # 4. Use supplied session or create a new session
    # --------------------------------------------------

    owns_session = db is None

    if owns_session:
        db = SessionLocal()

    try:

        # --------------------------------------------------
        # 5. Delete previous chunks for this document
        # --------------------------------------------------

        db.execute(
            text("""
                DELETE FROM document_chunks
                WHERE company_id = :company_id
                  AND document_name = :document_name
            """),
            {
                "company_id": company_id,
                "document_name": document_name
            }
        )

        # --------------------------------------------------
        # 6. Insert new chunks
        # --------------------------------------------------

        for item in prepared_chunks:

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
                item
            )

        # --------------------------------------------------
        # 7. Commit only if this function owns the session
        # --------------------------------------------------

        if owns_session:
            db.commit()

        print(
            f"Successfully prepared and stored "
            f"{len(prepared_chunks)} chunks for {document_name}"
        )

        return len(prepared_chunks)

    except Exception:

        if owns_session:
            db.rollback()

        raise

    finally:

        if owns_session:
            db.close()


# --------------------------------------------------
# Standalone testing
# --------------------------------------------------

if __name__ == "__main__":

    store_pdf(
        file_path="documents/company_faq.pdf",
        document_name="company_faq.pdf",
        company_id=1
    )
