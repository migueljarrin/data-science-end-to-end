# Semana 13, Sesión 1: Despliegue en producción: versionado y registro de modelos

> Objetivo de la sesión: versionar y registrar el modelo desplegado de tu proyecto, explicando qué problema resuelve un registro de modelos frente a sobrescribir el mismo archivo cada vez que se reentrena.

**Lectura previa de esta sesión:** ["What Is Model Governance?"](https://www.ibm.com/think/topics/model-governance), IBM.

**Referencia de esta sesión:** *Designing Machine Learning Systems*, Cap. 10: Infrastructure and Tooling for MLOps.

## Requisitos antes de esta sesión

Nada nuevo que instalar. El registro de modelos es parte del mismo servidor de MLflow que usas desde la Semana 11: se levanta solo al iniciar el Codespace, en el puerto 5050 (si no responde, `bash .devcontainer/mlflow-server.sh`). Los scripts lo encuentran por la variable `MLFLOW_TRACKING_URI`. Los laboratorios de hoy son scripts.

## Antes de empezar

A partir de la lectura previa:

**Según el artículo, ¿qué es la gobernanza de modelos, y qué componentes la forman?**

_(tu respuesta)_

**El artículo pide un inventario central de modelos. ¿Qué datos tendría que tener ese inventario sobre cada modelo, y para qué los necesita alguien que no lo entrenó?**

_(tu respuesta)_

## Pregunta de apertura

La sesión pasada, tu servicio cargaba `modelo.joblib`. Si la semana que viene reentrenas y vuelves a exportar, el archivo se reemplaza. Si mañana un usuario reclama por una predicción de hoy, ¿cómo sabrías qué modelo la produjo? ¿Y cómo volverías al modelo anterior si el nuevo resulta peor?

Con un solo archivo que se reemplaza, no lo sabría: el modelo de hoy desaparece en cuanto exporto el de la semana que viene. Hacen falta dos cosas. Primero, que cada predicción diga qué versión del modelo la calculó (la sesión pasada mi servicio ya respondía el `run_id`), y guardar las predicciones con esa versión. Segundo, que los modelos anteriores no se borren: con un registro de modelos, cada reentrenamiento crea una versión nueva y numerada, y un alias (`produccion`) marca cuál se sirve. Volver al anterior es mover el alias a la versión vieja y volver a desplegar, sin reentrenar nada.

## Ejercicio 1: la tarifa, con registro

Carpeta: [`starter/ejercicio1/`](./starter/ejercicio1/). Es el servicio de la tarifa de la sesión pasada, ahora con el modelo en el registro de MLflow en vez de un archivo. [`registrar_modelo.py`](./starter/ejercicio1/registrar_modelo.py) entrena la red neuronal con el número de neuronas que le pases y la registra como una versión nueva del modelo `tarifa-taxis`. [`promover.py`](./starter/ejercicio1/promover.py) pone el alias `produccion` en la versión que le pases. [`versiones.py`](./starter/ejercicio1/versiones.py) lista las versiones con su error y sus alias (no lo modifiques). [`servicio.py`](./starter/ejercicio1/servicio.py) carga la versión que tiene el alias `produccion`. Los 4 `TODO`: registrar, promover, cargar desde el registro y responder qué versión calculó cada tarifa.

Desde la carpeta del ejercicio, corre todo una vez antes de tocar nada:

```
python registrar_modelo.py 64
python versiones.py
python promover.py 1
pytest -v
```

**Respuesta 1 (antes de los TODO):** `registrar_modelo.py` dice `Version None`, `versiones.py` no imprime nada y `promover.py` termina con un error. ¿Qué dice el error, y qué te dice sobre lo que hay en el registro?

`mlflow.exceptions.RestException: INVALID_PARAMETER_VALUE: Registered model alias produccion not found.` El registro está vacío: `registrar_modelo.py` sí guardó una corrida (con su MAE de 1.1695), pero sin el `TODO 1` no guardó el modelo ni lo registró, por eso dijo `Version None`. `versiones.py` no imprime nada porque `tarifa-taxis` no tiene ninguna versión, y `promover.py` falla porque, sin el `TODO 2`, no pone el alias, y después lo busca en un modelo que no tiene ninguno.

**Respuesta 2 (TODO 1):** registra dos versiones, una con 64 neuronas y otra con 8. Antes de correr `versiones.py`, ¿cuántas versiones esperas ver, y qué pasó con la primera cuando registraste la segunda?

Dos, y la primera no cambia: registrar la segunda no la reemplaza ni la borra, solo agrega la versión 2 al lado. Así salió: la versión 1 es la red de 64 neuronas (MAE 1.1695) y la versión 2 la de 8 (MAE 1.1877), las dos sin alias hasta que corrí `promover.py`. Es justo lo contrario de sobrescribir `modelo.joblib`.

**Respuesta 3 (TODO 2 y 3):** pon `produccion` en la versión 2 y levanta el servicio (`uvicorn servicio:app --port 8000`). ¿Qué versión dice `/salud`? Ahora mueve el alias a la versión 1 sin reiniciar uvicorn: ¿qué versión responde el servicio? ¿Y después de reiniciarlo?

Con `produccion` en la versión 2, `/salud` dice `"version_modelo": "2"`. Al mover el alias a la versión 1 sin reiniciar uvicorn, el servicio sigue respondiendo con la versión 2 (`/salud` sigue diciendo `"2"`, y la tarifa no cambia): el servicio busca el alias y carga el modelo una sola vez, al arrancar, y después usa el que tiene en memoria. Después de reiniciarlo, responde con la versión 1. Mover el alias no cambia nada hasta que el servicio vuelve a arrancar: por eso conviene que cada respuesta diga qué versión la calculó.

**Respuesta 4 (TODO 4):** las pruebas usan un modelo de prueba y una versión inventada, `"7"`, sin servidor de MLflow. ¿Qué prueba falla antes del `TODO 4`, y qué comprueba que el `/salud` no comprobaba?

Falla `test_cada_prediccion_dice_que_version_la_calculo`: la respuesta era `{"tarifa_estimada": 20.0}` y la prueba esperaba también `"version_modelo": "7"`. `/salud` dice qué versión tiene el servicio ahora; la prueba comprueba que cada tarifa lleva la versión que la calculó. No es lo mismo: si la tarifa se guarda o se reclama días después, el servicio puede estar sirviendo otra versión, como se vio al mover el alias. La respuesta tiene que traer su propia versión.

**Lo que respondió el servicio:**

- **Versión 2** (8 neuronas): `{"tarifa_estimada": 69.98, "version_modelo": "2"}`.
- **Versión 1** (64 neuronas), después de mover el alias y reiniciar: `{"tarifa_estimada": 70.07, "version_modelo": "1"}`.
- Entre una y otra, con el alias ya en la versión 1 pero sin reiniciar, el servicio siguió respondiendo 69.98 con `"version_modelo": "2"`.

Las 2 pruebas pasan (`2 passed`).

## Durante el ConcepTest

**Tu voto, antes de discutir en pareja** (A, B, C o D):

_(tu voto)_

**Tu razonamiento:**

_(tu respuesta)_

**Después de discutir en pareja, ¿cambiaste de voto? ¿Por qué?**

_(tu respuesta)_

## Ejercicio 2: el ciclo de vida del modelo de fraude

Solo o en pareja. Carpeta: [`starter/ejercicio2/`](./starter/ejercicio2/). El equipo de fraude entrena modelos candidatos cada tanto, y quiere una regla: una versión llega a `produccion` solo si detecta más fraudes (mayor recall al umbral de 0.10) que la que está ahí. [`ciclo_fraude.py`](./starter/ejercicio2/ciclo_fraude.py) entrena tres candidatos, registra cada uno y decide si lo promueve. Los pasos 1 a 3 tienen `TODO`: registrar una versión con sus métricas, leer la métrica de una versión y averiguar qué versión está en producción. Los pasos 4 (decidir y mover el alias) y 5 (etiquetar la versión con el resultado) solo tienen un comentario. Resuelve y corre `python comprobar.py` hasta que los cinco pasos digan `OK`; después, `python ciclo_fraude.py`.

**Respuesta 1:** ¿qué versión quedó en producción, y por qué no la última que se registró?

La versión 2, el gradient boosting (recall 0.661, precisión 0.429). La última que se registró fue la 3, la regresión logística muy regularizada, pero su recall es de 0.102: detecta el 10% de los fraudes, contra el 66% de la versión 2. La regla no promueve la versión más nueva, sino la que detecta más fraudes que la que está en producción. La versión 1 (logística, recall 0.644) llegó primero porque no había ninguna, y la 2 la reemplazó porque su recall era mayor. Los cinco pasos de `comprobar.py` dicen `OK`.

**Respuesta 2:** la regresión logística muy regularizada tiene la mayor precisión de las tres. ¿Por qué la regla la rechazó? ¿Qué tendría que cambiar en la regla si la empresa decide que las falsas alarmas cuestan más que los fraudes no detectados?

Porque la regla solo mira el recall. Su precisión es la más alta (0.667: dos de cada tres alertas son fraudes de verdad), pero alerta tan poco que deja pasar el 90% de los fraudes, y su recall de 0.102 es mucho menor que el 0.661 de producción. Si las falsas alarmas costaran más, la regla tendría que comparar algo que las pese: por ejemplo, el costo total al umbral (fraudes no detectados por su costo más falsas alarmas por el suyo, como en la Semana 11), o maximizar la precisión exigiendo un recall mínimo. Con una regla así, una versión con más precisión podría ganar aunque detecte menos.

**Respuesta 3:** abre el modelo `fraude-pagos` en la interfaz de MLflow (puerto 5050, pestaña **Models**). Si dentro de un mes alguien pregunta por qué la versión 3 nunca llegó a producción, ¿dónde está la respuesta?

En la propia versión 3: sus etiquetas dicen `validacion` = `rechazada` y `comparada_con` = `2`, y su corrida guarda las métricas con las que se comparó (recall 0.102 y precisión 0.667, frente al recall de 0.661 de la versión 2). En la pestaña **Models**, entrando a `fraude-pagos` y a la versión 3, se ven las etiquetas, y el enlace a su corrida lleva a las métricas. La decisión queda escrita en el registro, no en la memoria de quien corrió el script.

**Si terminas antes:** vuelve a correr `python ciclo_fraude.py`. ¿Cuántas versiones hay ahora, y cuál está en producción? ¿Es lo que esperabas?

Seis: la segunda corrida registró las versiones 4, 5 y 6 (los mismos tres candidatos otra vez), y en producción sigue la versión 2. Las tres nuevas quedaron rechazadas y comparadas con la 2. Es lo esperable con esta regla: la versión 5 es el mismo gradient boosting, con el mismo recall (0.661), y la regla exige uno estrictamente mayor, así que un modelo idéntico no reemplaza al que ya está. Lo que no esperaba es que el registro se llene de versiones repetidas: cada vez que se corre el ciclo, se registran los candidatos aunque no cambie nada.

## Ejercicio 3: el registro de tu proyecto

Usa tu proyecto en [`psets/proyecto/`](../../psets/README.md) y el servicio que construiste la sesión pasada. Esta vez no hay plantilla.

### Entregable 1: el modelo, en el registro

- `servicio/registrar_modelo.py`: entrena tu modelo final, guarda su métrica principal en la corrida y lo registra como una versión nueva de un modelo con el nombre de tu proyecto. Cada vez que lo corres crea una versión; ninguna reemplaza a otra.
- `servicio/promover.py`: pone el alias `produccion` en la versión que le pases.
- Al menos dos versiones registradas (por ejemplo, con dos valores de un hiperparámetro), y una de ellas con el alias `produccion`.

Corre los scripts desde `psets/proyecto/` como módulos (`python -m servicio.registrar_modelo`), para que encuentren `modelado/`.

### Entregable 2: el servicio sabe qué versión sirve

- El script que exportaba el modelo (Semana 12) ahora exporta la versión con el alias `produccion`, y guarda su número junto al modelo (por ejemplo, en `servicio/modelo_version.txt`). La imagen lleva los dos archivos adentro: el contenedor no necesita llegar al servidor de MLflow.
- `/salud` y cada predicción responden `version_modelo`.
- Una prueba en `servicio/test_api.py` que compruebe que la predicción incluye la versión, con un modelo de prueba y una versión inventada.

### Entregable 3: `docs/despliegue.md`

Agrega la sección **Versionado y registro**: cómo se llama tu modelo en el registro, qué versión está en producción y con qué métrica, con qué criterio se mueve el alias, y los pasos para volver a la versión anterior.

**¿Con qué criterio decides que una versión nueva de tu modelo pasa a producción? ¿Quién lo decide en tu proyecto, y dónde queda registrada la decisión?**

Registro: el modelo `ecu911-alta-demanda` en MLflow, con dos versiones del bosque. La versión 1 (`min_samples_leaf=100`) tiene una AP en prueba de 0.2327, y la versión 2 (`min_samples_leaf=300`), 0.2265. La versión 1 tiene el alias `produccion`. Scripts: [`registrar_modelo.py`](../../psets/proyecto/servicio/registrar_modelo.py), [`promover.py`](../../psets/proyecto/servicio/promover.py) y [`exportar_modelo.py`](../../psets/proyecto/servicio/exportar_modelo.py); el criterio y los pasos para volver atrás están en la sección "Versionado y registro" de [`docs/despliegue.md`](../../psets/proyecto/docs/despliegue.md).

**Criterio:** una versión nueva pasa a producción si tiene más AP en el periodo de prueba que la versión actual y no se sobreajusta (brecha entre entrenamiento y prueba menor que 0.05). La versión 2 no pasó: detecta peor (0.2265 frente a 0.2327). Si una versión ganara por muy poco (menos que la variación entre pliegues de la Semana 11, 0.028), repetiría la validación temporal antes de promoverla.

**Quién:** quien mantiene el modelo, a mano, con `python -m servicio.promover <versión> "<motivo>"`. No lo automaticé como en el Ejercicio 2, porque el modelo se reentrena pocas veces y una diferencia chica de AP necesita mirarse antes de decidir.

**Dónde queda registrada:** en la versión promovida. MLflow no guarda la historia de los alias, así que `promover.py` le pone tres etiquetas: `promovida_el` (fecha y hora), `motivo` y `reemplaza_a` (la versión que estaba antes). La versión 1 dice: `motivo` = "mayor AP en prueba (0.2327 frente a 0.2265 de la version 2) con brecha menor a 0.05" y `reemplaza_a` = `ninguna`. Las métricas que sostienen la decisión están en la corrida de cada versión.

**Si tu servicio corre en un contenedor sin acceso al servidor de MLflow, ¿cómo sabe qué versión está sirviendo?**

Porque la versión viaja con el modelo. `exportar_modelo.py` exporta la versión con el alias `produccion` y escribe su número en `servicio/modelo_version.txt`, al lado de `modelo.joblib`, y el `Dockerfile` copia los dos archivos a la imagen. Al arrancar, el servicio lee el número de ese archivo, sin consultar a MLflow, y lo responde en `/salud` y en cada predicción. Lo comprobé levantando el contenedor sin ninguna red (`docker run --network none`): arrancó igual. Con red, `/salud` dice `{"estado":"ok","modelo_cargado":true,"version_modelo":"1"}`, y la predicción de Quito del 29 de diciembre responde `"version_modelo":"1"`. Una prueba, `test_cada_prediccion_dice_que_version_la_calculo`, lo comprueba en GitHub Actions con una versión inventada. El costo: si se mueve el alias, la imagen sigue sirviendo la versión vieja hasta volver a exportar y reconstruir.

## Antes de la próxima sesión

**Lectura:** ["Machine learning model monitoring: Best practices"](https://www.datadoghq.com/blog/ml-model-monitoring-in-production-best-practices/), Datadog.

Tu servicio responde en unos milisegundos, `/salud` dice que todo está bien, y cada tarifa dice qué versión la calculó. ¿Qué le pasa a un modelo que responde rápido pero cada vez peor? ¿Cómo te enterarías?

Se degrada sin dar ningún error: sigue respondiendo rápido, con código 200 y la versión correcta, pero sus predicciones son cada vez peores, porque el mundo cambió y el modelo no. En mi proyecto, por ejemplo, el volumen de emergencias baja con los años (−14% de 2021 a 2025), y el umbral P90 de cada cantón está fijo desde el entrenamiento: con el tiempo, la tasa de alta demanda y el sentido de `nivel_vs_umbral_t3` se desplazan. Ni la latencia ni `/salud` lo muestran. Me enteraría guardando cada predicción con su versión y comparándola, tres días después, con lo que de verdad pasó (el conteo real de *t+3*), para calcular la AP y el costo semana a semana. Mientras esa respuesta llega, también vigilaría las entradas: si la distribución de las features o la proporción de alertas se aleja de la del entrenamiento, es una señal temprana.
