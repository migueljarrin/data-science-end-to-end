import random
import sys

fecha = sys.argv[1] if len(sys.argv) > 1 else "sin fecha"

if random.random() < 0.3:
    print(f"Error de conexion simulado: la estacion no respondio para {fecha}")
    sys.exit(1)

print(f"Lecturas de clima registradas para {fecha}")
