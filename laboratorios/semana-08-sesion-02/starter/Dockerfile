
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . ./starter

CMD ["python3", "starter/EDA.py"]
