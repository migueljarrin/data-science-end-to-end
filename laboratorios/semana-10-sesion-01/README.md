# Semana 10, Sesión 1: Entrenamiento y comparación de modelos I: línea base y ensamblajes

> Objetivo de la sesión: entrenar un modelo de línea base y un modelo de ensamblaje sobre los datos preparados de tu proyecto, y aplicar regularización cuando el modelo se sobreajusta, sin derivar la matemática del descenso de gradiente.

**Lectura previa de esta sesión:** ["Ensembles in Machine Learning"](https://towardsdatascience.com/ensembles-in-machine-learning-9128215629d1/), Towards Data Science.

**Referencia de esta sesión:** [Ensemble methods (documentación oficial de scikit-learn)](https://scikit-learn.org/stable/modules/ensemble.html).

## Requisitos antes de esta sesión

Nada nuevo que instalar: todo lo de hoy está en scikit-learn, que ya usaste la sesión pasada. Ten a mano el script `pipeline_proyecto.py` de tu proyecto, de la Semana 9, Sesión 2.

Los laboratorios de hoy son notebooks: entrenar y comparar modelos es experimentar, y en un notebook vuelves a correr solo el modelo que cambiaste, sin reentrenar los demás. La preparación no se copia en el notebook: se importa del script, para que todos los modelos usen exactamente la misma.

## Antes de empezar

A partir de la lectura previa:

**Según el artículo, ¿qué es un ensamblaje, y en qué se diferencian bagging y boosting en la forma de combinar sus modelos?**

_(tu respuesta)_

**¿Por qué un promedio de muchos árboles puede equivocarse menos que el mejor de esos árboles por separado?**

_(tu respuesta)_

## Pregunta de apertura

Ya tienes los datos listos para entrenar. Si entrenas dos modelos sobre el mismo conjunto y uno da un error mucho menor en entrenamiento que en prueba, ¿qué le está pasando?

_(tu respuesta)_

## Ejercicio 1: línea base, un árbol y un bosque

Notebook: [`starter/ejercicio1_linea_base_y_ensamblaje.ipynb`](./starter/ejercicio1_linea_base_y_ensamblaje.ipynb), sobre [`starter/viajes_features.csv`](./starter/viajes_features.csv), el mismo de la sesión pasada. La preparación de la Semana 9 está en [`starter/preparacion_taxis.py`](./starter/preparacion_taxis.py) y el notebook la importa. Ya trae una función `evaluar` que entrena cada modelo, mide el error absoluto medio en entrenamiento y en prueba, y lo registra en una tabla. Los 4 `TODO` son los modelos, cada uno en su celda. Córrelo completo una vez antes de tocar nada (**Run All**).

**Respuesta 1 (TODO 1):** la línea base predice siempre la mediana de la tarifa. ¿Cuánto esperas que se equivoque en promedio? ¿Para qué sirve un modelo que no usa ninguna columna?

_(tu respuesta)_

**Respuesta 2 (TODO 2):** un árbol sin límite puede seguir partiendo los datos hasta dejar un viaje por hoja. ¿Qué error esperas en entrenamiento, y qué esperas en prueba?

_(tu respuesta)_

**Respuesta 3 (TODO 3 y 4):** ¿qué esperas que pase con la brecha entre entrenamiento y prueba al limitar la profundidad? ¿Y con 200 árboles promediados?

_(tu respuesta)_

**Lo que confirmó la tabla, TODO por TODO:**

| modelo | MAE entrenamiento | MAE prueba | brecha | segundos |
|---|---|---|---|---|
| linea base (mediana) | 13.1998 | 12.5308 | −0.6690 | 0.010 |
| arbol sin limite | 0.0029 | 1.7017 | 1.6988 | 0.017 |
| arbol max_depth=8 | 1.0098 | 1.2728 | 0.2630 | 0.010 |
| bosque aleatorio (200 arboles) | 0.4739 | 1.3016 | 0.8276 | 1.247 |

- TODO 1: la línea base se equivoca 12.53 USD por viaje en prueba. No usa ninguna columna; sirve de piso: un modelo que no la supere no aporta nada.
- TODO 2: el árbol sin límite casi memoriza el entrenamiento (0.003 USD) pero en prueba sube a 1.70: brecha de 1.70, sobreajuste claro.
- TODO 3: con `max_depth=8` el error de entrenamiento sube a 1.01, pero el de prueba baja a 1.27 y la brecha cae de 1.70 a 0.26. Es el mejor en prueba de los cuatro.
- TODO 4: el bosque reduce mucho el error del árbol sin límite en prueba (1.70 → 1.30), porque promediar 200 árboles cancela parte de sus errores. Pero sus árboles siguen sin límite, así que la brecha sigue alta (0.83) y queda apenas por detrás del árbol limitado.

## Durante el ConcepTest

**Tu voto, antes de discutir en pareja** (A, B, C o D):

_(tu voto)_

**Tu razonamiento:**

_(tu respuesta)_

**Después de discutir en pareja, ¿cambiaste de voto? ¿Por qué?**

_(tu respuesta)_

## Ejercicio 2: regularizar una regresión que se sobreajusta

Solo o en pareja. Notebook: [`starter/ejercicio2_regularizacion.ipynb`](./starter/ejercicio2_regularizacion.ipynb), sobre el mismo `viajes_features.csv` y con la misma preparación importada. Mismo esqueleto del Ejercicio 1; `evaluar` acepta además `grado_interacciones=3`, que agrega como columnas todos los productos entre columnas hasta grado 3. Los pasos 1 a 3 tienen `TODO`; los pasos 4 y 5 solo tienen la comprobación. Complétalos hasta que todas digan `OK`.

**Respuesta 1:** ¿cuántas columnas recibe la regresión con interacciones de grado 3, y cuántas filas de entrenamiento hay? ¿Qué tiene que ver esa comparación con el error en prueba que obtuviste?

Recibe 3275 columnas y solo hay 2380 filas de entrenamiento: más columnas que filas. Con eso hay infinitas combinaciones de coeficientes que pasan exactamente por los datos de entrenamiento, así que la regresión memoriza (error de 0.91 USD en entrenamiento) en vez de aprender la relación real. En prueba, esos coeficientes enormes y arbitrarios producen predicciones absurdas: el error se dispara a 5.337.887.934 USD.

**Respuesta 2:** ¿qué cambió entre `lineal grado 3` y `ridge grado 3` en el error de entrenamiento, y qué cambió en el de prueba? ¿Por qué Ridge empeora un poco en entrenamiento?

En entrenamiento, el error subió un poco: de 0.9114 a 1.0272 USD. En prueba, bajó de 5.337.887.934 a 1.3209 USD. Ridge castiga los coeficientes grandes, así que ya no puede ajustar cada fila de entrenamiento a la perfección, ni el ruido. Esa es la parte que empeora en entrenamiento, y es justo la que no se repetía en datos nuevos. A cambio, generaliza: la brecha pasa de más de 5.000 millones a 0.29.

**Respuesta 3:** ¿qué modelo quedó mejor en prueba? ¿Cuánto mejor que la línea base?

`gradient boosting`, con un error de 1.2754 USD en prueba, frente a 12.5308 de la línea base: se equivoca 11.26 USD menos por viaje, un 90% menos de error (casi 10 veces menor). Queda apenas mejor que `ridge grado 3` (1.3209) y entrena en menos tiempo (0.32 s frente a 0.41 s).

**Si terminas antes:** la brecha de la línea base es negativa (se equivoca menos en prueba que en entrenamiento). ¿Cómo puede pasar eso con un modelo que no aprende nada?

La línea base predice siempre la mediana de entrenamiento, así que su error solo depende de qué tan lejos de esa mediana están las tarifas de cada conjunto. Por azar de la división, las tarifas de prueba quedaron un poco más concentradas cerca de la mediana, con menos viajes caros, y por eso el error es menor (12.53 frente a 13.20). No es que haya aprendido algo: con otra semilla de división la brecha podría salir positiva.

Los números de este ejercicio son del ambiente del curso (Python 3.11, scikit-learn 1.5.2). Con Python 3.14 y scikit-learn 1.9, `lineal grado 3` da 22.73 USD en prueba en vez de 5.300 millones, porque con más columnas que filas cada versión elige una solución distinta. El resto de los modelos da igual.

## Ejercicio 3: los primeros modelos de tu proyecto

Usa tu pipeline de la Semana 9, Sesión 2, con la misma división de entrenamiento y prueba. Esta vez no hay plantilla: escribe el notebook tú.

### Entregable 1: `modelos_proyecto.ipynb`

Un notebook, en la misma carpeta que tu `pipeline_proyecto.py`, que importe de ahí la preparación y la división (`from pipeline_proyecto import cargar_y_dividir, construir_preparacion`) en vez de copiarlas, y que entrene:

- Una línea base. Elige la que corresponde a tu problema y justifícala abajo: `DummyRegressor` o `DummyClassifier`, o una regla del dominio (por ejemplo, "mañana igual que hoy" si predices una serie en el tiempo).
- Un modelo lineal (`Ridge` si es regresión, `LogisticRegression` si es clasificación), con la regularización que haga falta.
- Un ensamblaje (`RandomForestRegressor`, `GradientBoostingRegressor` o sus versiones `Classifier`).

### Entregable 2: `resultados_proyecto.csv`

Una fila por modelo, con la métrica de tu proyecto en entrenamiento y en prueba, la brecha y los segundos de entrenamiento, escrita por el notebook. Antes de hacer commit, reinicia el kernel y corre todo: la tabla tiene que salir de una corrida completa, no de celdas corridas en momentos distintos.

### Entregable 3: respuestas

Script: [`proyecto/modelos_proyecto.py`](./proyecto/modelos_proyecto.py). Tabla: [`proyecto/resultados_proyecto.csv`](./proyecto/resultados_proyecto.csv). El proyecto (ECU 911) clasifica si un cantón tendrá alta demanda de emergencias en t+3 (`y_3`); entrenamiento hasta junio de 2025 (327.264 filas) y prueba desde julio de 2025 (94.976 filas). Como solo el 8% de los casos es clase 1, la métrica es la precisión promedio (AP, el área bajo la curva precision-recall): un modelo que no distingue nada saca la tasa de clase 1, y 1.0 es perfecto. La brecha es AP de entrenamiento menos AP de prueba.

| modelo | AP entrenamiento | AP prueba | brecha | segundos |
|---|---|---|---|---|
| dummy (tasa de clase 1) | 0.0808 | 0.0787 | 0.0022 | 0.70 |
| regla: t−4 superó el P90 | 0.0902 | 0.1163 | −0.0261 | 0.01 |
| logística C=1 | 0.1537 | 0.2249 | −0.0712 | 2.57 |
| logística C=0.01 | 0.1537 | 0.2252 | −0.0715 | 2.26 |
| bosque sin límite | 1.0000 | 0.1914 | 0.8086 | 11.32 |
| bosque min_samples_leaf=100 | 0.2408 | 0.2313 | 0.0095 | 9.18 |

**¿Cuál es tu línea base, y por qué esa y no otra?**

Una regla del dominio: "t+3 será alta demanda si t−4 superó el P90". Es la versión de "mañana igual que hoy" para mi problema. Uso t−4 y no t porque t−4 cae el mismo día de la semana que t+3, y el ciclo semanal es fuerte (hallazgo 2 de la Semana 8): comparar con t daría una regla peor. Es la línea base más exigente que se puede armar sin entrenar nada, y es lo que alguien del ECU 911 podría hacer a mano. También reporto `DummyClassifier(strategy="prior")` como piso: su AP es la tasa de clase 1 (0.079), y un modelo que no la supere no sirve para nada.

**¿Alguno de tus modelos se sobreajusta? Muestra la evidencia con números de tu tabla.**

Sí, el bosque sin límite: AP de 1.0000 en entrenamiento y de 0.1914 en prueba, una brecha de 0.81. Sus árboles crecen hasta memorizar cada fila de entrenamiento, y en prueba queda incluso por debajo de la regresión logística (0.2249). Las logísticas no se sobreajustan: su brecha es negativa (−0.07), y la de la regla también (−0.03). El periodo de prueba es más fácil que el de entrenamiento, que incluye 2021, con una tasa de alta demanda mucho más alta, y el periodo anómalo de enero de 2024 (hallazgo 3).

**¿Qué regularización aplicaste (o por qué no hizo falta), y qué cambió en la tabla?**

En el bosque, `min_samples_leaf=100`: cada hoja necesita al menos 100 filas, así que los árboles ya no pueden memorizar casos sueltos. La brecha bajó de 0.81 a 0.01 y el AP en prueba subió de 0.1914 a 0.2313, el mejor de la tabla, y además entrena más rápido (9.2 s frente a 11.3 s). En la logística probé una regularización 100 veces más fuerte (C de 1 a 0.01) y no cambió nada (0.2249 frente a 0.2252): con 327.264 filas y solo 42 columnas, un modelo lineal no tiene espacio para sobreajustarse, así que no hacía falta.

**¿Cuánto mejora tu mejor modelo a la línea base?**

El bosque regularizado saca un AP de 0.2313 en prueba, frente a 0.1163 de la regla: el doble (+0.115). Frente al piso del dummy (0.0787) es 2.9 veces mejor. Con el umbral de 0.5, detecta el 55% de los días de alta demanda (recall) con una precisión del 18%; la regla detecta el 24% con una precisión del 24%. Detecta más del doble de casos, a cambio de más falsas alarmas: el umbral se puede ajustar según cuánto cueste una falsa alarma frente a un día de alta demanda sin preparar.

## Antes de la próxima sesión

**Lectura:** ["Machine Learning vs LLM: Differences, Applications & Impact"](https://www.neuralconcept.com/post/ml-vs-llm-key-differences-applications-engineering-impact), Neural Concept.

Para estimar la tarifa de un viaje, podrías entrenar un ensamblaje, entrenar una red neuronal o escribirle a un LLM los datos del viaje y pedirle un número. ¿Qué tendrías que medir de cada opción, además del error, para decidir cuál usar en la app de taxis?

_(tu respuesta)_
