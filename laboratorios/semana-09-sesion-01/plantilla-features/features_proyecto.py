import numpy as np
import pandas as pd

# OBT del PSet 2 (ECU 911), la misma de la exploracion de la Semana 8.
datos = pd.read_csv(
    r"C:\Users\DELL\Downloads\obt_emergencias_canton_dia.csv",
    dtype={"cod_canton": str, "cod_provincia": str},
    parse_dates=["fecha"],
)
datos = datos.sort_values(["cod_canton", "fecha"]).reset_index(drop=True)

# El modelo predice y_3: alta demanda en t+3 (1 si el conteo supera el P90 del
# canton para el dia de la semana de t+3, calculado solo con entrenamiento).
OBJETIVO = "y_3"
CORTE = pd.Timestamp("2025-07-01")
datos["dia_semana_t3"] = (datos["dia_semana"] + 2) % 7 + 1
p90 = (datos[datos["fecha"] < CORTE]
       .groupby(["cod_canton", "dia_semana_t3"])["obj_n_emergencias_t3"].quantile(0.9)
       .rename("p90_t3"))
datos = datos.join(p90, on=["cod_canton", "dia_semana_t3"])
datos[OBJETIVO] = np.where(
    datos["obj_n_emergencias_t3"].isna(), np.nan,
    (datos["obj_n_emergencias_t3"] > datos["p90_t3"]).astype(float),
)

# Feature 1: nivel reciente del mismo dia de la semana que t+3, relativo al umbral.
# t-4, t-11, t-18 y t-25 caen el mismo dia de la semana que t+3 (hallazgo 2), y
# dividir por el P90 del canton compara a cada canton consigo mismo (hallazgo 1).
emergencias = datos.groupby("cod_canton")["n_emergencias"]
media_mismo_dia_t3 = sum(emergencias.shift(k) for k in [4, 11, 18, 25]) / 4
datos["nivel_vs_umbral_t3"] = media_mismo_dia_t3 / datos["p90_t3"]

# Feature 2: posicion de t+3 respecto a un feriado (vispera, feriado, dia despues).
# El calendario de feriados se conoce con anticipacion; es_feriado_t3 solo marca
# el feriado, no la vispera.
calendario = datos.drop_duplicates("fecha").set_index("fecha")["es_feriado"]

def es_feriado_en(dias):
    return datos["fecha"].add(pd.Timedelta(days=dias)).map(calendario).fillna(False).astype(bool)

datos["momento_feriado_t3"] = np.select(
    [datos["es_feriado_t3"], es_feriado_en(4), es_feriado_en(2)],
    ["feriado", "vispera", "dia_despues"],
    default="normal",
)

# Evidencia: compara el objetivo segun cada feature nueva.
print("Tasa global de y_3 = 1:", round(datos[OBJETIVO].mean(), 3))

print("\nFeature 1, correlacion con el objetivo:")
print(datos[["nivel_vs_umbral_t3", OBJETIVO]].corr().round(3))
print("Tasa de y_3 = 1 por quintil de nivel_vs_umbral_t3:")
quintil = pd.qcut(datos["nivel_vs_umbral_t3"], 5, labels=["Q1", "Q2", "Q3", "Q4", "Q5"])
print(datos.groupby(quintil, observed=True)[OBJETIVO].mean().round(3))
print("Correlacion en entrenamiento y en prueba:")
for nombre, filas in [("entrenamiento", datos["fecha"] < CORTE), ("prueba", datos["fecha"] >= CORTE)]:
    print(f"  {nombre}: {datos.loc[filas, ['nivel_vs_umbral_t3', OBJETIVO]].corr().iloc[0, 1]:.3f}")

print("\nFeature 2, tasa de y_3 = 1 por grupo:")
print(datos.groupby("momento_feriado_t3")[OBJETIVO].agg(["mean", "size"]).round(3))

print(datos[["cod_canton", "canton", "fecha", "nivel_vs_umbral_t3", "momento_feriado_t3", OBJETIVO]].head())
