# AI Code Reviewer - Main Backend API
FROM python:3.12-slim

WORKDIR /app

# Sistem araçları
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Çevresel değişkeni Development veya Production'a göre ayarlayabilirsiniz
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Backend FastAPI'yi çalıştır
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
