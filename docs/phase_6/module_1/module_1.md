---
tags:
  - Advanced
  - Phase 6
---

# Module 1: Docker Compose

> **Phase 6 — MLOps & Deployment**

---

## 🎯 What You Will Learn

- What Docker Compose is and why you need it when running multiple services
- How to write a `docker-compose.yml` file from scratch
- How to run a full stack: PostgreSQL + Redis + FastAPI + Celery in one command
- The difference between named volumes and bind mounts
- How to use `.env` files to manage environment variables
- How to add health checks so services start in the right order
- How to scale workers horizontally
- How to use profiles for optional services like monitoring

---

## 🧠 Concept Explained

So far you have been running containers one at a time with `docker run`. That works fine for a single service. But your application is not a single service — it is a team.

Your FastAPI app needs PostgreSQL to store data. It needs Redis to queue tasks. It needs Celery workers to process those tasks. If you had to start each one manually, in the right order, with the right network settings so they can find each other — you would do it wrong every time.

**Docker Compose solves this.** You describe your entire stack in one file — `docker-compose.yml` — and then run one command: `docker compose up`. Compose starts everything, connects them to the same network, and manages them as a group.

!!! note "The analogy"
If Docker is like hiring one person for a job, Docker Compose is like hiring an entire team, assigning them desks in the same office, giving them a phone directory so they can call each other, and telling them all to start work at 9am.

---

## 🔍 How It Works

```
docker-compose.yml defines:

┌─────────────────────────────────────────────────────────┐
│                    Docker network                        │
│                                                         │
│  ┌──────────┐    ┌──────────┐    ┌──────────────────┐  │
│  │PostgreSQL│    │  Redis   │    │    FastAPI app   │  │
│  │port:5432 │    │port:6379 │    │    port:8000     │  │
│  └────┬─────┘    └────┬─────┘    └────────┬─────────┘  │
│       │               │                   │             │
│       └───────────────┴───────────────────┘             │
│                       │                                 │
│              ┌────────┴────────┐                        │
│              │  Celery Worker  │                        │
│              │  (no port)      │                        │
│              └─────────────────┘                        │
└─────────────────────────────────────────────────────────┘

All services share the same internal network.
They call each other by service name, not IP address.
FastAPI calls PostgreSQL as: postgresql://postgres:password@db:5432/books_db
                                                               ^^
                                                    service name, not localhost!
```

---

## 🛠️ Step-by-Step Guide

### Step 1 — Install Docker Compose (already included with Docker Desktop)

```bash
# Verify Docker Compose is available
docker compose version

# Expected output:
# Docker Compose version v2.24.0
```

### Step 2 — Create your project folder structure

```bash
mkdir -p ~/roadmap-stack
cd ~/roadmap-stack

# Create the folder structure
mkdir -p app/            # FastAPI application code
mkdir -p worker/         # Celery worker code
mkdir -p nginx/          # optional reverse proxy config

touch docker-compose.yml  # main compose file
touch .env                # environment variables (never commit this!)
touch .env.example        # template showing what variables are needed (safe to commit)
```

### Step 3 — Write the .env file

### Step 4 — Write the docker-compose.yml

### Step 5 — Run the stack

### Step 6 — Inspect and debug running services

### Step 7 — Scale workers

### Step 8 — Add profiles for optional services

---

## 💻 Code Examples

### Step 3 — The .env file

```bash
# .env — secret values, never commit to git
# Add .env to your .gitignore immediately

POSTGRES_USER=postgres
POSTGRES_PASSWORD=supersecretpassword   # change this!
POSTGRES_DB=books_db
POSTGRES_PORT=5432

REDIS_PORT=6379

FASTAPI_PORT=8000
FASTAPI_SECRET_KEY=another-secret-key-change-me

CELERY_CONCURRENCY=4    # how many tasks each worker handles in parallel

FLOWER_PORT=5555         # Celery monitoring UI port
```

```bash
# .env.example — safe to commit, shows teammates what variables to set
POSTGRES_USER=postgres
POSTGRES_PASSWORD=             # set your own password
POSTGRES_DB=books_db
POSTGRES_PORT=5432
REDIS_PORT=6379
FASTAPI_PORT=8000
FASTAPI_SECRET_KEY=            # generate with: python -c "import secrets; print(secrets.token_hex(32))"
CELERY_CONCURRENCY=4
FLOWER_PORT=5555
```

```bash
# Add .env to .gitignore so you never accidentally commit secrets
echo ".env" >> .gitignore
```

---

### Step 4 — The complete docker-compose.yml

