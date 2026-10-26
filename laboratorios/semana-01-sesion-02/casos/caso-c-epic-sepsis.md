# Caso C: el modelo de sepsis de Epic

La sepsis es una respuesta extrema del cuerpo a una infección, y es una de las principales causas de muerte en hospitales: cada hora de retraso en el tratamiento empeora el pronóstico. Epic, la empresa que vende el sistema de historia clínica electrónica que usan muchos hospitales de Estados Unidos, desarrolló el Epic Sepsis Model, un modelo que calcula de forma periódica un puntaje de riesgo de sepsis para cada paciente hospitalizado y genera una alerta cuando ese puntaje supera un umbral.

Para leer el caso necesitas una sola métrica, el AUC: mide qué tan bien un modelo ordena a los pacientes de mayor a menor riesgo. Un AUC de 1.0 es un modelo perfecto; un AUC de 0.5 equivale a ordenarlos al azar, lanzando una moneda.

## Los hechos

**El modelo.** Es un modelo propietario: los hospitales que lo usan lo reciben como parte del sistema de Epic, sin acceso completo a cómo se construyó. Fue implementado en cientos de hospitales de Estados Unidos.

**El desempeño reportado.** Epic y University of Colorado Health reportaron un AUC entre 0.76 y 0.83.

**La validación externa.** Investigadores de Michigan Medicine, el sistema hospitalario de la Universidad de Michigan, evaluaron de forma retrospectiva sus puntajes en 38,455 hospitalizaciones entre diciembre de 2018 y octubre de 2019.

**Lo que encontraron.** El AUC fue 0.63. El modelo no detectó al 67% de los pacientes que sí tuvieron sepsis (una sensibilidad de 33%). Al mismo tiempo, generó alertas para el 18% de todos los pacientes hospitalizados, con o sin sepsis.

**21 de junio de 2021.** El estudio se publica en la revista JAMA Internal Medicine, junto con un editorial que cuestiona el uso de modelos propietarios en hospitales sin una validación independiente.

## Fuentes

- ["External Validation of a Widely Implemented Proprietary Sepsis Prediction Model in Hospitalized Patients"](https://jamanetwork.com/journals/jamainternalmedicine/fullarticle/2781307), Andrew Wong y otros, JAMA Internal Medicine, 21 de junio de 2021.
- ["Popular sepsis prediction tool less accurate than claimed"](https://ihpi.umich.edu/news/popular-sepsis-prediction-tool-less-accurate-claimed), Instituto de Políticas e Innovación en Salud de la Universidad de Michigan, 2021.
- [Editorial del mismo número](https://jamanetwork.com/journals/jamainternalmedicine/fullarticle/2781313), Anand R. Habib, Anthony L. Lin y Richard W. Grant, JAMA Internal Medicine, 2021.
