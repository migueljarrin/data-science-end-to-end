"""Comprobacion del Ejercicio 2. Correla desde esta carpeta, despues de
dbt run y dbt test:

    python3 comprobar.py

No la modifiques.
"""

import duckdb


def comprobar(numero, condicion):
    if condicion:
        print(f"TODO {numero}: OK")
    else:
        print(f"TODO {numero}: revisa")


def leer(ruta):
    with open(ruta) as archivo:
        texto = archivo.read().lower()
    return texto.replace(" ", "").replace('"', "'")


def columnas(con, relacion):
    try:
        return list(con.execute(f"SELECT * FROM {relacion} LIMIT 0").df().columns)
    except duckdb.Error:
        return []


def valor(con, consulta):
    try:
        return con.execute(consulta).fetchone()[0]
    except duckdb.Error:
        return None


con = duckdb.connect("ventas.duckdb", read_only=True)

stg_ventas = leer("models/staging/stg_ventas.sql")
stg_productos = leer("models/staging/stg_productos.sql")
comprobar(1, "select*" not in stg_ventas and "select*" not in stg_productos
          and "id_venta" in columnas(con, "stg_ventas")
          and "categoria" in columnas(con, "stg_productos"))

esquema = leer("models/staging/schema.yml")
comprobar(2, "stg_ventas" in esquema and "stg_productos" in esquema and esquema.count("unique") >= 2)

intermedia = leer("models/intermedia/int_ventas_con_producto.sql")
comprobar(3, "ref('stg_ventas')" in intermedia and "ref('stg_productos')" in intermedia
          and "raw_" not in intermedia and "categoria" in columnas(con, "int_ventas_con_producto"))

filas_marts = valor(con, "SELECT COUNT(*) FROM marts_monto_por_categoria")
comprobar(4, filas_marts == 3 and "ref('int_ventas_con_producto')" in leer("models/marts/marts_monto_por_categoria.sql"))

ventas_raw = valor(con, "SELECT COUNT(*) FROM raw_ventas")
ventas_stg = valor(con, "SELECT COUNT(*) FROM stg_ventas")
ids_stg = valor(con, "SELECT COUNT(DISTINCT id_venta) FROM stg_ventas")
comprobar(5, ventas_raw == 13 and ventas_stg is not None and ventas_stg == ids_stg == 12)

con.close()
