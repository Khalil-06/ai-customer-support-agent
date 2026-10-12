from pypdf import PdfReader


def extract_text_from_pdf(file_path: str):
    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


if __name__ == "__main__":
    pdf_path = "documents/company_faq.pdf"

    text = extract_text_from_pdf(pdf_path)

    print("PDF TEXT:")
    print(text)