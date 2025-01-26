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

# Copy source code and tests
COPY src/ src/

# Command to run your application (adjust to your entrypoint)
ENTRYPOINT ["poetry", "run", "python", "api.py"]