"""Ejercicio 1: encontrar y corregir la fuga en viajes_features.csv.

Corre el script antes de tocar nada:

    python3 ejercicio1_fuga.py

La primera parte es el codigo de un companero, con fuga. La segunda es
la version correcta, con 3 TODO. Corre sin errores sin resolverlos.
"""

import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

viajes = pd.read_csv("viajes_features.csv")
X = viajes[["distancia_km", "pasajeros"]]
y = viajes["tarifa"]

print("Version del companero")
imputador = SimpleImputer(strategy="median")
escalador = StandardScaler()
X_preparado = escalador.fit_transform(imputador.fit_transform(X))
X_ent_fuga, X_prueba_fuga, y_ent_fuga, y_prueba_fuga = train_test_split(
    X_preparado, y, test_size=0.2, random_state=42)
modelo_fuga = LinearRegression().fit(X_ent_fuga, y_ent_fuga)
mae_fuga = mean_absolute_error(y_prueba_fuga, modelo_fuga.predict(X_prueba_fuga))
print("Filas que vio el escalador:", escalador.n_samples_seen_)
print("Media de distancia usada para escalar:", round(escalador.mean_[0], 4))
print(f"Error absoluto medio en prueba: {mae_fuga:.4f}")

print()
print("Version correcta")
# TODO 1: divide X e y en entrenamiento (80%) y prueba (20%), con
# random_state=42, antes de calcular cualquier estadistica.
X_ent, X_prueba, y_ent, y_prueba = X, X, y, y

# TODO 2: un Pipeline con tres pasos: imputar con la mediana, escalar y
# la regresion lineal.
pipeline = Pipeline([
    ("imputar", SimpleImputer(strategy="median")),
    ("modelo", LinearRegression()),
])

# TODO 3: el pipeline aprende solo con entrenamiento.
pipeline.fit(X, y)

mae_correcto = mean_absolute_error(y_prueba, pipeline.predict(X_prueba))
if "escalar" in pipeline.named_steps:
    escalador_correcto = pipeline.named_steps["escalar"]
    print("Filas que vio el escalador:", escalador_correcto.n_samples_seen_)
    print("Media de distancia usada para escalar:", round(escalador_correcto.mean_[0], 4))
else:
    print("El pipeline todavia no escala")
print("Filas de prueba:", len(X_prueba))
print(f"Error absoluto medio en prueba: {mae_correcto:.4f}")
