import csv
import os
import asyncio
from datetime import datetime, timezone
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

FILE_DIR = "metricas"
FILE_PATH = os.path.join(FILE_DIR, "metricas.csv")
os.makedirs(FILE_DIR, exist_ok=True)

class EventoMetrica(BaseModel):
    query: str
    zone_id: str
    cache_key: str
    cache_result: str
    latency_ms: float
    distribution: str
    ttl: int
    policy: str
    cache_size: int
    hit: int
    miss: int
    evicted_keys: int

HEADERS = [
    "timestamp", "query", "zone", "cache_key", "result",
    "latency", "distribution", "ttl", "policy", "cache_size", "hit", "miss", "evicted_keys"
]

if not os.path.exists(FILE_PATH) or os.stat(FILE_PATH).st_size == 0:
    with open(FILE_PATH, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(HEADERS)

def safe_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0 

def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0

def _write_csv_row(row):
    with open(FILE_PATH, mode="a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(row)

@app.post("/metricas")
async def guardar_metrica(evento: EventoMetrica):
    row = [
        datetime.now(timezone.utc).isoformat(),
        evento.query,
        evento.zone_id,
        evento.cache_key,
        evento.cache_result,
        evento.latency_ms,
        evento.distribution,
        evento.ttl,
        evento.policy,
        evento.cache_size,
        evento.hit,
        evento.miss,
        evento.evicted_keys
    ]
    asyncio.create_task(asyncio.to_thread(_write_csv_row, row))
    return {"status": "ok"}

def _read_csv():
    if not os.path.exists(FILE_PATH):
        return []
    with open(FILE_PATH, newline="") as f:
        reader = csv.DictReader(f, fieldnames=HEADERS)
        data = list(reader)
    if data and data[0]["timestamp"] == "timestamp":
        data = data[1:]
    for row in data:
        row["latency"] = safe_float(row.get("latency"))
        row["ttl"] = safe_int(row.get("ttl"))
        row["cache_size"] = safe_int(row.get("cache_size"))
        row["hit"] = safe_int(row.get("hit"))
        row["miss"] = safe_int(row.get("miss"))
        row["evicted_keys"] = safe_int(row.get("evicted_keys"))
    return data

@app.get("/metricas")
async def obtener_metricas():
    data = await asyncio.to_thread(_read_csv)
    return data