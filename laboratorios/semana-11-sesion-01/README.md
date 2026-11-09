# Semana 11, Sesión 1: Gestión y trazabilidad de experimentos: eligiendo el modelo ganador con evidencia

> Objetivo de la sesión: registrar de forma trazable los parámetros, métricas y artefactos de las corridas de entrenamiento de las dos sesiones anteriores, y elegir el modelo final de tu proyecto con esa evidencia.

**Lectura previa de esta sesión:** ["Version Controlling in Practice: Data, ML Model, and Code"](https://towardsdatascience.com/version-controlling-in-practice-data-ml-model-and-code-e13c518067dc/), Towards Data Science.

**Referencia de esta sesión:** [ML Experiment Tracking (documentación oficial de MLflow)](https://mlflow.org/docs/latest/ml/tracking/).

## Requisitos antes de esta sesión

Hoy se agrega una herramienta: MLflow, que registra cada corrida de entrenamiento. Como en un equipo de datos, el registro vive en un servidor de seguimiento (tracking server), no en tu notebook: el Codespace levanta uno en el puerto 5050 cada vez que inicia, y los notebooks lo encuentran por la variable de entorno `MLFLOW_TRACKING_URI`.

Si tu Codespace se creó antes de esta sesión, sincroniza tu fork y reconstruye el contenedor (`Ctrl+Shift+P` o `Cmd+Shift+P` → "Codespaces: Rebuild Container"; en tu laptop, "Dev Containers: Rebuild Container"). Reconstruir instala MLflow y configura el servidor; tus archivos no se pierden. Al terminar, comprueba desde una terminal:

```
bash .devcontainer/verificar.sh
```

Las últimas líneas deben decir `mlflow, version 2.17.2` y `servidor de MLflow: responde en http://127.0.0.1:5050`. Si el servidor no responde (por ejemplo, después de detener y volver a abrir el Codespace sin que arranque), levántalo a mano con `bash .devcontainer/mlflow-server.sh`.

La interfaz de MLflow se abre desde la pestaña **Ports** de VS Code: el puerto 5050, "MLflow (Semana 11)", con el ícono del globo. Ahí ves cada experimento, sus corridas, y puedes compararlas lado a lado.

Los laboratorios de hoy son notebooks, como los de la Semana 10, y la preparación se importa de `preparacion_taxis.py`. El registro (la base de datos del servidor y los modelos guardados) queda en la carpeta `.mlflow/` de la raíz del repositorio, que no se sube (está en `.gitignore`): lo que entregas es el notebook y la tabla de corridas que exporta.

**Si trabajas en tu laptop sin el contenedor (Opción B del README):** instala con `pip install -r requirements.txt` y, en una terminal aparte desde la raíz de tu fork, levanta el mismo servidor con `mlflow server --backend-store-uri sqlite:///.mlflow/mlflow.db --artifacts-destination .mlflow/artefactos --port 5050`. Antes de abrir los notebooks, define la variable `MLFLOW_TRACKING_URI=http://127.0.0.1:5050`. Sin esa variable, MLflow guarda el registro en una carpeta `mlruns` al lado de cada notebook, sin servidor: los notebooks también funcionan, pero cada carpeta tiene su propio registro.

## Antes de empezar

A partir de la lectura previa:

**Según el artículo, ¿qué tres cosas hay que versionar en un proyecto de machine learning, y con qué herramienta versiona el autor cada una?**

_(tu respuesta)_

**¿Por qué no alcanza con Git para versionar los datos?**

_(tu respuesta)_

## Pregunta de apertura

Dos compañeros reportan errores distintos para "el mismo" gradient boosting sobre los mismos datos de taxis. ¿Qué tendrías que saber de cada corrida para descubrir por qué no coinciden?

_(tu respuesta)_

## Ejercicio 1: registrar cada corrida con MLflow

Notebook: [`starter/ejercicio1_registrar_corridas.ipynb`](./starter/ejercicio1_registrar_corridas.ipynb), sobre [`starter/viajes_features.csv`](./starter/viajes_features.csv), con la preparación de [`starter/preparacion_taxis.py`](./starter/preparacion_taxis.py). Entrena el bosque y el gradient boosting de la Semana 10, y después la corrida de un compañero. Los 4 `TODO` son el registro. Córrelo completo una vez antes de tocar nada (**Run All**).

**Respuesta 1 (antes de los TODO):** sin resolver, el notebook entrena los tres modelos e imprime sus errores. ¿Cuál de los dos gradient boosting tiene razón? ¿Qué parte de la salida te permite saberlo, y qué parte no?

Ninguno está equivocado: los dos miden bien su propio conjunto de prueba, y son conjuntos distintos. El mío da 1.2754 de error en prueba (división con semilla 42) y el del compañero 1.1867 (semilla 7). La salida lo deja ver solo porque `evaluar` imprime la semilla de la división (`division 42` frente a `division  7`): con eso sé que no midieron sobre los mismos viajes y que los números no se pueden comparar. Lo que la salida no dice es todo lo demás: si usaron el mismo CSV, los mismos hiperparámetros o la misma versión de las librerías. Y al reiniciar el kernel, esa salida desaparece.

**Respuesta 2 (TODO 2 y 3):** de todo lo que se puede registrar de una corrida, ¿qué crees que explica la diferencia entre los dos gradient boosting? ¿Qué parámetro esperas ver distinto en la tabla del paso 5?

La división de los datos: el mismo modelo, evaluado sobre 595 viajes distintos, da otro error. Espero ver distinto `semilla_division` (42 frente a 7), y en cambio iguales `huella_datos` (mismo CSV) y `n_estimators` (mismo modelo). Así fue en la tabla: lo único que cambia entre los dos gradient boosting es la semilla.

**Respuesta 3 (TODO 4):** el registro ya tiene los parámetros y las métricas. ¿Para qué guardar además el modelo entrenado?

Porque los parámetros y las métricas describen el modelo, pero no son el modelo. Con el artefacto guardado puedo cargar exactamente el objeto que produjo ese número y volver a predecir sin reentrenar: sirve para comprobar el resultado (como en el paso 5 del Ejercicio 2), para auditar sus predicciones y para llevarlo a producción. Reentrenar no garantiza el mismo modelo si cambian las librerías, la máquina o una semilla que no quedó registrada. MLflow además guarda junto al modelo las versiones de las librerías con que se entrenó (`requirements.txt`).

**Lo que mostró la tabla del paso 5:**

| corrida | `run_id` | semilla de la división | huella de los datos | error en prueba (MAE) |
|---|---|---|---|---|
| gradient boosting (compañero) | `edfe017186ab4d22ba2002e8d1b8952f` | 7 | `4800204d50c0` | 1.1867 |
| gradient boosting | `a9f2b5597d9e4813953f36847266c351` | 42 | `4800204d50c0` | 1.2754 |
| bosque aleatorio | `5d10752501c9458f90647c3c08ddc50d` | 42 | `4800204d50c0` | 1.3016 |

Los tres usan el mismo CSV (misma huella). Los dos gradient boosting tienen los mismos hiperparámetros (`n_estimators` = 100) y solo cambia la semilla de la división: la diferencia de 0.089 USD entre ellos se debe a los viajes que les tocaron en prueba, no al modelo.

## Durante el ConcepTest

**Tu voto, antes de discutir en pareja** (A, B, C o D):

_(tu voto)_

**Tu razonamiento:**

_(tu respuesta)_

**Después de discutir en pareja, ¿cambiaste de voto? ¿Por qué?**

_(tu respuesta)_

## Ejercicio 2: comparar con evidencia y elegir

Solo o en pareja. Notebook: [`starter/ejercicio2_comparar_y_elegir.ipynb`](./starter/ejercicio2_comparar_y_elegir.ipynb), sobre el mismo `viajes_features.csv`. Mismo esqueleto del Ejercicio 1, con los cinco modelos de la Semana 10 en un experimento propio. Los pasos 1 a 3 tienen `TODO`; los pasos 4 y 5 solo tienen la comprobación. Complétalos hasta que todas digan `OK`.

**Respuesta 1:** ¿qué modelo quedó primero en el registro, y por cuánto le gana al segundo?

La red neuronal, con 1.1695 USD de error en prueba. El segundo es el gradient boosting, con 1.2754: la red se equivoca 0.106 USD menos por viaje, un 8.3% menos. Después vienen el bosque aleatorio (1.3016), Ridge (2.5565) y la línea base (12.5308).

**Respuesta 2:** el paso 5 carga el modelo ganador desde el registro y vuelve a calcular su error. ¿Qué te garantiza que coincida con el número registrado? ¿Qué no te garantiza sobre ese modelo?

Me garantiza que el artefacto guardado es el mismo modelo que produjo la métrica registrada, y que la evaluación es reproducible: cargado desde el registro y aplicado a los mismos 595 viajes de prueba, da exactamente el mismo error (1.1695052296355013 en los dos casos). No me garantiza que el modelo sea bueno con viajes nuevos, ni que siga siendo el mejor con otra división: el error se midió sobre una sola división de 595 viajes, y el Ejercicio 1 mostró que solo cambiar la semilla mueve el error del gradient boosting en 0.089 USD, casi lo mismo que separa a la red del segundo lugar (0.106).

**Respuesta 3:** si mañana alguien cambia una fila de `viajes_features.csv` y vuelve a entrenar, ¿cómo lo notarías mirando solo el registro?

Por el parámetro `huella_datos`: es el hash MD5 del archivo, así que cambiar un solo byte de `viajes_features.csv` cambia la huella. Las corridas nuevas tendrían una huella distinta de `4800204d50c0`, y sabría que sus errores no se pueden comparar con los de hoy, aunque el modelo y la semilla sean los mismos.

**Si terminas antes:** abre la interfaz de MLflow (pestaña **Ports**, puerto 5050), entra al experimento `tarifa-taxis-comparacion`, selecciona las cinco corridas y compáralas lado a lado con **Compare**. Además del error, ¿qué te dice el registro de la red neuronal que no te diría una tabla escrita a mano?

Todos sus hiperparámetros, también los que no escribí y quedaron con el valor por defecto (activación `relu`, optimizador `adam`, `alpha` = 0.0001, tasa de aprendizaje inicial 0.001, tamaño de lote automático), junto a la semilla de la división, la huella de los datos y el tiempo de entrenamiento: 4.0 s, unas 20 veces más que el gradient boosting (0.19 s). Además tiene el modelo guardado, con las versiones de las librerías con que se entrenó, para volver a cargarlo. Una tabla a mano tendría el error y, con suerte, la capa de 64 neuronas.

## Ejercicio 3: el registro de tu proyecto

Usa tu `pipeline_proyecto.py` y los modelos que entrenaste en las dos sesiones de la Semana 10. Esta vez no hay plantilla.

### Entregable 1: `experimentos_proyecto.ipynb`

Un notebook, al lado de tu `pipeline_proyecto.py`, que importe de ahí la preparación y la división y registre en MLflow, en un experimento con el nombre de tu proyecto, una corrida por cada modelo de la Semana 10 (línea base, modelo lineal, ensamblaje, red neuronal). Cada corrida registra:

- Los hiperparámetros del modelo.
- Cómo se dividieron los datos (la semilla, o la fecha de corte si divides por fecha) y la huella del archivo de datos.
- La métrica de tu proyecto en entrenamiento y en prueba, y los segundos de entrenamiento.
- El pipeline entrenado, como artefacto.

Al final, el notebook marca la corrida que eliges como final (`candidato` = `final`), carga su modelo desde el registro y comprueba que reproduce la métrica registrada.

### Entregable 2: `corridas_proyecto.csv`

La tabla de corridas de tu experimento, exportada con `mlflow.search_runs(...).to_csv("corridas_proyecto.csv", index=False)` desde el mismo notebook. Antes de hacer commit, borra las corridas de prueba del experimento de tu proyecto (en la interfaz de MLflow: selecciónalas y **Delete**), reinicia el kernel y corre todo: la tabla tiene que salir de una corrida completa.

### Entregable 3: la decisión

**¿Qué modelo elegiste como final? Escribe su `run_id` y los números del registro que sostienen la decisión.**

Notebook: [`semana-09-sesion-02/plantilla-pipeline/experimentos_proyecto.ipynb`](../semana-09-sesion-02/plantilla-pipeline/experimentos_proyecto.ipynb), al lado de mi [`pipeline_proyecto.py`](../semana-09-sesion-02/plantilla-pipeline/pipeline_proyecto.py), que ahora tiene la preparación y la división en funciones (`cargar_y_dividir`, `construir_preparacion`). Tabla: [`corridas_proyecto.csv`](../semana-09-sesion-02/plantilla-pipeline/corridas_proyecto.csv). Experimento `ecu911-alta-demanda-t3`; métrica: precisión promedio (AP), porque solo el 8% de los casos es alta demanda.

| corrida | AP entrenamiento | AP prueba | brecha | segundos |
|---|---|---|---|---|
| red neuronal (32,) | 0.2021 | **0.2425** | −0.0404 | 12.3 |
| **bosque min_samples_leaf=100** (final) | 0.2514 | 0.2327 | 0.0187 | 13.4 |
| logística C=0.01 | 0.1537 | 0.2252 | −0.0715 | 3.5 |
| logística C=1 | 0.1537 | 0.2249 | −0.0712 | 5.7 |
| bosque sin límite | 1.0000 | 0.1830 | 0.8170 | 13.6 |
| regla: t−4 superó el P90 (línea base) | 0.0902 | 0.1163 | −0.0261 | 0.0 |
| dummy (tasa de clase 1) | 0.0808 | 0.0787 | 0.0022 | 0.7 |

Elegí el bosque regularizado, `run_id` **`a7c9689b915a4eb7ba39e5ba381ef6cb`**, marcado con `candidato` = `final`. Duplica la AP de la línea base (0.2327 frente a 0.1163) y no se sobreajusta (brecha de 0.0187, frente a 0.8170 del bosque sin límite). Cargado desde el registro reproduce su AP exacta (0.2326863296). La red neuronal saca más AP en prueba, pero solo por 0.0098, y en este registro entrena casi igual de rápido (12.3 s frente a 13.4 s), así que la razón para no elegirla es la explicabilidad: el bosque muestra que decide sobre todo por `nivel_vs_umbral_t3`, algo que un planificador del ECU 911 puede revisar. La diferencia de 0.0098 sale de una sola división por fecha; antes de cambiar de modelo la comprobaría con otros cortes.

**Si otra persona clona tu repositorio, ¿qué necesita para obtener exactamente el mismo número? ¿Qué de eso quedó registrado en MLflow y qué no?**

Necesita cuatro cosas: el mismo CSV, el mismo código, el mismo ambiente y las mismas decisiones de división y de semillas.

- **Quedó registrado:** las decisiones (`fecha_corte` = 2025-07-01, `division` = por fecha, filas de entrenamiento y de prueba), todos los hiperparámetros, incluido `random_state` = 42, y la huella del CSV (`7624e6f357a7`), que permite comprobar que se tiene el mismo archivo. Junto al modelo, MLflow guardó el ambiente: Python 3.11.17, scikit-learn 1.5.2, numpy 1.26.4 y pandas 2.2.2 (`requirements.txt` y `conda.yaml` del artefacto).
- **No quedó registrado:** el CSV en sí. Solo la huella: el archivo está en `data/raw/`, que no se sube a git, así que hay que volver a exportarlo de Snowflake (`OBT.OBT_EMERGENCIAS_CANTON_DIA`), y si el pipeline del PSet 2 cargó meses nuevos, la huella ya no coincidirá. Tampoco el código: MLflow no registró el commit de git, porque el notebook corre a través de Jupyter (`mlflow.source.name` apunta a `ipykernel_launcher.py`), así que hay que saber qué versión de `pipeline_proyecto.py` y del notebook se usó. Y el registro mismo (`.mlflow/`) tampoco se sube a git: quien clone el repositorio tiene el CSV de corridas, pero no los modelos guardados.

## Antes de la próxima sesión

**Lectura:** ["How Metrics (and LLMs) Can Trick You: A Field Guide to Paradoxes"](https://towardsdatascience.com/how-metrics-and-llms-can-trick-you-a-field-guide-to-paradoxes/), Towards Data Science.

Hoy elegiste el modelo con menor error sobre los 595 viajes de prueba. ¿Cuánto cambiaría ese error si la división hubiera sido otra? ¿Lo viste en algún lado del registro?

_(tu respuesta)_
