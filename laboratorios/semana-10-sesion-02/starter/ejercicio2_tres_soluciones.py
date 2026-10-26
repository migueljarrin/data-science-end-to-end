"""Ejercicio 2: el ensamblaje, la red neuronal y un LLM, sobre los mismos
20 viajes de prueba.

Primera corrida: el script escribe prompt_llm.txt. Copialo completo en
un LLM de chat (el que uses: ChatGPT, Claude, Gemini u otro), y guarda
los 20 numeros que responda, uno por linea, en respuestas_llm.txt, en
esta misma carpeta. Despues vuelve a correr el script:

    python3 ejercicio2_tres_soluciones.py

Al final se imprime una comprobacion por paso. No la modifiques: cuando
todas digan OK, pasa a las preguntas del README.
"""

import os
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
viajes["hora"] = pd.to_datetime(viajes["fecha_hora_inicio"]).dt.hour

NUMERICAS = ["distancia_km", "pasajeros"]
YA_LISTAS = ["hora_sin", "hora_cos", "es_fin_de_semana", "es_hora_pico", "es_tarifa_fija"]
CATEGORICAS = ["zona_origen", "zona_destino", "metodo_pago"]
LEGIBLES = ["zona_origen", "zona_destino", "distancia_km", "pasajeros", "hora", "es_fin_de_semana", "metodo_pago"]

X = viajes[NUMERICAS + YA_LISTAS + CATEGORICAS + ["hora"]]
y = viajes["tarifa"]
X_ent, X_prueba, y_ent, y_prueba = train_test_split(X, y, test_size=0.2, random_state=42)

# Los mismos 20 viajes de prueba para las tres soluciones, y 30 viajes de
# entrenamiento como ejemplos para el LLM.
muestra = X_prueba.sample(20, random_state=7)
y_muestra = y_prueba.loc[muestra.index]
ejemplos = X_ent.sample(30, random_state=7)
y_ejemplos = y_ent.loc[ejemplos.index]


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


def escribir_prompt():
    filas_ejemplo = ejemplos[LEGIBLES].copy()
    filas_ejemplo["tarifa"] = y_ejemplos.values
    texto = (
        "Estimas tarifas de taxi en dolares. Abajo hay 30 viajes con su tarifa real y "
        "20 viajes sin tarifa. Responde solo con 20 numeros, uno por linea, en el mismo "
        "orden de los viajes sin tarifa, sin texto adicional. La distancia esta en "
        "kilometros; si falta, el valor esta vacio.\n\n"
        "Viajes con tarifa:\n"
        + filas_ejemplo.to_csv(index=False)
        + "\nViajes sin tarifa:\n"
        + muestra[LEGIBLES].to_csv(index=False)
    )
    with open("prompt_llm.txt", "w") as archivo:
        archivo.write(texto)
    return texto


# TODO 1: la red neuronal del Ejercicio 1, con el nombre "red neuronal".
red = None

# TODO 2: el ensamblaje del Ejercicio 1, con el nombre "gradient boosting".
ensamblaje = None

# TODO 3: mae_red_muestra y mae_ensamblaje_muestra, el error absoluto
# medio de cada modelo sobre los 20 viajes de muestra.
mae_red_muestra = None
mae_ensamblaje_muestra = None

prompt = escribir_prompt()
print()
print("prompt_llm.txt escrito:", len(prompt), "caracteres")

# Paso 4: predicciones_llm, la lista de 20 numeros de respuestas_llm.txt,
# y mae_llm, su error absoluto medio sobre los mismos 20 viajes.
predicciones_llm = None
mae_llm = None

# Paso 5: el costo de estimar 10 000 viajes al mes con el LLM, en
# dolares, en costo_10000. Busca en la pagina de precios del proveedor
# que usaste el precio por millon de tokens de entrada y anotalo abajo.
# Cuenta un token cada 4 caracteres, y un prompt como este por cada 20
# viajes; ignora los tokens de salida.
PRECIO_POR_MILLON_DE_TOKENS = None
costo_10000 = None


def comprobar(numero, condicion):
    if condicion:
        print(f"Paso {numero}: OK")
    else:
        print(f"Paso {numero}: revisa")


print()
print("Comprobacion")
comprobar(1, red is not None and red.named_steps["modelo"].n_iter_ < 1000)
comprobar(2, ensamblaje is not None and isinstance(ensamblaje.named_steps["modelo"], GradientBoostingRegressor))
comprobar(3, mae_red_muestra is not None and mae_ensamblaje_muestra is not None
          and 0 < mae_red_muestra < 3 and 0 < mae_ensamblaje_muestra < 3)
comprobar(4, os.path.exists("respuestas_llm.txt") and predicciones_llm is not None
          and len(predicciones_llm) == 20 and mae_llm is not None)
comprobar(5, PRECIO_POR_MILLON_DE_TOKENS is not None and costo_10000 is not None and costo_10000 > 0)
