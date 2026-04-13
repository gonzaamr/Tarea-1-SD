FROM python:3.11

WORKDIR /app

COPY . .

RUN pip install pandas numpy fastapi uvicorn

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]