# Obraz backendu Sebastiana (autor: Sebastian Michulec).
# Jeden obraz, kilka kontenerów z różnymi poleceniami (docker-compose.yml):
#   api       — uvicorn app.main:app (bramka API, port 8000)
#   migrate   — alembic upgrade head (jednorazowo przed API)
#   consumer  — python -m app.stream.consumer
#   producer  — python -m app.stream.producer
#   backfill  — python -m app.stream.backfill (jednorazowo)
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Najpierw same zależności — warstwa z bibliotekami jest odbudowywana tylko po zmianie requirements.txt.
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY alembic.ini .
COPY alembic ./alembic
COPY app ./app

# Użytkownik bez uprawnień administratora (UID 1000 — ten sam w obrazie serwisu AI, bo oba piszą do Lakehouse).
RUN useradd --uid 1000 --create-home appuser \
    && mkdir -p /data/lakehouse \
    && chown -R appuser:appuser /data/lakehouse
USER appuser

ENV LAKEHOUSE_ROOT=/data/lakehouse
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
