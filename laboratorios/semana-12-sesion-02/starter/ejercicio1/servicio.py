"""Servicio de prediccion de la tarifa: el modelo detras de una API.

Cuando el pasajero elige su destino, la app manda el viaje como JSON a
/predecir y recibe la tarifa estimada en la misma respuesta. Para levantarlo
en el Codespace, desde esta carpeta y despues de python entrenar.py:

    uvicorn servicio:app --port 8000

La documentacion interactiva queda en el puerto 8000, ruta /docs.
"""

import os
from datetime import datetime

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

from features_taxis import agregar_features
from preparacion_taxis import CATEGORICAS, NUMERICAS, YA_LISTAS

RUTA_MODELO = os.environ.get("RUTA_MODELO", "modelo_tarifa.joblib")

# El modelo se carga una sola vez, al arrancar el servicio, y no en cada
# peticion: leer el archivo tarda mucho mas que predecir.
modelo = None
if os.path.exists(RUTA_MODELO):
    modelo = joblib.load(RUTA_MODELO)

app = FastAPI(title="Tarifa estimada de taxis")


class Viaje(BaseModel):
    """Lo que la app sabe de un viaje antes de que empiece."""
    # TODO 1: declara cada dato que manda la app, con su tipo. La fecha (como
    # datetime, para que una fecha mal escrita se rechace) y las zonas son
    # obligatorias; distancia_km, pasajeros y metodo_pago pueden llegar
    # vacios (la preparacion los imputa), con valor por defecto None.
    fecha_hora_inicio: datetime
    zona_origen: str
    zona_destino: str
    distancia_km: float | None = None
    pasajeros: float | None = None
    metodo_pago: str | None = None


@app.get("/salud")
def salud():
    return {"estado": "ok", "modelo_cargado": modelo is not None}


@app.post("/predecir")
def predecir(viaje: Viaje):
    # TODO 2: convierte el viaje en un DataFrame de una fila
    # (viaje.model_dump() lo da como diccionario), agrega las features y
    # estima la tarifa con el modelo.
    viajes = pd.DataFrame([viaje.model_dump()], dtype=object)
    # Un dato vacio llega como None, pero en el entrenamiento los vacios eran
    # NaN: la preparacion imputa NaN y trata None como una categoria
    # desconocida, y la tarifa cambia sin dar ningun error.
    viajes = viajes.where(viajes.notna(), np.nan).astype({"distancia_km": float, "pasajeros": float})
    viajes = agregar_features(viajes)
    tarifa = modelo.predict(viajes[NUMERICAS + YA_LISTAS + CATEGORICAS])[0]

    return {"tarifa_estimada": round(float(tarifa), 2)}
