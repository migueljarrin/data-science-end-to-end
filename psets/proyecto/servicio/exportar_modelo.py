"""Exporta la version de "ecu911-alta-demanda" que tiene el alias
"produccion" a servicio/modelo.joblib, guarda su numero en
servicio/modelo_version.txt, y guarda en servicio/referencias.joblib lo que
el servicio necesita para calcular las features y que no viene en la
peticion: el umbral P90 de cada canton y dia de la semana (sale del conteo de
t+3, que al predecir no existe) y la region de cada canton.

La imagen del servicio lleva los tres archivos adentro: el contenedor no
necesita llegar al servidor de MLflow. Ninguno se sube al repositorio: se
regeneran con este script, con el servidor de MLflow levantado y el CSV en
data/raw/.

    cd psets/proyecto
    python -m servicio.exportar_modelo
"""

import logging
from pathlib import Path

import joblib
import mlflow.sklearn
import pandas as pd
from mlflow import MlflowClient

from modelado.pipeline_proyecto import RUTA_DATOS, umbrales_p90

logging.getLogger("mlflow").setLevel(logging.ERROR)

NOMBRE = "ecu911-alta-demanda"
ALIAS = "produccion"
CARPETA = Path(__file__).resolve().parent

version = MlflowClient().get_model_version_by_alias(NOMBRE, ALIAS)
modelo = mlflow.sklearn.load_model(f"models:/{NOMBRE}/{version.version}")
joblib.dump(modelo, CARPETA / "modelo.joblib")
(CARPETA / "modelo_version.txt").write_text(version.version + "\n")

datos = pd.read_csv(RUTA_DATOS, dtype={"cod_canton": str, "cod_provincia": str}, parse_dates=["fecha"])
referencias = {
    "run_id": version.run_id,
    "p90": umbrales_p90(datos),
    "regiones": datos.drop_duplicates("cod_canton").set_index("cod_canton")["region"].to_dict(),
}
joblib.dump(referencias, CARPETA / "referencias.joblib")

print(f"{NOMBRE}@{ALIAS}: version {version.version} (corrida {version.run_id[:12]}) exportada a servicio/modelo.joblib")
print(f"Referencias: {len(referencias['p90'])} umbrales P90 y {len(referencias['regiones'])} cantones en servicio/referencias.joblib")
