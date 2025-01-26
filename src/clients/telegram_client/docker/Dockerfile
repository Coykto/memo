# Use an official Python runtime as a base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONPATH=/app/src \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies and Poetry
RUN pip install --upgrade pip && \
    pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install project dependencies (without root package)
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

# Copy source code
COPY src/ src/

ENTRYPOINT ["poetry", "run", "python", "src/clients/telegram_client/bot.py"]