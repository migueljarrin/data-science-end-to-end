"""Ejercicio 2: un job de Spark sobre envios.csv.

Mismos pasos del Ejercicio 1, sobre otro archivo. Corre el script con:

    python3 ejercicio2_envios.py

Al final se imprime una comprobacion por cada TODO. No la modifiques:
cuando las cinco digan OK, pasa a las preguntas del README.
"""

import os

import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder.appName("costo-de-envios").master("local[*]").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

envios = spark.read.csv("envios.csv", header=True, inferSchema=True)

print("Paso 1: filtrar")
# TODO 1: quedate solo con los envios en estado entregado.
entregados = envios
print(f"Envios entregados: {entregados.count()}")

print()
print("Paso 2: una columna calculada")
# TODO 2: agrega la columna costo = peso_kg * tarifa_por_kg.
con_costo = entregados
con_costo.show(3)

print()
print("Paso 3: agregar por ciudad")
# TODO 3: numero de envios (numero_envios) y costo total (costo_total)
# por ciudad.
resumen = con_costo
resumen.show()

print()
print("Paso 4: guardar el resultado")
# TODO 4: guarda resumen como CSV con encabezado en la carpeta
# resumen_envios, reemplazandola si ya existe.

print()
print("Paso 5: el mismo total con pandas")
total_spark = None
if "costo_total" in resumen.columns:
    total_spark = resumen.agg(F.sum("costo_total")).first()[0]
# TODO 5: calcula con pandas, desde envios.csv, el costo total de los
# envios entregados.
total_pandas = None
print(f"Total con Spark: {total_spark} | total con pandas: {total_pandas}")


def comprobar(numero, condicion):
    if condicion:
        print(f"TODO {numero}: OK")
    else:
        print(f"TODO {numero}: revisa")


print()
print("Comprobacion")
comprobar(1, entregados.count() == 10)
comprobar(2, "costo" in con_costo.columns)
comprobar(3, resumen.count() == 3 and "costo_total" in resumen.columns)
comprobar(4, os.path.exists("resumen_envios/_SUCCESS"))
comprobar(5, total_pandas is not None and total_spark is not None
          and abs(total_pandas - total_spark) < 0.001)

spark.stop()
