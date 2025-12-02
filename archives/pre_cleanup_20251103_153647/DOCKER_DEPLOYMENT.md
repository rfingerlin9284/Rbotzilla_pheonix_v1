# RBOTzilla Streamlit Dashboard - Docker Setup

## Dockerfile for Backend

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir fastapi uvicorn websockets oandapyV20 coinbase-advanced-py

# Copy app
COPY backend.py .

# Expose port
EXPOSE 8000

# Run
CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8000"]
```

Save as `Dockerfile.backend`

## Dockerfile for Dashboard

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir streamlit websocket-client

# Copy app
COPY dashboard.py .

# Expose port
EXPOSE 8501

# Run
CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Save as `Dockerfile.dashboard`

## Docker Compose

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - OANDA_ACCESS_TOKEN=${OANDA_ACCESS_TOKEN}
      - OANDA_ACCOUNT_ID=${OANDA_ACCOUNT_ID}
      - COINBASE_API_KEY=${COINBASE_API_KEY}
      - COINBASE_API_SECRET=${COINBASE_API_SECRET}
    volumes:
      - ./rbotzilla_backend.log:/app/rbotzilla_backend.log
    networks:
      - rbotzilla
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s

  dashboard:
    build:
      context: .
      dockerfile: Dockerfile.dashboard
    ports:
      - "8501:8501"
    environment:
      - BACKEND_URL=http://backend:8000
      - WEBSOCKET_URL=ws://backend:8000/ws
    depends_on:
      backend:
        condition: service_healthy
    networks:
      - rbotzilla
    volumes:
      - ~/.streamlit:/root/.streamlit

networks:
  rbotzilla:
    driver: bridge
```

Save as `docker-compose.yml`

## Running with Docker

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Run specific service
docker-compose up backend      # Only backend
docker-compose up dashboard    # Only dashboard
```

## Kubernetes Deployment (Advanced)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rbotzilla-backend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: rbotzilla-backend
  template:
    metadata:
      labels:
        app: rbotzilla-backend
    spec:
      containers:
      - name: backend
        image: rbotzilla:backend-latest
        ports:
        - containerPort: 8000
        env:
        - name: OANDA_ACCESS_TOKEN
          valueFrom:
            secretKeyRef:
              name: rbotzilla-secrets
              key: oanda-token
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: rbotzilla-backend
spec:
  selector:
    app: rbotzilla-backend
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
  type: LoadBalancer
```

Save as `k8s-deployment.yaml`

Deploy:
```bash
kubectl apply -f k8s-deployment.yaml
```

## Production Checklist

- [ ] Use secrets management (AWS Secrets Manager, HashiCorp Vault)
- [ ] Add SSL/TLS certificates (Let's Encrypt)
- [ ] Enable authentication/authorization
- [ ] Set up monitoring (Prometheus, Grafana)
- [ ] Configure logging (ELK Stack)
- [ ] Add rate limiting & DDoS protection
- [ ] Use reverse proxy (Nginx, HAProxy)
- [ ] Set up database for persistence
- [ ] Enable backups & disaster recovery
- [ ] Document runbooks for operations

