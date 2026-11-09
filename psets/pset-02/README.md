# PSet 2: Pipeline de datos del proyecto

**Asignado:** Semana 4, Sesión 1. **Vence:** Semana 7, Sesión 2.

El pipeline de datos de tu proyecto, corriendo de principio a fin: la ingesta que contenerizaste en el PSet 1, orquestada, con la calidad de los datos resuelta, cargada a un warehouse y modelada en capas. Cada pieza la construiste en el Ejercicio 3 de una sesión de las Semanas 4 a 6, y el Laboratorio Integrador (Semana 7, Sesión 1) las conecta. Lo que se califica es que la cadena funcione completa: que cada etapa entregue exactamente el archivo o la tabla que la siguiente lee.

## Entregables

Todo en [`../proyecto/`](../proyecto/), en estas carpetas:

| Pieza | Dónde | Sale de |
|---|---|---|
| El flow de Kestra, con reintento y horario | `orquestacion/flow_proyecto.yml` | Semana 4, Sesión 1 |
| El diagnóstico de calidad | `calidad/diagnostico_proyecto.ipynb` | Semana 4, Sesión 2 |
| La limpieza, como script | `calidad/limpiar.py` | Semana 7, Sesión 1 |
| La carga a DuckDB | `warehouse/construir_warehouse.py` | Semana 5, Sesión 1 |
| El modelado en capas | `warehouse/dbt/` | Semana 5, Sesión 2 |
| El job de Spark sobre el histórico | `procesamiento/job_spark.py` | Semana 6, Sesión 1 |
| Streaming, si tu proyecto lo justifica | `procesamiento/productor.py` y `procesamiento/consumidor.py` | Semana 6, Sesión 2 |

Si corregiste el `Dockerfile`, la ingesta o la infraestructura del PSet 1 para que la cadena funcione, esos cambios también entran: el pipeline corre sobre la versión actual.

En `proyecto/README.md`, completa la sección **Cómo correr el pipeline de datos**: los comandos, en orden y desde qué carpeta, para ir de la fuente al warehouse. Al final de esa sección, un párrafo que diga si tu proyecto necesita streaming o le alcanza con batch, con el criterio de la Semana 6, Sesión 2: ¿la decisión que habilita tu proyecto pierde valor con datos de horas o días de antigüedad?

## Lo que reviso

Sigo tu `README.md` desde un Codespace nuevo, comando por comando. Si un paso necesita algo que no está escrito (una carpeta que hay que crear a mano, una variable que solo existe en tu máquina, un archivo que no está en el repositorio ni dice cómo obtenerlo), la cadena se corta ahí.

Los mismos cruces de la checklist del integrador: el flow corre el tag actual de tu imagen; `limpiar.py` corre sobre el histórico que acumuló tu pipeline, no sobre un archivo de ejemplo; el warehouse carga el archivo limpio y su cuenta de filas coincide con la del archivo; `dbt run` y `dbt test` usan el mismo `.duckdb` que construyó la carga; y el resultado de Spark coincide con el de dbt o pandas sobre el mismo dato.

## Cómo se evalúa

La rúbrica, con sus cuatro criterios y niveles, está en [`rubrica.md`](./rubrica.md). Para entregar, sigue la sección "Cómo entregar" de [`psets/README.md`](../README.md): el tag de este PSet es `pset-02`.
