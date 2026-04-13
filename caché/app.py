from fastapi import FastAPI
import redis

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
        result = "resultado_falso"
        return result
  