```yaml
# docker-compose.yml — the full stack for the AI & MLOps Roadmap
# Run with: docker compose up -d

version: "3.9" # compose file format version

# ── Named volumes ──────────────────────────────────────────────────────────
# Named volumes persist data across container restarts and recreations
# Unlike bind mounts, Docker manages where they live on the host
volumes:
  postgres_data: # PostgreSQL data files
  redis_data: # Redis persistence files
  mlflow_data: # MLflow experiment tracking data

# ── Custom network ─────────────────────────────────────────────────────────
# All services join this network and can reach each other by service name
networks:
  app_network:
    driver: bridge # default network driver, works for single-host setups

# ── Services ───────────────────────────────────────────────────────────────
services:
  # ── PostgreSQL database ─────────────────────────────────────────────────
  db:
    image: postgres:16-alpine # alpine = smaller image size
    container_name: roadmap_postgres
    restart: unless-stopped # restart if it crashes, but not if manually stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER} # read from .env file
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD} # read from .env file
      POSTGRES_DB: ${POSTGRES_DB} # read from .env file
    ports:
      - "${POSTGRES_PORT}:5432" # host_port:container_port
    volumes:
      - postgres_data:/var/lib/postgresql/data # persist database files
      - ./sql/init.sql:/docker-entrypoint-initdb.d/init.sql # run on first start
    networks:
      - app_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s # check every 10 seconds
      timeout: 5s # fail if no response within 5 seconds
      retries: 5 # mark as unhealthy after 5 failures
      start_period: 30s # wait 30s before starting health checks (DB needs time to init)

  # ── Redis message broker ────────────────────────────────────────────────
  redis:
    image: redis:7-alpine
    container_name: roadmap_redis
    restart: unless-stopped
    command: redis-server --appendonly yes # enable persistence (AOF mode)
    ports:
      - "${REDIS_PORT}:6379"
    volumes:
      - redis_data:/data # persist Redis data
    networks:
      - app_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"] # redis-cli ping returns PONG if healthy
      interval: 10s
      timeout: 5s
      retries: 5

  # ── FastAPI application ─────────────────────────────────────────────────
  api:
    build:
      context: ./app # build from the ./app directory
      dockerfile: Dockerfile # using ./app/Dockerfile
    container_name: roadmap_api
    restart: unless-stopped
    ports:
      - "${FASTAPI_PORT}:8000"
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      # Note: hostname is 'db' — the service name, not localhost
      REDIS_URL: redis://redis:6379/0
      # Note: hostname is 'redis' — the service name
      SECRET_KEY: ${FASTAPI_SECRET_KEY}
    volumes:
      - ./app:/app # bind mount: code changes reflect immediately
    depends_on:
      db:
        condition: service_healthy # wait for DB to be healthy before starting API
      redis:
        condition: service_healthy # wait for Redis to be healthy too
    networks:
      - app_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

  # ── Celery worker ───────────────────────────────────────────────────────
  worker:
    build:
      context: ./worker
      dockerfile: Dockerfile
    container_name: roadmap_worker
    restart: unless-stopped
    command: celery -A tasks worker --loglevel=info --concurrency=${CELERY_CONCURRENCY}
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      REDIS_URL: redis://redis:6379/0
      CELERY_BROKER_URL: redis://redis:6379/0
      CELERY_RESULT_BACKEND: redis://redis:6379/0
    volumes:
      - ./worker:/app
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - app_network

  # ── Celery Beat (task scheduler) ────────────────────────────────────────
  beat:
    build:
      context: ./worker
      dockerfile: Dockerfile
    container_name: roadmap_beat
    restart: unless-stopped
    command: celery -A tasks beat --loglevel=info # runs the scheduler, not a worker
    environment:
      REDIS_URL: redis://redis:6379/0
      CELERY_BROKER_URL: redis://redis:6379/0
    depends_on:
      - redis
    networks:
      - app_network

  # ── Flower (Celery monitoring UI) ───────────────────────────────────────
  flower:
    build:
      context: ./worker
      dockerfile: Dockerfile
    container_name: roadmap_flower
    restart: unless-stopped
    command: celery -A tasks flower --port=5555
    ports:
      - "${FLOWER_PORT}:5555"
    environment:
      CELERY_BROKER_URL: redis://redis:6379/0
    depends_on:
      - redis
    networks:
      - app_network
    profiles:
      - monitoring # only starts when: docker compose --profile monitoring up

  # ── MLflow experiment tracking ──────────────────────────────────────────
  mlflow:
    image: ghcr.io/mlflow/mlflow:latest
    container_name: roadmap_mlflow
    restart: unless-stopped
    command: >
      mlflow server
      --host 0.0.0.0
      --port 5000
      --backend-store-uri postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/mlflow_db
      --default-artifact-root /mlflow/artifacts
    ports:
      - "5000:5000"
    volumes:
      - mlflow_data:/mlflow/artifacts # persist ML model artifacts
    depends_on:
      db:
        condition: service_healthy
    networks:
      - app_network
    profiles:
      - mlops # only starts when: docker compose --profile mlops up

  # ── Prometheus (metrics collection) ────────────────────────────────────
  prometheus:
    image: prom/prometheus:latest
    container_name: roadmap_prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    networks:
      - app_network
    profiles:
      - monitoring # only starts with monitoring profile

  # ── Grafana (metrics visualisation) ────────────────────────────────────
  grafana:
    image: grafana/grafana:latest
    container_name: roadmap_grafana
    restart: unless-stopped
    ports:
      - "3001:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin123
    networks:
      - app_network
    profiles:
      - monitoring
```

