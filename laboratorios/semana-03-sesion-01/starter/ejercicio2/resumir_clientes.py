import pandas as pd

ENTRADA = "datos/clientes.csv"
SALIDA = "datos/clientes_por_ciudad.csv"

if __name__ == "__main__":
    clientes = pd.read_csv(ENTRADA)
    resumen = clientes.groupby("ciudad")["cliente_id"].count().reset_index(name="clientes")
    resumen.to_csv(SALIDA, index=False)
    print(resumen.to_string(index=False))
    print(f"Guardado en {SALIDA}")
