# Data Security Service - Dockerfile.

# Stage 1: Builder - install dependencies using Poetry
FROM python:3.11-slim AS builder

# Some labels are defined to store metadata.
LABEL image_version="1.1.1"
LABEL app_version="1.1.1"
LABEL maintainer="Lucía Cabanillas Rodríguez"

# --- Install Poetry ---
ARG POETRY_VERSION=1.8

ENV POETRY_HOME=/opt/poetry
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VIRTUALENVS_IN_PROJECT=1
ENV POETRY_VIRTUALENVS_CREATE=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Poetry cache for dependencies
ENV POETRY_CACHE_DIR=/opt/.cache

# Install Poetry
RUN pip install "poetry==${POETRY_VERSION}"

WORKDIR /app

# --- Install dependencies ---
# Copy only the dependency definitions
COPY pyproject.toml poetry.lock ./

# Install dependencies in a virtual environment
RUN poetry install --no-root && rm -rf $POETRY_CACHE_DIR

# Stage 2: Runtime - copy the app and virtual environment from the builder
FROM python:3.11-slim AS runtime

# Set up the virtual environment path
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy the FastAPI app code
COPY ./data_security_service /app/data_security_service

# Set working directory
WORKDIR /app/data_security_service

# Expose the port for the FastAPI app
EXPOSE 8001

# Start FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
