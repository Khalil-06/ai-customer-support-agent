def chunk_text(text: str, chunk_size: int = 300):
    chunks = []

    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size].strip()

        if chunk:
            chunks.append(chunk)

    return chunks


if __name__ == "__main__":
    sample_text = """
    Customers can return eligible products within 7 days of delivery.
    Standard delivery usually takes 3 to 5 business days.
    Orders can be cancelled before they are shipped.
    Refunds are processed after the returned product is received.
    """

    chunks = chunk_text(sample_text)

    for index, chunk in enumerate(chunks, start=1):
        print(f"\n--- Chunk {index} ---")
        print(chunk)