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

# Copy source code and tests
COPY src/ src/

# Command to run your application (adjust to your entrypoint)
ENTRYPOINT ["uv", "run", "python", "api.py"]