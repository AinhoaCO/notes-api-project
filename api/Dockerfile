# Small image, non-root user, config only via env vars.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

# Dependencies first: this layer is cached until requirements.txt changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# Which code is this? CI/you pass --build-arg VERSION=...; shown in /api/message.
ARG VERSION=dev
ENV APP_VERSION=$VERSION

RUN useradd --system --uid 10001 appuser
USER appuser

EXPOSE 8080
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
