"""Ejercicio 2: diagnostico de calidad de pedidos_tienda.csv.

Mismos pasos del Ejercicio 1, sobre otro archivo. Corre el script con:

    python3 ejercicio2_pedidos.py

Al final se imprime una comprobacion por cada TODO. No la modifiques:
cuando las cinco digan OK, pasa a las preguntas del README.
"""

import pandas as pd

datos = pd.read_csv("pedidos_tienda.csv")
print(f"Filas leidas: {len(datos)}")

print()
print("Paso 1: duplicados")
# TODO 1: cuenta las filas que repiten todas sus columnas y quitalas.
duplicados = None
print(f"Filas duplicadas: {duplicados}")
print(f"Filas despues de quitarlas: {len(datos)}")

print()
print("Paso 2: tipos y faltantes visibles")
print(datos.dtypes)
# TODO 2: cuenta los valores faltantes de cada columna.
faltantes = None
print(faltantes)

print()
print("Paso 3: faltantes disfrazados de texto")
print("Valores distintos de monto:", datos["monto"].unique())
# TODO 3: convierte monto a numero en una columna nueva, monto_num.
datos["monto_num"] = datos["monto"]
print(f"Montos faltantes despues de convertir: {datos['monto_num'].isna().sum()}")

print()
print("Paso 4: fechas con dos formatos")


def normalizar_fecha(valor):
    # TODO 4: mismo criterio que en el Ejercicio 1.
    return pd.to_datetime(valor)


datos["fecha_normalizada"] = datos["fecha"].apply(normalizar_fecha)
print(datos[["pedido_id", "fecha", "fecha_normalizada"]])

print()
print("Paso 5: lo que duplicated() no ve")
# TODO 5: cuantos pedido_id aparecen mas de una vez despues del Paso 1.
# Pista: compara la cantidad de filas con la cantidad de pedido_id
# distintos.
pedidos_repetidos = None
print(f"Pedidos repetidos con valores distintos: {pedidos_repetidos}")


def comprobar(numero, condicion):
    if condicion:
        print(f"TODO {numero}: OK")
    else:
        print(f"TODO {numero}: revisa")


print()
print("Comprobacion")
comprobar(1, duplicados == 2 and len(datos) == 11)
comprobar(2, faltantes is not None and faltantes["cantidad"] == 2)
comprobar(3, datos["monto_num"].isna().sum() == 2)
comprobar(4, (datos["fecha_normalizada"].dt.month == 3).all())
comprobar(5, pedidos_repetidos == 1)
