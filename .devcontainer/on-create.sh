#!/usr/bin/env bash
# Se ejecuta una sola vez, cuando se crea el Codespace (o el contenedor local).
# Instala las librerias de Python del curso. Si requirements.txt cambia despues de
# sincronizar tu fork, vuelve a correr: pip install -r requirements.txt
set -euo pipefail

echo "--- Instalando librerias de Python del curso (requirements.txt) ---"
python -m pip install --user --upgrade pip --quiet
python -m pip install --user -r requirements.txt --quiet
