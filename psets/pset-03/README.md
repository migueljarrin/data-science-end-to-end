# PSet 3: Exploración, features y modelo del proyecto

**Asignado:** Semana 8, Sesión 2. **Vence:** Semana 12, Sesión 1.

Del archivo limpio que deja tu pipeline (PSet 2) a un modelo elegido con evidencia: qué encontraste al explorar los datos, qué features construiste a partir de eso, la preparación convertida en un script que tus modelos importan, los candidatos entrenados y comparados con la misma división, cada corrida registrada en MLflow, la validación que corresponde a tus datos y una decisión escrita que alguien más puede verificar. Cada pieza sale del Ejercicio 3 de una sesión de las Semanas 8 a 11.

## Paso 0: ordena tu proyecto en `psets/proyecto/`

Antes de entregar, mueve lo que construiste en las semanas anteriores a la estructura de [`psets/proyecto/`](../proyecto/) que describe [`psets/README.md`](../README.md). Este PSet se califica sobre esa estructura, y la Semana 12 empaqueta tu modelo como un servicio que la necesita en un solo lugar.

Mueve cada archivo con `git mv`, no copiándolo: así git conserva su historia y el archivo no queda duplicado en dos carpetas.

```
git mv laboratorios/semana-09-sesion-02/plantilla-pipeline/pipeline_proyecto.py psets/proyecto/modelado/
```

| Lo que tienes | A dónde va |
|---|---|
| Tu Dockerfile y tu `requirements.txt` (Semana 3, Sesión 1) | `proyecto/`, en la raíz |
| Tu script de ingesta | `proyecto/ingesta/` |
| Tu `docker-compose.yml` o `main.tf` | `proyecto/infra/` |
| `flow_proyecto.yml` | `proyecto/orquestacion/` |
| Tu notebook de diagnóstico y tu script de limpieza | `proyecto/calidad/` |
| Tu `construir_warehouse.py` y tu proyecto de dbt | `proyecto/warehouse/` y `proyecto/warehouse/dbt/` |
| Tu job de Spark, y tu productor y consumidor si los tienes | `proyecto/procesamiento/` |
| Tus notebooks de exploración, features, modelos y experimentos, `pipeline_proyecto.py` y sus tablas `.csv` | `proyecto/modelado/` |
| Tu canvas, tu propuesta y tu presentación (PSet 1) | `proyecto/docs/` |
| Tus archivos de datos | `proyecto/data/raw/` (crudos) y `proyecto/data/processed/` (limpios) |

Después de mover, actualiza las rutas que cambiaron. Las que más se rompen son la ruta a los datos (desde `modelado/` es `../data/processed/<archivo>`), los `COPY` del Dockerfile (ahora los scripts están en subcarpetas, como `ingesta/`), la ruta al `.duckdb` en el `profiles.yml` de dbt y el comando del flow de Kestra si cambió la ruta del script dentro de la imagen. Comprueba que `python pipeline_proyecto.py` corre desde `modelado/` y que `docker build -t <tu-imagen> .` corre desde `proyecto/`.

## Entregables

Todo en [`../proyecto/modelado/`](../proyecto/modelado/), sobre el archivo limpio de `data/processed/`, salvo la decisión, que va en `docs/`:

| Pieza | Archivo | Sale de |
|---|---|---|
| La exploración, con tres hallazgos que afectan el modelado | `explorar_proyecto.ipynb` | Semana 8, Sesión 2 |
| Dos features, con su evidencia y su justificación | `features_proyecto.ipynb` | Semana 9, Sesión 1 |
| La preparación y la división, como script | `pipeline_proyecto.py` | Semana 9, Sesión 2 |
| Línea base, modelo lineal y ensamblaje, con su tabla | `modelos_proyecto.ipynb` y `resultados_proyecto.csv` | Semana 10, Sesión 1 |
| Ensamblaje contra red neuronal, y la prueba del LLM | `comparar_proyecto.ipynb` | Semana 10, Sesión 2 |
| Cada modelo registrado en MLflow, y el modelo final recuperado del registro | `experimentos_proyecto.ipynb` y `corridas_proyecto.csv` | Semana 11, Sesión 1 |
| Validación cruzada con el esquema de tus datos, y la métrica del negocio | `validacion_proyecto.ipynb` | Semana 11, Sesión 2 |
| La decisión del modelo final | `proyecto/docs/decision_modelo.md` | Semanas 10 y 11 |

`corridas_proyecto.csv` es la evidencia del registro: tu servidor de MLflow vive en tu Codespace y yo no lo veo, así que la tabla exportada tiene que salir de una corrida completa del notebook (borra antes las corridas de prueba del experimento).

### `docs/decision_modelo.md`

Una a dos páginas, escritas para alguien del equipo que no estuvo en clase y tiene que decidir si ese modelo pasa a producción:

1. Qué modelo elegiste, con su `run_id` en MLflow.
2. Contra qué lo comparaste: la línea base y los demás candidatos, con la métrica de prueba de cada uno, la misma división y la misma huella de datos.
3. Si la diferencia con el segundo mejor es real: el promedio y la desviación de la validación cruzada, con el esquema que corresponde a tus datos.
4. Qué error es más caro en tu proyecto, cuánto, y qué dice la métrica del negocio del modelo elegido.
5. Costo y explicabilidad: segundos de entrenamiento, y si alguien puede entender por qué el modelo predice lo que predice.
6. Qué necesita otra persona para obtener exactamente el mismo número, y qué de eso quedó registrado en MLflow.

En `proyecto/README.md`, completa **Cómo entrenar y evaluar el modelo** (qué archivo lee `pipeline_proyecto.py`, cómo divide los datos, y qué notebook corre cada etapa y en qué orden) y **Modelo final** (el modelo, su `run_id` y la métrica que lo sostiene).

## Lo que reviso

Que cada decisión tenga detrás un número o un gráfico de tu propio dataset o de tu registro. Un hallazgo de la exploración vale cuando dice qué cambia en el modelo por su causa; una feature vale cuando muestra su evidencia y existe en el momento en que el modelo va a predecir; un modelo vale contra una línea base, con la misma división y la misma métrica que los demás.

`pipeline_proyecto.py` tiene que correr solo desde una terminal nueva, y todos los notebooks de modelos lo importan en vez de copiar su código. Los notebooks se califican con la salida guardada de una corrida completa (**Restart** y **Run All**).

## Cómo se evalúa

La rúbrica, con sus cinco criterios y niveles, está en [`rubrica.md`](./rubrica.md). Para entregar, sigue la sección "Cómo entregar" de [`psets/README.md`](../README.md): el tag de este PSet es `pset-03`.
