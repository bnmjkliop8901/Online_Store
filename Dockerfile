FROM python:3.12-slim AS builder
# FROM dockerproxy.com/library/python:3.12-slim AS builder
# FROM registry.docker-cn.com/library/python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install build deps
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m venv /venv && /venv/bin/pip install --upgrade pip && /venv/bin/pip install -r requirements.txt

COPY . .

FROM python:3.12-slim
# FROM dockerproxy.com/library/python:3.12-slim
# FROM registry.docker-cn.com/library/python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/venv/bin:$PATH"

WORKDIR /app

RUN apt-get update && apt-get install -y libpq5 && rm -rf /var/lib/apt/lists/*

COPY --from=builder /venv /venv
COPY . .

# Collect static into shared volume path
RUN mkdir -p /shared/static /shared/media && python manage.py collectstatic --noinput

CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers=3"]

