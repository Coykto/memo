# Use an official Python runtime as a base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONPATH=/app/src \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies and UV
RUN pip install --upgrade pip && \
    pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install project dependencies (without root package)
RUN uv sync

# Copy source code
COPY src/ src/

ENTRYPOINT ["uv", "run", "python", "src/clients/telegram_client/bot.py"]