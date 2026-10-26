# Semana 1, Sesión 2: Ciclo de vida de un proyecto de ciencia de datos

> Objetivo: describir las fases del ciclo de vida de un sistema de ciencia de datos y ubicar, en un caso real, en qué fase se originó una falla del proyecto.

**Lectura previa de esta sesión:** ["Machine Learning vs Traditional Software Development"](https://billcrichmond.medium.com/machine-learning-vs-traditional-software-development-96923dc5ffbc), Bill Richmond.

**Referencia de esta sesión:** Designing Machine Learning Systems, Capítulo 1: Overview of Machine Learning Systems (Chip Huyen).

## Antes de empezar

Lectura:

**Según el artículo, ¿en qué se diferencia construir un sistema de machine learning de construir software tradicional?**

_(tu respuesta)_

**¿Qué fase necesita un proyecto de machine learning que no existiría si el mismo sistema se construyera con reglas escritas a mano?**

_(tu respuesta)_

## Las siete fases del ciclo de vida

Anota, en una frase, qué implica cada fase mientras se explica:

1. Formular el problema: _(tu respuesta)_
2. Conseguir y preparar los datos: _(tu respuesta)_
3. Construir features: _(tu respuesta)_
4. Desarrollar y evaluar el modelo: _(tu respuesta)_
5. Desplegar: _(tu respuesta)_
6. Monitorear: _(tu respuesta)_
7. Comunicar: _(tu respuesta)_

**¿Qué significa que el ciclo sea iterativo? Da un ejemplo de una fase que regresa a otra.**

_(tu respuesta)_

## Ejercicio 1: un filtro de spam

Enunciado: un servicio de correo quiere construir un filtro de spam.

**Respuesta 1, antes de ver la solución:** ¿qué datos necesita este proyecto, y de dónde sale la etiqueta "spam" o "no spam" de cada correo?

_(tu respuesta)_

**Respuesta 2:** de las siete fases, ¿cuál crees que es la más fácil de subestimar en este proyecto? ¿Por qué?

_(tu respuesta)_

**Las siete fases, tal como las resuelvo yo:**

_(anota aquí qué implica cada fase para el filtro de spam, mientras se revisan en clase)_

## Ejercicio 2: Zillow Offers

Enunciado: Zillow, la plataforma inmobiliaria más grande de Estados Unidos, operó Zillow Offers, un negocio en el que un algoritmo compraba casas directamente a sus dueños, a un precio calculado por el propio modelo, para revenderlas después con margen. El 2 de noviembre de 2021, Zillow anunció el cierre total del negocio: una pérdida de 304 millones de dólares en un solo trimestre, 9,680 casas compradas en ese trimestre que ya no podía revender al precio esperado, y el despido de 2,000 empleados.

**Respuesta 1, antes de ver la solución:** el modelo funcionó lo suficientemente bien como para escalar el negocio a miles de compras antes de fallar. ¿Qué te dice eso sobre si la falla estuvo en la fase de desarrollo del modelo?

_(tu respuesta)_

**Respuesta 2:** ¿en qué fase ubicas el origen de la falla? Nombra el hecho del caso que sostiene tu respuesta.

_(tu respuesta)_

**El recorrido completo, tal como lo resuelvo yo:**

_(anota aquí qué hizo Zillow en cada fase y en cuál se originó la falla, mientras se revisa en clase)_

## Durante el ConcepTest

**Tu voto** (A, B, C o D):

_(tu voto)_

**Tu razonamiento:**

_(tu respuesta)_

**Después de discutir en pareja, ¿cambiaste de voto? ¿Por qué?**

_(tu respuesta)_

## Ejercicio 3: mapear un caso al ciclo de vida

En pareja. Cada pareja recibe uno de estos tres casos:

- [Caso A: la herramienta de reclutamiento de Amazon](./casos/caso-a-amazon-reclutamiento.md)
- [Caso B: Google Flu Trends](./casos/caso-b-google-flu-trends.md)
- [Caso C: el modelo de sepsis de Epic](./casos/caso-c-epic-sepsis.md)

Copia [`mapa-ciclo-de-vida.md`](./mapa-ciclo-de-vida.md) en esta misma carpeta con el nombre `mapa-<tu-nombre>.md` y llénalo con tu pareja a partir de los hechos del caso. Cada uno sube su propio archivo a su fork.

El criterio es el mismo de la diapositiva 12: ubicar un evento en una fase exige señalar el hecho del caso que lo sostiene (una fecha, una cifra, una decisión documentada). Si no hay un hecho que lo sostenga, escríbelo como hipótesis, no como mapeo.

## Antes de la próxima sesión

Pregunta: si la falla de Zillow estuvo en cómo se vigiló el problema de negocio y no en el modelo en sí, ¿qué tendría que haber estado definido desde el principio del proyecto para detectar el problema antes de que costara 304 millones de dólares?

_(tu respuesta)_
