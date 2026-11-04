"""Tres soluciones para el proyecto ECU 911 (alta demanda a t+3): el mejor
ensamblaje de la sesion pasada, una red neuronal simple y un LLM.

Usa la misma preparacion y la misma division por fecha de la Semana 10,
Sesion 1 (semana-10-sesion-01/proyecto/modelos_proyecto.py).

Primera corrida: entrena los dos modelos y escribe prompt_llm_proyecto.txt.
Copialo completo en un LLM de chat y guarda los 10 numeros que responda,
uno por linea, en respuestas_llm_proyecto.txt, en esta misma carpeta.
Despues vuelve a correr el script:

    python comparar_proyecto.py

Guarda las tablas en resultados_comparacion.csv y resultados_muestra_10.csv.
"""

import os
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, average_precision_score
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# Datos y features: igual que en la Semana 10, Sesion 1. El CSV va en data/raw/
# de la raiz del repo (esta en .gitignore, no se sube).
RUTA_DATOS = Path(__file__).resolve().parents[3] / "data" / "raw" / "obt_emergencias_canton_dia.csv"
datos = pd.read_csv(
    RUTA_DATOS,
    dtype={"cod_canton": str, "cod_provincia": str},
    parse_dates=["fecha"],
)
datos = datos.sort_values(["cod_canton", "fecha"]).reset_index(drop=True)

CORTE = pd.Timestamp("2025-07-01")
datos["dia_semana_t3"] = (datos["dia_semana"] + 2) % 7 + 1
p90 = (datos[datos["fecha"] < CORTE]
       .groupby(["cod_canton", "dia_semana_t3"])["obj_n_emergencias_t3"].quantile(0.9)
       .rename("p90_t3"))
datos = datos.join(p90, on=["cod_canton", "dia_semana_t3"])
datos["y_3"] = np.where(
    datos["obj_n_emergencias_t3"].isna(), np.nan,
    (datos["obj_n_emergencias_t3"] > datos["p90_t3"]).astype(float),
)

emergencias = datos.groupby("cod_canton")["n_emergencias"]
datos["lag_4d"] = emergencias.shift(4)
media_mismo_dia_t3 = sum(emergencias.shift(k) for k in [4, 11, 18, 25]) / 4
datos["nivel_vs_umbral_t3"] = media_mismo_dia_t3 / datos["p90_t3"]

calendario = datos.drop_duplicates("fecha").set_index("fecha")["es_feriado"]


def es_feriado_en(dias):
    return datos["fecha"].add(pd.Timedelta(days=dias)).map(calendario).fillna(False).astype(bool)


datos["momento_feriado_t3"] = np.select(
    [datos["es_feriado_t3"], es_feriado_en(4), es_feriado_en(2)],
    ["feriado", "vispera", "dia_despues"],
    default="normal",
)

datos = datos[datos["y_3"].notna()].copy()
datos["y_3"] = datos["y_3"].astype(int)

OBJETIVO = "y_3"
NUMERICAS = [
    "n_emergencias", "lag_1d", "lag_4d", "lag_7d", "lag_14d", "lag_28d",
    "media_prev_7d", "media_prev_28d", "nivel_vs_umbral_t3",
    "n_seguridad_ciudadana", "n_gestion_sanitaria", "n_transito_movilidad",
]
CATEGORICAS = ["momento_feriado_t3", "region", "dia_semana_t3", "mes"]
YA_LISTAS = ["es_fin_de_semana", "es_feriado"]

X = datos[NUMERICAS + CATEGORICAS + YA_LISTAS].astype({c: int for c in YA_LISTAS})
y = datos[OBJETIVO]
es_entrenamiento = datos["fecha"] < CORTE
X_ent, X_prueba = X[es_entrenamiento], X[~es_entrenamiento]
y_ent, y_prueba = y[es_entrenamiento], y[~es_entrenamiento]


