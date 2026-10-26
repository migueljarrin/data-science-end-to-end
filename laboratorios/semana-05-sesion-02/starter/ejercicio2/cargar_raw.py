import duckdb

# Carga las tablas crudas en ventas.duckdb. Correlo una vez antes de dbt run.
con = duckdb.connect("ventas.duckdb")
con.execute("CREATE OR REPLACE TABLE raw_ventas AS SELECT * FROM read_csv_auto('ventas.csv')")
con.execute("CREATE OR REPLACE TABLE raw_productos AS SELECT * FROM read_csv_auto('productos.csv')")
con.close()
print("raw_ventas y raw_productos cargadas en ventas.duckdb")
