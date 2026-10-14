# Stage 1: builder
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY pyproject.toml README.md ./
COPY src/ src/

RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --upgrade pip setuptools \
    && /opt/venv/bin/pip install --no-cache-dir .

# Stage 2: runtime
FROM python:3.12-slim

LABEL maintainer="SE-Emam"
LABEL version="1.1.0"
LABEL description="ARGUS - verified research reports CLI"

COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

ENTRYPOINT ["argus"]