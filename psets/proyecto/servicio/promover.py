"""Pone el alias "produccion" en una version de "ecu911-alta-demanda": la
version que exporta servicio/exportar_modelo.py. Volver a la version anterior
es correr este mismo script con su numero.

    cd psets/proyecto
    python -m servicio.promover 2 "mayor AP en prueba que la version 1, brecha menor a 0.05"

MLflow no guarda la historia de los alias: este script deja escrito en la
version cuando se promovio, por que y a cual reemplazo.
"""

import logging
import sys
from datetime import datetime

from mlflow import MlflowClient
from mlflow.exceptions import MlflowException

logging.getLogger("mlflow").setLevel(logging.ERROR)

NOMBRE = "ecu911-alta-demanda"
ALIAS = "produccion"

version = sys.argv[1]
motivo = sys.argv[2] if len(sys.argv) > 2 else "sin motivo escrito"
cliente = MlflowClient()

try:
    anterior = cliente.get_model_version_by_alias(NOMBRE, ALIAS).version
except MlflowException:
    anterior = "ninguna"

cliente.set_registered_model_alias(NOMBRE, ALIAS, version)
cliente.set_model_version_tag(NOMBRE, version, "promovida_el", datetime.now().isoformat(timespec="seconds"))
cliente.set_model_version_tag(NOMBRE, version, "motivo", motivo)
cliente.set_model_version_tag(NOMBRE, version, "reemplaza_a", anterior)

actual = cliente.get_model_version_by_alias(NOMBRE, ALIAS)
metricas = cliente.get_run(actual.run_id).data.metrics
print(f"{NOMBRE}@{ALIAS} es ahora la version {actual.version} (antes: {anterior}), "
      f"AP prueba {metricas['ap_prueba']:.4f}")
