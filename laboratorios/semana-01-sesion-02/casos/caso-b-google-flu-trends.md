# Caso B: Google Flu Trends

Los Centros para el Control y la Prevención de Enfermedades de Estados Unidos (CDC) publican cada semana qué proporción de las visitas médicas corresponden a síntomas de influenza, pero ese reporte llega con alrededor de dos semanas de retraso. En 2008, Google lanzó Google Flu Trends (GFT), un sistema que estimaba esa misma proporción a partir de lo que la gente buscaba en Google, con la promesa de anticipar los reportes de los CDC.

## Los hechos

**Cómo se construyó el modelo original.** Google evaluó alrededor de 50 millones de términos de búsqueda para encontrar los que mejor seguían a 1,152 datos históricos de los CDC. El modelo final usó 45 términos, que nunca se publicaron. En el proceso, el equipo tuvo que descartar a mano términos que coincidían con la temporada de gripe sin tener relación con ella, como búsquedas sobre baloncesto de secundaria, que también se juega en invierno.

**2009.** La primera versión de GFT no detecta la pandemia de influenza H1N1, que no siguió el patrón estacional de una gripe normal. Google actualiza el algoritmo ese mismo año.

**2011 y 2012: cambios en el buscador.** En junio de 2011, Google empieza a sugerir búsquedas relacionadas a sus usuarios. En febrero de 2012, el buscador empieza a mostrar posibles diagnósticos cuando alguien busca síntomas como "fiebre" o "tos". Solo en junio y julio de 2012, el blog del buscador reporta 86 cambios.

**Temporada 2011-2012.** GFT sobreestima la proporción real de visitas por influenza en más de 50%.

**Febrero de 2013.** La revista Nature reporta que GFT estimó más del doble de la proporción de visitas médicas por influenza que reportaron los CDC.

**De agosto de 2011 a septiembre de 2013.** GFT reporta una proporción de influenza más alta que la real en 100 de 108 semanas.

**Comparación con una alternativa simple.** Un estudio de 2010 ya había encontrado que GFT no era mucho mejor que proyectar la influenza actual con los datos de los CDC de hace dos semanas. Para 2014, incluso los datos de los CDC de hace tres semanas predecían la influenza actual mejor que GFT.

**Octubre de 2013.** Google anuncia cambios al modelo.

**Marzo de 2014.** Investigadores de Northeastern, Harvard y la Universidad de Houston publican en la revista Science el análisis "The Parable of Google Flu: Traps in Big Data Analysis".

**Agosto de 2015.** Google deja de publicar las estimaciones de GFT.

## Fuentes

- ["The Parable of Google Flu: Traps in Big Data Analysis"](https://dash.harvard.edu/server/api/core/bitstreams/7312037d-0e0d-6bd4-e053-0100007fdf3b/content), David Lazer, Ryan Kennedy, Gary King y Alessandro Vespignani, Science, 14 de marzo de 2014.
- ["When Big Isn't Better: How the Flu Bug Bit Google"](https://www.uh.edu/news-events/stories/2014/march/03132014googleflu.php), Universidad de Houston, marzo de 2014.
