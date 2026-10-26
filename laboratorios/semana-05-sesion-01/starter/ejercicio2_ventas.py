"""Ejercicio 2: un warehouse local con ventas.csv y productos.csv.

Mismos pasos del Ejercicio 1, sobre otros archivos. Corre el script con:

    python3 ejercicio2_ventas.py

Al final se imprime una comprobacion por cada TODO. No la modifiques:
cuando las cinco digan OK, pasa a las preguntas del README.
"""

import duckdb

con = duckdb.connect("ventas.duckdb")

print("Paso 1: cargar los dos archivos")
# TODO 1: crea las tablas ventas y productos a partir de sus CSV.
print(con.execute("SHOW TABLES").df())

print()
print("Paso 2: cuantas ventas hay")
# TODO 2: cuenta las filas de ventas.
total_ventas = None
print(f"Ventas: {total_ventas}")

print()
print("Paso 3: unidades por producto")
# TODO 3: total de unidades por id_producto, sin unir con productos.
unidades_por_producto = None
print(unidades_por_producto)

print()
print("Paso 4: monto por categoria")
# TODO 4: une ventas con productos y calcula el monto total
# (unidades * precio) por categoria.
monto_por_categoria = None
print(monto_por_categoria)

print()
print("Paso 5: lo que el JOIN deja afuera")
# TODO 5: cuantas ventas no aparecen en el resultado del JOIN del Paso 4.
# Pista: compara el total del Paso 2 con un COUNT(*) sobre el JOIN.
ventas_perdidas = None
print(f"Ventas que el JOIN deja afuera: {ventas_perdidas}")


def comprobar(numero, condicion):
    if condicion:
        print(f"TODO {numero}: OK")
    else:
        print(f"TODO {numero}: revisa")


print()
print("Comprobacion")
tablas = list(con.execute("SHOW TABLES").df()["name"])
comprobar(1, "ventas" in tablas and "productos" in tablas)
comprobar(2, total_ventas == 12)
comprobar(3, unidades_por_producto is not None and len(unidades_por_producto) == 5)
comprobar(4, monto_por_categoria is not None and len(monto_por_categoria) == 3)
comprobar(5, ventas_perdidas == 1)

con.close()