---

### Step 5 — Run the stack

```bash
# Start all services in detached mode (background)
docker compose up -d

# Expected output:
# [+] Running 6/6
#  ✔ Network roadmap_app_network   Created
#  ✔ Container roadmap_postgres    Started
#  ✔ Container roadmap_redis       Started
#  ✔ Container roadmap_api         Started
#  ✔ Container roadmap_worker      Started
#  ✔ Container roadmap_beat        Started

# Start with monitoring stack included
docker compose --profile monitoring up -d

# Start with MLOps tools included
docker compose --profile monitoring --profile mlops up -d

# Stop all services (keeps data volumes)
docker compose down

# Stop and DELETE all data volumes (clean slate)
docker compose down -v   # WARNING: this deletes your database!

# Rebuild images and restart (after code changes)
docker compose up -d --build
```

---

### Step 6 — Inspect and debug

```bash
# See all running containers in this compose project
docker compose ps

# Expected output:
# NAME                  IMAGE          STATUS          PORTS
# roadmap_postgres      postgres:16    Up (healthy)    0.0.0.0:5432->5432/tcp
# roadmap_redis         redis:7        Up (healthy)    0.0.0.0:6379->6379/tcp
# roadmap_api           roadmap-api    Up (healthy)    0.0.0.0:8000->8000/tcp
# roadmap_worker        roadmap-worker Up
# roadmap_beat          roadmap-worker Up

# Follow live logs from all services
docker compose logs -f

# Follow logs from one specific service
docker compose logs -f api

# Follow logs from multiple services
docker compose logs -f api worker

# Run a command inside a running container
docker compose exec api bash          # open bash inside the api container
docker compose exec db psql -U postgres -d books_db   # open psql inside db

# See resource usage
docker compose stats

# Restart one service without restarting everything
docker compose restart worker
```

---

### Step 7 — Scale workers

```bash
# Run 3 Celery worker containers instead of 1
# Useful when you have many tasks queued and need more processing power
docker compose up -d --scale worker=3

# Expected output:
# roadmap_worker_1   Up
# roadmap_worker_2   Up
# roadmap_worker_3   Up

# Check all workers registered with Redis/Celery
docker compose exec worker celery -A tasks inspect active

# Scale back down to 1
docker compose up -d --scale worker=1

# Note: you cannot scale services that have a fixed container_name
# Remove the container_name from the worker service definition
# if you want to scale it
```

!!! warning "Remove container_name to enable scaling"
If a service has `container_name: roadmap_worker`, Docker cannot create
multiple instances with different names. Remove `container_name` from any
service you want to scale.

---

### Named volumes vs bind mounts

```yaml
volumes:
  # Named volume: Docker manages where data lives
  # Use for: databases, persistent application data
  # Data survives: container restarts, docker compose down
  # Data lost: docker compose down -v
  - postgres_data:/var/lib/postgresql/data

  # Bind mount: maps a folder on your machine into the container
  # Use for: development code (so changes reflect immediately)
  # Changes on host = immediate change in container
  # Full path or relative path with ./
  - ./app:/app

  # Read-only bind mount: container can read but not write
  # Use for: config files you don't want the container to modify
  - ./config/settings.py:/app/config/settings.py:ro
```

```
Named volume              Bind mount
┌──────────────┐          ┌──────────────┐
│  Container   │          │  Container   │
│  /var/lib/   │          │  /app/       │
│  postgresql  │          │  main.py     │
└──────┬───────┘          └──────┬───────┘
       │ Docker manages           │ you control
       ▼                          ▼
┌──────────────┐          ┌──────────────┐
│ /var/lib/    │          │ ~/roadmap/   │
│ docker/      │          │ app/main.py  │
│ volumes/     │          │ (your code)  │
└──────────────┘          └──────────────┘
```

---

### Health checks ensure correct startup order

```yaml
# Without health checks, 'depends_on' only waits for the container to START
# not for the service inside it to be READY
# The database container can be running but PostgreSQL not yet accepting connections

# WRONG (just waits for container to start):
depends_on:
  - db

# CORRECT (waits for the health check to pass):
depends_on:
  db:
    condition: service_healthy   # waits until healthcheck reports healthy
```

