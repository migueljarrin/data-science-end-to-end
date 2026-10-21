import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

os.makedirs("figuras", exist_ok=True)

# OBT del PSet 2 (ECU 911), exportada desde Snowflake: OBT.OBT_EMERGENCIAS_CANTON_DIA.
# Los codigos DPA se leen como texto para no perder el cero inicial (0101 = Cuenca).
datos = pd.read_csv(
    r"C:\Users\DELL\Downloads\obt_emergencias_canton_dia.csv",
    dtype={"cod_canton": str, "cod_provincia": str},
    parse_dates=["fecha"],
)

# El modelo clasifica alta demanda a t+3 (y_3); su insumo es el conteo futuro real.
OBJETIVO = "obj_n_emergencias_t3"

# Paso 1: resumen.
print("Filas y columnas:", datos.shape)
print(datos.dtypes)
print(datos.isna().sum())
print(datos.describe().round(2))

# Paso 2: distribucion de la variable objetivo.
# dropna: los ultimos 3 dias de cada canton no tienen conteo futuro (672 nulos).
plt.figure()
plt.hist(datos[OBJETIVO].dropna(), bins=40)
plt.title(OBJETIVO)
plt.savefig("figuras/distribucion_objetivo.png")
plt.close()

# Paso 3: atipicos de la variable objetivo con la regla del IQR.
q1 = datos[OBJETIVO].quantile(0.25)
q3 = datos[OBJETIVO].quantile(0.75)
iqr = q3 - q1
fuera = datos[(datos[OBJETIVO] < q1 - 1.5 * iqr) | (datos[OBJETIVO] > q3 + 1.5 * iqr)]
print(f"Atipicos de {OBJETIVO} segun IQR: {len(fuera)}")
print(fuera.head(10))

# Paso 4: relacion del objetivo con el volumen previo, dentro de un mismo canton.
# t+3 cae en otro dia de la semana que t; t-4 cae en el mismo dia que t+3.
datos = datos.sort_values(["cod_canton", "fecha"])
datos["lag_4d"] = datos.groupby("cod_canton")["n_emergencias"].shift(4)
quito = datos[datos["canton"] == "QUITO"]

fig, ejes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
ejes[0].scatter(quito["n_emergencias"], quito[OBJETIVO], s=4)
ejes[0].set_title("Quito: emergencias en t vs t+3")
ejes[0].set_xlabel("n_emergencias (t)")
ejes[0].set_ylabel(OBJETIVO)
ejes[1].scatter(quito["lag_4d"], quito[OBJETIVO], s=4)
ejes[1].set_title("Quito: emergencias en t-4 vs t+3")
ejes[1].set_xlabel("lag_4d (mismo dia de la semana que t+3)")
fig.tight_layout()
fig.savefig("figuras/quito_relacion_objetivo.png")
plt.close(fig)

# Paso 5: consultas que confirman los hallazgos.

# Hallazgo 1: los atipicos del IQR son cantones grandes completos, no errores.
print("\n--- Hallazgo 1: escala entre cantones ---")
print("Cantones distintos entre los atipicos:", fuera["canton"].nunique())
print(fuera["canton"].value_counts().head(5))
total_canton = datos.groupby("canton")["n_emergencias"].sum().sort_values(ascending=False)
print("Proporcion de Quito + Guayaquil:", round(total_canton.head(2).sum() / total_canton.sum(), 3))
print("Cantones con mediana diaria <= 2:", (datos.groupby("canton")["n_emergencias"].median() <= 2).sum())
print("Correlacion global n_emergencias vs objetivo:",
      round(datos["n_emergencias"].corr(datos[OBJETIVO]), 3))

# Hallazgo 2: ciclo semanal; el rezago util es el del mismo dia de la semana que t+3.
print("\n--- Hallazgo 2: ciclo semanal ---")
print(datos.groupby("nombre_dia")["n_emergencias"].mean().round(1).sort_values())
for canton in ["QUITO", "GUAYAQUIL", "CUENCA"]:
    serie = datos[datos["canton"] == canton]
    print(canton, serie[["n_emergencias", "lag_7d", "lag_4d", OBJETIVO]]
          .corr()[OBJETIVO].drop(OBJETIVO).round(3).to_dict())

# Hallazgo 3: el volumen baja con los anios, asi que un P90 fijo cambia la tasa de alta demanda.
# Etiqueta y_3 como en el PSet 1: P90 por canton y dia de la semana de t+3, solo con entrenamiento.
print("\n--- Hallazgo 3: deriva temporal y etiqueta ---")
print("Emergencias por dia (todo el pais):")
print((datos.groupby("anio")["n_emergencias"].sum() / datos.groupby("anio")["fecha"].nunique()).round(0))

CORTE = pd.Timestamp("2025-07-01")
datos["dia_semana_t3"] = (datos["dia_semana"] + 2) % 7 + 1
p90 = (datos[datos["fecha"] < CORTE]
       .groupby(["cod_canton", "dia_semana_t3"])[OBJETIVO].quantile(0.9).rename("p90"))
datos = datos.join(p90, on=["cod_canton", "dia_semana_t3"])
datos["y_3"] = np.where(datos[OBJETIVO].isna(), np.nan, (datos[OBJETIVO] > datos["p90"]).astype(float))

print("Tasa de y_3 = 1 global:", round(datos["y_3"].mean(), 3))
print("Tasa de y_3 = 1 por anio:")
print(datos.groupby("anio")["y_3"].mean().round(3))
print("Tasa de y_3 = 1 en el periodo anomalo (enero 2024):",
      round(datos.loc[datos["es_periodo_anomalo"], "y_3"].mean(), 3))
print("Tasa de y_3 = 1 segun feriado en t+3:")
print(datos.groupby("es_feriado_t3")["y_3"].mean().round(3))
