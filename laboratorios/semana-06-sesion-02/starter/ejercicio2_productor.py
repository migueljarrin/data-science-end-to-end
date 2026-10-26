"""Ejercicio 2, productor: publica 8 lecturas de temperatura en el topico
lecturas. Corre:

    python3 ejercicio2_productor.py
"""

import json
import time

from kafka import KafkaProducer


def serializar_evento(evento):
    return json.dumps(evento).encode("utf-8")


productor = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=serializar_evento,
)

lecturas = [
    {"sensor": "bodega", "temperatura": 21.5},
    {"sensor": "camara_fria", "temperatura": 4.0},
    {"sensor": "techo", "temperatura": 28.0},
    {"sensor": "bodega", "temperatura": 22.0},
    {"sensor": "techo", "temperatura": 31.5},
    {"sensor": "camara_fria", "temperatura": 3.5},
    {"sensor": "techo", "temperatura": 33.0},
    {"sensor": "bodega", "temperatura": 22.5},
]

for lectura in lecturas:
    # TODO 1: publica la lectura en el topico lecturas.
    print(f"Lectura lista: {lectura}")
    time.sleep(0.3)

productor.flush()
productor.close()
print("Productor terminado")
