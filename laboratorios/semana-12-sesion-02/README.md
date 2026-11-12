# Semana 12, Sesión 2: Despliegue de modelos como servicio de predicción

> Objetivo de la sesión: exponer el modelo entrenado de tu proyecto como un servicio de predicción mediante una API, empaquetado en un contenedor, con pruebas de su contrato de entrada y salida.

**Lectura previa de esta sesión:** ["Journey to Full-Stack Data Scientist: Model Deployment"](https://towardsdatascience.com/journey-to-full-stack-data-scientist-model-deployment-f385f244ec67/), Towards Data Science.

**Referencia de esta sesión:** [Machine Learning Zoomcamp, Módulo 5 (DataTalksClub)](https://github.com/DataTalksClub/machine-learning-zoomcamp).

## Requisitos antes de esta sesión

Nada nuevo que instalar: FastAPI y uvicorn ya llegaron con el contenedor reconstruido la sesión pasada. Los laboratorios de hoy son scripts y un `Dockerfile`. El servicio escucha en el puerto 8000: cuando lo levantes, aparece en la pestaña **Ports** como "Servicio de predicción (Semana 12)", y su documentación interactiva queda en la ruta `/docs` de ese puerto.

## Antes de empezar

A partir de la lectura previa:

**Según el artículo, ¿qué pasos separan un modelo entrenado en un notebook de un modelo que otra aplicación puede usar?**

_(tu respuesta)_

**¿Para qué usa el artículo un contenedor, si el servicio ya corre en la máquina de quien lo escribió?**

_(tu respuesta)_

## Pregunta de apertura

La sesión pasada, la app leía las tarifas de una tabla calculada de noche. Cuando un pasajero escribe un destino que no estaba reservado, no hay ninguna fila que leer. ¿Qué tendría que existir para que la app le pregunte al modelo en ese momento, y qué le mandaría?

Un servicio de predicción en línea: un programa encendido todo el tiempo, con el modelo ya cargado en memoria, que escuche en una dirección (una API) y responda en menos de un segundo. La app le mandaría los datos del viaje como los conoce antes de que empiece (fecha y hora, zona de origen y de destino, distancia estimada, pasajeros y método de pago), y el servicio calcularía el resto de las features igual que en el entrenamiento y respondería la tarifa estimada. Es lo que construye el Ejercicio 1.

## Ejercicio 1: la tarifa, como servicio

Carpeta: [`starter/ejercicio1/`](./starter/ejercicio1/). [`servicio.py`](./starter/ejercicio1/servicio.py) es una API de FastAPI con dos rutas: `/salud`, que dice si el servicio está vivo y tiene su modelo, y `/predecir`, que recibe un viaje como JSON y devuelve la tarifa estimada. El viaje llega como lo conoce la app (fecha y hora, zonas, distancia, pasajeros, método de pago), y [`features_taxis.py`](./starter/ejercicio1/features_taxis.py) calcula el resto de las features igual que se calcularon para entrenar. [`test_servicio.py`](./starter/ejercicio1/test_servicio.py) prueba la API sin levantarla, y el [`Dockerfile`](./starter/ejercicio1/Dockerfile) la empaqueta. Los 5 `TODO`: el esquema de entrada, la predicción, dos pruebas y el comando del contenedor.

Desde la carpeta del ejercicio, corre todo una vez antes de tocar nada:

```
python entrenar.py
pytest -v
uvicorn servicio:app --port 8000
```

Con el servicio levantado, abre el puerto 8000 desde la pestaña **Ports**, agrega `/docs` a la dirección y prueba `/predecir` con **Try it out**. También desde otra terminal:

```
curl -X POST localhost:8000/predecir -H "Content-Type: application/json" -d '{"fecha_hora_inicio": "2026-11-05 08:30", "zona_origen": "Midtown", "zona_destino": "JFK Airport", "distancia_km": 26.4, "pasajeros": 2, "metodo_pago": "tarjeta"}'
```

**Respuesta 1 (antes de los TODO):** sin resolver, `/salud` dice que el modelo está cargado, `/predecir` responde 200 y `pytest` dice `3 passed`. ¿Qué de esa salida debería preocuparte?

Que todo sale en verde y el servicio no sirve. `/predecir` responde 200, pero con una tarifa de 0.0 para cualquier viaje: el esquema solo pide las zonas y el código nunca llama al modelo. `/salud` solo dice que el archivo del modelo se cargó, no que las predicciones tengan sentido. Y de las 3 pruebas, dos no tienen ningún `assert` (los `TODO` 3 y 4), así que pasan sin comprobar nada. Un código 200 y unas pruebas en verde no dicen que la respuesta sea correcta.

**Respuesta 2 (TODO 1):** con el esquema completo, ¿qué esperas que responda el servicio a un viaje sin `distancia_km`? ¿Y a uno sin `zona_origen`?

Sin `distancia_km`, una tarifa: el campo es opcional (vale `None` por defecto) y la preparación lo imputa con la mediana, como en el entrenamiento. El viaje de Midtown a JFK sin distancia dio 68.56 USD (con 26.4 km, 70.39). Sin `zona_origen`, un 422 con `"Field required"` en `["body", "zona_origen"]`: es obligatoria y FastAPI rechaza la petición antes de llegar al modelo. También rechaza con 422 una fecha mal escrita (`"5 de noviembre"`), porque `fecha_hora_inicio` es un `datetime`.

**Respuesta 3 (TODO 2):** el modelo se entrenó con `hora_sin`, `hora_cos` y `es_hora_pico`, pero la app manda solo la fecha y hora. ¿Qué pasaría si el servicio calculara `es_hora_pico` con otras horas que las del entrenamiento?

El modelo se equivocaría sin dar ningún error. Aprendió que `es_hora_pico = 1` (de 7 a 9 y de 16 a 19, días laborables) significa más tiempo por kilómetro y una tarifa más alta; si el servicio marcara otras horas, aplicaría ese recargo a los viajes equivocados y se lo quitaría a los de hora pico real. Midtown a Harlem, 8 km: el jueves a las 8:30 cuesta 27.19 USD y a las 11:30, 24.35. Por eso `features_taxis.py` es un solo archivo que importan el entrenamiento y el servicio. Encontré un caso real de este problema: si un pedido llega sin método de pago, Pydantic lo deja como `None`, pero en el entrenamiento los vacíos eran `NaN`. La preparación imputa `NaN` y trata `None` como una categoría desconocida: la tarifa de un mismo viaje pasaba de 27.19 a 18.68 USD, sin ningún error. El servicio convierte los `None` a `NaN` antes de predecir.

**Respuesta 4 (TODO 3 y 4):** el código 422 del viaje sin zona de origen, ¿lo produce tu código o FastAPI? ¿La petición llega al modelo?

Lo produce FastAPI, no mi código: antes de llamar a `predecir`, valida el cuerpo contra el esquema `Viaje`, y si falta un campo obligatorio responde 422 por su cuenta. La petición no llega al modelo, ni siquiera a la función. La prueba lo comprueba mirando que el error apunte a `["body", "zona_origen"]`.

**Respuesta 5 (TODO 5):** construye y corre la imagen con el `CMD` sin resolver (`docker build -t servicio-tarifa .` y `docker run -p 8000:8000 servicio-tarifa`). El log dice que uvicorn está corriendo, pero `curl localhost:8000/salud` falla. ¿Por qué?

Porque sin `--host`, uvicorn escucha en `127.0.0.1`, que es el localhost de adentro del contenedor, no el de mi laptop. `docker run -p 8000:8000` reenvía el puerto 8000 de la laptop a la interfaz de red del contenedor, y ahí no escucha nadie. Lo comprobé: el log decía `Uvicorn running on http://127.0.0.1:8000` y `curl` falló con código 52 (respuesta vacía). Con `--host 0.0.0.0` escucha en todas las interfaces del contenedor: el log dice `running on http://0.0.0.0:8000` y `/salud` responde.

**Lo que respondió el servicio:**

Midtown a JFK Airport (26.4 km, 2 pasajeros, tarjeta, jueves 8:30): `{"tarifa_estimada": 70.39}`, la tarifa fija del aeropuerto. La misma respuesta desde el contenedor de Docker.

Sin zona de origen, HTTP 422:

```
{"detail":[{"type":"missing","loc":["body","zona_origen"],"msg":"Field required","input":{"fecha_hora_inicio":"2026-11-05 08:30","zona_destino":"JFK Airport","distancia_km":26.4,"pasajeros":2,"metodo_pago":"tarjeta"}}]}
```

Las 3 pruebas pasan (`3 passed`).

## Durante el ConcepTest

**Tu voto, antes de discutir en pareja** (A, B, C o D):

_(tu voto)_

**Tu razonamiento:**

_(tu respuesta)_

**Después de discutir en pareja, ¿cambiaste de voto? ¿Por qué?**

_(tu respuesta)_

## Ejercicio 2: el fraude, en el momento del pago

Solo o en pareja. Carpeta: [`starter/ejercicio2/`](./starter/ejercicio2/). La sesión pasada, los pagos se revisaban al día siguiente. Ahora la empresa quiere decidir en el momento del cobro si un pago va a revisión. [`servicio_fraude.py`](./starter/ejercicio2/servicio_fraude.py) expone el mismo gradient boosting en `/evaluar_pago`, que devuelve la probabilidad de fraude y la decisión. Mismo esqueleto del Ejercicio 1: los pasos 1 a 3 tienen `TODO` (el esquema, la probabilidad y la prueba del pago válido); el paso 4 (la decisión con el umbral) y el paso 5 (la prueba del pago sin monto) solo tienen un comentario. El `Dockerfile` ya está completo. Primero `python entrenar_fraude.py`; después resuelve y corre `python comprobar.py` hasta que los cinco pasos digan `OK`.

**Respuesta 1:** levanta el servicio y evalúa dos pagos: uno de madrugada, por app, con tarjeta nueva, dos intentos fallidos y ningún viaje previo; otro de la tarde, con tarjeta conocida y 22 viajes previos. ¿Qué probabilidad y qué decisión recibió cada uno?

El de madrugada (02:40, por app, tarjeta nueva, 2 intentos fallidos, 0 viajes previos): probabilidad de fraude de 0.9996 y `"revisar": true`. El de la tarde (14:10, tarjeta conocida, 22 viajes previos): 0.0159 y `"revisar": false`. Los cinco pasos de `comprobar.py` dicen `OK`.

**Respuesta 2:** el servicio devuelve la decisión (`revisar`) además de la probabilidad. ¿Qué gana la app con eso? ¿Qué tendría que cambiar si la empresa decide mañana que el umbral es 0.20?

La app no necesita saber nada del modelo ni del umbral: recibe la decisión lista y la ejecuta, y la regla del negocio queda en un solo lugar. Si cada app comparara la probabilidad por su cuenta, un cambio de umbral obligaría a cambiar todas. Con el umbral en 0.20 cambia solo la constante `UMBRAL` de `servicio_fraude.py`: se reconstruye la imagen y se vuelve a desplegar, y la app sigue igual. Las pruebas siguen pasando (el modelo de prueba da 0.25, que también alcanza 0.20). Mejor todavía sería leer el umbral de una variable de entorno, como `RUTA_MODELO`, para cambiarlo sin reconstruir la imagen.

**Respuesta 3:** el mismo pago, evaluado por este servicio y por el lote de la sesión pasada, ¿da la misma probabilidad? ¿Qué tiene que ser igual en los dos para que así sea?

Sí. Mandé al servicio los 300 pagos de ayer y comparé con `pagos_puntuados.csv` del lote de la sesión pasada: la diferencia máxima es 0.000000 (el pago 70058, por ejemplo, da 0.9984 en los dos). Para que coincida tienen que ser iguales el modelo (los mismos datos de entrenamiento, el mismo código, `random_state=42` y la misma versión de scikit-learn) y la preparación: los dos importan `agregar_features` y `columnas` de `preparacion_pagos.py`, en vez de calcular `hora` y `monto_por_km` cada uno a su manera. Curiosamente, los dos `.joblib` no son idénticos byte a byte, pero sus predicciones sí: lo que importa es el modelo que contienen, no los bytes del archivo.

**Si terminas antes:** manda a `/evaluar_pago` un pago con `"monto": "cuarenta"`. ¿Qué responde el servicio, y qué línea de `servicio_fraude.py` produce esa respuesta?

Un 422: `{"type": "float_parsing", "loc": ["body", "monto"], "msg": "Input should be a valid number, unable to parse string as a number", "input": "cuarenta"}`. Lo produce la línea `monto: float` del esquema `Pago` (línea 34): FastAPI valida el cuerpo contra ese tipo antes de llamar a `evaluar_pago`, así que la función nunca se ejecuta.

## Ejercicio 3: el servicio de tu proyecto

Usa tu proyecto en [`psets/proyecto/`](../../psets/README.md) y el modelo final que registraste en MLflow (Semana 11). Esta vez no hay plantilla. Aunque tu proyecto se despliegue por lotes, el servicio también se construye: es la forma en que otro sistema (tu propio lote, un tablero, otra aplicación) le pide una predicción a tu modelo.

### Entregable 1: el servicio, en `psets/proyecto/servicio/`

- Un script que exporte tu modelo final desde MLflow a `servicio/modelo.joblib` (`mlflow.sklearn.load_model("runs:/<run_id>/modelo")` y `joblib.dump`). El archivo no se sube: se regenera con ese script.
- `servicio/api.py`, con `/salud` y una ruta de predicción. El esquema de entrada recibe los datos como los conoce quien llama, y el servicio calcula las features con las mismas funciones de tu `modelado/pipeline_proyecto.py`, importadas desde ahí (`from modelado.pipeline_proyecto import ...`), no copiadas.
- `servicio/Dockerfile` y `servicio/requirements.txt`, con la misma versión de scikit-learn con que entrenaste. La imagen se construye desde `psets/proyecto/`, porque necesita `modelado/` además de `servicio/`: `docker build -f servicio/Dockerfile -t <tu-servicio> .`

El servicio corre desde `psets/proyecto/`: `uvicorn servicio.api:app --port 8000`. El archivo [`psets/proyecto/conftest.py`](../../psets/proyecto/conftest.py) hace que las pruebas también encuentren `modelado/` desde ahí.

### Entregable 2: `servicio/test_api.py`

Al menos tres pruebas con `TestClient`: `/salud`, una predicción válida con un modelo de prueba (no tu `modelo.joblib`, que no existe en GitHub Actions) y una entrada inválida que recibe 422. El workflow de la sesión pasada ya corre todo lo que hay en `psets/proyecto`: en tu próximo push, GitHub corre también estas pruebas.

### Entregable 3: respuestas

En `proyecto/README.md`, agrega la sección **Cómo correr el servicio**: cómo se exporta el modelo, cómo se construye y se levanta el contenedor, y un ejemplo de petición con su respuesta.

**¿Qué datos recibe tu servicio, y cuáles de tus features calcula él mismo? ¿Cómo sabes que las calcula igual que en el entrenamiento?**

Servicio: [`psets/proyecto/servicio/api.py`](../../psets/proyecto/servicio/api.py), con sus pruebas en [`test_api.py`](../../psets/proyecto/servicio/test_api.py) y cómo correrlo en [`psets/proyecto/README.md`](../../psets/proyecto/README.md).

**Lo que recibe:** lo que el ECU 911 sabe al cierre del día *t*: el cantón, la fecha, las emergencias de los 29 días de *t−28* a *t*, los conteos por servicio del día *t* (seguridad, sanitaria, tránsito) y los feriados entre *t* y *t+4*.

**Lo que calcula él mismo:** todas las demás features. Los rezagos (`lag_1d` a `lag_28d`) y las medias de 7 y 28 días, con `rezagos_y_medias`, que replica lo que calcula el job de Spark del PSet 2. `lag_4d`, `nivel_vs_umbral_t3`, `dia_semana_t3` y `momento_feriado_t3`, con `calcular_features`. Más el mes, el fin de semana y el feriado del día. El umbral P90 de cada cantón y la región no se pueden calcular al predecir (el P90 sale del conteo de *t+3*), así que se exportan con el modelo en `referencias.joblib`.

**Cómo sé que las calcula igual:**

- **Son las mismas funciones.** Separé `pipeline_proyecto.py` en `calcular_features` (features, sirve para entrenar y para predecir) y `agregar_features` (agrega la etiqueta, solo para entrenar), y el servicio importa la primera. Comprobé que la reorganización no cambió ni un valor: la huella de las tablas de entrenamiento y prueba es idéntica antes y después.
- **`rezagos_y_medias` reproduce la OBT de Spark** en las 422.912 filas, con diferencia 0 en los seis rezagos y medias.
- **Lo comparé de punta a punta:** armé desde la OBT la petición de 1000 cantón-días del periodo de prueba, como la mandaría el ECU 911. Las 18 features del servicio son idénticas a las del entrenamiento en los 1000 casos, la probabilidad también (diferencia 0) y ninguna alerta cambia.
- **Una prueba lo vigila en cada push:** `test_features_del_servicio_calculadas_a_mano` comprueba en GitHub Actions valores calculados a mano (`lag_4d` = 24, `nivel_vs_umbral_t3` = 1.35, `media_prev_7d` = 24, el feriado en *t+3*).

**Pega una petición a tu servicio corriendo en el contenedor, y su respuesta:**

Contenedor construido con `docker build -f servicio/Dockerfile -t servicio-ecu911 .` desde `psets/proyecto/` y levantado con `docker run -p 8000:8000 servicio-ecu911`. Quito al cierre del lunes 29 de diciembre de 2025:

```
curl -X POST localhost:8000/predecir -H "Content-Type: application/json" -d '{"cod_canton": "1701", "fecha": "2025-12-29", "emergencias": [1824, 1730, 2006, 2365, 2626, 2686, 2309, 1670, 1681, 1626, 1872, 1979, 2414, 2350, 1694, 1782, 2003, 1957, 2336, 2725, 2519, 1855, 1910, 1916, 1809, 1810, 2069, 2143, 1723], "n_seguridad_ciudadana": 1206, "n_gestion_sanitaria": 187, "n_transito_movilidad": 155, "feriados": ["2026-01-01", "2026-01-02"]}'
```

```
{"cod_canton":"1701","fecha_objetivo":"2026-01-01","probabilidad_alta_demanda":0.8337,"alerta":true,"run_id":"a7c9689b915a4eb7ba39e5ba381ef6cb"}
```

El servicio anticipa alta demanda para el 1 de enero (83%, por encima del umbral de 0.66). Fue un acierto: ese día Quito tuvo 2806 emergencias, por encima de su umbral P90 de los jueves (2196.4). Con solo 28 días de historia, el mismo pedido recibe un 422 (`List should have at least 29 items`).

## Antes de la próxima sesión

**Lectura:** ["What Is Model Governance?"](https://www.ibm.com/think/topics/model-governance), IBM.

Tu servicio carga `modelo.joblib`, el archivo que exportaste hoy. Si la semana que viene reentrenas y vuelves a exportar, el archivo se reemplaza. Si mañana un usuario reclama por una predicción de hoy, ¿cómo sabrías qué modelo la produjo? ¿Y cómo volverías al modelo anterior si el nuevo resulta peor?

Cada respuesta del servicio trae el `run_id` del modelo que la produjo, y `/salud` también lo dice. Si guardo cada petición con su respuesta (un registro de predicciones, que todavía no tengo), ante un reclamo busco esa predicción y su `run_id` me lleva a la corrida en MLflow, con sus parámetros, sus métricas, la huella de los datos y el modelo guardado. Para volver al anterior, el modelo viejo no se pierde: sigue en MLflow. Muevo la etiqueta `candidato` = `final` a la corrida anterior, vuelvo a correr `python -m servicio.exportar_modelo` y reconstruyo la imagen. Para que la vuelta sea inmediata, conviene etiquetar cada imagen con su `run_id` (`servicio-ecu911:a7c9689b`) y guardar la anterior: volver es levantar la imagen vieja, sin reconstruir nada. El punto débil es que `modelo.joblib` se reemplaza al exportar, así que el archivo local no sirve como historial: el historial está en MLflow.
