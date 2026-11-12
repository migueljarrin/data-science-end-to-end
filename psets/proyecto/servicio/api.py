"""Servicio de prediccion de alta demanda de emergencias del ECU 911.

Al cierre de cada dia, quien llama (el lote nocturno, un tablero) manda lo que
sabe de un canton: las emergencias de los ultimos 29 dias, los conteos por
servicio del dia y los feriados proximos. El servicio calcula las features con
las mismas funciones del entrenamiento (modelado/pipeline_proyecto.py) y
responde la probabilidad de alta demanda en t+3. Desde psets/proyecto, despues
de python -m servicio.exportar_modelo:

    uvicorn servicio.api:app --port 8000

La documentacion interactiva queda en el puerto 8000, ruta /docs.
"""

import os
from datetime import date, timedelta
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, NonNegativeInt

from modelado.pipeline_proyecto import CATEGORICAS, NUMERICAS, YA_LISTAS, calcular_features, rezagos_y_medias

CARPETA = Path(__file__).resolve().parent
RUTA_MODELO = Path(os.environ.get("RUTA_MODELO", CARPETA / "modelo.joblib"))
RUTA_REFERENCIAS = Path(os.environ.get("RUTA_REFERENCIAS", CARPETA / "referencias.joblib"))

# El umbral de la Semana 11, Sesion 2: el que minimiza el costo en la
# validacion temporal (un dia de alta demanda sin detectar cuesta 5, una falsa
# alarma 1).
UMBRAL = 0.66
# lag_28d y media_prev_28d necesitan los 28 dias anteriores a t.
DIAS_HISTORIA = 29

# El modelo y sus referencias se cargan una sola vez, al arrancar.
modelo = None
referencias = None
if RUTA_MODELO.exists() and RUTA_REFERENCIAS.exists():
    modelo = joblib.load(RUTA_MODELO)
    referencias = joblib.load(RUTA_REFERENCIAS)

app = FastAPI(title="Alta demanda de emergencias del ECU 911")


class CantonDia(BaseModel):
    """Lo que el ECU 911 sabe de un canton al cierre del dia t."""
    cod_canton: str = Field(examples=["0101"])
    fecha: date = Field(description="El dia t, ya cerrado")
    emergencias: list[NonNegativeInt] = Field(
        min_length=DIAS_HISTORIA, max_length=DIAS_HISTORIA,
        description="Emergencias de cada dia, de t-28 a t: la ultima es la del dia t")
    n_seguridad_ciudadana: NonNegativeInt
    n_gestion_sanitaria: NonNegativeInt
    n_transito_movilidad: NonNegativeInt
    feriados: list[date] = Field(default=[], description="Los feriados entre t y t+4, del calendario")


@app.get("/salud")
def salud():
    return {
        "estado": "ok",
        "modelo_cargado": modelo is not None,
        "run_id": referencias["run_id"] if referencias is not None else None,
    }


def preparar(dia):
    """Arma la historia del canton, de t-28 a t+4 (los dias futuros solo
    traen el calendario), y devuelve las features del dia t, calculadas con
    las funciones del entrenamiento."""
    fechas = [dia.fecha + timedelta(days=dias) for dias in range(-(DIAS_HISTORIA - 1), 5)]
    feriados = set(dia.feriados)
    historia = pd.DataFrame({
        "cod_canton": dia.cod_canton,
        "fecha": pd.to_datetime(fechas),
        "dia_semana": [fecha.isoweekday() for fecha in fechas],
        "n_emergencias": list(dia.emergencias) + [np.nan] * 4,
        "es_feriado": [fecha in feriados for fecha in fechas],
        "es_feriado_t3": [fecha + timedelta(days=3) in feriados for fecha in fechas],
    })
    historia = calcular_features(rezagos_y_medias(historia), referencias["p90"])

    fila = historia[historia["fecha"] == pd.Timestamp(dia.fecha)].assign(
        n_seguridad_ciudadana=dia.n_seguridad_ciudadana,
        n_gestion_sanitaria=dia.n_gestion_sanitaria,
        n_transito_movilidad=dia.n_transito_movilidad,
        region=referencias["regiones"][dia.cod_canton],
        mes=dia.fecha.month,
        es_fin_de_semana=int(dia.fecha.isoweekday() >= 6),
        es_feriado=int(dia.fecha in feriados),
    )
    return fila[NUMERICAS + CATEGORICAS + YA_LISTAS]


@app.post("/predecir")
def predecir(dia: CantonDia):
    if dia.cod_canton not in referencias["regiones"]:
        raise HTTPException(status_code=404, detail=f"Canton desconocido: {dia.cod_canton}")
    probabilidad = float(modelo.predict_proba(preparar(dia))[0, 1])
    return {
        "cod_canton": dia.cod_canton,
        "fecha_objetivo": dia.fecha + timedelta(days=3),
        "probabilidad_alta_demanda": round(probabilidad, 4),
        "alerta": probabilidad >= UMBRAL,
        "run_id": referencias["run_id"],
    }
