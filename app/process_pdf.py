from .store_pdf import store_pdf


def process_pdf(file_path: str, document_name: str, company_id: int):
    store_pdf(
        file_path=file_path,
        document_name=document_name,
        company_id=company_id
    )


if __name__ == "__main__":
    process_pdf(
        "documents/company_faq.pdf",
        "company_faq.pdf",
        1
    )