```
Timeline without health checks:       Timeline with health checks:
t=0  db container starts              t=0  db container starts
t=1  api container starts             t=10 db healthcheck: STARTING
t=1  api tries to connect to db       t=20 db healthcheck: HEALTHY ✅
t=1  CONNECTION REFUSED ❌            t=20 api container starts
     api crashes and restarts         t=21 api connects successfully ✅
```

---

## ⚠️ Common Mistakes

**Mistake 1: Using localhost inside containers**

```yaml
# WRONG: inside a Docker container, localhost means the container itself
DATABASE_URL: postgresql://postgres:password@localhost:5432/books_db
#                                             ^^^^^^^^^
#                                   this looks for PostgreSQL INSIDE the api container

# CORRECT: use the service name as the hostname
DATABASE_URL: postgresql://postgres:password@db:5432/books_db
#                                             ^^
#                            Docker's internal DNS resolves 'db' to the db container's IP
```

**Mistake 2: Committing the .env file**

```bash
# WRONG: .env contains real passwords — never commit it
git add .env   # ❌ now your passwords are in git history forever

# CORRECT: add .env to .gitignore immediately
echo ".env" >> .gitignore
git add .env.example   # ✅ commit the template, not the real values
```

**Mistake 3: Using depends_on without health checks for databases**

```yaml
# WRONG: database container is running but PostgreSQL isn't ready yet
depends_on:
  - db   # only waits for container start, not for PostgreSQL to accept connections

# CORRECT: wait for the health check to pass
depends_on:
  db:
    condition: service_healthy
```

---

## ✅ Exercises

**Exercise 1 — Easy**
Add a `pgadmin` service to the `docker-compose.yml` that runs `dpage/pgadmin4` on port 5050. Connect it to the `app_network` and add it to the `monitoring` profile so it only starts when needed.

**Exercise 2 — Medium**
Add a `COMPOSE_PROJECT_NAME=roadmap` variable to your `.env` file. Verify that all container names now start with `roadmap_`. Then write a bash one-liner that uses `docker compose ps` to check if all services are healthy and prints "All healthy" or lists the unhealthy ones.

**Exercise 3 — Hard**
Modify the `docker-compose.yml` so that the Celery worker uses a `deploy.replicas` setting of 2. Add a custom `worker` network so workers can only talk to Redis and not directly to the API. Verify the isolation with `docker network inspect`.

---

## 🏗️ Mini Project — Add Airflow to the Stack

**Goal:** Extend the `docker-compose.yml` to include Apache Airflow, connected to the same PostgreSQL database.

```yaml
# Add these services to your docker-compose.yml

# Airflow requires a metadata database — we reuse our PostgreSQL
airflow-init:
  image: apache/airflow:2.8.0
  container_name: airflow_init
  entrypoint: /bin/bash
  command:
    - -c
    - |
      airflow db init &&
      airflow users create \
        --username admin \
        --password admin \
        --firstname Admin \
        --lastname User \
        --role Admin \
        --email admin@example.com
  environment:
    AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/airflow_db
    AIRFLOW__CORE__EXECUTOR: LocalExecutor
  depends_on:
    db:
      condition: service_healthy
  networks:
    - app_network
  profiles:
    - airflow

airflow-webserver:
  image: apache/airflow:2.8.0
  container_name: airflow_webserver
  restart: unless-stopped
  command: webserver
  ports:
    - "8080:8080"
  environment:
    AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/airflow_db
    AIRFLOW__CORE__EXECUTOR: LocalExecutor
  volumes:
    - ./dags:/opt/airflow/dags # your DAG files
    - ./logs:/opt/airflow/logs
  depends_on:
    - airflow-init
  networks:
    - app_network
  profiles:
    - airflow

airflow-scheduler:
  image: apache/airflow:2.8.0
  container_name: airflow_scheduler
  restart: unless-stopped
  command: scheduler
  environment:
    AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/airflow_db
    AIRFLOW__CORE__EXECUTOR: LocalExecutor
  volumes:
    - ./dags:/opt/airflow/dags
  depends_on:
    - airflow-init
  networks:
    - app_network
  profiles:
    - airflow
```

```bash
# Create the airflow database first
docker compose exec db psql -U postgres -c "CREATE DATABASE airflow_db;"

# Start Airflow services
docker compose --profile airflow up -d

# Open Airflow UI at http://localhost:8080
# Login: admin / admin

# Verify the full pipeline runs:
# 1. Trigger your book scraper DAG from Airflow UI
# 2. Check the FastAPI /books endpoint returns the scraped data
# 3. Check Celery Flower shows the processing tasks
```

---

## 🔗 What's Next

In **Module 6-2: Containerising Applications**, you will learn how to write production-grade Dockerfiles that build small, secure, fast-starting images — and how to push them to Docker Hub for deployment anywhere.
