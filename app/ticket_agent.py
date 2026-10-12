from sqlalchemy import text
from .database import SessionLocal


def create_ticket(customer_id: int, subject: str, description: str):
    db = SessionLocal()

    try:
        result = db.execute(
            text("""
                SELECT COALESCE(MAX(ticket_id), 5000) + 1
                FROM tickets
            """)
        )

        ticket_id = result.scalar()

        db.execute(
            text("""
                INSERT INTO tickets
                (ticket_id, customer_id, subject, description, status)
                VALUES
                (:ticket_id, :customer_id, :subject, :description, :status)
            """),
            {
                "ticket_id": ticket_id,
                "customer_id": customer_id,
                "subject": subject,
                "description": description,
                "status": "Open"
            }
        )

        db.commit()

        return {
            "ticket_id": ticket_id,
            "customer_id": customer_id,
            "subject": subject,
            "status": "Open"
        }

    finally:
        db.close()


if __name__ == "__main__":
    ticket = create_ticket(
        customer_id=3,
        subject="Damaged product",
        description="Customer received a damaged product."
    )

    print("\nTICKET CREATED:")
    print(ticket)