from .database import SessionLocal
from .ai import client
from sqlalchemy import text


def search_product(product_name: str, company_id: int):
    db = SessionLocal()

    try:
        result = db.execute(
            text("""
                SELECT product_id, name, price
                FROM products
                WHERE company_id = :company_id
                  AND LOWER(name) LIKE LOWER(:name)
                LIMIT 5
            """),
            {
                "company_id": company_id,
                "name": f"%{product_name}%"
            }
        ).fetchall()

        return [
            {
                "product_id": row.product_id,
                "name": row.name,
                "price": row.price
            }
            for row in result
        ]

    finally:
        db.close()


def answer_product_question(product_name: str, company_id: int):
    products = search_product(
        product_name,
        company_id
    )

    if not products:
        return f"Sorry, I couldn't find a product matching '{product_name}'."

    product_text = "\n".join(
        f"Product ID: {p['product_id']}, "
        f"Name: {p['name']}, "
        f"Price: ₹{p['price']}"
        for p in products
    )

    prompt = f"""
You are a customer support agent.

Available products from the database:

{product_text}

Customer is asking about:
{product_name}

Answer using ONLY the product information above.
Do not invent products or prices.
Keep the answer short and friendly.
"""

    response = client.models.generate_content(
        model="gemini-flash-lite-latest",
        contents=prompt
    )

    return response.text


if __name__ == "__main__":
    print(
        answer_product_question(
            "phone",
            1
        )
    )
