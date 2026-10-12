from sqlalchemy import text
from .database import SessionLocal


def get_order_status(order_id: int):
    db = SessionLocal()

    try:
        result = db.execute(
            text("""
                SELECT order_id, customer_id, status
                FROM orders
                WHERE order_id = :order_id
            """),
            {"order_id": order_id}
        ).fetchone()

        if not result:
            return None

        return {
            "order_id": result.order_id,
            "customer_id": result.customer_id,
            "status": result.status
        }

    finally:
        db.close()


if __name__ == "__main__":
    order = get_order_status(2002)

    print(order)