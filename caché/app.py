from fastapi import FastAPI  # python -m uvicorn caché.app:app --reload
import redis
import json
from gen_respuesta.main import q1_count, q2_area, q3_density, q4_compare, q5_confidence_dist


app = FastAPI()
r = redis.Redis(host="localhost", port=6379)
print(r.ping())

@app.post("/consulta")
def consulta(datos: dict):
    key = f"{datos['query']}:{datos['zone_id']}:{datos['params']}"
    value = r.get(key)
    if value:
        return value.decode()  # HIT
    else:  # MISS
        query   = datos['query']
        zone_id = datos['zone_id']
        params  = datos['params']
        confidence_min = params.get('confidence_min', 0.0)

        if query == 'Q1':
            result = q1_count(zone_id, confidence_min)
        elif query == 'Q2':
            result = q2_area(zone_id, confidence_min)
        elif query == 'Q3':
            result = q3_density(zone_id, confidence_min)
        elif query == 'Q4':
            result = q4_compare(zone_id, params['zone_b'], confidence_min)
        elif query == 'Q5':
            result = q5_confidence_dist(zone_id, params.get('bins', 5))
        else:
            return {"error": "consulta no válida"}

        r.set(key, json.dumps(result))  # guardar en redis
        return result