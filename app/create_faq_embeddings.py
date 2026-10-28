from sqlalchemy import text

from .database import SessionLocal


def create_faq_entries():
    db = SessionLocal()

    try:
        faqs = [
            {
                "question": "How many days do I have to return a product?",
                "answer": "Products can be returned within 7 days of delivery."
            },
            {
                "question": "How can I contact customer support?",
                "answer": "You can contact customer support through the support chat."
            },
            {
                "question": "How long does delivery take?",
                "answer": "Standard delivery usually takes 3 to 5 business days."
            }
        ]

        for faq in faqs:
            db.execute(
                text("""
                    INSERT INTO faqs
                    (question, answer, company_id)
                    VALUES
                    (:question, :answer, :company_id)
                """),
                {
                    "question": faq["question"],
                    "answer": faq["answer"],
                    "company_id": 1
                }
            )

        db.commit()

        print(f"Stored {len(faqs)} FAQs successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    create_faq_entries()