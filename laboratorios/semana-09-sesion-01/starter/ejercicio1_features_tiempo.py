"""Ejercicio 1: features de fecha y hora de viajes_taxi.csv.

Corre el script antes de tocar nada:

    python3 ejercicio1_features_tiempo.py

Corre sin errores y sin los TODO resueltos.
"""

import numpy as np
import pandas as pd

viajes = pd.read_csv("viajes_taxi.csv")
viajes = viajes[(viajes["tarifa"] != 999.99) & (viajes["duracion_min"] >= 0)].copy()
inicio = pd.to_datetime(viajes["fecha_hora_inicio"])

print("Paso 1: partes de la fecha")
# TODO 1: la hora (0 a 23) y el dia de la semana (0 es lunes) de inicio.
viajes["hora"] = 0
viajes["dia_semana"] = 0
# TODO 2: es_fin_de_semana, 1 los sabados y domingos, 0 el resto.
viajes["es_fin_de_semana"] = 0

print("Paso 2: hora pico")
horas_pico = [7, 8, 9, 16, 17, 18, 19]
# TODO 3: es_hora_pico, 1 si la hora esta en horas_pico y no es fin de
# semana, 0 el resto.
viajes["es_hora_pico"] = 0

print("Paso 3: la hora como ciclo")
# TODO 4: hora_sin y hora_cos, la hora como un punto en un reloj de 24
# horas.
viajes["hora_sin"] = 0.0
viajes["hora_cos"] = 0.0

columnas = ["fecha_hora_inicio", "hora", "dia_semana", "es_fin_de_semana", "es_hora_pico", "hora_sin", "hora_cos"]
print(viajes[columnas].head())

print()
print("Paso 4: la hora pico aporta algo a la tarifa?")
normales = viajes[(viajes["tarifa"] != 70.0) & (viajes["distancia_km"] > 0)].copy()
normales["tarifa_por_km"] = normales["tarifa"] / normales["distancia_km"]
print("Tarifa por km, mediana, segun hora pico:")
print(normales.groupby("es_hora_pico")["tarifa_por_km"].median().round(2))

print()
print("Paso 5: que tan lejos quedan dos horas")


def distancia(fila_a, fila_b):
    a = np.array([fila_a["hora_sin"], fila_a["hora_cos"]])
    b = np.array([fila_b["hora_sin"], fila_b["hora_cos"]])
    return np.sqrt(((a - b) ** 2).sum())


ejemplo = viajes.drop_duplicates("hora").set_index("hora")
for h1, h2 in [(23, 0), (11, 12)]:
    if h1 in ejemplo.index and h2 in ejemplo.index:
        print(f"{h1} y {h2}: como numero {abs(h1 - h2)}, como ciclo {distancia(ejemplo.loc[h1], ejemplo.loc[h2]):.2f}")
    else:
        print(f"{h1} y {h2}: todavia no hay horas distintas para comparar")
