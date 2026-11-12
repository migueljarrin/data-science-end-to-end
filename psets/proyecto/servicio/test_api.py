"""Pruebas del servicio. Desde la raiz del fork:

    pytest psets/proyecto -v

No usan servicio/modelo.joblib (en GitHub Actions no existe): reemplazan el
modelo por uno que responde 0.25 para cualquier canton, y las referencias
por un canton escrito a mano. Revisan el contrato de la API y las features
que calcula el servicio, no la calidad del modelo.
"""

import pandas as pd
from fastapi.testclient import TestClient
from sklearn.dummy import DummyClassifier
from sklearn.pipeline import Pipeline

from modelado.pipeline_proyecto import construir_preparacion
from servicio import api

# Domingo 1 de junio de 2025: t+3 es el miercoles 4, feriado. Las emergencias
# de t-28 a t son 0, 1, ..., 28.
DIA = {
    "cod_canton": "0101",
    "fecha": "2025-06-01",
    "emergencias": list(range(29)),
    "n_seguridad_ciudadana": 12,
    "n_gestion_sanitaria": 8,
    "n_transito_movilidad": 5,
    "feriados": ["2025-06-04"],
}
# El P90 del canton es 10 para todos los dias de la semana de t+3.
api.referencias = {
    "run_id": "corrida-de-prueba",
    "p90": pd.Series(10.0, index=pd.MultiIndex.from_tuples(
        [("0101", dia) for dia in range(1, 8)], names=["cod_canton", "dia_semana_t3"]), name="p90_t3"),
    "regiones": {"0101": "Sierra"},
}


def modelo_de_prueba():
    """La preparacion real con un modelo que responde 0.25: un caso de alta
    demanda de cuatro."""
    X = pd.concat([api.preparar(api.CantonDia(**DIA))] * 4)
    return Pipeline([("preparar", construir_preparacion()), ("modelo", DummyClassifier(strategy="prior"))]).fit(X, [1, 0, 0, 0])


api.modelo = modelo_de_prueba()
cliente = TestClient(api.app)


def test_salud():
    respuesta = cliente.get("/salud")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"estado": "ok", "modelo_cargado": True, "run_id": "corrida-de-prueba"}


def test_prediccion_valida():
    respuesta = cliente.post("/predecir", json=DIA)
    assert respuesta.status_code == 200
    # 0.25 no alcanza el umbral de 0.66: no hay alerta.
    assert respuesta.json() == {
        "cod_canton": "0101",
        "fecha_objetivo": "2025-06-04",
        "probabilidad_alta_demanda": 0.25,
        "alerta": False,
        "run_id": "corrida-de-prueba",
    }


def test_historia_incompleta_se_rechaza():
    dia = {**DIA, "emergencias": list(range(28))}
    respuesta = cliente.post("/predecir", json=dia)
    # 28 dias no alcanzan para lag_28d: FastAPI la rechaza antes de llegar al modelo.
    assert respuesta.status_code == 422
    assert respuesta.json()["detail"][0]["loc"] == ["body", "emergencias"]


def test_canton_desconocido_se_rechaza():
    respuesta = cliente.post("/predecir", json={**DIA, "cod_canton": "9999"})
    assert respuesta.status_code == 404


def test_features_del_servicio_calculadas_a_mano():
    fila = api.preparar(api.CantonDia(**DIA)).iloc[0]
    # t-4, t-11, t-18 y t-25 son 24, 17, 10 y 3: (24 + 17 + 10 + 3) / 4 = 13.5,
    # y 13.5 / 10 = 1.35.
    assert fila["lag_4d"] == 24
    assert fila["nivel_vs_umbral_t3"] == 1.35
    # t-1 es 27; la media de los 7 dias anteriores a t (21 a 27) es 24.
    assert fila["lag_1d"] == 27
    assert fila["media_prev_7d"] == 24
    assert fila["momento_feriado_t3"] == "feriado"
    assert fila["dia_semana_t3"] == 3
    assert fila["es_fin_de_semana"] == 1
