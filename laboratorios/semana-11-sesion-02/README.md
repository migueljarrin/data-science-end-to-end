# Semana 11, Sesión 2: Esquemas de validación y evaluación de modelos

> Objetivo de la sesión: seleccionar un esquema de validación adecuado al contexto de los datos de tu proyecto (aleatorio, temporal, por grupo) y elegir la métrica de evaluación correcta según el costo relativo de cada tipo de error.

**Lectura previa de esta sesión:** ["How Metrics (and LLMs) Can Trick You: A Field Guide to Paradoxes"](https://towardsdatascience.com/how-metrics-and-llms-can-trick-you-a-field-guide-to-paradoxes/), Towards Data Science.

**Referencia de esta sesión:** *Designing Machine Learning Systems*, Chip Huyen, capítulo 6 (desarrollo y evaluación de modelos offline).

## Requisitos antes de esta sesión

Nada nuevo que instalar: todo lo de hoy está en scikit-learn. Ten a mano tu `pipeline_proyecto.py` y el modelo final que elegiste la sesión pasada. Los laboratorios de hoy son notebooks, como los de la Semana 10 y la sesión pasada.

## Antes de empezar

A partir de la lectura previa:

**Según el artículo, ¿qué es la paradoja de la exactitud (accuracy paradox)? ¿Qué métricas recomienda en su lugar?**

_(tu respuesta)_

**El artículo cita la ley de Goodhart: "cuando una medida se convierte en objetivo, deja de ser una buena medida". ¿Qué ejemplo da, y qué tiene que ver con elegir un modelo por una sola métrica?**

_(tu respuesta)_

## Pregunta de apertura

La sesión pasada elegiste el modelo con menor error sobre los 595 viajes de prueba. ¿Cuánto cambiaría ese error si la división hubiera sido otra? ¿Lo viste en algún lado del registro?

Bastante, comparado con las diferencias entre modelos. El registro de la sesión pasada lo mostró en los dos gradient boosting del Ejercicio 1: el mismo modelo, sobre el mismo CSV (misma huella), dio 1.2754 con la división de semilla 42 y 1.1867 con la de semilla 7. Lo único distinto en el registro era `semilla_division`, y la diferencia (0.089 USD) es casi la que separaba al primer modelo del segundo en el Ejercicio 2 (0.106). Hoy la validación cruzada al azar lo confirma: los 5 pliegues del gradient boosting van de 1.16 a 1.28, con una desviación de 0.036. Un registro con una sola corrida por modelo no muestra esa variación: hay que repetir la evaluación con otras divisiones.

## Ejercicio 1: tres formas de validar el mismo modelo

Notebook: [`starter/ejercicio1_validacion.ipynb`](./starter/ejercicio1_validacion.ipynb), sobre [`starter/viajes_features.csv`](./starter/viajes_features.csv), con la preparación de [`starter/preparacion_taxis.py`](./starter/preparacion_taxis.py). Ya trae una función `evaluar` que corre una validación cruzada con el esquema que le pases y guarda el error de cada pliegue. Los 4 `TODO` son tres esquemas de validación y dos métricas. Córrelo completo una vez antes de tocar nada (**Run All**).

**Respuesta 1 (TODO 1):** con una sola división, el gradient boosting dio 1.2754 y el bosque 1.3016. Con 5 pliegues al azar, ¿esperas que los cinco errores del gradient boosting sean parecidos entre sí? ¿Cuánto esperas que varíen?

Parecidos, pero no iguales: espero que se muevan unos pocos centavos alrededor de 1.27, como lo que vimos al cambiar la semilla (0.089 USD). Salió así: 1.28, 1.24, 1.16, 1.24 y 1.23, con un promedio de 1.2288 y una desviación de 0.0361. El 1.2754 de la Semana 10 cae dentro de ese rango: era una de muchas divisiones posibles, no el error del modelo. Aun así, el gradient boosting le gana al bosque (1.30, 1.27, 1.25, 1.34 y 1.28) en los 5 pliegues.

**Respuesta 2 (TODO 2):** en la validación temporal, cada pliegue entrena con los viajes anteriores y valida con los siguientes. ¿Esperas un error mayor o menor que con pliegues al azar? ¿Por qué?

Mayor. Con pliegues al azar, el modelo entrena con viajes de todo el periodo, incluidos días vecinos a los que valida; en la validación temporal solo ve el pasado, y además los primeros pliegues entrenan con muy pocos viajes (el primero, con una sexta parte). Salió 1.3099 de promedio frente a 1.2288, con el doble de desviación (0.0693 frente a 0.0361), y el peor pliegue es el primero (1.40), el que entrena con menos datos. Como los viajes son solo de septiembre y octubre de 2026, el efecto del tiempo es chico; en datos de varios años sería mayor.

**Respuesta 3 (TODO 3):** en la validación por zona, ninguna zona de origen aparece a la vez en entrenamiento y en validación. ¿Qué pliegue crees que va a tener el peor error?

El que deje fuera a JFK Airport: sus viajes tienen la tarifa fija de 70 USD y son los más largos, y si el modelo nunca vio viajes que salen del aeropuerto, no puede aprender su patrón. Así fue: el pliegue 5 (Brooklyn y JFK Airport) dio 6.43 de error, cuando los otros cuatro quedaron entre 1.19 y 1.31. De los 210 viajes que salen de JFK, 165 tienen tarifa fija. Ese solo pliegue sube el promedio a 2.2996 y la desviación a 2.0648: el promedio esconde que el modelo funciona bien en todas las zonas menos en una.

**Respuesta 4 (TODO 4):** la app muestra una tarifa estimada antes del viaje, y el pasajero reclama si la real sale más de 20% por encima. ¿Qué métrica dice mejor cuántos reclamos va a haber: el MAE, el RMSE, o el porcentaje de viajes subestimados en más de 20%?

El porcentaje de viajes subestimados en más de 20%, porque cuenta exactamente los casos que generan un reclamo. El MAE (1.2754) y el RMSE (1.9213) son simétricos: castigan igual cobrar de más que de menos, y no dicen cuántos viajes cruzan el límite del 20%. Un error de 3 USD en un viaje de 70 no genera reclamo; el mismo error en uno de 10 sí. Con el gradient boosting, el 4.4% de los viajes de prueba sale subestimado en más de 20%: unos 44 reclamos por cada 1000 viajes.

**Lo que confirmó la tabla, esquema por esquema:**

| esquema y modelo | MAE promedio | desviación | peor pliegue | pliegues |
|---|---|---|---|---|
| una división (Semana 10), gradient boosting | 1.2754 | — | — | — |
| aleatorio, gradient boosting | 1.2288 | 0.0361 | 1.28 | 1.28, 1.24, 1.16, 1.24, 1.23 |
| aleatorio, bosque | 1.2880 | 0.0291 | 1.34 | 1.30, 1.27, 1.25, 1.34, 1.28 |
| temporal, gradient boosting | 1.3099 | 0.0693 | 1.40 | 1.40, 1.21, 1.38, 1.27, 1.29 |
| por zona, gradient boosting | 2.2996 | 2.0648 | 6.43 (Brooklyn y JFK) | 1.27, 1.31, 1.29, 1.19, 6.43 |

Paso 4, sobre los 595 viajes de prueba: MAE 1.2754, RMSE 1.9213 y 4.4% de viajes subestimados en más de 20%.

## Durante los ConcepTests

**ConcepTest 1. Tu voto, antes de discutir en pareja** (A, B, C o D):

_(tu voto)_

**Tu razonamiento:**

_(tu respuesta)_

**Después de discutir en pareja, ¿cambiaste de voto? ¿Por qué?**

_(tu respuesta)_

**ConcepTest 2. Tu voto, antes de discutir en pareja** (A, B, C o D):

_(tu voto)_

**Tu razonamiento:**

_(tu respuesta)_

## Ejercicio 2: el 95% que no detecta nada

Solo o en pareja. Notebook: [`starter/ejercicio2_fraude_y_umbral.ipynb`](./starter/ejercicio2_fraude_y_umbral.ipynb), sobre [`starter/pagos_taxi.csv`](./starter/pagos_taxi.csv): 6000 pagos de la app de taxis, de los que unos 300 resultaron fraudulentos. Mismo esqueleto del Ejercicio 1, con un problema de clasificación. Los pasos 1 a 3 tienen `TODO`; los pasos 4 y 5 solo tienen la comprobación. Complétalos hasta que todas digan `OK`.

**Respuesta 1:** ¿qué accuracy tiene la línea base que nunca predice fraude? ¿Y qué recall?

Accuracy de 0.9508 y recall de 0. Acierta el 95% porque el 95% de los pagos son legítimos (295 fraudes de 6000), pero no detecta ni un solo fraude.

**Respuesta 2:** ¿cuánto mejora la accuracy del gradient boosting sobre la línea base, y cuánto mejora el recall? ¿Cuál de los dos números describe mejor lo que gana la empresa?

La accuracy sube de 0.9508 a 0.9712: apenas 2 puntos. El recall sube de 0 a 0.4610: el modelo pasa de no detectar ningún fraude a detectar el 46%. El recall describe mejor lo que gana la empresa, porque cada fraude detectado es un contracargo que no paga. La accuracy casi no se mueve porque está dominada por los 5705 pagos legítimos, que la línea base ya acertaba.

**Respuesta 3:** con el umbral 0.5, ¿cuántos fraudes deja pasar el gradient boosting? ¿Qué umbral eligió el paso 5, y cuántos fraudes y falsas alarmas tiene con ese umbral?

Con el umbral 0.5 deja pasar 159 de los 295 fraudes (detecta 136) y solo da 14 falsas alarmas: un costo de 6402 USD. El paso 5 eligió el umbral 0.1: deja pasar 122 fraudes y da 222 falsas alarmas, con un costo de 5546 USD, 856 menos. Como un fraude sin detectar cuesta 40 y una falsa alarma 3, conviene aceptar 208 falsas alarmas más (624 USD) a cambio de detectar 37 fraudes más (1480 USD).

**Si terminas antes:** si la revisión manual de una falsa alarma costara 20 dólares en vez de 3, ¿el umbral elegido sube o baja? Cambia la constante y comprueba.

Sube, de 0.1 a 0.5. Con la falsa alarma a 20 USD, cada pago legítimo marcado cuesta la mitad de un fraude no detectado, así que conviene alertar mucho menos: el costo baja a medida que sube el umbral (9320 USD con 0.1, 7300 con 0.2, 6640 con 0.5). Lo comprobé aparte, sin cambiar la constante del notebook, para que su comprobación siga diciendo `OK`.

## Ejercicio 3: la validación y la métrica de tu proyecto

Usa tu `pipeline_proyecto.py` y el modelo final de la sesión pasada. Esta vez no hay plantilla.

### Entregable 1: `validacion_proyecto.ipynb`

Un notebook, al lado de tu `pipeline_proyecto.py`, que evalúe tu modelo final (y el segundo mejor) con validación cruzada, con dos esquemas: el que corresponde a tus datos (temporal si predices el futuro, por grupo si la misma entidad aparece muchas veces, estratificado si clasificas una clase poco frecuente) y uno al azar, para comparar. El notebook guarda una tabla con el promedio, la desviación y cada pliegue.

### Entregable 2: la métrica del negocio

Escribe qué error es más caro en tu proyecto (sobreestimar o subestimar, un falso positivo o un falso negativo) y cuánto, aunque sea aproximado. Calcula en el mismo notebook una métrica que refleje ese costo, además de la métrica que venías usando.

### Entregable 3: respuestas

**¿Qué esquema de validación corresponde a tu proyecto, y por qué?**

Notebook: [`semana-09-sesion-02/plantilla-pipeline/validacion_proyecto.ipynb`](../semana-09-sesion-02/plantilla-pipeline/validacion_proyecto.ipynb), al lado de mi `pipeline_proyecto.py`. Tabla: [`validacion_proyecto.csv`](../semana-09-sesion-02/plantilla-pipeline/validacion_proyecto.csv). La validación cruzada usa solo el periodo de entrenamiento (julio de 2021 a junio de 2025); el periodo de prueba se mide una sola vez al final.

El temporal, porque el modelo predice el futuro: al cierre de un día decide si un cantón tendrá alta demanda tres días después. Cada pliegue entrena con los días anteriores y valida con los siguientes, cortado por fecha para que un mismo día no quede repartido entre entrenamiento y validación. Un esquema al azar haría trampa de dos formas: entrenaría con días de 2024 para validar días de 2022, y, como cada fila tiene los rezagos de los días anteriores del mismo cantón, el modelo vería en entrenamiento los días vecinos de los que valida. Además, el volumen baja con los años (hallazgo 3 de la Semana 8), y solo un esquema temporal mide si el modelo aguanta ese cambio.

**¿Cambió la conclusión entre el esquema al azar y el tuyo? Muestra los números.**

| esquema | modelo | AP promedio | desviación | peor pliegue |
|---|---|---|---|---|
| temporal | bosque `min_samples_leaf=100` | 0.1339 | 0.0282 | 0.0890 |
| temporal | red neuronal (32,) | 0.1243 | 0.0261 | 0.0805 |
| al azar | bosque `min_samples_leaf=100` | 0.1945 | 0.0052 | 0.1870 |
| al azar | red neuronal (32,) | 0.1894 | 0.0029 | 0.1846 |

Cambió la conclusión sobre qué tan bueno y qué tan estable es el modelo, no sobre cuál elegir. Al azar, el bosque parece tener una AP de 0.19; con el esquema temporal es 0.13: el esquema al azar sobreestima el rendimiento en un 45%. También esconde la variación: su desviación es 5 veces menor (0.0052 frente a 0.0282), porque cada pliegue mezcla todos los años; en el temporal, el peor pliegue (el que valida de marzo a octubre de 2024) baja a 0.089. En los dos esquemas el bosque queda primero.

**¿La diferencia entre tu modelo final y el segundo es mayor que la variación entre pliegues? ¿Sigues eligiendo el mismo?**

No: en el esquema temporal, el bosque le gana a la red por 0.0096 de AP en promedio, y la desviación entre pliegues es de 0.0282, casi tres veces más. Pero como los dos modelos se validaron en los mismos pliegues, se pueden comparar pliegue por pliegue: el bosque gana en los 5 (por entre 0.0004 y 0.0163), y en 4 de 5 en el esquema al azar. La variación entre pliegues es grande porque algunos periodos son más difíciles que otros para los dos modelos, no porque cambie cuál es mejor.

Sigo eligiendo el bosque. En el periodo de prueba la red saca más AP (0.2425 frente a 0.2327), pero la validación temporal muestra que esa ventaja no se repite en ningún pliegue, y con la métrica del negocio el bosque cuesta menos también en prueba (348.9 frente a 361.5 por cada 1000 cantón-días).

**¿Qué métrica del negocio elegiste, y qué dice que no decía la anterior?**

El costo de los errores por cada 1000 cantón-días: un día de alta demanda sin detectar cuesta 5 (no se refuerza el turno y las emergencias de ese día esperan más) y una falsa alarma cuesta 1 (horas extra por un refuerzo que no hacía falta). La proporción 5 a 1 es una estimación mía, no un dato del ECU 911. El umbral de cada modelo se elige con la validación temporal: 0.66 para el bosque y 0.26 para la red (sus probabilidades no están en la misma escala).

La AP no dice tres cosas que dice el costo:

- **Cuánto gana el ECU 911 frente a no hacer nada.** En prueba, el bosque cuesta 348.9, frente a 393.4 de nunca alertar y 921.3 de alertar siempre: ahorra un 11%. Es una mejora real, pero modesta.
- **Qué hace el modelo en la práctica.** Con ese umbral, el bosque anticipa 1260 de los 7472 días de alta demanda del periodo de prueba (17%) y da 2076 falsas alarmas. Con una AP de 0.23 no se ve que el modelo deja pasar la mayoría de los días de alta demanda.
- **Cuál conviene.** Por AP en prueba, la red parecía mejor; por costo, el bosque es mejor (348.9 frente a 361.5), porque con su umbral detecta 1260 días frente a 805 de la red.

Si el ECU 911 estimara que un día sin detectar cuesta más que 5 falsas alarmas, el umbral bajaría y el modelo alertaría más.

## Antes de la próxima sesión

**Lectura:** ["MLOps: Batch vs Online ML Systems"](https://medium.com/mlops-republic/mlops-batch-vs-online-ml-system-cbacee834837), MLOps Republic.

La app de taxis usa dos modelos: uno estima la tarifa antes de pedir el viaje, otro decide si un pago es fraude. ¿Alguno de los dos se podría calcular una vez por noche para todos los casos posibles? ¿Cuál tiene que responder en el momento, y en cuánto tiempo?

La tarifa se podría calcular de noche como aproximación: con 8 zonas de origen, 8 de destino, 24 horas y fin de semana o no, son 3072 combinaciones, y una tabla precalculada respondería al instante. Pero la distancia exacta y los pasajeros cambian en cada pedido, así que una tabla nocturna perdería precisión; si se calcula en el momento, debe responder en menos de un segundo, mientras el pasajero mira la app. El de fraude tiene que responder en el momento sí o sí: depende del pago concreto (tarjeta nueva, intentos fallidos, monto), que no existe hasta que el pasajero paga, y tiene que decidir antes de aprobar el cobro, en uno o dos segundos como mucho.
