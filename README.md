# Tarea 1 — Sistemas Distribuidos

## Requisitos

Antes de ejecutar el proyecto, asegúrate de contar con:

- Sistema operativo **Linux** o **WSL**
- **Docker** instalado  
  ```bash
  sudo apt install docker
  ```
- Archivo de configuración `.env` en la raíz del proyecto con el siguiente formato:

```env
# --- Configuración del entorno ---

CACHE_SIZE_MB=50        # Opciones: 50, 200, 500
CACHE_POLICY=allkeys-lru  # Opciones: allkeys-lru, allkeys-lfu, volatile-ttl (FIFO)
CACHE_TTL=1000         # Tiempo de vida en segundos
CACHE_DISTRIBUTION=uniforme  # Opciones: uniforme, zipf
```

---

## Instalación y uso

### 1. Clonar el repositorio

```bash
git clone https://github.com/gonzaamr/Tarea-1-SD
cd Tarea-1-SD
```

---

### 2. Levantar el sistema

Construye y ejecuta todos los servicios definidos en `docker-compose.yml`:

```bash
sudo docker compose up --build
```

---

### 3. Detener el tráfico

Si deseas detener únicamente la generación de tráfico:

```bash
sudo docker compose stop trafico
```

---

### 4. Obtener métricas

Para generar un resumen de métricas de la simulación:

```bash
sudo docker exec -it tarea-1-sd-master-metricas-1 python analisis_metricas.py
```

---

### 5. Reiniciar la simulación

Si quieres ejecutar nuevamente la simulación desde cero:

1. Detén la ejecución actual:
   ```bash
   Ctrl + C
   ```

2. Elimina contenedores y volúmenes:
   ```bash
   sudo docker compose down -v
   ```

3. (Opcional) Modifica los parámetros en el archivo `.env`

4. Vuelve a ejecutar desde el paso 2

---

##  Notas

- Asegúrate de que el archivo `.env` esté correctamente configurado antes de levantar los servicios.
- Los parámetros permiten experimentar con distintas políticas de caché y distribuciones de carga. 