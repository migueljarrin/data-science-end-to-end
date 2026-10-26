"""Ejercicio 2, consumidor: lee el topico lecturas, cuenta las lecturas
por sensor y detecta las que pasan de 30 grados. Corre el productor
primero y despues:

    python3 ejercicio2_consumidor.py

Al final se imprime una comprobacion por cada TODO. No la modifiques.
"""

import json

from kafka import KafkaConsumer

UMBRAL = 30.0


def deserializar_evento(datos):
    # TODO 3: mismo criterio que en el Ejercicio 1.
    return datos


consumidor = KafkaConsumer(
    "lecturas",
    bootstrap_servers="localhost:9092",
    value_deserializer=deserializar_evento,
    # TODO 2: lee el topico desde el primer evento.
    consumer_timeout_ms=10000,
)

lecturas_por_sensor = {}
alertas = []
primera = None
recibidas = 0

for mensaje in consumidor:
    lectura = mensaje.value
    print(f"Consumido: {lectura}")
    recibidas += 1
    if primera is None:
        primera = lectura
    # TODO 4: suma 1 a las lecturas del sensor de esta lectura.
    # TODO 5: si la temperatura pasa de UMBRAL, agrega la lectura a
    # alertas e imprime un aviso con el sensor y la temperatura.

consumidor.close()
print("Lecturas por sensor:", lecturas_por_sensor)
print("Alertas:", alertas)


def comprobar(numero, condicion):
    if condicion:
        print(f"TODO {numero}: OK")
    else:
        print(f"TODO {numero}: revisa")


# El topico tiene las 8 lecturas una vez por cada corrida del productor.
corridas = recibidas // 8 if recibidas % 8 == 0 else 0
print()
print("Comprobacion")
comprobar("1 y 2", primera is not None)
comprobar(3, isinstance(primera, dict))
comprobar(4, corridas > 0 and lecturas_por_sensor == {
    "bodega": 3 * corridas, "camara_fria": 2 * corridas, "techo": 3 * corridas})
comprobar(5, corridas > 0 and len(alertas) == 2 * corridas)
