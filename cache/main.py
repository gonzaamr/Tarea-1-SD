import os
import json
import asyncio
from time import time
from fastapi import FastAPI
import httpx
import redis.asyncio as redis
import socket

app = FastAPI()
hit = 0
miss = 0
ttl = int(os.getenv("CACHE_TTL", 600))
distribution = os.getenv("CACHE_DISTRIBUTION", "zipf")
politica = os.getenv("CACHE_POLICY", "LFU")
buffer_simulado = "X" * 30000

r = redis.Redis(host="redis", port=6379, decode_responses=True)

client = httpx.AsyncClient(
    limits=httpx.Limits(
        max_connections=500,
        max_keepalive_connections=100
    ),
    timeout=10.0
)

_background_tasks: set[asyncio.Task] = set()

def _crear_task_background(coro):
    task = asyncio.create_task(coro)
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)
    return task

@app.get("/ping")
async def ping():
    return {"contenedor": socket.gethostname()}

def generar_cache_key(query: str, zone_id: str, params: dict) -> str:
    if query == "Q1":
        return f"count:{zone_id}:conf={params.get('confidence_min', 0.0)}"
    elif query == "Q2":
        return f"area:{zone_id}:conf={params.get('confidence_min', 0.0)}"
    elif query == "Q3":
        return f"density:{zone_id}:conf={params.get('confidence_min', 0.0)}"
    elif query == "Q4":
        zone_b = params.get("zone_b")
        return f"compare:density:{zone_id}:{zone_b}:conf={params.get('confidence_min', 0.0)}"
    elif query == "Q5":
        return f"confidence_dist:{zone_id}:bins={params.get('bins', 5)}"
    return f"{query}:{zone_id}"

async def enviar_metrica(query, zone_id, cache_key, cache_result, latency_ms, distribution, ttl):
    try:
        info = await r.info("stats")
        evictions = info["evicted_keys"]
        await client.post(
            "http://metricas:8002/metricas",
            json={
                "query": query,
                "zone_id": zone_id,
                "cache_key": cache_key,
                "cache_result": cache_result,
                "latency_ms": latency_ms,
                "distribution": distribution,
                "ttl": ttl,
                "policy": politica,
                "cache_size": int(os.getenv("CACHE_SIZE_MB", 50)),
                "hit": hit,
                "miss": miss,
                "evicted_keys": evictions
            }
        )
    except Exception as e:
        print(f"[métricas] Error: {type(e).__name__}: {e}")

@app.post("/consulta")
async def consulta(datos: dict):
    global hit, miss
    start = time()

    query = datos["query"]
    zone_id = datos["zone_id"]
    params = datos["params"]
    key = generar_cache_key(query, zone_id, params)

    value = await r.get(key)

    if value:
        hit += 1
        latency = (time() - start) * 1000
        _crear_task_background(
            enviar_metrica(query, zone_id, key, "hit", latency, distribution, ttl)
        )
        return json.loads(value)

    miss += 1
    try:
        response = await client.post(
            "http://respuesta:8080/respuesta",
            json=datos
        )
        result = response.json()
    except httpx.TimeoutException:
        return {"error": "timeout al contactar generador de respuestas"}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}

    resultado_engordado = {"data": result, "metadata_geo": buffer_simulado}
    await r.set(key, json.dumps(resultado_engordado), ex=ttl)

    latency = (time() - start) * 1000
    _crear_task_background(
        enviar_metrica(query, zone_id, key, "miss", latency, distribution, ttl)
    )

    return result