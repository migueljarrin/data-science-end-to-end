"""Comprobacion del Ejercicio 2. Lee el flow tal como quedo en Kestra.

    python3 comprobar.py

No la modifiques.
"""

import datetime
import json

import requests

KESTRA = "http://localhost:8080/api/v1/main"
USUARIO = ("admin@kestra.io", "Admin1234")


def comprobar(numero, condicion):
    if condicion:
        print(f"TODO {numero}: OK")
    else:
        print(f"TODO {numero}: revisa")


respuesta = requests.get(f"{KESTRA}/flows/proyecto.clima/ingesta_clima", auth=USUARIO)
flow = respuesta.json() if respuesta.status_code == 200 else {}
tarea = (flow.get("tasks") or [{}])[0]
reintento = tarea.get("retry") or {}
comandos = tarea.get("commands") or []
if isinstance(comandos, str):
    comandos = json.loads(comandos)
disparadores = flow.get("triggers") or [{}]

comprobar(1, bool(flow))
comprobar(2, reintento.get("maxAttempts") == 4 and reintento.get("interval") == "PT5S")
comprobar(3, any("ingesta_clima.py" in c and "trigger.date" in c for c in comandos))
comprobar(4, disparadores[0].get("cron") == "0 7 * * 1")

respuesta = requests.get(
    f"{KESTRA}/executions/search",
    params={
        "filters[namespace][EQUALS]": "proyecto.clima",
        "filters[flowId][EQUALS]": "ingesta_clima",
        "size": 100,
    },
    auth=USUARIO,
)
ejecuciones = respuesta.json().get("results", []) if respuesta.status_code == 200 else []
hoy = datetime.date.today().isoformat()
pasadas = [
    e for e in ejecuciones
    if e["flowId"] == "ingesta_clima" and e["state"]["current"] == "SUCCESS"
    and ((e.get("trigger") or {}).get("variables") or {}).get("date", hoy)[:10] < hoy
]
comprobar(5, len(pasadas) >= 3)
