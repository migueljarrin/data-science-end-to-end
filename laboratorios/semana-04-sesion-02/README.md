# Semana 4, Sesión 2: Calidad de datos, diagnóstico y limpieza de los datos

> Objetivo de la sesión: diagnosticar problemas de calidad en el dataset de tu proyecto (duplicados, valores faltantes, inconsistencias de esquema) y justificar qué estrategia de limpieza aplica a cada uno.

**Lectura previa de esta sesión:** ["An Introduction to Data Quality"](https://medium.com/towards-data-science/an-introduction-to-data-quality-951cc6fe0274), Towards Data Science / Medium.

**Referencia de esta sesión:** *Designing Machine Learning Systems*, Cap. 3, Data Engineering Fundamentals (Chip Huyen).

## Requisitos antes de esta sesión

Confirma que tienes pandas (ya viene en el Codespace; en tu laptop, `pip install -r requirements.txt` desde la raíz del repositorio) y acceso al dataset real de tu proyecto, aunque sea en una versión parcial o de muestra.

## Antes de empezar

A partir de la lectura previa:

**Según el artículo, ¿por qué un modelo puede entrenar sin ningún error y producir métricas razonables, aunque los datos de entrada tengan problemas serios de calidad?**

_(tu respuesta)_

**El artículo distingue varias dimensiones de calidad de datos. ¿Cuál te parece más difícil de detectar solo con un vistazo rápido al dataset, sin código?**

_(tu respuesta)_

## Pregunta de apertura

Tu modelo entrena sin ningún error, y las métricas se ven razonables. ¿Eso significa que los datos de entrada estaban bien?

_(tu respuesta)_

## Ejercicio 1: diagnóstico completo de un archivo de sensores

Archivo: [`starter/ejercicio1_diagnostico.py`](./starter/ejercicio1_diagnostico.py), sobre [`starter/lecturas_sensores.csv`](./starter/lecturas_sensores.csv). El script ya lee el archivo, imprime cada paso y guarda el resultado; faltan las líneas que hacen el diagnóstico, marcadas como `TODO 1` a `TODO 4`. Córrelo una vez antes de tocar nada:

```
cd laboratorios/semana-04-sesion-02/starter
python3 ejercicio1_diagnostico.py
```

**Respuesta 1 (TODO 1), antes de ver la solución:** sin el TODO 1, el script dice que quedan 10 filas. Mirando el CSV, ¿cuántas esperas que queden después de quitar las filas repetidas, y con qué método de pandas las contarías antes de quitarlas?

_(tu respuesta)_

**Respuesta 2 (TODO 2 y 3):** `isna()` va a contar 1 temperatura faltante. ¿Cuántas esperas después de convertir `temperatura` a número con `errors="coerce"`, y de dónde sale la diferencia?

_(tu respuesta)_

**Respuesta 3 (TODO 4):** sin el TODO 4, el script convierte las fechas con `pd.to_datetime` sin indicar formato. ¿Qué fecha le asignó a S3 (`01/02/2026`) y a S8 (`03/02/2026`)? ¿Apareció algún error?

_(tu respuesta)_

**Lo que confirmó la salida, TODO por TODO:**

_(anota los números que no esperabas)_

## Durante el ConcepTest

**Tu voto, antes de discutir en pareja** (A, B, C o D):

_(tu voto)_

**Tu razonamiento:**

_(tu respuesta)_

**Después de discutir en pareja, ¿cambiaste de voto? ¿Por qué?**

_(tu respuesta)_

## Ejercicio 2: pedidos de una tienda

Solo o en pareja. Archivo: [`starter/ejercicio2_pedidos.py`](./starter/ejercicio2_pedidos.py), sobre [`starter/pedidos_tienda.csv`](./starter/pedidos_tienda.csv). Son los mismos pasos del Ejercicio 1 sobre otro archivo, más uno nuevo (TODO 5). Al final, el script imprime una comprobación por TODO: completa los 5 hasta que todas digan `OK`.

```
python3 ejercicio2_pedidos.py
```

**Respuesta 1:** la columna `monto` usa dos marcadores distintos para un dato que no existe. ¿Cuáles son, y cuántos de ellos contó `isna()` antes de convertir?

_(tu respuesta)_

**Respuesta 2:** después de quitar los duplicados, el TODO 5 encuentra un `pedido_id` que todavía aparece dos veces. ¿Por qué `duplicated()` no lo marcó? ¿Qué necesitarías saber del negocio para decidir cuál de las dos filas conservar?

_(tu respuesta)_

**Si terminas antes:** `cantidad` también tiene faltantes, pero `dtypes` la muestra como `float64` aunque todas sus cantidades son enteras. ¿Por qué?

_(tu respuesta)_

## Ejercicio 3: diagnóstico del dataset de tu proyecto

Corre sobre tu propio dataset las mismas verificaciones de los Ejercicios 1 y 2 (`duplicated()`, `isna()`, `dtypes`, conversión con `errors="coerce"`, revisión manual de formatos mezclados), y documenta lo que encuentres en la plantilla [`plantilla-diagnostico/diagnostico.md`](./plantilla-diagnostico/diagnostico.md).

El resultado de hoy es el diagnóstico documentado y justificado, no todavía la limpieza completa implementada: antes de corregir hay que entender qué se está corrigiendo y por qué, como muestra el ConcepTest de esta sesión.

### Paso 1: corre las verificaciones (10 minutos)

Adapta el código de los Ejercicios 1 y 2 a las columnas reales de tu dataset.

_(qué verificaciones corriste)_

### Paso 2: revisa manualmente lo que el código no captura solo (5 minutos)

Duplicados, faltantes y tipos se detectan con código; los formatos mezclados (fechas, categorías escritas de más de una forma, unidades distintas) muchas veces requieren mirar valores únicos de una columna (`datos["columna"].unique()`) para notarlos.

_(qué encontraste al revisar manualmente)_

### Paso 3: completa la plantilla de diagnóstico (5 minutos)

Para cada problema encontrado, documenta la estrategia que aplicarías y por qué, no solo que el problema existe.

_(tu plantilla completa, o un resumen si la completaste aparte)_

## Antes de la próxima sesión

Ya diagnosticaste los problemas de calidad de tu dataset.

Pregunta: ¿cómo decides, con evidencia y no solo con intuición, qué variables de ese dataset ayudan a predecir lo que tu proyecto necesita predecir, y cuáles solo parecen ayudar?

_(tu respuesta)_
