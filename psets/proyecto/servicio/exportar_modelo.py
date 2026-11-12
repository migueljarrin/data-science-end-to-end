"""Exporta el modelo final del registro de MLflow a servicio/modelo.joblib,
y a servicio/referencias.joblib lo que el servicio necesita para calcular
las features y que no viene en la peticion: el umbral P90 de cada canton y
dia de la semana (sale del conteo de t+3, que al predecir no existe) y la
region de cada canton. Ninguno de los dos archivos se sube: se regeneran
con este script, con el servidor de MLflow levantado y el CSV en data/raw/.

    cd psets/proyecto
    python -m servicio.exportar_modelo
"""

from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import pandas as pd

from modelado.pipeline_proyecto import RUTA_DATOS, umbrales_p90

EXPERIMENTO = "ecu911-alta-demanda-t3"
CARPETA = Path(__file__).resolve().parent

# La corrida final es la que la Semana 11 marco con candidato = final.
corridas = mlflow.search_runs(experiment_names=[EXPERIMENTO], filter_string="tags.candidato = 'final'")
if len(corridas) != 1:
    raise SystemExit(f"Se esperaba una corrida con candidato = final en {EXPERIMENTO}, hay {len(corridas)}")
run_id = corridas.loc[0, "run_id"]

modelo = mlflow.sklearn.load_model(f"runs:/{run_id}/modelo")
joblib.dump(modelo, CARPETA / "modelo.joblib")

datos = pd.read_csv(RUTA_DATOS, dtype={"cod_canton": str, "cod_provincia": str}, parse_dates=["fecha"])
referencias = {
    "run_id": run_id,
    "p90": umbrales_p90(datos),
    "regiones": datos.drop_duplicates("cod_canton").set_index("cod_canton")["region"].to_dict(),
}
joblib.dump(referencias, CARPETA / "referencias.joblib")

print(f"Corrida {run_id} ({corridas.loc[0, 'tags.mlflow.runName']}) exportada a servicio/modelo.joblib")
print(f"Referencias: {len(referencias['p90'])} umbrales P90 y {len(referencias['regiones'])} cantones en servicio/referencias.joblib")
