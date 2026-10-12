from sqlalchemy import text

from .database import SessionLocal


def get_conversation_history(conversation_id: int, limit: int = 10):
    db = SessionLocal()

    try:
        result = db.execute(
            text("""
                SELECT sender, message
                FROM messages
                WHERE conversation_id = :conversation_id
                ORDER BY id DESC
                LIMIT :limit
            """),
            {
                "conversation_id": conversation_id,
                "limit": limit
            }
        ).fetchall()

        messages = list(reversed(result))

        return [
            {
                "sender": row.sender,
                "message": row.message
            }
            for row in messages
        ]

    finally:
        db.close()


if __name__ == "__main__":
    history = get_conversation_history(1)

    print("\nCONVERSATION HISTORY:")

    for item in history:
        print(f"{item['sender']}: {item['message']}")