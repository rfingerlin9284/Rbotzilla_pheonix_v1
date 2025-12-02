# Dockerfile.orchestrator
FROM python:3.11-slim

# Set environment
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project
COPY . .

# Expose FastAPI port (edit if using a different port)
EXPOSE 8007

# Default command to run FastAPI
CMD ["uvicorn", "backend.orchestrator.api:app", "--host", "0.0.0.0", "--port", "8007"]

# Dockerfile for all Python agents & orchestrator

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project source
COPY . .

# Set environment variables default (can be overridden by docker-compose)
ENV REDIS_URL=redis://redis:6379
ENV DATABASE_URL=postgresql://postgres:password@postgres:5432/agentic_trading

# Default command (override in docker-compose for each agent)
CMD ["python3", "backend/agents/chartanalyst/main.py"]
