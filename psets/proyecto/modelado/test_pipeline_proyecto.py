"""Pruebas de pipeline_proyecto.py. Desde la raiz del fork:

    pytest psets/proyecto -v

No leen el CSV de data/raw/ (en GitHub Actions no existe): cada prueba arma
un canton de pocos dias escrito a mano, con numeros elegidos para que el
valor esperado de cada feature se pueda calcular de cabeza.
"""

import numpy as np
import pandas as pd

from modelado.pipeline_proyecto import (
    CATEGORICAS,
    NUMERICAS,
    OBJETIVO,
    YA_LISTAS,
    agregar_features,
    construir_preparacion,
)


def canton_de_prueba():
    """35 dias de un canton, antes de la fecha de corte. Las emergencias del
    dia i son i (0, 1, 2, ...), y el conteo de t+3 siempre es 10, asi que el
    P90 de cada dia de la semana tambien es 10. El dia 20 es feriado."""
    fechas = pd.date_range("2025-05-01", periods=35, freq="D")
    es_feriado = pd.Series(False, index=range(35))
    es_feriado[20] = True
    return pd.DataFrame({
        "cod_canton": "0101",
        "fecha": fechas,
        "dia_semana": fechas.dayofweek + 1,
        "n_emergencias": range(35),
        "obj_n_emergencias_t3": 10,
        "es_feriado": es_feriado,
        "es_feriado_t3": es_feriado.shift(-3, fill_value=False),
    })


def test_el_modelo_no_recibe_la_etiqueta_ni_el_futuro():
    columnas_del_modelo = NUMERICAS + CATEGORICAS + YA_LISTAS
    assert OBJETIVO not in columnas_del_modelo
    # El conteo de t+3 y el umbral definen la etiqueta: con ellos el modelo
    # veria la respuesta.
    for columna in ["obj_n_emergencias_t3", "obj_n_emergencias_t7", "p90_t3"]:
        assert columna not in columnas_del_modelo


def test_nivel_vs_umbral_calculado_a_mano():
    datos = agregar_features(canton_de_prueba())
    dia_30 = datos[datos["fecha"] == pd.Timestamp("2025-05-31")].iloc[0]
    # t-4, t-11, t-18 y t-25 del dia 30 son los dias 26, 19, 12 y 5:
    # (26 + 19 + 12 + 5) / 4 = 15.5, y 15.5 / 10 = 1.55.
    assert dia_30["lag_4d"] == 26
    assert dia_30["nivel_vs_umbral_t3"] == 1.56


def test_momento_feriado_alrededor_del_feriado():
    datos = agregar_features(canton_de_prueba()).set_index("fecha")["momento_feriado_t3"]
    # El feriado es el dia 20 (21 de mayo). Para el dia 17, t+3 es el feriado;
    # para el 16, t+3 es la vispera; para el 18, t+3 es el dia despues.
    assert datos[pd.Timestamp("2025-05-18")] == "feriado"
    assert datos[pd.Timestamp("2025-05-17")] == "vispera"
    assert datos[pd.Timestamp("2025-05-19")] == "dia_despues"
    assert datos[pd.Timestamp("2025-05-05")] == "normal"


def test_las_features_no_miran_el_futuro():
    original = agregar_features(canton_de_prueba())
    alterado = canton_de_prueba()
    # Cambiar los dias posteriores al 30 no puede cambiar las features del 30.
    alterado.loc[alterado.index > 30, "n_emergencias"] = 999
    alterado = agregar_features(alterado)
    dia = pd.Timestamp("2025-05-31")
    for columna in ["lag_4d", "nivel_vs_umbral_t3"]:
        antes = original.loc[original["fecha"] == dia, columna].iloc[0]
        despues = alterado.loc[alterado["fecha"] == dia, columna].iloc[0]
        assert antes == despues


def test_la_preparacion_acepta_una_region_que_no_vio():
    filas = pd.DataFrame({columna: [1.0, 2.0, 3.0] for columna in NUMERICAS})
    filas["momento_feriado_t3"] = ["normal", "feriado", "vispera"]
    filas["region"] = ["Sierra", "Costa", "Sierra"]
    filas["dia_semana_t3"] = [1, 2, 3]
    filas["mes"] = [1, 1, 2]
    filas["es_fin_de_semana"] = [0, 0, 1]
    filas["es_feriado"] = [0, 1, 0]

    preparacion = construir_preparacion().fit(filas)
    nueva = filas.iloc[[0]].assign(region="Insular")
    transformada = preparacion.transform(nueva)

    nombres = list(preparacion.get_feature_names_out())
    columnas_region = [i for i, nombre in enumerate(nombres) if "region_" in nombre]
    assert transformada.shape == (1, len(nombres))
    # Una region que no estaba en el entrenamiento queda en cero, sin error.
    assert np.all(transformada[0, columnas_region] == 0)
