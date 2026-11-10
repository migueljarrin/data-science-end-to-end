# Semana 12, Sesión 1: Patrones de despliegue: ¿batch u online?

> Objetivo de la sesión: elegir entre servir el modelo de tu proyecto en modalidad batch o en modalidad online, justificando la decisión según la latencia que exige el caso de uso propuesto, y proteger con pruebas automáticas, que corren en cada cambio, el código que lo sirve.

**Lectura previa de esta sesión:** ["MLOps: Batch vs Online ML Systems"](https://medium.com/mlops-republic/mlops-batch-vs-online-ml-system-cbacee834837), MLOps Republic.

**Referencia de esta sesión:** *Designing Machine Learning Systems*, Chip Huyen, capítulo 7 (despliegue de modelos y servicio de predicción).

## Requisitos antes de esta sesión

Hoy se agregan tres herramientas: joblib (guardar un modelo entrenado en un archivo), pytest (pruebas automáticas) y GitHub Actions (integración continua). Las librerías nuevas ya están en `requirements.txt`, junto con FastAPI para la sesión siguiente. Sincroniza tu fork y reconstruye el contenedor ("Rebuild Container"), como en la Semana 11. Comprueba desde una terminal:

```
bash .devcontainer/verificar.sh
```

Debe mostrar `pytest 8.3.3` y `fastapi 0.115.4`.

Los laboratorios de hoy son scripts, no notebooks: lo que producen corre sin nadie mirando. Cada ejercicio entrena primero su modelo con un script que ya viene completo (`entrenar.py`), que lo guarda en un archivo `.joblib` dentro de la carpeta del ejercicio. Ese archivo no se sube al repositorio (`*.joblib` está en `.gitignore`).

## Antes de empezar

A partir de la lectura previa:

**Según el artículo, ¿qué distingue un sistema de predicción batch de uno online? Da un ejemplo de cada uno.**

_(tu respuesta)_

**¿Qué limitación tiene el sistema batch que el online resuelve, y qué cuesta resolverla?**

_(tu respuesta)_

## Pregunta de apertura

La app de taxis usa dos modelos: uno estima la tarifa antes de pedir el viaje, otro decide si un pago es fraude. ¿Alguno de los dos se podría calcular una vez por noche para todos los casos posibles? ¿Cuál tiene que responder en el momento, y en cuánto tiempo?

La tarifa se podría calcular de noche, aproximada: con 8 zonas de origen, 8 de destino, 24 horas y fin de semana o no, son 3072 combinaciones, y una tabla precalculada respondería al instante. Pero la distancia exacta y los pasajeros cambian en cada pedido, así que una tabla nocturna pierde precisión; para los viajes reservados del día siguiente sí se puede calcular por lotes, porque se conocen de antemano (es el Ejercicio 1). El de fraude tiene que responder en el momento: depende del pago concreto (tarjeta nueva, intentos fallidos, monto), que no existe hasta que el pasajero paga, y tiene que decidir antes de aprobar el cobro, en uno o dos segundos como mucho.

## Ejercicio 1: la tarifa de los viajes programados, por lotes

Carpeta: [`starter/ejercicio1/`](./starter/ejercicio1/). La app permite reservar un viaje para el día siguiente. Cada noche, [`predecir_lote.py`](./starter/ejercicio1/predecir_lote.py) estima la tarifa de los 60 viajes reservados en [`viajes_programados.csv`](./starter/ejercicio1/viajes_programados.csv) con la red neuronal que elegiste en la Semana 11, y deja las estimaciones en una tabla que la app lee por la mañana. [`test_predecir_lote.py`](./starter/ejercicio1/test_predecir_lote.py) tiene sus pruebas. Los 5 `TODO`: cargar el modelo, estimar, armar la tabla de salida y dos pruebas.

Desde la carpeta del ejercicio, corre todo una vez antes de tocar nada:

```
python entrenar.py
python predecir_lote.py
pytest -v
```

**Respuesta 1 (antes de los TODO):** sin resolver, `predecir_lote.py` escribe una tabla con una sola columna, y `pytest` dice `1 failed, 2 passed`. ¿Cómo pueden pasar dos pruebas si el script no estima ninguna tarifa?

Porque esas dos pruebas no tenían ningún `assert`: eran los `TODO 4` y `5`. Una prueba de pytest solo falla si un `assert` resulta falso o si el código lanza un error; `predecir_lote` corría sin errores (devolvía una tabla con una columna), así que las dos pasaban sin comprobar nada. La única que comprobaba algo era la de las columnas, y esa sí fallaba. Una prueba que pasa no dice nada si no tiene un `assert` que pueda fallar.

**Respuesta 2 (TODO 1 y 2):** 4 de los 60 viajes no tienen pasajeros y 2 no tienen método de pago. ¿Esperas que el script falle en esos viajes, que los salte, o que les estime una tarifa? ¿Por qué?

Que les estime una tarifa. El modelo guardado es el pipeline completo, con la preparación incluida: `SimpleImputer` rellena los pasajeros vacíos con la mediana y el método de pago vacío con el más frecuente, valores que aprendió al entrenar. Así fue: los 4 viajes sin pasajeros recibieron 33.94, 29.88, 25.80 y 17.58 USD, y los 2 sin método de pago 60.79 y 29.59. Saltarlos sería peor: el pasajero que reservó no vería ninguna tarifa por la mañana.

**Respuesta 3 (TODO 3):** todas las filas de la tabla llevan la misma `version_modelo`. ¿Para qué guardarla en cada fila?

Para saber qué modelo produjo cada estimación cuando la tabla se use después, sin depender de recordarlo. Si el modelo se reentrena, las tablas de distintas noches pueden venir de modelos distintos, y la versión (la huella MD5 del archivo `.joblib`, `e1f3c3fcaf73`) permite investigar un reclamo con el modelo exacto que dio esa tarifa, comparar versiones o volver a la anterior si una sale peor. Va en cada fila porque cada fila puede terminar sola: en un reclamo, en otra tabla, en un reporte.

**Respuesta 4 (TODO 4 y 5):** antes de escribir las dos pruebas, ¿qué cambio en `predecir_lote.py` haría fallar la del `TODO 4`? ¿Y la del `TODO 5`?

La del `TODO 4` (una fila por viaje, mismos `id_viaje`, mismo orden) fallaría si el script descartara viajes, por ejemplo con un `dropna()` para quitar los incompletos; si duplicara filas; o si ordenara la salida por tarifa en vez de dejarla en el orden de entrada. La del `TODO 5` fallaría si un viaje incompleto quedara con la tarifa vacía (si se quitara el imputador de la preparación, o si se pusiera `NaN` a mano en los viajes sin pasajeros), o si la columna `version_modelo` no llevara la versión que se pasó (si quedara vacía o fija en otro valor).

**Lo que mostró el lote:**

Versión del modelo: `e1f3c3fcaf73`, igual en las 60 filas, ninguna sin tarifa.

- **Más baja:** 4.67 USD, el viaje 90014, dentro de Upper East Side (0.4 km).
- **Más alta:** 70.26 USD, el viaje 90051, de Upper East Side a JFK Airport (24.04 km): la tarifa fija de 70 del aeropuerto.
- **Sin pasajeros:** 90023 (Queens a Upper West Side, 10.58 km) 33.94 USD; 90024 (Brooklyn a Harlem, 10.17 km) 29.88; 90025 (Midtown a Harlem, 8.40 km) 25.80; 90048 (Harlem a Upper East Side, 4.75 km) 17.58. Tarifas que siguen la distancia, como cualquier otro viaje.

Las 3 pruebas pasan (`3 passed`).

## Durante el ConcepTest

**Tu voto, antes de discutir en pareja** (A, B, C o D):

_(tu voto)_

**Tu razonamiento:**

_(tu respuesta)_

**Después de discutir en pareja, ¿cambiaste de voto? ¿Por qué?**

_(tu respuesta)_

## Ejercicio 2: la cola de revisión de fraude

Solo o en pareja. Carpeta: [`starter/ejercicio2/`](./starter/ejercicio2/). Cada madrugada, [`puntuar_pagos.py`](./starter/ejercicio2/puntuar_pagos.py) calcula la probabilidad de fraude de los 300 pagos de ayer ([`pagos_ayer.csv`](./starter/ejercicio2/pagos_ayer.csv)) con el gradient boosting de la Semana 11, y arma la cola de revisión manual con los pagos que alcanzan el umbral de 0.10 que elegiste ese día. Mismo esqueleto del Ejercicio 1: los pasos 1 a 3 tienen `TODO`; el paso 4 (la cola) y el paso 5 (las pruebas de [`test_puntuar_pagos.py`](./starter/ejercicio2/test_puntuar_pagos.py)) solo tienen un comentario que dice qué hacer. Primero `python entrenar_fraude.py`; después resuelve y corre `python comprobar.py` hasta que los cinco pasos digan `OK`.

**Respuesta 1:** ¿cuántos pagos quedaron en la cola de revisión? ¿Cuántos fraudes esperarías encontrar en los 300 pagos, si la proporción es la de la Semana 11?

26 pagos quedaron en la cola de revisión, con el umbral de 0.10. Con la proporción de la Semana 11 (295 fraudes en 6000 pagos, 4.9%), esperaría unos 15 fraudes en los 300 pagos. La cola tiene más pagos que fraudes esperados porque el umbral 0.10 se eligió para dejar pasar pocos fraudes a cambio de más falsas alarmas: revisar un pago legítimo cuesta 3 USD, y un fraude sin detectar, 40.

**Respuesta 2:** este modelo corre por lotes, una vez al día. ¿Qué pierde la empresa por no evaluar cada pago en el momento en que ocurre? ¿Qué tendría que pasar con la revisión para que eso importe?

Pierde la posibilidad de frenar el fraude antes de que ocurra: cuando el lote de la madrugada marca un pago, el cobro ya se aprobó y el viaje ya se hizo, así que lo único que queda es intentar recuperar el dinero y bloquear la tarjeta para los pagos siguientes. Mientras tanto, la misma tarjeta robada puede usarse en varios viajes durante el día. Eso importa si la revisión puede actuar sobre el pago mismo: bloquear o retener el cobro antes de aprobarlo, o pedir otra verificación en la app. Entonces la decisión tiene que tomarse en el momento del pago, en uno o dos segundos, y el modelo tiene que responder en línea. Si la revisión es manual y se hace al día siguiente, el lote alcanza.

**Respuesta 3:** la prueba de la cola de revisión arma su propia tabla de cuatro pagos con probabilidades escritas a mano, en vez de usar el modelo. ¿Qué gana la prueba con eso?

Que prueba solo la lógica de la cola, con un resultado que se conoce de antemano: con 0.05, 0.40, 0.10 y 0.90 y el umbral 0.10, la cola tiene que ser 4, 2 y 3, en ese orden, y el 0.10 justo en el límite tiene que entrar. Con el modelo real, las probabilidades cambiarían al reentrenar y no sabría qué resultado esperar; si la prueba fallara, no sabría si el error está en el código o en el modelo. Además corre en un instante y en cualquier máquina, también en GitHub Actions, donde no existe el `.joblib` ni los pagos de ayer.

**Si terminas antes:** sube `UMBRAL` a 0.50 y vuelve a correr `puntuar_pagos.py`. ¿Cuántos pagos quedan en la cola? ¿Siguen pasando todas las pruebas? ¿Por qué?

Con el umbral de 0.50 quedan 13 pagos en la cola, la mitad que con 0.10 (26). Las pruebas siguen pasando: la de la cola le pasa a `a_revisar` su propio umbral (0.10) en vez de leer la constante `UMBRAL`, y las demás no usan el umbral. Prueban que el código filtra y ordena bien con cualquier umbral, no qué umbral eligió la empresa. Lo comprobé llamando a `a_revisar` con 0.50 sobre los pagos puntuados, sin cambiar la constante del script, para que `comprobar.py` siga diciendo `OK`.

## Ejercicio 3: el despliegue y las pruebas de tu proyecto

Usa tu proyecto en [`psets/proyecto/`](../../psets/README.md). Esta vez no hay plantilla.

### Entregable 1: `docs/despliegue.md`

Una página que diga si tu modelo se sirve por lotes o en línea, y por qué:

- Qué decisión habilita la predicción, quién la usa y cuánto tiempo puede esperar por ella (un número: milisegundos, horas, un día).
- Cuántos casos distintos hay que predecir, y si se conocen de antemano.
- Qué datos necesitan tus features en el momento de predecir, y si están disponibles en ese momento.
- Qué se pierde con el patrón que descartas.

### Entregable 2: las primeras pruebas de tu proyecto

Un archivo `psets/proyecto/modelado/test_pipeline_proyecto.py` con al menos tres pruebas sobre tu `pipeline_proyecto.py`, cada una con al menos un `assert`. Las pruebas arman sus propios datos (un `DataFrame` de pocas filas escrito a mano), no leen tu archivo de `data/`: en GitHub Actions ese archivo no existe. Ideas de qué probar: que la columna objetivo no está entre las que recibe el modelo; que una feature calculada da el valor que sabes calcular a mano; que una feature que mira hacia atrás en el tiempo no usa una fila del futuro; que la preparación acepta una categoría que no vio al entrenar.

Comprueba desde la raíz de tu fork que pasan, con el mismo comando que va a usar GitHub:

```
pytest psets/proyecto -v
```

### Entregable 3: la integración continua de tu fork

El archivo [`.github/workflows/pruebas.yml`](../../.github/workflows/pruebas.yml) le pide a GitHub que, en cada push, cree una máquina limpia, instale `requirements.txt` y corra `pytest psets/proyecto`. En tu fork viene apagado: en la página de tu fork, pestaña **Actions**, presiona "I understand my workflows, go ahead and enable them". Haz push de tus pruebas y espera la marca verde junto a tu commit.

**Pega el enlace a la ejecución de GitHub Actions donde pasan tus pruebas:**

_(tu respuesta)_

**¿Qué patrón elegiste para tu proyecto, y qué número de latencia lo decide?**

Por lotes, una vez al día. Lo explico en [`psets/proyecto/docs/despliegue.md`](../../psets/proyecto/docs/despliegue.md). El número es **unas 6 horas**: entre el cierre del día *t* (medianoche, cuando el conteo del día está completo) y el inicio de la planificación de turnos (06:00), con una decisión que es sobre el día *t+3*. Además son siempre los mismos 224 casos, uno por cantón, conocidos de antemano. Responder en milisegundos no cambiaría ninguna decisión, y a mitad del día las features estarían incompletas.

**Rompe a propósito una de tus pruebas (cambia un valor esperado), haz push y mira qué pasa en GitHub. Después arréglala. ¿Qué te dijo GitHub, y dónde lo viste?**

_(tu respuesta)_

## Antes de la próxima sesión

**Lectura:** ["Journey to Full-Stack Data Scientist: Model Deployment"](https://towardsdatascience.com/journey-to-full-stack-data-scientist-model-deployment-f385f244ec67/), Towards Data Science.

Hoy la app lee las tarifas de una tabla calculada de noche. Pero cuando un pasajero escribe un destino que no estaba reservado, no hay ninguna fila que leer. ¿Qué tendría que existir para que la app le pregunte al modelo en ese momento, y qué le mandaría?

Un servicio de predicción en línea: un programa encendido todo el tiempo, con el modelo ya cargado en memoria, que escuche en una dirección (una API, por ejemplo con FastAPI) y responda en menos de un segundo. La app le mandaría los datos de ese viaje en una petición (zona de origen, zona de destino, distancia estimada de la ruta, pasajeros, método de pago y la hora del pedido, o las features ya calculadas como `hora_sin`, `hora_cos`, `es_hora_pico` y `es_tarifa_fija`), y el servicio respondería la tarifa estimada y la versión del modelo. Tendría que preparar esos datos exactamente igual que en el entrenamiento: por eso conviene que use el mismo pipeline guardado.
