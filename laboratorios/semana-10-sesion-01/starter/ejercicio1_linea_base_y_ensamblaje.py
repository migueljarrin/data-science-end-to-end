"""Ejercicio 1: linea base, un arbol que se sobreajusta, el mismo arbol
regularizado y un bosque aleatorio, sobre viajes_features.csv.

Corre el script antes de tocar nada:

    python3 ejercicio1_linea_base_y_ensamblaje.py

La preparacion es el pipeline de la Semana 9, Sesion 2. Cada modelo se
evalua con la misma division y se registra en la tabla de resultados.
Corre sin errores sin resolver los 4 TODO.
"""

import time

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeRegressor

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
        "brecha": round(mae_prueba - mae_ent, 4),
        "segundos": round(segundos, 3),
    })
    print(f"{nombre:28s} entrenamiento {mae_ent:7.4f}   prueba {mae_prueba:7.4f}")
    return pipeline


# TODO 1: la linea base, un DummyRegressor que siempre predice la mediana
# de la tarifa de entrenamiento.
linea_base = DummyRegressor()
evaluar("linea base", linea_base)

# TODO 2: un arbol de decision (DecisionTreeRegressor) sin ningun limite,
# con random_state=42.
arbol = DummyRegressor()
evaluar("arbol sin limite", arbol)

# TODO 3: el mismo arbol, regularizado con max_depth=8.
arbol_limitado = DummyRegressor()
evaluar("arbol max_depth=8", arbol_limitado)

# TODO 4: un bosque aleatorio (RandomForestRegressor) de 200 arboles, con
# random_state=42.
bosque = DummyRegressor()
evaluar("bosque aleatorio", bosque)

tabla = pd.DataFrame(resultados)
tabla.to_csv("resultados_ejercicio1.csv", index=False)
print()
print(tabla.to_string(index=False))
