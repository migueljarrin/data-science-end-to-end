#!/usr/bin/env bash
# Verifica que cada herramienta del curso responde. Corre al crear el Codespace y
# puedes repetirla cuando quieras: bash .devcontainer/verificar.sh
set -euo pipefail
# sed -n en vez de head: head cierra la tuberia antes de que el comando termine
# de escribir, y con pipefail eso aborta el script (codigo 141, SIGPIPE).

echo "--- Verificacion del ambiente ---"
python --version
java -version 2>&1 | sed -n '1p'
terraform -version | sed -n '1p'
docker --version
docker compose version
dbt --version | sed -n '1,3p'
python - <<'PY'
import duckdb, kafka, matplotlib, pandas, pyspark, sklearn
print(f"pandas {pandas.__version__} | duckdb {duckdb.__version__} | pyspark {pyspark.__version__}")
print(f"scikit-learn {sklearn.__version__} | matplotlib {matplotlib.__version__} | kafka-python {kafka.__version__}")
PY

echo
echo "Ambiente listo. Si algo de lo anterior fallo, avisame antes de la proxima sesion."
