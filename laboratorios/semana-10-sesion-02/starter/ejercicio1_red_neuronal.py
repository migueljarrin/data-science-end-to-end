"""Ejercicio 1: una red neuronal simple frente al ensamblaje de la sesion
pasada, sobre viajes_features.csv: error, tiempo y que se puede explicar
de cada uno.

Corre el script antes de tocar nada:

    python3 ejercicio1_red_neuronal.py

La preparacion y la funcion evaluar son las de la sesion pasada. Corre
sin errores sin resolver los 3 TODO.
"""

import time

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

viajes = pd.read_csv("viajes_features.csv")

NUMERICAS = ["distancia_km", "pasajeros"]
YA_LISTAS = ["hora_sin", "hora_cos", "es_fin_de_semana", "es_hora_pico", "es_tarifa_fija"]
CATEGORICAS = ["zona_origen", "zona_destino", "metodo_pago"]

X = viajes[NUMERICAS + YA_LISTAS + CATEGORICAS]
y = viajes["tarifa"]
X_ent, X_prueba, y_ent, y_prueba = train_test_split(X, y, test_size=0.2, random_state=42)


def preparacion():
    return ColumnTransformer([
        ("numericas", Pipeline([
            ("imputar", SimpleImputer(strategy="median")),
            ("escalar", StandardScaler()),
        ]), NUMERICAS),
        ("ya_listas", "passthrough", YA_LISTAS),
        ("categoricas", Pipeline([
            ("imputar", SimpleImputer(strategy="most_frequent")),
            ("codificar", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]), CATEGORICAS),
    ])


resultados = []


def evaluar(nombre, modelo):
    pipeline = Pipeline([("preparar", preparacion()), ("modelo", modelo)])
    inicio = time.perf_counter()
    pipeline.fit(X_ent, y_ent)
    segundos = time.perf_counter() - inicio
    mae_ent = mean_absolute_error(y_ent, pipeline.predict(X_ent))
    mae_prueba = mean_absolute_error(y_prueba, pipeline.predict(X_prueba))
    resultados.append({
        "modelo": nombre,
        "mae_entrenamiento": round(mae_ent, 4),
        "mae_prueba": round(mae_prueba, 4),
        "segundos": round(segundos, 3),
    })
    print(f"{nombre:20s} entrenamiento {mae_ent:7.4f}   prueba {mae_prueba:7.4f}   {segundos:6.2f} s")
    return pipeline


ensamblaje = evaluar("gradient boosting", GradientBoostingRegressor(random_state=42))

# TODO 1: una red neuronal (MLPRegressor) con una capa oculta de 64
# neuronas, hasta 1000 iteraciones y random_state=42.
red = evaluar("red neuronal", MLPRegressor(hidden_layer_sizes=(64,), random_state=42))

# TODO 2: parametros_red, cuantos numeros aprendio la red: la suma de los
# tamanos (.size) de todas las matrices de coefs_ y todos los vectores
# de intercepts_ del paso "modelo".
parametros_red = None

# TODO 3: importancias, una serie de pandas con feature_importances_ del
# ensamblaje, indexada por los nombres de columna que produce la
# preparacion (get_feature_names_out), ordenada de mayor a menor.
importancias = None

print()
print(pd.DataFrame(resultados).to_string(index=False))
print()
if parametros_red is None:
    print("Parametros de la red: pendiente")
else:
    print("Parametros de la red:", parametros_red)
if importancias is None:
    print("Importancias del ensamblaje: pendiente")
else:
    print("Las 3 columnas mas importantes para el ensamblaje:")
    print(importancias.head(3).round(4).to_string())
