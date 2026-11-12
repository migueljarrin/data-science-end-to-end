# [Nombre de tu proyecto]

> Este es el README de tu proyecto: reemplaza cada sección entre corchetes a medida que avanzas. Escríbelo para alguien que clona tu fork sin haber estado en clase y necesita entender qué hace el proyecto y correrlo, no como una nota para ti.

[Un párrafo: qué problema de negocio resuelve, para quién, y qué predice el modelo. Sale de tu propuesta del PSet 1, que está completa en `docs/`.]

**Métrica de éxito:** [la métrica de negocio y el umbral de decisión del PSet 1]

## Datos

| Fuente | Qué contiene | Cómo se obtiene | Dónde queda |
|---|---|---|---|
| [nombre de la fuente] | [qué filas y columnas trae, desde qué fecha] | [la URL, la API o el procedimiento exacto] | `data/raw/[archivo]` |

Los datos no están en el repositorio. Para regenerarlos desde cero: [los comandos, en orden]. Se completa con el PSet 1.

## Cómo correr el pipeline de datos

[Los comandos, en orden y desde qué carpeta, para ir de la fuente al warehouse: levantar la infraestructura, construir la imagen, subir el flow a Kestra, limpiar, cargar y correr dbt. Cada paso dice qué archivo deja y dónde. Se completa con el PSet 2.]

## Cómo entrenar y evaluar el modelo

[Qué notebook corre cada etapa del modelado, en qué orden, y qué necesita levantado (MLflow). Se completa con el PSet 3.]

## Modelo final

[El modelo elegido, su `run_id` en MLflow y la métrica que lo sostiene. El razonamiento completo está en `docs/decision_modelo.md`. Se completa con el PSet 3.]

## Cómo correr el servicio

El servicio (`servicio/api.py`) recibe lo que el ECU 911 sabe de un cantón al cierre del día *t* y responde la probabilidad de alta demanda en *t+3*. Calcula todas las features con las funciones de `modelado/pipeline_proyecto.py` (`rezagos_y_medias` y `calcular_features`), las mismas del entrenamiento. Por qué se sirve por lotes y no en línea está en [`docs/despliegue.md`](docs/despliegue.md); el servicio es la forma en que el lote nocturno, un tablero u otra aplicación le piden una predicción al modelo.

**1. Exportar el modelo.** Con el servidor de MLflow levantado (en el contenedor, `bash .devcontainer/mlflow-server.sh`) y la OBT en `data/raw/obt_emergencias_canton_dia.csv`, desde `psets/proyecto/`:

```
python -m servicio.exportar_modelo
```

Busca en el experimento `ecu911-alta-demanda-t3` la corrida marcada con `candidato` = `final` (hoy, el bosque con `min_samples_leaf=100`, `run_id` `a7c9689b915a4eb7ba39e5ba381ef6cb`) y deja dos archivos que no se suben al repositorio: `servicio/modelo.joblib` (el pipeline entrenado) y `servicio/referencias.joblib` (el umbral P90 de cada cantón y día de la semana, y la región de cada cantón, que el servicio necesita y la petición no trae).

**2. Construir y levantar el contenedor**, desde `psets/proyecto/` (la imagen necesita `modelado/` además de `servicio/`):

```
docker build -f servicio/Dockerfile -t servicio-ecu911 .
docker run -p 8000:8000 servicio-ecu911
```

Sin Docker: `uvicorn servicio.api:app --port 8000`. La documentación interactiva queda en `http://localhost:8000/docs`, y `/salud` dice si el modelo está cargado y qué `run_id` tiene.

**3. Pedir una predicción.** El cuerpo trae el cantón, el día *t*, las emergencias de los 29 días de *t−28* a *t* (la última es la del día *t*), los conteos por servicio del día *t* y los feriados entre *t* y *t+4*. Quito al cierre del 29 de diciembre de 2025:

```
curl -X POST localhost:8000/predecir -H "Content-Type: application/json" -d '{"cod_canton": "1701", "fecha": "2025-12-29", "emergencias": [1824, 1730, 2006, 2365, 2626, 2686, 2309, 1670, 1681, 1626, 1872, 1979, 2414, 2350, 1694, 1782, 2003, 1957, 2336, 2725, 2519, 1855, 1910, 1916, 1809, 1810, 2069, 2143, 1723], "n_seguridad_ciudadana": 1206, "n_gestion_sanitaria": 187, "n_transito_movilidad": 155, "feriados": ["2026-01-01", "2026-01-02"]}'
```

```
{"cod_canton":"1701","fecha_objetivo":"2026-01-01","probabilidad_alta_demanda":0.8337,"alerta":true,"run_id":"a7c9689b915a4eb7ba39e5ba381ef6cb"}
```

`alerta` es `true` cuando la probabilidad alcanza 0.66, el umbral que minimizó el costo en la validación temporal (un día de alta demanda sin detectar cuesta 5, una falsa alarma 1). Si la historia no trae 29 días, la respuesta es 422; si el cantón no existe, 404. Las pruebas están en `servicio/test_api.py` y corren con `pytest psets/proyecto`, también en GitHub Actions.
