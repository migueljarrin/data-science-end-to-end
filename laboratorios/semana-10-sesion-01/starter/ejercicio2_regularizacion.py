"""Ejercicio 2: una regresion lineal que se sobreajusta, la misma con
regularizacion, y un ensamblaje por boosting, sobre viajes_features.csv.

Corre el script con:

    python3 ejercicio2_regularizacion.py

Al final se imprime una comprobacion por paso. No la modifiques: cuando
todas digan OK, pasa a las preguntas del README.
"""

import os
import time

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, PolynomialFeatures, StandardScaler

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


def evaluar(nombre, modelo, grado_interacciones=None):
    """Igual que en el Ejercicio 1. Con grado_interacciones, agrega despues
    de la preparacion un PolynomialFeatures de ese grado: todos los
    productos entre columnas hasta ese grado, como columnas nuevas."""
    pasos = [("preparar", preparacion())]
    if grado_interacciones is not None:
        pasos.append(("interacciones", PolynomialFeatures(degree=grado_interacciones, include_bias=False)))
    pasos.append(("modelo", modelo))
    pipeline = Pipeline(pasos)
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
    print(f"{nombre:34s} entrenamiento {mae_ent:7.4f}   prueba {mae_prueba:.4f}")
    return pipeline


# TODO 1: la misma linea base del Ejercicio 1, con el nombre "linea base".

# TODO 2: una regresion lineal sobre las interacciones de grado 3, con el
# nombre "lineal grado 3". Guarda en columnas_grado_3 cuantas columnas
# recibe el modelo (el atributo n_output_features_ del paso
# "interacciones" del pipeline que devuelve evaluar).
columnas_grado_3 = None

# TODO 3: la misma regresion, regularizada con Ridge(alpha=10.0), con el
# nombre "ridge grado 3".

# Paso 4: un ensamblaje por boosting, con el nombre "gradient boosting".

# Paso 5: guarda la tabla en resultados_ejercicio2.csv y deja en "mejor"
# el nombre del modelo con menor error en prueba.
mejor = None


def comprobar(numero, condicion):
    if condicion:
        print(f"Paso {numero}: OK")
    else:
        print(f"Paso {numero}: revisa")


def fila(nombre):
    for resultado in resultados:
        if resultado["modelo"] == nombre:
            return resultado
    return None


print()
print("Comprobacion")
comprobar(1, fila("linea base") is not None and 12.0 < fila("linea base")["mae_prueba"] < 13.0)
comprobar(2, fila("lineal grado 3") is not None and fila("lineal grado 3")["brecha"] > 100 and columnas_grado_3 == 3275)
comprobar(3, fila("ridge grado 3") is not None and fila("ridge grado 3")["mae_prueba"] < 1.5)
comprobar(4, fila("gradient boosting") is not None and fila("gradient boosting")["mae_prueba"] < 1.35)
comprobar(5, mejor == "gradient boosting" and os.path.exists("resultados_ejercicio2.csv"))
