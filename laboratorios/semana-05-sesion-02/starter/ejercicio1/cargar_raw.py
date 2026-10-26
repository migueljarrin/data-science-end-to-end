import duckdb

# Recrea las tablas crudas de la Sesion 1 en almacen.duckdb, para
# modelarlas hoy en capas. Correlo una vez antes de dbt run.
con = duckdb.connect("almacen.duckdb")
con.execute("CREATE OR REPLACE TABLE raw_pedidos AS SELECT * FROM read_csv_auto('pedidos.csv')")
con.execute("CREATE OR REPLACE TABLE raw_clientes AS SELECT * FROM read_csv_auto('clientes.csv')")
con.close()
print("raw_pedidos y raw_clientes cargadas en almacen.duckdb")
