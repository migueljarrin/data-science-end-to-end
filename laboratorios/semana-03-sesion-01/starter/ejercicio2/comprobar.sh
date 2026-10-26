#!/usr/bin/env bash
# Comprobacion del Ejercicio 2. Correla desde esta carpeta, despues de
# construir y correr tu imagen: bash comprobar.sh
# No la modifiques.

comprobar() {
    if [ "$2" = "si" ]; then
        echo "TODO $1: OK"
    else
        echo "TODO $1: revisa"
    fi
}

linea() {
    grep -n -E "$1" Dockerfile | head -1 | cut -d: -f1
}

desde=$(grep -q -E "^FROM python:3\.11" Dockerfile && echo si)
comprobar 1 "$desde"

req=$(linea "^COPY requirements\.txt")
pip=$(linea "^RUN pip install")
codigo=$(linea "^COPY (\.|.*\.py)")
orden=""
if [ -n "$req" ] && [ -n "$pip" ] && [ -n "$codigo" ] && [ "$req" -lt "$pip" ] && [ "$pip" -lt "$codigo" ]; then
    orden=si
fi
comprobar 2 "$orden"

cmd=$(grep -q -E "^CMD.*resumir_clientes\.py" Dockerfile && echo si)
comprobar 3 "$cmd"

resumen=$([ -f datos/clientes_por_ciudad.csv ] && echo si)
comprobar 4 "$resumen"

conteo=$([ -f datos/conteo.txt ] && echo si)
comprobar 5 "$conteo"
