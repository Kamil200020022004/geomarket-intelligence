# Obraz serwisu AI Patryka (backend-ai) — przygotowany przez Sebastiana do Docker Compose całości.
# Plik leży poza folderem backend-ai/, żeby nie zmieniać kodu autora serwisu.
# Kontekst budowania: backend-ai/ (patrz docker-compose.yml). Klucze API: backend-ai/.env.
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app ./app

# UID 1000 jak w obrazie backendu — obie usługi piszą do wspólnego wolumenu Lakehouse.
RUN useradd --uid 1000 --create-home appuser \
    && mkdir -p /data/lakehouse /app/data \
    && chown -R appuser:appuser /data/lakehouse /app/data
USER appuser

ENV LAKEHOUSE_ROOT=/data/lakehouse
EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
