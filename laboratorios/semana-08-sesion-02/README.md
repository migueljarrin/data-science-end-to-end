# Semana 8, Sesión 2: Exploración y visualización de datos

> Objetivo de la sesión: explorar el dataset de tu proyecto con estadística descriptiva y visualizaciones para identificar patrones, outliers y supuestos que romperían un modelo antes de entrenarlo.

**Lectura previa de esta sesión:** ["A Data Scientist's Essential Guide to Exploratory Data Analysis"](https://towardsdatascience.com/a-data-scientists-essential-guide-to-exploratory-data-analysis-25637eee0cf6/), Towards Data Science.

**Referencia de esta sesión:** [Machine Learning Zoomcamp, Módulo 1 (DataTalksClub)](https://github.com/DataTalksClub/machine-learning-zoomcamp).

## Requisitos antes de esta sesión

pandas ya lo tienes desde la Semana 4. Instala matplotlib:

```
pip install matplotlib
```

Verifica con:

```
python3 -c "import matplotlib; print(matplotlib.__version__)"
```

Los scripts de hoy guardan cada gráfico como imagen en una carpeta `figuras/`. También puedes correr el mismo código en un notebook de Jupyter, donde el gráfico aparece debajo de la celda.

## Antes de empezar

A partir de la lectura previa:

**Según el artículo, ¿qué preguntas responde la exploración de datos antes de entrenar cualquier modelo?**

_(tu respuesta)_

**El artículo distingue la exploración de una sola variable de la exploración de la relación entre dos. ¿Qué herramienta propone para cada una?**

_(tu respuesta)_

## Pregunta de apertura

Entrenas un modelo que predice la tarifa de un viaje en taxi. Sin que lo sepas, 15 de los 3000 viajes tienen una tarifa de 999.99 por un error de captura. ¿Qué le pasa al modelo? ¿Lo notarías mirando solo su resultado final?

_(tu respuesta)_

## Ejercicio 1: resumen, distribución y atípicos

Enunciado: [`starter/viajes_taxi.csv`](./starter/viajes_taxi.csv) tiene 3000 viajes en taxi de Nueva York: fecha y hora de inicio, zona de origen y de destino, distancia, duración, pasajeros, método de pago, tarifa y propina. Primera mirada: qué contiene, cómo se distribuye la tarifa y qué valores están fuera de lo esperable.

**Respuesta 1, antes de ver la solución:** en `describe()`, ¿qué dos valores de la tabla te harían sospechar de un error sin necesidad de graficar nada?

El máximo de `tarifa` (999.99) y el mínimo de `duracion_min` (−74). Una tarifa de 999.99 está muy lejos del percentil 75 (32.55) y además parece un valor de relleno, y una duración negativa es imposible. También la desviación estándar de la tarifa (70.99) es mayor que su media (31.39), señal de que unos pocos valores extremos la están inflando.

**Respuesta 2:** la regla del IQR marca más de 300 viajes con tarifa atípica. ¿Esperas que todos sean errores? ¿Cómo lo averiguarías?

No. El IQR solo dice que un valor es poco común, no que esté mal. Lo averiguo mirando qué tienen en común los atípicos (`value_counts` de la tarifa, origen y destino). De los 334 atípicos, solo 15 son errores (tarifa 999.99). 302 tienen una tarifa exacta de 70 en viajes entre JFK y Manhattan, que es la tarifa fija del aeropuerto, y los 17 restantes son viajes largos y reales entre JFK y Queens/Brooklyn (19 a 24 km).

**La formulación completa, tal como la resuelvo yo:**

[`starter/EDA.py`](./starter/EDA.py) revisa tipos, faltantes y duplicados, imprime `describe()`, guarda el histograma y el boxplot de la tarifa, marca atípicos con la regla del IQR (límites −13.85 y 60.40, 334 viajes) y grafica tarifa contra distancia con y sin atípicos. Encontró dos errores confirmados: 15 tarifas de 999.99 y 10 duraciones negativas. Con los atípicos, la correlación tarifa–distancia es 0.23; al quitar solo esos errores sube a 0.96. El script corre dentro de Docker con `docker compose up --build` desde `starter/`, y las figuras quedan en `starter/data-contenedor/`.

## Durante el ConcepTest

**Tu voto, antes de discutir en pareja** (A, B, C o D):

_(tu voto)_

**Tu razonamiento:**

_(tu respuesta)_

**Después de discutir en pareja, ¿cambiaste de voto? ¿Por qué?**

_(tu respuesta)_

## Ejercicio 2: relaciones entre variables

Solo o en pareja. Parte de la plantilla [`plantilla-ejercicio2/explorar_relaciones.py`](./plantilla-ejercicio2/explorar_relaciones.py) y córrela desde su carpeta (`cd plantilla-ejercicio2`, `python3 explorar_relaciones.py`): lee el mismo `starter/viajes_taxi.csv`. Quita solo los errores que el Ejercicio 1 ya confirmó y completa los 5 `TODO`: dispersión de distancia contra tarifa, propina por método de pago, correlaciones con la tarifa, y pasajeros vacíos o en 0.

**Hallazgo 1: qué muestra el gráfico de distancia contra tarifa, además de la tendencia general.**

Además de la diagonal (correlación de 0.96), hay una línea horizontal en 70 USD: 300 viajes entre JFK y Manhattan/Harlem que pagan la tarifa fija del aeropuerto sin importar la distancia. También hay una columna vertical en distancia 0: 25 viajes que duran entre 4 y 81 minutos y cobran tarifa sin registrar kilómetros, lo que apunta a un fallo del medidor de distancia. Un modelo que solo use la distancia se equivoca en ambos grupos.

**Hallazgo 2: qué pasa con la propina según el método de pago, y si crees que describe a los pasajeros o al sistema que registra los datos.**

Los 888 viajes en efectivo tienen propina 0 (100%), mientras que con tarjeta la propina promedio es 4.73 y ningún viaje tiene propina 0. Describe al sistema, no a los pasajeros: las propinas en efectivo no se registran. Además, 60 viajes no tienen método de pago.

**Hallazgo 3: la duración tiene una correlación con la tarifa tan alta como la distancia. Si el modelo tiene que estimar la tarifa en el momento en que alguien pide el taxi, ¿puede usar la duración?**

No. Su correlación con la tarifa es 0.96, pero la duración solo se conoce al terminar el viaje. Usarla sería fuga de información: el modelo se vería muy bien en las pruebas y fallaría en producción. Lo mismo pasa con la propina (0.63). La distancia estimada de la ruta sí se puede calcular al pedir el taxi.

## Ejercicio 3: explora el dataset de tu proyecto

Usa el archivo que tu pipeline de la Semana 7 deja listo para modelar, y la plantilla [`plantilla-eda/explorar_proyecto.py`](./plantilla-eda/explorar_proyecto.py).

### Paso 1: resumen y variable objetivo (5 minutos)

Reemplaza la ruta del archivo y el nombre de la columna que tu modelo va a predecir. Corre los pasos 1 a 3.

Dataset: OBT del PSet 2 (`OBT.OBT_EMERGENCIAS_CANTON_DIA`, exportada de Snowflake), una fila por cantón y día. El modelo clasifica alta demanda a t+3 (`y_3`): `y_3 = 1` cuando `obj_n_emergencias_t3` supera el P90 del cantón para ese día de la semana, calculado solo con el periodo de entrenamiento. Como `y_3` todavía no existe en la OBT, el EDA usa `obj_n_emergencias_t3` como objetivo.

422.912 filas × 37 columnas, 224 cantones, de julio de 2021 a agosto de 2026. Los faltantes son los esperados: rezagos al inicio de cada serie (`lag_1d` 224, `lag_7d` y `media_prev_7d` 1.568, `lag_14d` 3.136, `lag_28d` y `media_prev_28d` 6.272), objetivos al final (`obj_n_emergencias_t3` 672, `obj_n_emergencias_t7` 1.568) y `nombre_feriado` en los días que no son feriado (406.784). El IQR marcó 53.357 atípicos en `obj_n_emergencias_t3`.

### Paso 2: relaciones (10 minutos)

Completa los pasos 4 y 5: la relación entre tu objetivo y la variable que esperas que más influya, y las consultas que confirman lo que encuentres.

Gráfico de dispersión de `obj_n_emergencias_t3` contra las emergencias de t y de t−4 en Quito (`plantilla-eda/figuras/quito_relacion_objetivo.png`). Contra t salen dos nubes separadas y la correlación es negativa (−0.33): t+3 cae en otro día de la semana, y el ciclo semanal invierte la relación. Contra t−4, que cae el mismo día de la semana que t+3, sale una diagonal clara (0.73). Las consultas del paso 5 confirman esto en Guayaquil (0.85) y Cuenca (0.66), y miden la escala por cantón y la tendencia anual.

### Paso 3: tres hallazgos que afectarían el modelado (10 minutos)

Para cada hallazgo, escribe qué encontraste, el número o el gráfico que lo confirma, y qué cambia en el modelo por su causa (una fila que quitas, una columna que no puedes usar, una variable que hay que transformar).

**Hallazgo 1:**

Los atípicos del IQR no son errores: los 53.357 corresponden a 76 cantones grandes que aparecen completos, con los 1.885 días cada uno (Quito, Guayaquil, Loja...). Quito y Guayaquil suman el 39,1% de las emergencias, mientras que 36 cantones tienen una mediana de 2 o menos por día. Por eso la correlación global entre `n_emergencias` y el objetivo (0.95) mide el tamaño del cantón, no la capacidad de predecir. **Cambio en el modelo:** no se quita ninguna fila. Cada cantón se compara con su propio P90, y las métricas se reportan por grupo de tamaño para que Quito y Guayaquil no dominen la evaluación.

**Hallazgo 2:**

Hay un ciclo semanal fuerte: el domingo promedia 52,6 emergencias y el martes 35,5. Por eso `n_emergencias` y `lag_7d` tienen correlación negativa con el conteo de t+3 (Quito: −0.33 y −0.37), mientras que t−4, el mismo día de la semana que t+3, tiene 0.73 en Quito, 0.85 en Guayaquil y 0.66 en Cuenca. **Cambio en el modelo:** agregar a la OBT un rezago `lag_4d` para h=3. Para h=7 sirve `n_emergencias`, porque t ya cae el mismo día de la semana que t+7.

**Hallazgo 3:**

El volumen baja con los años: de 10.342 emergencias por día en 2021 a 8.870 en 2025 (−14%). Con un P90 fijo calculado hasta junio de 2025, la tasa de `y_3 = 1` cambia según el año: 13,3% en 2021 y 5,9% en 2024. En promedio solo el 8% de los casos es clase 1. Enero de 2024 (periodo anómalo) tiene 1,4%, y un feriado en t+3 sube la tasa a 19,6% (frente a 7,6%). **Cambio en el modelo:** división temporal en lugar de aleatoria, métricas para clases desbalanceadas (precision/recall, no accuracy), evaluar un P90 móvil con ventana reciente, decidir explícitamente cómo tratar enero de 2024 y mantener `es_feriado_t3` como variable.

## Antes de la próxima sesión

**Lectura:** ["Feature Engineering that Makes Business Sense"](https://towardsdatascience.com/feature-engineering-that-makes-business-sense-419b9403236e/), Towards Data Science.

La tarifa fija de JFK y la hora del día no existen como columnas del dataset de taxis. ¿Cómo le darías esa información a un modelo?

_(tu respuesta)_
