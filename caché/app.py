from fastapi import FastAPI #python -m uvicorn caché.app:app --reload
import redis
from gen_respuesta.main import calculo # mientras no hayan contenedores

app = FastAPI()

r = redis.Redis(host="localhost", port=6379)
print(r.ping())

@app.post("/consulta")
def consulta(data:dict):
    key =  f"{data['query']}:{data['zone']}:{data['params']}"
    value = r.get(key)

    if value:
        return value.decode() #HIT
    else:
        if(calculo(data)):
            print("calculo recibido")
            return calculo(data)
  
