# AI Code Reviewer - Sidecar
FROM python:3.12-alpine

WORKDIR /app

# Yardımcı os araçları
RUN apk add --no-cache bash procps grep curl wget

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
