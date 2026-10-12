from sqlalchemy import text
from .database import SessionLocal


def escalate_to_human(customer_id: int, reason: str):
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
                "subject": "Human Agent Escalation",
                "description": reason,
                "status": "Escalated"
            }
        )

        db.commit()

        return {
            "ticket_id": ticket_id,
            "status": "Escalated",
            "message": "Your request has been escalated to a human support agent."
        }

    finally:
        db.close()


if __name__ == "__main__":
    result = escalate_to_human(
        customer_id=3,
        reason="Customer requested to speak with a human agent."
    )

    print("\nESCALATION:")
    print(result)
    