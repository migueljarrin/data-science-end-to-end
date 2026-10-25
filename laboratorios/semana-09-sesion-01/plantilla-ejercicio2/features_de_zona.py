import pandas as pd

viajes = pd.read_csv("../starter/viajes_taxi.csv")
viajes = viajes[(viajes["tarifa"] != 999.99) & (viajes["duracion_min"] >= 0)].copy()

ZONAS_MANHATTAN = ["Midtown", "Upper East Side", "Upper West Side", "Lower Manhattan", "Harlem"]

# TODO 1: crea la columna es_tarifa_fija (1 o 0): vale 1 cuando el viaje
# va de JFK Airport a una zona de Manhattan, o de una zona de Manhattan a
# JFK Airport. Imprime cuantos viajes la tienen en 1, y la tarifa minima
# y maxima de esos viajes.
jfk_a_manhattan = (viajes["zona_origen"] == "JFK Airport") & viajes["zona_destino"].isin(ZONAS_MANHATTAN)
manhattan_a_jfk = viajes["zona_origen"].isin(ZONAS_MANHATTAN) & (viajes["zona_destino"] == "JFK Airport")
viajes["es_tarifa_fija"] = (jfk_a_manhattan | manhattan_a_jfk).astype(int)

tarifa_fija = viajes[viajes["es_tarifa_fija"] == 1]
print("Viajes con es_tarifa_fija = 1:", len(tarifa_fija))
print("Tarifa minima:", tarifa_fija["tarifa"].min())
print("Tarifa maxima:", tarifa_fija["tarifa"].max())

# TODO 2: codifica zona_origen con one-hot (pd.get_dummies), con el
# prefijo "origen" y dtype=int. Imprime los nombres de las columnas
# nuevas.
one_hot = pd.get_dummies(viajes["zona_origen"], prefix="origen", dtype=int)
viajes = pd.concat([viajes, one_hot], axis=1)
print("\nColumnas one-hot:", len(one_hot.columns))
print(one_hot.columns.tolist())

# TODO 3: codifica zona_origen de forma ordinal: un numero entero por
# zona, en orden alfabetico, en una columna origen_ordinal.
zonas_ordenadas = sorted(viajes["zona_origen"].unique())
codigo_zona = {zona: i for i, zona in enumerate(zonas_ordenadas)}
viajes["origen_ordinal"] = viajes["zona_origen"].map(codigo_zona)
print("\nCodificacion ordinal (1 columna):")
print(codigo_zona)

# TODO 4: para cada columna original del dataset, decide si existe en el
# momento en que alguien pide el taxi (antes del viaje) e imprime la
# decision.
disponibilidad = {
    "id_viaje": ("si", "se asigna al pedir, pero es un identificador: no sirve como feature"),
    "fecha_hora_inicio": ("si", "se sabe cuando y a que hora se pide el taxi"),
    "zona_origen": ("si", "el pasajero esta ahi al pedir"),
    "zona_destino": ("si", "el pasajero indica a donde va"),
    "distancia_km": ("no", "es la distancia recorrida; al pedir solo existe una estimacion de la ruta"),
    "duracion_min": ("no", "se conoce al terminar el viaje"),
    "pasajeros": ("si", "se sabe cuantas personas suben"),
    "metodo_pago": ("no", "se define al pagar, al final del viaje"),
    "tarifa": ("no", "es lo que el modelo debe predecir"),
    "propina": ("no", "se paga al final, despues de la tarifa"),
}
print("\nDisponibilidad al pedir el taxi:")
for columna in pd.read_csv("../starter/viajes_taxi.csv", nrows=0).columns:
    existe, razon = disponibilidad[columna]
    print(f"  {columna:<18} {existe:<3} {razon}")

# Guarda el dataset con las features nuevas para poder revisarlo
viajes.to_csv("viajes_con_features.csv", index=False)
print("\nDataset guardado en viajes_con_features.csv:", viajes.shape)
