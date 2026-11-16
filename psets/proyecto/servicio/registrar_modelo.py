"""Entrena el modelo final del proyecto (el bosque aleatorio de la Semana 11)
y lo registra como una version nueva de "ecu911-alta-demanda" en el registro
de MLflow. Cada vez que lo corres crea una version: ninguna reemplaza a otra.

    cd psets/proyecto
    python -m servicio.registrar_modelo 100

El numero es min_samples_leaf, la regularizacion del bosque: cuantas filas
de entrenamiento necesita, como minimo, cada hoja de cada arbol.
"""

import hashlib
import logging
import sys
import time

import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score
from sklearn.pipeline import Pipeline

from modelado.pipeline_proyecto import CORTE, RUTA_DATOS, cargar_y_dividir, construir_preparacion

logging.getLogger("mlflow").setLevel(logging.ERROR)

NOMBRE = "ecu911-alta-demanda"


def huella(ruta):
    """Los primeros 12 caracteres del MD5 del archivo de datos."""
    with open(ruta, "rb") as archivo:
        return hashlib.md5(archivo.read()).hexdigest()[:12]


hojas = int(sys.argv[1])
X_entrenamiento, X_prueba, y_entrenamiento, y_prueba = cargar_y_dividir()

mlflow.set_experiment("ecu911-alta-demanda-registro")
with mlflow.start_run(run_name=f"bosque-hojas-{hojas}"):
    modelo = Pipeline([
        ("preparar", construir_preparacion()),
        ("modelo", RandomForestClassifier(
            n_estimators=100, min_samples_leaf=hojas, class_weight="balanced", n_jobs=-1, random_state=42)),
    ])
    inicio = time.perf_counter()
    modelo.fit(X_entrenamiento, y_entrenamiento)
    segundos = time.perf_counter() - inicio
    ap_entrenamiento = average_precision_score(y_entrenamiento, modelo.predict_proba(X_entrenamiento)[:, 1])
    ap_prueba = average_precision_score(y_prueba, modelo.predict_proba(X_prueba)[:, 1])

    mlflow.log_params({
        "min_samples_leaf": hojas,
        "n_estimators": 100,
        "fecha_corte": str(CORTE.date()),
        "huella_datos": huella(RUTA_DATOS),
    })
    mlflow.log_metrics({
        "ap_prueba": ap_prueba,
        "ap_entrenamiento": ap_entrenamiento,
        "brecha": ap_entrenamiento - ap_prueba,
        "segundos": segundos,
    })
    info = mlflow.sklearn.log_model(modelo, "modelo", registered_model_name=NOMBRE)

print(f"Version {info.registered_model_version} de {NOMBRE}: bosque con min_samples_leaf={hojas}, "
      f"AP prueba {ap_prueba:.4f}, brecha {ap_entrenamiento - ap_prueba:.4f}")
