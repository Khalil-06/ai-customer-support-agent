from sentence_transformers import SentenceTransformer
from .pdf_reader import extract_text_from_pdf
from .chunker import chunk_text


model = SentenceTransformer("all-MiniLM-L6-v2")


def process_pdf(file_path: str):
    text = extract_text_from_pdf(file_path)

    chunks = chunk_text(text)

    print(f"Total chunks: {len(chunks)}")

    for index, chunk in enumerate(chunks, start=1):
        embedding = model.encode(chunk)

        print(f"\n--- Chunk {index} ---")
        print(chunk)
        print("Embedding size:", len(embedding))


if __name__ == "__main__":
    process_pdf("documents/company_faq.pdf")