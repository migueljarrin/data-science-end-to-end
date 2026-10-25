import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# OBT del PSet 2 (ECU 911). Las 2 features de la sesion pasada se agregan abajo,
# con el mismo codigo de semana-09-sesion-01/plantilla-features.
datos = pd.read_csv(
    r"C:\Users\DELL\Downloads\obt_emergencias_canton_dia.csv",
    dtype={"cod_canton": str, "cod_provincia": str},
    parse_dates=["fecha"],
)
datos = datos.sort_values(["cod_canton", "fecha"]).reset_index(drop=True)

# Objetivo y_3: alta demanda en t+3 (conteo > P90 del canton para el dia de la
# semana de t+3, calculado solo con entrenamiento).
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

# Feature 1: nivel reciente del mismo dia de la semana que t+3, relativo al umbral.
emergencias = datos.groupby("cod_canton")["n_emergencias"]
datos["lag_4d"] = emergencias.shift(4)
media_mismo_dia_t3 = sum(emergencias.shift(k) for k in [4, 11, 18, 25]) / 4
datos["nivel_vs_umbral_t3"] = media_mismo_dia_t3 / datos["p90_t3"]

# Feature 2: posicion de t+3 respecto a un feriado.
calendario = datos.drop_duplicates("fecha").set_index("fecha")["es_feriado"]

def es_feriado_en(dias):
    return datos["fecha"].add(pd.Timedelta(days=dias)).map(calendario).fillna(False).astype(bool)

datos["momento_feriado_t3"] = np.select(
    [datos["es_feriado_t3"], es_feriado_en(4), es_feriado_en(2)],
    ["feriado", "vispera", "dia_despues"],
    default="normal",
)

# Los ultimos 3 dias de cada canton no tienen t+3 observado: no sirven para entrenar ni evaluar.
datos = datos[datos["y_3"].notna()].copy()
datos["y_3"] = datos["y_3"].astype(int)

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

X = datos[NUMERICAS + CATEGORICAS + YA_LISTAS].astype({c: int for c in YA_LISTAS})
y = datos[OBJETIVO]

# Division por fecha: el modelo predice el futuro, asi que entrena con el pasado
# y se evalua con lo que viene despues. El corte es el mismo del P90.
es_entrenamiento = datos["fecha"] < CORTE
X_ent, X_prueba = X[es_entrenamiento], X[~es_entrenamiento]
y_ent, y_prueba = y[es_entrenamiento], y[~es_entrenamiento]
print("Entrenamiento:", datos.loc[es_entrenamiento, "fecha"].min().date(), "a",
      datos.loc[es_entrenamiento, "fecha"].max().date())
print("Prueba:", datos.loc[~es_entrenamiento, "fecha"].min().date(), "a",
      datos.loc[~es_entrenamiento, "fecha"].max().date())
print("Tasa de y_3 = 1  entrenamiento:", round(y_ent.mean(), 3), " prueba:", round(y_prueba.mean(), 3))

preparacion = ColumnTransformer([
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

X_ent_listo = preparacion.fit_transform(X_ent)
X_prueba_listo = preparacion.transform(X_prueba)
print("Entrenamiento:", X_ent_listo.shape, "Prueba:", X_prueba_listo.shape)
print(list(preparacion.get_feature_names_out()))
