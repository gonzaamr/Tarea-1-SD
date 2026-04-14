from fastapi import FastAPI  # python -m uvicorn caché.app:app --reload
import redis
import json
import requests

app = FastAPI()
r = redis.Redis(host="redis", port=6379)
print(r.ping())

@app.post("/consulta")
def consulta(datos: dict):
    query   = datos['query']
    zone_id = datos['zone_id']
    params  = datos['params']
    confidence_min = params.get('confidence_min', 0.0)

    if query == 'Q1':
        key = f"count:{zone_id}:conf={confidence_min}"
    elif query == 'Q2':
        key = f"area:{zone_id}:conf={confidence_min}"
    elif query == 'Q3':
        key = f"density:{zone_id}:conf={confidence_min}"
    elif query == 'Q4':
        key = f"compare:density:{zone_id}:{params['zone_b']}:conf={confidence_min}"
    elif query == 'Q5':
        key = f"confidence_dist:{zone_id}:bins={params.get('bins', 5)}"
    else:
        return {"error": "consulta no válida"}

    value = r.get(key)
    if value:
        return json.loads(value)  # HIT
    else:
        try:
            response = requests.post(
                "http://gen_respuesta:8001/respuesta",
                json=datos
            )

            result = response.json()
            
        except Exception as e:
            return {"error": str(e)}

        r.set(key, json.dumps(result), ex=90)
        return result