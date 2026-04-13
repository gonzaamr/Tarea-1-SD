import os
import pandas as pd
import numpy as np
from statistics import mean

ZONAS = {
    'Z1': {'lat_min': -33.445, 'lat_max': -33.420, 'lon_min': -70.640, 'lon_max': -70.600},
    'Z2': {'lat_min': -33.420, 'lat_max': -33.390, 'lon_min': -70.600, 'lon_max': -70.550},
    'Z3': {'lat_min': -33.530, 'lat_max': -33.490, 'lon_min': -70.790, 'lon_max': -70.740},
    'Z4': {'lat_min': -33.460, 'lat_max': -33.430, 'lon_min': -70.670, 'lon_max': -70.630},
    'Z5': {'lat_min': -33.470, 'lat_max': -33.430, 'lon_min': -70.810, 'lon_max': -70.760},
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(BASE_DIR, '967.csv'))

# Precarga zonas al inicio
zona_data = {}
for zid, z in ZONAS.items():
    zona_data[zid] = df[
        (df['latitude'] >= z['lat_min']) & (df['latitude'] <= z['lat_max']) &
        (df['longitude'] >= z['lon_min']) & (df['longitude'] <= z['lon_max'])
    ]

def data(zone_id):
    return zona_data.get(zone_id, None)

def q1_count(zone_id, confidence_min=0.0):
    records = zona_data[zone_id]
    return int(len(records[records['confidence'] >= confidence_min]))

def q2_area(zone_id, confidence_min=0.0):
    records = zona_data[zone_id]
    filtered = records[records['confidence'] >= confidence_min]['area_in_meters']
    return {
        "avg_area": float(filtered.mean()),
        "total_area": float(filtered.sum()),
        "n": int(len(filtered))
    }

def q3_density(zone_id, confidence_min=0.0):
    count = q1_count(zone_id, confidence_min)
    z = ZONAS[zone_id]
    lat_diff = abs(z['lat_max'] - z['lat_min'])
    lon_diff = abs(z['lon_max'] - z['lon_min'])
    area_km2 = lat_diff * lon_diff * 12321
    return float(count / area_km2) if area_km2 > 0 else 0.0

def q4_compare(zone_a, zone_b, confidence_min=0.0):
    da = q3_density(zone_a, confidence_min)
    db = q3_density(zone_b, confidence_min)
    return {
        "zone_a": da,
        "zone_b": db,
        "winner": zone_a if da > db else zone_b
    }

def q5_confidence_dist(zone_id, bins=5):
    records = zona_data[zone_id]
    scores = records['confidence'].values
    counts, edges = np.histogram(scores, bins=bins, range=(0, 1))
    return [
        {"bucket": i, "min": float(edges[i]), "max": float(edges[i+1]), "count": int(counts[i])}
        for i in range(bins)
    ]
