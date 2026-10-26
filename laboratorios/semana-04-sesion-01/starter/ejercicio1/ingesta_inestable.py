import random
import sys

if random.random() < 0.5:
    print("Error de conexion simulado: la fuente de datos no respondio")
    sys.exit(1)

print("Ingesta completada correctamente")
