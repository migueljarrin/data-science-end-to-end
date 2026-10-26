#!/usr/bin/env bash
# Sube a Kestra un flow y los scripts que necesita, como archivos de su
# namespace. Si el flow ya existe, lo actualiza.
#
# Uso, desde la carpeta del ejercicio:
#     bash ../subir_a_kestra.sh <flow.yml> <script.py> [otro.py ...]
#
# No lo modifiques.

set -e
KESTRA=${KESTRA:-http://localhost:8080/api/v1/main}
USUARIO=admin@kestra.io:Admin1234

flow=$1
shift
id=$(grep -E '^id:' "$flow" | awk '{print $2}')
namespace=$(grep -E '^namespace:' "$flow" | awk '{print $2}')

for archivo in "$@"; do
    curl -sf -u "$USUARIO" -X POST "$KESTRA/namespaces/$namespace/files?path=/$(basename "$archivo")" \
        -F "fileContent=@$archivo" > /dev/null
    echo "Archivo $archivo subido al namespace $namespace"
done

if curl -sf -u "$USUARIO" "$KESTRA/flows/$namespace/$id" > /dev/null; then
    curl -sf -u "$USUARIO" -X PUT -H "Content-Type: application/x-yaml" \
        --data-binary @"$flow" "$KESTRA/flows/$namespace/$id" > /dev/null
    echo "Flow $namespace.$id actualizado"
else
    curl -sf -u "$USUARIO" -X POST -H "Content-Type: application/x-yaml" \
        --data-binary @"$flow" "$KESTRA/flows" > /dev/null
    echo "Flow $namespace.$id creado"
fi
