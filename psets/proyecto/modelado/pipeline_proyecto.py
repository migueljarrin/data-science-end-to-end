"""Preparacion de los datos del proyecto ECU 911 (alta demanda a t+3), lista
para produccion.

Las features de la Semana 9 viven aqui, dentro de funciones. Los notebooks
de experimentos importan este archivo en vez de copiar el codigo:

    from pipeline_proyecto import cargar_y_dividir, construir_preparacion

Para comprobar que corre de principio a fin, sin notebook:

    python3 pipeline_proyecto.py
"""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# OBT del PSet 2 (ECU 911), exportada de Snowflake. El CSV va en
# psets/proyecto/data/raw/ (esta en .gitignore, no se sube).
RUTA_DATOS = Path(__file__).resolve().parent.parent / "data" / "raw" / "obt_emergencias_canton_dia.csv"

# Division por fecha: el modelo predice el futuro, asi que entrena con el pasado
# y se evalua con lo que viene despues. El P90 de la etiqueta usa el mismo corte.
CORTE = pd.Timestamp("2025-07-01")

# Solo columnas que existen al cierre del dia t. Quedan fuera obj_*, p90_t3 (definen
# la etiqueta), es_periodo_anomalo (se marca despues, al revisar el mes) y anio.
OBJETIVO = "y_3"
NUMERICAS = [
    "n_emergencias", "lag_1d", "lag_4d", "lag_7d", "lag_14d", "lag_28d",
    "media_prev_7d", "media_prev_28d", "nivel_vs_umbral_t3",
    "n_seguridad_ciudadana", "n_gestion_sanitaria", "n_transito_movilidad",
]
CATEGORICAS = ["momento_feriado_t3", "region", "dia_semana_t3", "mes"]
YA_LISTAS = ["es_fin_de_semana", "es_feriado"]


def dia_semana_mas(dia_semana, dias):
    """El dia de la semana (1 es lunes, 7 domingo) dentro de `dias` dias."""
    return (dia_semana + dias - 1) % 7 + 1


def umbrales_p90(datos):
    """El P90 del conteo de t+3 por canton y dia de la semana de t+3, solo con
    el periodo de entrenamiento. Se calcula una vez, al entrenar, y se guarda
    junto al modelo: al predecir, el conteo de t+3 todavia no existe."""
    entrenamiento = datos[datos["fecha"] < CORTE]
    entrenamiento = entrenamiento.assign(dia_semana_t3=dia_semana_mas(entrenamiento["dia_semana"], 3))
    return (entrenamiento.groupby(["cod_canton", "dia_semana_t3"])["obj_n_emergencias_t3"]
            .quantile(0.9).rename("p90_t3"))


def rezagos_y_medias(datos):
    """Los rezagos y las medias que build_obt.py (Spark, PSet 2) agrega a la
    OBT, para cuando los datos no vienen de la OBT (el servicio). Los rezagos
    son el conteo de hace k dias; las medias excluyen el dia t y necesitan la
    ventana completa. Supone una fila por canton y dia, sin dias faltantes."""
    datos = datos.sort_values(["cod_canton", "fecha"]).reset_index(drop=True)
    emergencias = datos.groupby("cod_canton")["n_emergencias"]
    for dias in [1, 7, 14, 28]:
        datos[f"lag_{dias}d"] = emergencias.shift(dias)
    for dias in [7, 28]:
        datos[f"media_prev_{dias}d"] = emergencias.transform(
            lambda serie: serie.shift(1).rolling(dias, min_periods=dias).mean())
    return datos


