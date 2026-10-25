import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

viajes = pd.read_csv("../starter/viajes_features.csv")

NUMERICAS = ["distancia_km", "pasajeros"]
YA_LISTAS = ["hora_sin", "hora_cos", "es_fin_de_semana", "es_hora_pico", "es_tarifa_fija"]
CATEGORICAS = ["zona_origen", "zona_destino", "metodo_pago"]

X = viajes[NUMERICAS + YA_LISTAS + CATEGORICAS]
y = viajes["tarifa"]

# TODO 1: divide X e y en entrenamiento (80%) y prueba (20%), con
# random_state=42.
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print("Entrenamiento:", X_train.shape, " Prueba:", X_test.shape)

# TODO 2: arma un Pipeline para las columnas NUMERICAS (imputar con la
# mediana, despues escalar) y otro para las CATEGORICAS (imputar con el
# valor mas frecuente, despues OneHotEncoder con handle_unknown="ignore" y
# sparse_output=False). Juntalos en un ColumnTransformer llamado
# "preparacion", con las columnas YA_LISTAS pasando sin cambios
# ("passthrough").
pipeline_numericas = Pipeline([
    ("imputar", SimpleImputer(strategy="median")),
    ("escalar", StandardScaler()),
])
pipeline_categoricas = Pipeline([
    ("imputar", SimpleImputer(strategy="most_frequent")),
    ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
])
preparacion = ColumnTransformer([
    ("numericas", pipeline_numericas, NUMERICAS),
    ("ya_listas", "passthrough", YA_LISTAS),
    ("categoricas", pipeline_categoricas, CATEGORICAS),
])

# TODO 3: aprende la preparacion solo con entrenamiento y transforma
# entrenamiento y prueba. Imprime cuantas columnas quedan.
preparacion.fit(X_train)
X_train_listo = preparacion.transform(X_train)
X_test_listo = preparacion.transform(X_test)
print("\nColumnas despues de preparar:", X_train_listo.shape[1])
print("  numericas:", len(NUMERICAS), " ya listas:", len(YA_LISTAS),
      " one-hot:", X_train_listo.shape[1] - len(NUMERICAS) - len(YA_LISTAS))
print("Prueba preparada:", X_test_listo.shape)

# TODO 4: imprime las medianas que aprendio el imputador de numericas
# (atributo statistics_) junto a las medianas de entrenamiento y las de
# todo el dataset.
imputador = preparacion.named_transformers_["numericas"].named_steps["imputar"]
medianas = pd.DataFrame({
    "imputador": imputador.statistics_,
    "entrenamiento": X_train[NUMERICAS].median(),
    "todo_el_dataset": X[NUMERICAS].median(),
})
print("\nMedianas:")
print(medianas)

# TODO 5: transforma el viaje nuevo de abajo, que sale de una zona que el
# entrenamiento nunca vio, e imprime cuantas columnas de zona_origen
# quedan en 1.
nuevo = pd.DataFrame([{
    "distancia_km": 9.0, "pasajeros": 1, "hora_sin": 0.5, "hora_cos": -0.866,
    "es_fin_de_semana": 0, "es_hora_pico": 1, "es_tarifa_fija": 0,
    "zona_origen": "Bronx", "zona_destino": "Midtown", "metodo_pago": "tarjeta",
}])
nuevo_listo = pd.DataFrame(preparacion.transform(nuevo), columns=preparacion.get_feature_names_out())
columnas_origen = [c for c in nuevo_listo.columns if c.startswith("categoricas__zona_origen_")]
print("\nViaje desde el Bronx:")
print("Columnas de zona_origen:", len(columnas_origen))
print("Columnas de zona_origen en 1:", int(nuevo_listo[columnas_origen].sum(axis=1).iloc[0]))
print("Columnas en 1 de todas las categoricas:",
      [c for c in nuevo_listo.columns if c.startswith("categoricas__") and nuevo_listo[c].iloc[0] == 1])
