import random
import sys
import requests
import time

consultas = ["Q1","Q2","Q3","Q4","Q5"]
zonas = ["Z1","Z2","Z3","Z4","Z5"]
pesos = [1/(i+1) for i in range(len(zonas))]

def zipf():
    zona = random.choices(zonas, weights=pesos)[0]
    consulta = random.choices(consultas, weights=pesos)[0]
    return zona, consulta

def uniforme():
    zona = random.choices(zonas)[0]
    consulta = random.choices(consultas)[0]
    return zona, consulta


def consulta():
    confidence = round(random.uniform(0, 1), 2)
    zone, query = uniforme()
    
    if query == "Q4":
        pesos_q4 = [1 if zona != zone else 0 for zona in zonas]
        zona_b = random.choices(zonas, weights=pesos_q4)[0]
        datos = {
            "query": query,
            "zone_id": zone,
            "params": {
                "zone_b": zona_b,
                "confidence_min": confidence
            }   
        }
    elif query == "Q5":
        bins = random.randint(3, 10)
        datos = {
            "query": query,
            "zone_id": zone,
            "params": {
                "bins": bins
            }   
        }
    else:
        datos = {
            "query": query,
            "zone_id": zone,
            "params": {
                "confidence_min": confidence
            }   
        }
    
    print(datos)
    return datos

def main():
    data = consulta()
    try:
        response = requests.post(
            "http://api:8000/consulta",   
            json=data
        )
        print(response.json())

    except Exception as e:
        print("Error:", e)

while True:
    main()
    time.sleep(random.expovariate(2))   #promedio de 2 consultas/seg, pero tiempo random

    
    