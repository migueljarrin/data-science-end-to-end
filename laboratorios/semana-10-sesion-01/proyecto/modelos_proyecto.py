"""Primeros modelos del proyecto ECU 911: alta demanda de emergencias a t+3.

Usa la misma preparacion y la misma division por fecha de la Semana 9,
Sesion 2 (semana-09-sesion-02/plantilla-pipeline/pipeline_proyecto.py).

    python modelos_proyecto.py

Guarda la tabla en resultados_proyecto.csv.
"""

import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, precision_score, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# Datos y features: igual que en la Semana 9, Sesion 2. El CSV va en data/raw/
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


# Metrica del proyecto: precision promedio (area bajo la curva precision-recall).
# Solo el 8% de los casos es clase 1, asi que accuracy no sirve: predecir siempre 0
# acierta el 92%. La precision promedio no depende de un umbral y vale la tasa
# de clase 1 para un modelo que no distingue nada.
resultados = []


def registrar(nombre, puntaje_ent, puntaje_prueba, prediccion_prueba, segundos):
    ap_ent = average_precision_score(y_ent, puntaje_ent)
    ap_prueba = average_precision_score(y_prueba, puntaje_prueba)
    resultados.append({
        "modelo": nombre,
        "ap_entrenamiento": round(ap_ent, 4),
        "ap_prueba": round(ap_prueba, 4),
        "brecha": round(ap_ent - ap_prueba, 4),
        "precision_prueba": round(precision_score(y_prueba, prediccion_prueba, zero_division=0), 4),
        "recall_prueba": round(recall_score(y_prueba, prediccion_prueba), 4),
        "segundos": round(segundos, 2),
    })
    print(f"{nombre:40s} AP entrenamiento {ap_ent:.4f}   prueba {ap_prueba:.4f}   ({segundos:.1f} s)")


def evaluar(nombre, modelo):
    pipeline = Pipeline([("preparar", preparacion()), ("modelo", modelo)])
    inicio = time.perf_counter()
    pipeline.fit(X_ent, y_ent)
    segundos = time.perf_counter() - inicio
    registrar(
        nombre,
        pipeline.predict_proba(X_ent)[:, 1],
        pipeline.predict_proba(X_prueba)[:, 1],
        pipeline.predict(X_prueba),
        segundos,
    )
    return pipeline


print(f"Entrenamiento: {len(X_ent)} filas, prueba: {len(X_prueba)} filas")
print(f"Tasa de clase 1  entrenamiento: {y_ent.mean():.3f}  prueba: {y_prueba.mean():.3f}\n")

# Linea base 1: no usa ninguna columna; su AP es la tasa de clase 1.
evaluar("dummy (tasa de clase 1)", DummyClassifier(strategy="prior"))

# Linea base 2, regla del dominio: "t+3 igual que t-4", el ultimo dia que cayo
# el mismo dia de la semana. Alta demanda si ese dia ya supero el P90.
inicio = time.perf_counter()
regla_ent = (X_ent["lag_4d"] > datos.loc[es_entrenamiento, "p90_t3"]).astype(int)
regla_prueba = (X_prueba["lag_4d"] > datos.loc[~es_entrenamiento, "p90_t3"]).astype(int)
registrar("regla: t-4 supero el P90", regla_ent, regla_prueba, regla_prueba, time.perf_counter() - inicio)

# Modelo lineal. class_weight="balanced" compensa el desbalance; C es la
# regularizacion (mas chico = mas fuerte).
evaluar("logistica C=1", LogisticRegression(C=1.0, class_weight="balanced", max_iter=2000))
evaluar("logistica C=0.01", LogisticRegression(C=0.01, class_weight="balanced", max_iter=2000))

# Ensamblaje: bosque sin limites (se sobreajusta) y regularizado con hojas de
# al menos 100 filas.
evaluar("bosque sin limite", RandomForestClassifier(
    n_estimators=100, class_weight="balanced", n_jobs=-1, random_state=42))
evaluar("bosque min_samples_leaf=100", RandomForestClassifier(
    n_estimators=100, min_samples_leaf=100, class_weight="balanced", n_jobs=-1, random_state=42))

tabla = pd.DataFrame(resultados)
tabla.to_csv("resultados_proyecto.csv", index=False)
print()
print(tabla.to_string(index=False))
