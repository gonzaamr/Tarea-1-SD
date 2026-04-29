FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --timeout 120 --retries 10 --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4"]