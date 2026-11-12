# La imagen del servicio del proyecto. Se construye desde psets/proyecto,
# porque necesita modelado/ ademas de servicio/. Antes, exporta el modelo con
# python -m servicio.exportar_modelo:
#
#     docker build -f servicio/Dockerfile -t servicio-ecu911 .
#     docker run -p 8000:8000 servicio-ecu911
FROM python:3.11-slim
WORKDIR /app
COPY servicio/requirements.txt servicio/requirements.txt
RUN pip install --no-cache-dir -r servicio/requirements.txt
COPY modelado/pipeline_proyecto.py modelado/
COPY servicio/api.py servicio/modelo.joblib servicio/referencias.joblib servicio/
EXPOSE 8000

CMD ["uvicorn", "servicio.api:app", "--host", "0.0.0.0", "--port", "8000"]
