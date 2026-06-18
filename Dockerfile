FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml LICENSE docs/README.md ./
COPY axiomai ./axiomai
COPY apps ./apps

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e ".[console]"

EXPOSE 8000 8501
