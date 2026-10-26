ENTRADA = "datos/clientes.csv"
SALIDA = "datos/conteo.txt"

if __name__ == "__main__":
    with open(ENTRADA) as archivo:
        filas = len(archivo.readlines()) - 1
    with open(SALIDA, "w") as archivo:
        archivo.write(f"{filas}\n")
    print(f"{filas} clientes. Guardado en {SALIDA}")
