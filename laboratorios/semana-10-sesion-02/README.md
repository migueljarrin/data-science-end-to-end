# Semana 10, Sesión 2: Entrenamiento y comparación de modelos II: ¿ensamblaje, red neuronal simple o un LLM?

> Objetivo de la sesión: comparar, sobre el problema de tu proyecto, un modelo de ensamblaje, una red neuronal simple entrenada con una librería de alto nivel y un LLM usado vía prompting, y decidir cuál conviene según desempeño, costo y explicabilidad.

**Lectura previa de esta sesión:** ["Machine Learning vs LLM: Differences, Applications & Impact"](https://www.neuralconcept.com/post/ml-vs-llm-key-differences-applications-engineering-impact), Neural Concept.

**Referencia de esta sesión:** [Neural network models, supervised (documentación oficial de scikit-learn)](https://scikit-learn.org/stable/modules/neural_networks_supervised.html).

## Requisitos antes de esta sesión

- Nada nuevo que instalar: la red neuronal es `MLPRegressor`, de scikit-learn.
- Acceso a un LLM de chat (ChatGPT, Claude, Gemini u otro; la versión gratuita alcanza), para el Ejercicio 2.
- La tabla de resultados de tu proyecto de la sesión pasada, y tu `pipeline_proyecto.py`.

Como la sesión pasada, los laboratorios son notebooks que importan la preparación de un script (`preparacion_taxis.py` en los Ejercicios 1 y 2, tu `pipeline_proyecto.py` en el 3).

## Antes de empezar

A partir de la lectura previa:

**Según el artículo, ¿para qué tipo de datos y de problema conviene el aprendizaje automático clásico, y para cuál un LLM?**

_(tu respuesta)_

**El artículo compara las dos opciones en datos, costo y explicabilidad. ¿Cuál de esas tres diferencias pesa más para tu proyecto?**

_(tu respuesta)_

## Pregunta de apertura

Para estimar la tarifa de un viaje, podrías entrenar un ensamblaje, entrenar una red neuronal o escribirle a un LLM los datos del viaje y pedirle un número. ¿Qué tendrías que medir de cada opción, además del error, para decidir cuál usar en la app de taxis?

_(tu respuesta)_

## Ejercicio 1: una red neuronal frente al ensamblaje

Notebook: [`starter/ejercicio1_red_neuronal.ipynb`](./starter/ejercicio1_red_neuronal.ipynb), sobre [`starter/viajes_features.csv`](./starter/viajes_features.csv). Ya entrena el gradient boosting de la sesión pasada con la misma preparación y la misma división, importadas de [`starter/preparacion_taxis.py`](./starter/preparacion_taxis.py). Los 3 `TODO` son la red neuronal, cuántos parámetros aprendió y qué columnas usa más el ensamblaje. Córrelo completo una vez antes de tocar nada (**Run All**).

**Respuesta 1 (TODO 1):** sin resolver, la red sale peor que el ensamblaje y aparece una advertencia `ConvergenceWarning`. ¿Qué crees que significa? ¿Qué esperas al dejarla entrenar hasta 1000 iteraciones?

Significa que el optimizador llegó al límite de iteraciones (200 por defecto) y los pesos todavía estaban cambiando: la red no terminó de aprender. Por eso sale peor (1.69 USD en prueba, frente a 1.28 del gradient boosting). Con hasta 1000 iteraciones espero que converja antes del límite, que desaparezca la advertencia y que el error baje al nivel del ensamblaje o un poco mejor, a cambio de tardar más en entrenar.

**Respuesta 2 (TODO 2):** una capa oculta de 64 neuronas recibe las 25 columnas preparadas y entrega una tarifa. ¿Cuántos números tiene que aprender?

De la entrada a la capa oculta: 25 × 64 = 1600 pesos más 64 sesgos. De la capa oculta a la salida: 64 pesos más 1 sesgo. En total, 1600 + 64 + 64 + 1 = 1729 números.

**Respuesta 3 (TODO 3):** ¿qué columna esperas que el ensamblaje use más? Si la app le muestra al conductor por qué la tarifa estimada es 70 dólares, ¿cuál de los dos modelos te permite responder?

Espero `distancia_km`, porque la tarifa crece casi en proporción a la distancia, y después `es_tarifa_fija`, que marca los viajes al aeropuerto de 70 dólares. El ensamblaje permite responder: sus importancias muestran qué columnas pesan, y se puede seguir qué reglas de los árboles llevaron a 70. La red reparte la decisión en 1729 números sin significado propio, así que no hay una explicación directa.

**Lo que confirmó la salida, TODO por TODO:**

| modelo | MAE entrenamiento | MAE prueba | segundos |
|---|---|---|---|
| gradient boosting | 1.0705 | 1.2754 | 0.18 |
| red neuronal, 200 iteraciones (sin resolver) | 1.6009 | 1.6854 | 1.72 |
| red neuronal, hasta 1000 iteraciones | 1.0882 | 1.1695 | 5.14 |

- TODO 1: con hasta 1000 iteraciones la red converge en 692, sin `ConvergenceWarning`, y queda mejor que el ensamblaje en prueba (1.17 frente a 1.28 USD). Tarda unas 28 veces más en entrenar (5.1 s frente a 0.18 s).
- TODO 2: la red aprendió 1729 parámetros.
- TODO 3: las 3 columnas más importantes para el ensamblaje son `distancia_km` (0.9824), `es_tarifa_fija` (0.0120) y `es_hora_pico` (0.0028). La distancia explica casi todo.

## Durante el ConcepTest

**Tu voto, antes de discutir en pareja** (A, B, C o D):

_(tu voto)_

**Tu razonamiento:**

_(tu respuesta)_

**Después de discutir en pareja, ¿cambiaste de voto? ¿Por qué?**

_(tu respuesta)_

## Ejercicio 2: tres soluciones sobre los mismos 20 viajes

Solo o en pareja. Notebook: [`starter/ejercicio2_tres_soluciones.ipynb`](./starter/ejercicio2_tres_soluciones.ipynb), sobre el mismo `viajes_features.csv`. Los pasos 1 a 3 tienen `TODO`; los pasos 4 y 5 solo tienen la comprobación.

1. Completa los `TODO` 1 a 3 y corre las celdas hasta la que escribe `prompt_llm.txt`: 30 viajes con su tarifa como ejemplos y 20 viajes sin tarifa.
2. Copia `prompt_llm.txt` completo en un LLM de chat. Guarda los 20 números que responda, uno por línea, en `respuestas_llm.txt`, en la carpeta `starter`.
3. Completa los pasos 4 y 5 y corre sus celdas y la de la comprobación hasta que todas digan `OK`. Los modelos ya están entrenados en el kernel: no hace falta volver a correr las celdas de arriba. Para el paso 5, busca el precio por millón de tokens de entrada del modelo que usaste en la página de precios de su proveedor.

**Respuesta 1:** ¿qué LLM usaste? Completa la tabla con los números de tu corrida.

Claude Sonnet 5 (2.00 USD por millón de tokens de entrada). El prompt tiene 2902 caracteres, unos 726 tokens, y 10 000 viajes al mes son 500 prompts: 363 000 tokens, 0.73 USD al mes. Los modelos de scikit-learn predicen 10 000 viajes en 0.02 s en la máquina del curso, así que su costo por predicción es prácticamente cero.

| | Error en los 20 viajes | Costo de entrenar | Costo de 10 000 viajes al mes | ¿Puedes explicar una predicción? |
|---|---|---|---|---|
| Gradient boosting | 0.90 USD | 0.18 s en CPU | ≈ 0 (0.015 s de CPU) | Sí: importancias de columnas y reglas de los árboles |
| Red neuronal | 0.96 USD | 5.1 s en CPU (692 iteraciones) | ≈ 0 (0.024 s de CPU) | Difícil: 1729 pesos sin significado propio |
| LLM | 3.74 USD | 0 (no se entrena; usa 30 ejemplos en el prompt) | 0.73 USD (solo tokens de entrada) | No de forma confiable: puede dar una razón, pero no es el cálculo que hizo |

**Respuesta 2:** corre el mismo prompt otra vez, en una conversación nueva. ¿Te dio los mismos 20 números? ¿Qué problema le trae eso a una app que le cobra al pasajero?

No. En la segunda conversación (Claude Sonnet, mismo prompt) solo 1 de los 20 números coincidió, el 70 del viaje 2; en promedio cambiaron 4.40 USD por viaje. El error bajó de 3.74 a 1.89 USD, pero no porque fuera más preciso en todo: corrigió el JFK→JFK (de 70 a 7.0) y a cambio le cobró 85 USD al viaje 18 (JFK→Midtown, 37 km), que es de tarifa fija de 70, y bajó a 68 el viaje 15, también de tarifa fija. Para una app que cobra, eso es un problema serio: el mismo viaje tendría precios distintos según el momento en que se pregunte, no se puede reproducir ni auditar un cobro, y un pasajero que pide dos cotizaciones ve dos precios. El gradient boosting y la red, con el modelo ya entrenado, dan siempre el mismo número para el mismo viaje.

**Respuesta 3:** busca en tus 20 respuestas la peor predicción del LLM. ¿Qué tiene de particular ese viaje? ¿Lo habría aprendido el ensamblaje con las 2380 filas de entrenamiento?

El viaje 13: JFK Airport → JFK Airport, 1.01 km, en efectivo. La tarifa real era 11.46 USD y el LLM respondió 70.0: se equivocó en 58.54 USD, y ese viaje solo explica casi todo su error (sin él, el error de los otros 19 es 0.86 USD). En los 30 ejemplos, los dos viajes que salen de JFK cuestan 70, así que el LLM aplicó la regla "JFK = 70". Pero la tarifa fija es para los viajes largos entre el aeropuerto y Manhattan; un viaje corto dentro del aeropuerto se cobra por distancia. El ensamblaje sí lo aprendió: en los datos hay 9 viajes JFK→JFK, todos por distancia (entre 10 y 19 USD), y en entrenamiento tiene la columna `es_tarifa_fija`. Predijo 12.74 USD (error de 1.28) y la red 13.79.

**Si terminas antes:** el error en los 20 viajes de muestra no es el mismo que en los 595 de prueba. ¿Por qué no se mide el LLM sobre los 595, y qué tan confiable es una comparación sobre 20?

Porque el LLM se usa copiando y pegando en un chat: 595 viajes serían 30 prompts a mano, con más costo y más riesgo de que las respuestas se desordenen o falten números. Los modelos de scikit-learn evalúan los 595 en milisegundos. Con 20 viajes la comparación es poco confiable: un solo viaje raro (el JFK→JFK) cambia el error del LLM de 0.86 a 3.74 USD. Entre los modelos pasa algo parecido: en los 20 viajes el gradient boosting le gana a la red (0.90 frente a 0.96), pero en los 595 es al revés (1.28 frente a 1.17). Sirve para ver tendencias grandes, no para decidir entre opciones parecidas.

## Ejercicio 3: ¿qué solución conviene para tu proyecto?

Usa tu pipeline y la tabla de resultados de la sesión pasada. Esta vez no hay plantilla.

### Entregable 1: `comparar_proyecto.ipynb`

Un notebook, al lado de tu `pipeline_proyecto.py`, que importe de ahí tu preparación y tu división, y entrene el mejor ensamblaje de la sesión pasada y una red neuronal simple (`MLPRegressor` o `MLPClassifier`), y registre para cada uno la métrica de prueba, los segundos de entrenamiento y, para la red, la cantidad de parámetros.

### Entregable 2: la prueba del LLM

Elige 10 filas de tu conjunto de prueba y escribe un prompt con algunas filas de entrenamiento como ejemplos, como el de `prompt_llm.txt`. Pásalo a un LLM y registra su métrica sobre esas 10 filas, junto con la de tus dos modelos sobre las mismas 10. Si tu problema no se puede plantear así (por ejemplo, porque cada predicción necesita una historia larga), explica por qué; eso también es una respuesta.

### Entregable 3: la decisión

Una tabla con las tres opciones (métrica, costo, explicabilidad) y un párrafo que diga cuál usarías en tu proyecto y por qué, con los números de tu tabla.

Script: [`proyecto/comparar_proyecto.py`](./proyecto/comparar_proyecto.py), con la misma preparación y la misma división por fecha de la sesión pasada (entrenamiento hasta junio de 2025, prueba desde julio de 2025). Tablas: [`proyecto/resultados_comparacion.csv`](./proyecto/resultados_comparacion.csv) (todo el conjunto de prueba) y [`proyecto/resultados_muestra_10.csv`](./proyecto/resultados_muestra_10.csv) (las 10 filas). La métrica es la precisión promedio (AP), como en la sesión pasada: solo el 8% de los casos es alta demanda.

**La prueba del LLM.** El problema sí se puede plantear con filas sueltas, porque la historia de cada cantón ya está resumida en columnas (rezagos, medias y `nivel_vs_umbral_t3`). El prompt ([`proyecto/prompt_llm_proyecto.txt`](./proyecto/prompt_llm_proyecto.txt)) lleva 30 casos de entrenamiento con su respuesta y pide la probabilidad de alta demanda para 10 de prueba; lo respondió ChatGPT. Las 10 filas no son al azar: con 8% de clase 1, casi nunca habría un caso de alta demanda, y el AP necesita al menos uno. Tomé 3 de alta demanda y 7 normales (y 10 y 20 en los ejemplos), así que el AP sobre estas 10 filas no se puede comparar con el de todo el conjunto de prueba.

| | Bosque (`min_samples_leaf=100`) | Red neuronal (1 capa de 32) | LLM (ChatGPT) |
|---|---|---|---|
| AP en todo el conjunto de prueba (94.976 filas) | 0.2313 | **0.2425** | no medido: habría que mandar unos 9.500 prompts |
| AP en las mismas 10 filas | 0.8333 | 0.6250 | **0.8667** |
| Accuracy en las 10 filas (umbral 0.5) | 0.6 | **0.8** | 0.7 |
| Costo de entrenar | 14.5 s | 22.6 s (1.409 parámetros, 21 iteraciones) | no se entrena: solo ve 30 ejemplos de 327.264 |
| Costo de predecir el mes (6.720 predicciones) | prácticamente 0, en la propia máquina | prácticamente 0, en la propia máquina | ≈ 0.99 USD al mes en tokens de entrada (2.00 USD por millón), más la latencia de la API |
| Explicabilidad | alta: la importancia de cada columna (`nivel_vs_umbral_t3` 32%, `media_prev_28d` 7%, `momento_feriado_t3` 6%) | baja: 1.409 pesos sin una lectura directa | baja: puede dar una razón en texto, pero no hay garantía de que sea la que usó, y la respuesta puede cambiar entre corridas |

**Decisión:** usaría el bosque aleatorio regularizado. La red neuronal es la mejor en todo el conjunto de prueba, pero solo por 0.011 de AP (0.2425 frente a 0.2313); a cambio tarda un 56% más en entrenar (22.6 s frente a 14.5 s) y no se puede explicar. Para el ECU 911 la explicación importa: el bosque muestra que decide sobre todo por `nivel_vs_umbral_t3`, es decir, porque el cantón ya venía cerca de su umbral el mismo día de la semana, y esa es una razón que un planificador de turnos puede revisar y en la que puede confiar. El LLM sacó el mejor AP en las 10 filas (0.8667), pero 10 filas no alcanzan para concluir nada: si el caso de alta demanda al que le dio 0.48 hubiera quedado debajo de un caso normal más, su AP bajaría a 0.8333, el mismo del bosque. Además, sus probabilidades siguen de cerca el orden de `nivel_vs_umbral` (correlación de rangos de 0.93), la misma señal que el bosque ya usa. No se puede evaluar sobre las 94.976 filas de prueba sin mandar miles de prompts, su respuesta no es reproducible entre corridas y obliga a enviar los datos del ECU 911 a un proveedor externo. Antes de cambiar el bosque por la red, repetiría la comparación con varias semillas para ver si la diferencia de 0.011 se mantiene.

## Antes de la próxima sesión

**Lectura:** ["Version Controlling in Practice: Data, ML Model, and Code"](https://towardsdatascience.com/version-controlling-in-practice-data-ml-model-and-code-e13c518067dc/), Towards Data Science.

Dos compañeros reportan errores distintos para "el mismo" gradient boosting sobre los mismos datos de taxis. ¿Qué tendrías que saber de cada corrida para descubrir por qué no coinciden?

_(tu respuesta)_
