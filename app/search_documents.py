import re

from sqlalchemy import text

from .database import SessionLocal


STOP_WORDS = {
    "how", "many", "can", "i", "a", "an", "the",
    "do", "to", "is", "are", "what", "when", "where",
    "my", "me", "you", "your", "of", "for", "in", "on"
}


def search_documents(question: str, company_id: int):
    words = re.findall(r"\b[a-zA-Z]+\b", question.lower())

    keywords = [
        word for word in words
        if word not in STOP_WORDS and len(word) > 2
    ]

    if not keywords:
        return []

    db = SessionLocal()

    try:
        conditions = []
        params = {"company_id": company_id}

        for index, keyword in enumerate(keywords):
            key = f"keyword_{index}"
            conditions.append(f"chunk_text ILIKE :{key}")
            params[key] = f"%{keyword}%"

        query = text(f"""
            SELECT
                document_name,
                chunk_text
            FROM document_chunks
            WHERE company_id = :company_id
              AND ({' OR '.join(conditions)})
            LIMIT 5
        """)

        result = db.execute(query, params)

        return result.fetchall()

    finally:
        db.close()