def calcular_features(datos, p90):
    """Las 2 features de la Semana 9, Sesion 1, a partir de la historia de cada
    canton, el calendario y los umbrales p90 guardados. La usan el
    entrenamiento y el servicio, para que las features se calculen igual en
    los dos. Necesita cod_canton, fecha, dia_semana, n_emergencias, es_feriado
    y es_feriado_t3."""
    datos = datos.sort_values(["cod_canton", "fecha"]).reset_index(drop=True)
    datos["dia_semana_t3"] = dia_semana_mas(datos["dia_semana"], 3)
    datos = datos.join(p90, on=["cod_canton", "dia_semana_t3"])

    # Feature 1: nivel reciente del mismo dia de la semana que t+3, relativo al umbral.
    emergencias = datos.groupby("cod_canton")["n_emergencias"]
    datos["lag_4d"] = emergencias.shift(4)
    media_mismo_dia_t3 = sum(emergencias.shift(k) for k in [4, 11, 18, 25]) / 4
    datos["nivel_vs_umbral_t3"] = media_mismo_dia_t3 / datos["p90_t3"]

    # Feature 2: posicion de t+3 respecto a un feriado.
    calendario = datos.drop_duplicates("fecha").set_index("fecha")["es_feriado"]

    def es_feriado_en(dias):
        # Las fechas fuera del calendario quedan como NaN, y NaN == True es False.
        return datos["fecha"].add(pd.Timedelta(days=dias)).map(calendario).eq(True)

    datos["momento_feriado_t3"] = np.select(
        [datos["es_feriado_t3"], es_feriado_en(4), es_feriado_en(2)],
        ["feriado", "vispera", "dia_despues"],
        default="normal",
    )
    return datos


def agregar_features(datos):
    """Para entrenar: las features y la etiqueta y_3, alta demanda en t+3 (el
    conteo de t+3 supera el P90 del canton para el dia de la semana de t+3)."""
    datos = calcular_features(datos, umbrales_p90(datos))
    datos["y_3"] = np.where(
        datos["obj_n_emergencias_t3"].isna(), np.nan,
        (datos["obj_n_emergencias_t3"] > datos["p90_t3"]).astype(float),
    )

    # Los ultimos 3 dias de cada canton no tienen t+3 observado: no sirven para entrenar ni evaluar.
    datos = datos[datos["y_3"].notna()].copy()
    datos["y_3"] = datos["y_3"].astype(int)
    return datos


def cargar_y_dividir(ruta=RUTA_DATOS, columnas_extra=()):
    """Entrenamiento antes de CORTE y prueba desde CORTE. columnas_extra se
    agregan a X (por ejemplo p90_t3 para la regla de la linea base), pero la
    preparacion las descarta."""
    datos = pd.read_csv(ruta, dtype={"cod_canton": str, "cod_provincia": str}, parse_dates=["fecha"])
    datos = agregar_features(datos)
    X = datos[NUMERICAS + CATEGORICAS + YA_LISTAS + list(columnas_extra)].astype({c: int for c in YA_LISTAS})
    y = datos[OBJETIVO]
    es_entrenamiento = datos["fecha"] < CORTE
    return X[es_entrenamiento], X[~es_entrenamiento], y[es_entrenamiento], y[~es_entrenamiento]


def construir_preparacion():
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


class ReglaUmbral(BaseEstimator, ClassifierMixin):
    """Linea base del dominio: "t+3 igual que t-4", el ultimo dia que cayo el
    mismo dia de la semana. Alta demanda si ese dia ya supero el P90. No
    aprende nada; necesita lag_4d y p90_t3 en X."""

    def fit(self, X, y):
        self.classes_ = np.array([0, 1])
        return self

    def predict_proba(self, X):
        alta = (X["lag_4d"] > X["p90_t3"]).astype(float).to_numpy()
        return np.column_stack([1 - alta, alta])

    def predict(self, X):
        return (self.predict_proba(X)[:, 1] >= 0.5).astype(int)


# Esto corre con "python3 pipeline_proyecto.py", pero no cuando un
# notebook hace "from pipeline_proyecto import ...".
if __name__ == "__main__":
    X_ent, X_prueba, y_ent, y_prueba = cargar_y_dividir()
    print("Entrenamiento:", len(X_ent), "filas antes de", CORTE.date(), " Prueba:", len(X_prueba), "filas")
    print("Tasa de y_3 = 1  entrenamiento:", round(y_ent.mean(), 3), " prueba:", round(y_prueba.mean(), 3))
    preparacion = construir_preparacion()
    X_ent_listo = preparacion.fit_transform(X_ent)
    X_prueba_listo = preparacion.transform(X_prueba)
    print("Entrenamiento:", X_ent_listo.shape, "Prueba:", X_prueba_listo.shape)
    print(list(preparacion.get_feature_names_out()))
