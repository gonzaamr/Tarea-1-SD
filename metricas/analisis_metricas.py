import pandas as pd
import os

# Rutas internas del contenedor
INPUT_FILE = "/app/metricas/metricas.csv"
OUTPUT_FILE = "/app/metricas/resumen_metricas.csv"

def procesar():
    if not os.path.exists(INPUT_FILE) or os.stat(INPUT_FILE).st_size == 0:
        print("El archivo de métricas está vacío o no existe.")
        return

    # Leer datos (usando nombres de columnas del app.py)
    df = pd.read_csv(INPUT_FILE)
    
    # Asegurar tipos de datos
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["hit"] = (df["result"] == "hit").astype(int)

    def calc(gr):
        total = len(gr)
        hits = gr["hit"].sum()
        
        # Duración del experimento
        tiempo = (gr["timestamp"].max() - gr["timestamp"].min()).total_seconds()
        throughput = total / tiempo if tiempo > 0 else 0
        
        # Eviction rate basado en el máximo reportado (ya que es acumulativo en Redis)
        evictions = gr["evicted_keys"].max()
        
        return pd.Series({
            "hit_rate": hits / total if total else 0,
            "p50": gr["latency"].quantile(0.5),
            "p95": gr["latency"].quantile(0.95),
            "throughput": throughput,
            "total_evictions": evictions
        })

    # Procesar
    resumen = df.groupby(["distribution", "ttl", "policy", "cache_size"]).apply(calc, include_groups=False).reset_index()
    
    # Guardar resumen
    resumen.to_csv(OUTPUT_FILE, index=False)
    print(f"Resumen generado exitosamente en {OUTPUT_FILE}")

    # --- LIMPIEZA ---
    # Vaciamos el archivo pero mantenemos los headers para el app.py
    headers = "timestamp,query,zone,cache_key,result,latency,distribution,ttl,policy,cache_size,hit,miss,evicted_keys\n"
    with open(INPUT_FILE, "w") as f:
        f.write(headers)
    print("Archivo metricas.csv vaciado para el siguiente experimento.")

if __name__ == "__main__":
    procesar()