def preparacion():
    return ColumnTransformer([
        ("numericas", Pipeline([
            ("imputar", SimpleImputer(strategy="median")),
            ("escalar", StandardScaler()),
        ]), NUMERICAS),
        ("categoricas", Pipeline([
            ("imputar", SimpleImputer(strategy="most_frequent")),
            ("codificar", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]), CATEGORICAS),
        ("ya_listas", "passthrough", YA_LISTAS),
    ])


# Metrica del proyecto: precision promedio (AP), como en la sesion pasada.
resultados = []


def evaluar(nombre, modelo):
    pipeline = Pipeline([("preparar", preparacion()), ("modelo", modelo)])
    inicio = time.perf_counter()
    pipeline.fit(X_ent, y_ent)
    segundos = time.perf_counter() - inicio
    ap_prueba = average_precision_score(y_prueba, pipeline.predict_proba(X_prueba)[:, 1])
    resultados.append({"modelo": nombre, "ap_prueba": round(ap_prueba, 4), "segundos": round(segundos, 2)})
    print(f"{nombre:30s} AP prueba {ap_prueba:.4f}   ({segundos:.1f} s)")
    return pipeline


print(f"Entrenamiento: {len(X_ent)} filas, prueba: {len(X_prueba)} filas\n")

# El mejor ensamblaje de la sesion pasada.
bosque = evaluar("bosque min_samples_leaf=100", RandomForestClassifier(
    n_estimators=100, min_samples_leaf=100, class_weight="balanced", n_jobs=-1, random_state=42))

# Una red neuronal simple: una capa oculta de 32 neuronas. early_stopping aparta
# el 10% del entrenamiento y se detiene cuando deja de mejorar ahi.
red = evaluar("red neuronal (32,)", MLPClassifier(
    hidden_layer_sizes=(32,), early_stopping=True, max_iter=200, random_state=42))

capa = red.named_steps["modelo"]
parametros_red = sum(w.size for w in capa.coefs_) + sum(b.size for b in capa.intercepts_)
resultados[-1]["parametros"] = parametros_red
print(f"Parametros de la red: {parametros_red} (iteraciones: {capa.n_iter_})")

# Explicabilidad del bosque: las columnas que mas usa para decidir.
importancias = pd.Series(
    bosque.named_steps["modelo"].feature_importances_,
    index=bosque.named_steps["preparar"].get_feature_names_out(),
).sort_values(ascending=False)
print("\nColumnas mas importantes del bosque:")
print(importancias.head(5).round(3).to_string())

# La prueba del LLM. Con solo 8% de clase 1, 10 filas al azar tendrian casi
# siempre 0 o 1 casos de alta demanda, y el AP necesita al menos uno: tomo 3
# de clase 1 y 7 de clase 0. Los 30 ejemplos de entrenamiento: 10 y 20.
prueba = datos[~es_entrenamiento]
entrenamiento = datos[es_entrenamiento]
muestra = pd.concat([
    prueba[prueba[OBJETIVO] == 1].sample(3, random_state=7),
    prueba[prueba[OBJETIVO] == 0].sample(7, random_state=7),
]).sample(frac=1, random_state=7)
ejemplos = pd.concat([
    entrenamiento[entrenamiento[OBJETIVO] == 1].sample(10, random_state=7),
    entrenamiento[entrenamiento[OBJETIVO] == 0].sample(20, random_state=7),
]).sample(frac=1, random_state=7)

DIAS = {1: "lunes", 2: "martes", 3: "miercoles", 4: "jueves", 5: "viernes", 6: "sabado", 7: "domingo"}
LEGIBLES = {
    "canton": "canton",
    "dia_t3": "dia_de_t+3",
    "momento_feriado_t3": "feriado_en_t+3",
    "p90_t3": "umbral_p90",
    "lag_4d": "emergencias_t-4",
    "media_prev_7d": "media_ultimos_7_dias",
    "media_prev_28d": "media_ultimos_28_dias",
    "nivel_vs_umbral_t3": "nivel_vs_umbral",
}


def tabla_legible(filas):
    tabla = filas.assign(dia_t3=filas["dia_semana_t3"].map(DIAS))[list(LEGIBLES)]
    return tabla.rename(columns=LEGIBLES).round(2)


filas_ejemplo = tabla_legible(ejemplos)
filas_ejemplo["alta_demanda"] = ejemplos[OBJETIVO].values
prompt = (
    "Predices si un canton de Ecuador tendra alta demanda de emergencias del ECU 911 "
    "dentro de 3 dias (t+3). Alta demanda significa que las emergencias de ese dia superan "
    "el umbral_p90 del canton para ese dia de la semana. emergencias_t-4 es el ultimo dia "
    "que cayo el mismo dia de la semana que t+3; nivel_vs_umbral es el promedio de los "
    "ultimos 4 dias iguales dividido por el umbral. Abajo hay 30 casos con su respuesta "
    "(1 alta, 0 normal) y 10 casos sin respuesta. Responde solo con 10 numeros entre 0 y 1, "
    "la probabilidad de alta demanda, uno por linea, en el mismo orden, sin texto adicional.\n\n"
    "Casos con respuesta:\n"
    + filas_ejemplo.to_csv(index=False)
    + "\nCasos sin respuesta:\n"
    + tabla_legible(muestra).to_csv(index=False)
)
with open("prompt_llm_proyecto.txt", "w", encoding="utf-8") as archivo:
    archivo.write(prompt)
print(f"\nprompt_llm_proyecto.txt escrito: {len(prompt)} caracteres")

# Costo del LLM: 224 cantones x 30 dias = 6720 predicciones al mes, 10 por
# prompt. Un token cada 4 caracteres; se ignoran los de salida. Mismo precio
# por millon de tokens de entrada que en el Ejercicio 2: verificalo en la
# pagina de precios del proveedor que uses.
PRECIO_POR_MILLON_DE_TOKENS = 2.00
predicciones_al_mes = datos["cod_canton"].nunique() * 30
tokens_por_prompt = len(prompt) / 4
costo_mensual_llm = tokens_por_prompt * (predicciones_al_mes / 10) / 1_000_000 * PRECIO_POR_MILLON_DE_TOKENS
print(f"Costo del LLM: {predicciones_al_mes} predicciones al mes, {costo_mensual_llm:.2f} USD al mes")


def metricas_muestra(nombre, probabilidades):
    return {
        "modelo": nombre,
        "ap_10_filas": round(average_precision_score(muestra[OBJETIVO], probabilidades), 4),
        "accuracy_10_filas": accuracy_score(muestra[OBJETIVO], np.asarray(probabilidades) >= 0.5),
        "probabilidades": " ".join(f"{p:.2f}" for p in probabilidades),
    }


X_muestra = muestra[NUMERICAS + CATEGORICAS + YA_LISTAS].astype({c: int for c in YA_LISTAS})
comparacion_10 = [
    metricas_muestra("bosque min_samples_leaf=100", bosque.predict_proba(X_muestra)[:, 1]),
    metricas_muestra("red neuronal (32,)", red.predict_proba(X_muestra)[:, 1]),
]
if os.path.exists("respuestas_llm_proyecto.txt"):
    with open("respuestas_llm_proyecto.txt", encoding="utf-8") as archivo:
        predicciones_llm = [float(linea) for linea in archivo if linea.strip()]
    comparacion_10.append(metricas_muestra("LLM", predicciones_llm))
else:
    print("\nFalta respuestas_llm_proyecto.txt: pasa el prompt a un LLM y vuelve a correr.")

tabla_10 = pd.DataFrame(comparacion_10)
tabla_10.to_csv("resultados_muestra_10.csv", index=False)
print("\nLas mismas 10 filas de prueba (respuesta real: "
      + " ".join(str(v) for v in muestra[OBJETIVO]) + "):")
print(tabla_10.to_string(index=False))

tabla = pd.DataFrame(resultados)
tabla.to_csv("resultados_comparacion.csv", index=False)
print("\nTodo el conjunto de prueba:")
print(tabla.to_string(index=False))
