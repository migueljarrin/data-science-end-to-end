# Fundamentos de Ciencia de Datos

Repositorio base del curso.

Aquí viven los laboratorios y los PSets, construidos en torno a un único proyecto de ciencia de datos que cada estudiante define y lleva a cabo de principio a fin durante la clase. Es la fuente de la verdad: todo tu trabajo del semestre va aquí, no en otro lado.

## Antes de empezar

No clones ni hagas push a este repositorio directamente. Cada estudiante trabaja en su propio fork:

1. Arriba a la derecha, haz clic en **"Fork"** y créalo en tu propia cuenta de GitHub.
2. Todo tu trabajo del semestre (laboratorios, PSets) va en tu fork, no aquí.

## Tu ambiente de desarrollo

Las primeras dos semanas del curso son de formulación y diseño del proyecto: no requieren código. Desde la Semana 3, cada laboratorio usa herramientas que se instalan una sola vez: Python, Docker, Terraform, Java (para Spark), DuckDB, dbt y las librerías fijadas en [`requirements.txt`](./requirements.txt). Tienes dos opciones, y las dos llegan exactamente al mismo ambiente.

### Opción A (recomendada): GitHub Codespaces

Un Codespace es una máquina en la nube con VS Code en el navegador, ya configurada con todo lo del curso. No instalas nada en tu laptop, y funciona igual en Windows, Mac o Linux.

1. Activa [GitHub Education](https://education.github.com/pack) con tu correo de la universidad. Es gratis y sube tu cuota mensual de Codespaces.
2. En la página de tu fork, haz clic en **"Code" → pestaña "Codespaces" → "Create codespace on master"**.
3. La primera vez tarda varios minutos: instala todo y al final corre una verificación ([`.devcontainer/verificar.sh`](./.devcontainer/verificar.sh)). Cuando la terminal muestre `Ambiente listo.`, ya puedes trabajar. Si algo deja de funcionar más adelante, vuelve a correr `bash .devcontainer/verificar.sh` para ver qué herramienta falla. Las siguientes veces abre el mismo Codespace desde [github.com/codespaces](https://github.com/codespaces), no crees uno nuevo.

Cinco reglas para no quedarte sin cuota ni perder trabajo:

- **Detén el Codespace al terminar** (desde [github.com/codespaces](https://github.com/codespaces), menú "..." → "Stop codespace"). Se apaga solo después de 30 minutos sin actividad, pero consume cuota hasta entonces. La cuota gratuita equivale a unas 60 horas al mes en una máquina de 2 núcleos (unas 90 con GitHub Education): alcanza para el curso solo si lo apagas.
- **Haz commit y push seguido.** Un Codespace sin usar durante 30 días se borra con todo lo que no hayas subido a tu fork.
- **Tus datos no se suben a git** (`data/raw/` y `data/processed/` están en `.gitignore`). Guarda la fuente original de tu dataset fuera del Codespace (el enlace de descarga, o una copia en tu Drive), para poder volver a traerlo si el Codespace se borra.
- **Usa una máquina de 4 núcleos solo cuando el laboratorio lo pida.** Kestra (Semana 4, Sesión 1) y el laboratorio integrador (Semana 7, Sesión 1) levantan varios servicios a la vez; ahí cambia el tipo de máquina ("Change machine type"). El resto del curso funciona con 2 núcleos, que gasta la mitad de la cuota.
- **Las interfaces web no se abren en el `localhost` de tu navegador.** pgAdmin (puerto 8085) y Kestra (puerto 8080) corren dentro del Codespace: ábrelas desde la pestaña **Ports** de VS Code, con el ícono del globo junto al puerto.

### Opción B: tu propia laptop

Instala [Docker Desktop](https://www.docker.com/products/docker-desktop/), [Terraform](https://developer.hashicorp.com/terraform/install), Java 17 y Python 3.11, y después, desde la raíz de tu fork:

```
pip install -r requirements.txt
```

Si ya tienes Docker Desktop y VS Code con la extensión Dev Containers, hay un atajo: abre tu fork en VS Code y elige "Reopen in Container". Usa la misma configuración del Codespace, pero corriendo en tu máquina.

### El Codespace es un contenedor, y no reemplaza al de tu proyecto

El Codespace trae las herramientas del curso, iguales para todos. Tu proyecto, en cambio, se empaqueta en su propia imagen de Docker (Semana 3, Sesión 1), con solo lo que necesita para correr en cualquier máquina. Son dos cosas distintas, y el curso necesita las dos.

## Estructura del repositorio

```
.devcontainer/          Configuración del Codespace (no la modifiques)
requirements.txt        Librerías de Python del curso, con versión fija
laboratorios/           Laboratorio de cada clase, uno por carpeta
  semana-01-sesion-02/
  semana-02-sesion-01/
  semana-02-sesion-02/
  semana-03-sesion-01/
  semana-03-sesion-02/
  ...
psets/                  Tus entregas de PSet, una carpeta por PSet
  pset-01/
  ...
```

Cada carpeta de `laboratorios/` y `psets/` tiene su propio `README.md` con las instrucciones de esa entrega.

## Cómo actualizar tu fork cada semana

Cuando se agregue una semana nueva, sincroniza tu fork:

1. En la página de tu fork en GitHub, haz clic en el botón **"Sync fork" → "Update branch"**.
2. En tu copia local o en tu Codespace, ejecuta `git pull` para obtener esos cambios.
3. Si el cambio tocó `requirements.txt`, corre `pip install -r requirements.txt`. Si tocó `.devcontainer/`, reconstruye el contenedor: en VS Code, `Ctrl+Shift+P` (`Cmd+Shift+P` en Mac) → "Codespaces: Rebuild Container" (o "Dev Containers: Rebuild Container" en tu laptop).

Por terminal, en vez del botón:
```
git fetch upstream
git merge upstream/master
```
(la primera vez, agrega el remoto: `git remote add upstream https://github.com/ErickNaunay/fundamentos-ciencia-datos.git`)

## Cómo trabajar aquí

- Haz commits de tu avance de forma continua, con mensajes que indiquen qué hiciste, no `"cambios"` ni `"fix"`.
- Cada entrega (laboratorio, PSet) tiene su propia carpeta con su propio `README.md`: revísalo antes de empezar.
