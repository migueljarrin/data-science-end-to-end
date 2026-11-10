# Despliegue: predicción por lotes, una vez al día

El modelo de alta demanda de emergencias del ECU 911 se sirve **por lotes**: cada noche, después del cierre del día *t*, un proceso calcula la probabilidad de alta demanda en *t+3* para los 224 cantones y deja una tabla que el equipo de planificación lee por la mañana. No hace falta un servicio en línea.

## Qué decisión habilita, quién la usa y cuánto puede esperar

La predicción sirve para **planificar los turnos con tres días de anticipación**: si un cantón va a tener un día de alta demanda (más emergencias que su percentil 90 para ese día de la semana), el ECU 911 refuerza el turno de operadores y de unidades de respuesta de ese día. La usa el equipo de planificación de turnos, no un sistema automático ni un ciudadano.

La decisión se toma una vez al día, sobre un día que está tres días adelante. La predicción puede tardar **horas**: basta con que la tabla esté lista antes de que empiece la jornada de planificación, por ejemplo a las 06:00 de *t+1*. Entre el cierre del día *t* (medianoche) y las 06:00 hay unas 6 horas de margen, y cada predicción sigue siendo útil hasta el momento en que hay que confirmar el turno de *t+3*. Responder en milisegundos no cambia ninguna decisión.

## Cuántos casos hay y si se conocen de antemano

Son **224 predicciones por día**: una por cantón (incluidas las tres zonas no delimitadas). La lista de cantones es fija y se conoce de antemano. No hay casos nuevos que aparezcan durante el día: el lote de mañana es el mismo conjunto de 224 cantones, con las features del día que acaba de cerrar. Al mes son unas 6720 predicciones, que el bosque calcula en segundos.

## Qué datos necesitan las features y si están disponibles

Las features de `modelado/pipeline_proyecto.py` usan:

- **Conteos hasta el día *t*:** `n_emergencias` y los conteos por servicio, los rezagos (`lag_1d` a `lag_28d`), las medias de 7 y 28 días y `nivel_vs_umbral_t3`, que promedia los días *t−4*, *t−11*, *t−18* y *t−25*. Existen recién **después de que el día *t* cierra**. Esto es justo lo que encaja con un lote nocturno: el conteo del día está completo a medianoche, no antes.
- **El calendario:** día de la semana, mes, fin de semana y feriados de *t+2* a *t+4* (`momento_feriado_t3`). Se conoce con anticipación.
- **El umbral `p90_t3` por cantón y día de la semana:** sale del periodo de entrenamiento y queda fijo, guardado con el modelo.

Una limitación: hoy los datos vienen del portal público del ECU 911, que publica **un archivo por mes**, con retraso. Para usar el modelo en operación, el lote nocturno necesita los conteos del día anterior directamente del ECU 911. Esa integración no está hecha (ver la sección de limitaciones del PSet 2).

## Qué se pierde con el patrón descartado

Un servicio **en línea** respondería en el momento a quien pregunte por un cantón. Para este caso no aporta nada y cuesta más:

- Las features dependen del día completo: a mitad del día, `n_emergencias` estaría incompleto y la predicción sería peor, no mejor.
- Las 224 predicciones son siempre las mismas preguntas: calcularlas una vez por noche es más barato que tener un servidor encendido las 24 horas para responder unas 224 consultas al día.
- La decisión (el turno de *t+3*) no cambia por tener la respuesta en milisegundos en vez de en horas.

Lo que sí se pierde con el lote es **la reacción durante el día**: si a mediodía empieza una emergencia grande (un deslave, un accidente múltiple), la tabla de esa noche no lo refleja hasta el siguiente lote. Detectar picos dentro de la jornada sería otro problema: un modelo distinto, con datos por hora o en streaming, como se describe en la sección "Batch vs. streaming" del PSet 2. Para planificar turnos a tres días, el lote nocturno alcanza.
