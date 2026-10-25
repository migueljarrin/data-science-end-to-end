# Semana 9, Sesión 1: Ingeniería de características: principios aplicados

> Objetivo de la sesión: explicar por qué una misma variable cruda puede necesitar codificaciones distintas según el modelo que la consuma, y diseñar al menos dos features derivadas para el dataset de tu proyecto.

**Lectura previa de esta sesión:** ["Feature Engineering that Makes Business Sense"](https://towardsdatascience.com/feature-engineering-that-makes-business-sense-419b9403236e/), Towards Data Science.

**Referencia de esta sesión:** *Designing Machine Learning Systems*, Chip Huyen (O'Reilly, 2022), Capítulo 5: Feature Engineering.

## Requisitos antes de esta sesión

pandas y matplotlib, de la sesión pasada. numpy se instala junto con pandas; verifica con:

```
python3 -c "import numpy; print(numpy.__version__)"
```

Ten a mano tus 3 hallazgos de la exploración de la Semana 8, Sesión 2: las features de hoy salen de ahí.

## Antes de empezar

A partir de la lectura previa:

**Según el artículo, ¿qué diferencia a una feature que tiene sentido de negocio de una que solo mejora una métrica?**

_(tu respuesta)_

**Elige uno de los ejemplos del artículo: ¿qué conocimiento del negocio traduce a una columna, y cómo?**

_(tu respuesta)_

## Pregunta de apertura

La exploración encontró dos patrones que no existen como columnas: la tarifa fija entre JFK y Manhattan, y viajes que cuestan más por kilómetro a ciertas horas. El modelo solo ve columnas. ¿Cómo le das esa información?

Convirtiendo cada patrón en una columna nueva a partir de las que ya existen. Para la tarifa fija, una columna binaria `es_tarifa_fija` que vale 1 cuando el viaje va entre JFK y una zona de Manhattan, sacada de `zona_origen` y `zona_destino`. Para el costo por kilómetro según la hora, columnas derivadas de `fecha_hora_inicio`: la hora, el día de la semana y una bandera `es_hora_pico`. Así el modelo puede aprender que esos viajes se comportan distinto sin tener que adivinarlo.

## Ejercicio 1: features de fecha y hora

Enunciado: [`starter/viajes_taxi.csv`](./starter/viajes_taxi.csv), el mismo dataset de la sesión pasada, sin los errores confirmados. A partir de `fecha_hora_inicio`, construir hora, día de la semana, fin de semana, hora pico y la hora como ciclo, y comprobar si la hora pico aporta algo a la tarifa.

**Respuesta 1, antes de ver la solución:** si dejas la hora como un número del 0 al 23, ¿qué tan lejos queda la hora 23 de la hora 0 para un modelo que mide distancias entre números? ¿Y en el reloj?

Como número, la hora 23 queda a 23 unidades de la hora 0: la máxima distancia posible, como si fueran las horas más diferentes del día. En el reloj están a solo 1 hora. Al convertir la hora en ciclo con `hora_sin` y `hora_cos`, la distancia entre 23 y 0 es 0.26, la misma que entre 12 y 13, mientras que las 0 y las 12, opuestas en el reloj, quedan a 2.0, la máxima distancia.

**Respuesta 2:** la duración del viaje no existe al pedir el taxi, pero la hora sí. ¿Qué parte de lo que la duración le diría al modelo puede traer `es_hora_pico`?

La duración le diría al modelo cuánto tráfico hubo: un viaje lento por kilómetro cuesta más. Eso no se sabe al pedir el taxi, pero la hora pico lo anticipa. En hora pico (días laborables de 7 a 9 y de 16 a 19), los viajes tardan 3.64 minutos por km frente a 2.79 fuera de ella (+30%), y cuestan 3.52 USD por km frente a 3.22 (+9%). `es_hora_pico` trae la parte "esperada" del tráfico; lo que no puede traer es el tráfico imprevisto de un viaje concreto.

**La formulación completa, tal como la resuelvo yo:**

[`starter/mi_primer_feature_eng.py`](./starter/mi_primer_feature_eng.py) quita los errores confirmados (tarifa 999.99 y duración negativa, quedan 2975 viajes), saca de `fecha_hora_inicio` la hora y el día de la semana, convierte la hora en ciclo con `hora_sin` y `hora_cos`, codifica las zonas con one-hot y el método de pago con `OrdinalEncoder`. Para comprobar la hora pico, sin contar viajes de tarifa fija ni de distancia 0: una regresión lineal con solo la distancia explica el 96.7% de la tarifa (R²), y al agregar `es_hora_pico` sube a 97.5%, con un coeficiente de +2.14 USD por viaje en hora pico. Sola, su correlación con la tarifa es casi nula (0.03): aporta en combinación con la distancia, no por sí misma.

## Durante el ConcepTest

**Tu voto, antes de discutir en pareja** (A, B, C o D):

_(tu voto)_

**Tu razonamiento:**

_(tu respuesta)_

**Después de discutir en pareja, ¿cambiaste de voto? ¿Por qué?**

_(tu respuesta)_

## Ejercicio 2: zona, codificación y disponibilidad

Solo o en pareja. Parte de la plantilla [`plantilla-ejercicio2/features_de_zona.py`](./plantilla-ejercicio2/features_de_zona.py) y córrela desde su carpeta. Completa los 4 `TODO`.

**Respuesta 1:** ¿cuántos viajes tienen `es_tarifa_fija` en 1, y qué tarifa mínima y máxima tienen? ¿Qué te dice eso sobre lo que un modelo lineal puede aprender con esta columna?

300 viajes, todos con tarifa mínima y máxima de 70 USD. La columna es casi una regla perfecta: cuando vale 1, la tarifa es 70 sin importar la distancia. Pero un modelo lineal suma efectos (`tarifa = a·distancia + b·es_tarifa_fija + ...`), así que no puede apagar el efecto de la distancia en esos viajes y seguiría sumando kilómetros a algo que siempre cuesta 70. Para aprenderlo bien necesita una interacción (`distancia × (1 − es_tarifa_fija)`) o un modelo de árboles.

**Respuesta 2:** ¿cuántas columnas crea one-hot para la zona de origen, y cuántas la codificación ordinal? Si el modelo es una regresión lineal, ¿cuál de las dos usarías, y por qué la otra le da información falsa?

One-hot crea 8 columnas, una por zona; la ordinal, 1 sola columna con valores de 0 (Brooklyn) a 7 (Upper West Side). Para una regresión lineal usaría one-hot. La ordinal le dice al modelo que las zonas tienen un orden y una distancia entre ellas, por ejemplo que Upper West Side (7) es "más" que Harlem (1), o que Midtown (4) está entre JFK (2) y Upper East Side (6). Ese orden es solo alfabético: el modelo aprendería un efecto que crece de zona en zona y que no existe.

**Respuesta 3:** ¿qué columnas del dataset no existen al pedir el taxi? ¿Qué pasaría con el modelo si las usaras para entrenar?

`duracion_min`, `propina` y `metodo_pago` (en un taxi se define al pagar) solo se conocen al terminar el viaje. `distancia_km` es la distancia recorrida; al pedir el taxi solo existe una estimación de la ruta. `tarifa` es el objetivo. Si las usaras para entrenar, el modelo saldría excelente en las pruebas, porque esas columnas ya contienen parte de la respuesta, pero fallaría en producción, donde esos datos todavía no existen (fuga de información).

## Ejercicio 3: dos features para tu proyecto

Usa el mismo archivo de la exploración de la Semana 8 y la plantilla [`plantilla-features/features_proyecto.py`](./plantilla-features/features_proyecto.py).

### Paso 1: el momento de la predicción (5 minutos)

Escribe qué predice tu modelo y en qué momento: qué información existe en ese instante y cuál todavía no.

El modelo predice, al cierre del día t, si un cantón tendrá demanda alta de emergencias del ECU 911 en t+3 (`y_3 = 1` cuando el conteo de t+3 supera el P90 del cantón para ese día de la semana, calculado solo con entrenamiento). En ese momento existen los conteos hasta t (`n_emergencias` y por servicio), los rezagos y medias previas, el calendario y los feriados futuros (`es_feriado_t3`). Todavía no existen los conteos de t+1 a t+3: `obj_n_emergencias_t3` y `obj_n_emergencias_t7` solo sirven para construir la etiqueta.

### Paso 2: construye las 2 features (15 minutos)

Completa la plantilla con 2 columnas nuevas, derivadas de las existentes. Al menos una tiene que salir de uno de tus hallazgos de la exploración.

Código completo en [`plantilla-features/features_proyecto.py`](./plantilla-features/features_proyecto.py).

```python
# Feature 1: nivel reciente del mismo dia de la semana que t+3, relativo al umbral
emergencias = datos.groupby("cod_canton")["n_emergencias"]
media_mismo_dia_t3 = sum(emergencias.shift(k) for k in [4, 11, 18, 25]) / 4
datos["nivel_vs_umbral_t3"] = media_mismo_dia_t3 / datos["p90_t3"]

# Feature 2: posicion de t+3 respecto a un feriado
datos["momento_feriado_t3"] = np.select(
    [datos["es_feriado_t3"], es_feriado_en(4), es_feriado_en(2)],
    ["feriado", "vispera", "dia_despues"],
    default="normal",
)
```

### Paso 3: justifica cada feature (5 minutos)

Para cada una: de qué hallazgo o conocimiento del dominio sale, qué evidencia muestra que aporta (una correlación, una diferencia de promedios), y por qué existe en el momento de predecir. Si alguna es categórica, di qué codificación usarías según el modelo que planeas entrenar.

**Feature 1:**

`nivel_vs_umbral_t3`: el promedio de emergencias de los últimos 4 días que caen el mismo día de la semana que t+3 (t−4, t−11, t−18 y t−25), dividido por el P90 del cantón para ese día. Sale de dos hallazgos de la Semana 8: el ciclo semanal (el rezago útil es el del mismo día de la semana que t+3, no `lag_7d`) y la escala entre cantones (dividir por el P90 compara a cada cantón consigo mismo). Evidencia: correlación de 0.132 con `y_3`, mientras que las proporciones contra la media del cantón no pasaban de 0.02. En el quintil más alto, la tasa de alta demanda es 14.9%, frente a 4.8% en el más bajo. En el periodo de prueba la correlación sube a 0.214 (0.106 en entrenamiento). Existe al predecir porque usa solo días pasados, y el P90 es un valor fijo calculado con entrenamiento. Es numérica: se escala.

**Feature 2:**

`momento_feriado_t3`: si t+3 es `feriado`, `vispera` (t+4 es feriado), `dia_despues` (t+2 fue feriado) o `normal`. Sale del conocimiento del dominio: las vísperas de feriado traen viajes, fiestas y más tránsito, y la OBT solo marcaba el feriado (`es_feriado_t3`), no la víspera. Evidencia, tasa de `y_3 = 1`: feriado 19.6% (16.128 días), víspera 13.9% (10.304), día después 8.9% (10.304) y normal 7.4% (386.176). La víspera casi duplica la tasa de un día normal. Existe al predecir porque el calendario de feriados se publica con anticipación. Es categórica: con una regresión logística usaría one-hot, porque la ordinal inventaría un orden entre las categorías; con un modelo de árboles cualquiera de las dos funciona.

## Antes de la próxima sesión

**Lectura:** ["The Dreaded Antagonist: Data Leakage in Machine Learning"](https://towardsdatascience.com/the-dreaded-antagonist-data-leakage-in-machine-learning-5f08679852cc/), Towards Data Science.

Para escalar la distancia antes de entrenar, le restas la media y la divides por la desviación estándar. ¿Con qué viajes calculas esa media: con todos, o solo con los de entrenamiento? ¿Cambia algo?

Solo con los de entrenamiento. Si uso todos los viajes, la media y la desviación incluyen información del conjunto de prueba, que representa datos que el modelo no debería haber visto: es fuga de información. El número puede cambiar poco, pero la evaluación deja de ser honesta y sale más optimista que en producción, donde los datos nuevos no estaban al calcular la media. La media y la desviación aprendidas en entrenamiento se aplican después, sin recalcular, a prueba y a los datos nuevos.
