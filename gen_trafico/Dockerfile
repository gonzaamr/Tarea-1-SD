FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .

RUN pip install --timeout 120 --retries 10 --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-u", "main.py"]