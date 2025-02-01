# Use an official Python runtime as a base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies and UV
RUN pip install --upgrade pip && \
    pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock api.py ./

# Install project dependencies
RUN uv sync

# Copy source code and tests
COPY src/ src/

# Command to run your application
ENTRYPOINT ["uv", "run", "python", "api.py"]