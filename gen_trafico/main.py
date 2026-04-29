import os
import random
import asyncio
import httpx

NUM_WORKERS = 50      
TASA = 10
DISTRIBUCION = os.getenv("CACHE_DISTRIBUTION", "zipf")

def generar_confidence():
    return round(random.uniform(0, 1), 4)

consultas = ["Q1", "Q2", "Q3", "Q4", "Q5"]
zonas = ["Z1", "Z2", "Z3", "Z4", "Z5"]
pesos = [1 / (i + 1) for i in range(5)] 

def zipf():
    zona = random.choices(zonas, weights=pesos)[0]
    consulta = random.choices(consultas, weights=pesos)[0]
    return zona, consulta

def uniforme():
    zona = random.choice(zonas)
    consulta = random.choice(consultas)
    return zona, consulta

def generar_consulta():
    confidence = generar_confidence()

    if DISTRIBUCION == "zipf":
        zone, query = zipf()
    else:
        zone, query = uniforme()

    if query == "Q4":
        pesos_q4 = [1 if z != zone else 0 for z in zonas]
        zona_b = random.choices(zonas, weights=pesos_q4)[0]
        return {
            "query": query,
            "zone_id": zone,
            "params": {
                "zone_b": zona_b,
                "confidence_min": confidence
            }
        }
    elif query == "Q5":
        bins = random.randint(100, 200)
        return {
            "query": query,
            "zone_id": zone,
            "params": {"bins": bins}
        }
    else: 
        return {
            "query": query,
            "zone_id": zone,
            "params": {"confidence_min": confidence}
        }

async def worker(client: httpx.AsyncClient, worker_id: int):
    while True:
        data = generar_consulta()
        try:
            response = await client.post(
                "http://cache:8000/consulta",
                json=data,
                timeout=10.0
            )
            print(f"[{worker_id}] {response.status_code} | {data['query']} {data['zone_id']}")
        except httpx.ConnectError:
            print(f"[{worker_id}] ConnectError: nginx no disponible, reintentando...")
            await asyncio.sleep(2)
        except httpx.TimeoutException:
            print(f"[{worker_id}] Timeout: el sistema está saturado")
            await asyncio.sleep(1)
        except Exception as e:
            print(f"[{worker_id}] Error {type(e).__name__}: {e}")
            await asyncio.sleep(0.5)
        await asyncio.sleep(random.expovariate(TASA))

async def main():
    limits = httpx.Limits(
        max_connections=100,
        max_keepalive_connections=20
    )
    async with httpx.AsyncClient(limits=limits, timeout=10.0) as client:
        tasks = [
            asyncio.create_task(worker(client, i))
            for i in range(NUM_WORKERS)
        ]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())