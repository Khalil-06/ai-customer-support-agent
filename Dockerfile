FROM python:3.11-slim

WORKDIR /APP

ENV PYTHONDONTWRITEBYCODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

RUN pip install --default-timeout=300 --retries=10 --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu torch

COPY requirements.txt .

RUN pip install --default-timeout=300 --retries=10 --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
