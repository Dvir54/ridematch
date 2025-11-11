# ============================================
# Stage 1: Base Python Image
# ============================================
# Use Python 3.11 slim variant (smaller than full Python, includes essentials)
FROM python:3.11-slim

# Set environment variables
# PYTHONUNBUFFERED=1: Ensures Python output is sent straight to terminal (no buffering)
#                     Important for seeing logs in real-time in Docker
# PYTHONDONTWRITEBYTECODE=1: Prevents Python from writing .pyc files (compiled bytecode)
#                            Keeps container clean and reduces size
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Set working directory inside container
# All subsequent commands will run from this directory
WORKDIR /app

# ============================================
# Stage 2: Install System Dependencies
# ============================================
# Install system packages needed for Python packages
# - gcc, g++: C/C++ compilers needed to build some Python packages
# - postgresql-dev: PostgreSQL development files (needed for psycopg2)
# - musl-dev: C standard library development files
# We clean up after to keep image size small
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# ============================================
# Stage 3: Install Python Dependencies
# ============================================
# Copy requirements.txt first (before copying all code)
# This leverages Docker layer caching:
# - If requirements.txt doesn't change, Docker reuses this layer
# - Only re-installs packages when requirements.txt changes
COPY requirements.txt .

# Install Python packages
# --no-cache-dir: Don't cache pip downloads (saves space)
# --upgrade: Ensure latest compatible versions
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ============================================
# Stage 4: Copy Application Code
# ============================================
# Copy the entire app directory
# This comes AFTER installing dependencies for better caching
COPY ./app ./app
COPY ./alembic ./alembic
COPY ./alembic.ini ./alembic.ini

# ============================================
# Stage 5: Create Non-Root User (Security)
# ============================================
# Running as root in containers is a security risk
# Create a dedicated user with limited permissions
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# ============================================
# Stage 6: Expose Port & Run Application
# ============================================
# Expose port 8001 (this is just documentation, doesn't actually publish the port)
# The actual port mapping happens in docker-compose.yml
EXPOSE 8001

# Health check: Verifies the service is responding
# Every 30 seconds, curl the /health endpoint
# Fails if 3 consecutive checks fail
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/health')" || exit 1

# Default command to run the application
# uvicorn: ASGI server that runs FastAPI
# app.main:app: Import 'app' object from app/main.py
# --host 0.0.0.0: Listen on all network interfaces (required for Docker)
# --port 8001: Port to listen on
# --reload: Auto-reload on code changes (ONLY for development, remove in production)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]

