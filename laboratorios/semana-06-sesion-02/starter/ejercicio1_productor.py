"""Ejercicio 1, productor: publica 10 pedidos en el topico pedidos.

Con Redpanda levantado (docker compose up -d), corre:

    python3 ejercicio1_productor.py
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

categorias = ["electronica", "hogar", "ropa"]

for id_pedido in range(1, 11):
    evento = {
        "id_pedido": id_pedido,
        "categoria": categorias[id_pedido % len(categorias)],
        "monto": round(10 + id_pedido * 3.5, 2),
    }
    # TODO 1: publica el evento en el topico pedidos.
    print(f"Evento listo: {evento}")
    time.sleep(0.5)

productor.flush()
productor.close()
print("Productor terminado")
