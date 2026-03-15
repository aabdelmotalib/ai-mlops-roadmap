---
tags:
  - Advanced
  - Phase 6
---

# Module 2: Containerising Applications

> **Phase 6 — MLOps & Deployment**

---

## 🎯 What You Will Learn

- How to write production-grade Dockerfiles for Python applications
- How to use multi-stage builds to shrink image sizes dramatically
- How to use `.dockerignore` to keep images clean and fast
- How to run containers as a non-root user for security
- How to handle secrets safely — never baking them into images
- How to tag and version your images using semantic versioning
- How to push images to Docker Hub and GitHub Container Registry
- How to add health checks to Dockerfiles
- How to debug containers using `exec`, `logs`, and `inspect`

---

## 🧠 Concept Explained

Think of a Docker image like a recipe book. When you share it with someone, they can reproduce your exact dish every time — same ingredients, same steps, same result.

But a badly written recipe book is massive. It includes every tool in the kitchen, even the ones you never use. It lists every ingredient bought, even the ones that went into the bin. And it leaves the kitchen door unlocked.

A well-written Dockerfile is a minimal, precise, secure recipe. It includes only what is needed to run the application, nothing more.

!!! note "Why image size matters"
A 1GB image takes 60 seconds to pull on a fast connection. A 100MB image takes 6 seconds.
In production, new versions deploy faster, CI/CD pipelines finish sooner, and costs are lower.
Every megabyte you remove from an image saves real time and money.

---

## 🔍 How It Works

```
Bad Dockerfile process:               Good Dockerfile process:
┌─────────────────────┐               ┌─────────────────────┐
│ Start: python:3.11  │               │ Stage 1: builder    │
│ (900MB base image)  │               │ python:3.11-slim    │
│                     │               │ Install build tools │
│ Copy all files      │               │ Install dependencies│
│ Install everything  │               │ Compile if needed   │
│ Run as root         │               └──────────┬──────────┘
│                     │                          │ copy only
│ Final image: 1.2GB  │               ┌──────────▼──────────┐
└─────────────────────┘               │ Stage 2: runtime    │
                                      │ python:3.11-slim    │
                                      │ Copy deps from stage1│
                                      │ Copy app code only  │
                                      │ Run as non-root user│
                                      │                     │
                                      │ Final image: 180MB  │
                                      └─────────────────────┘
```

---

## 🛠️ Step-by-Step Guide

### Step 1 — Write a basic Dockerfile (the wrong way first)

### Step 2 — Optimise with .dockerignore

### Step 3 — Use slim base images

### Step 4 — Leverage layer caching

### Step 5 — Add a non-root user

### Step 6 — Multi-stage build

### Step 7 — Add a HEALTHCHECK

### Step 8 — Tag, version, and push to Docker Hub

---

## 💻 Code Examples

### Step 1 — The naive Dockerfile (before optimisation)

```dockerfile
# Dockerfile.bad — what NOT to do (shows why we need to optimise)

FROM python:3.11           # full Python image — 900MB!

WORKDIR /app

COPY . .                   # copies EVERYTHING including .git, __pycache__, tests

RUN pip install -r requirements.txt   # no cache, reinstalls every time

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Problems:
# 1. python:3.11 base = 900MB (we don't need compilers in production)
# 2. COPY . . copies .git folder, test files, local .env files
# 3. No layer caching — pip reinstalls on every code change
# 4. Running as root (security risk)
# 5. No health check
```

```bash
# Build and check the size of the bad image
docker build -f Dockerfile.bad -t myapp:bad .
docker images myapp:bad
# REPOSITORY   TAG    IMAGE ID   SIZE
# myapp        bad    abc123     1.18GB   ← huge!
```

---

### Step 2 — .dockerignore

```
# .dockerignore — like .gitignore but for Docker
# Files listed here are NOT sent to the Docker build context
# This speeds up builds and prevents secrets leaking into images

# Version control
.git/
.gitignore

# Python artifacts (rebuilt inside the container)
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.egg-info/
dist/
build/
.eggs/

# Virtual environments (we install deps fresh inside the container)
venv/
.venv/
env/
.env/

# Secrets and local config (NEVER in the image)
.env
.env.local
*.env
secrets/
*.pem
*.key

# Test files (not needed in production image)
tests/
test_*.py
*_test.py
pytest.ini
.coverage
htmlcov/

# Development tools
.idea/
.vscode/
*.swp

# Documentation
docs/
*.md
README*

# Docker files themselves
Dockerfile*
docker-compose*.yml

# OS files
.DS_Store
Thumbs.db
```

---

### Step 3 — Slim base image with layer caching

```dockerfile
# Dockerfile.slim — better, using slim base and layer caching

# python:3.11-slim: 125MB vs 900MB for python:3.11
# 'slim' removes compilers, header files, and other build tools
FROM python:3.11-slim

# Set environment variables that improve Python in Docker
ENV PYTHONDONTWRITEBYTECODE=1 \
    # Don't write .pyc files (we don't need them in containers)
    PYTHONUNBUFFERED=1
    # Print logs immediately without buffering (important for docker logs)

WORKDIR /app

# ── LAYER CACHING TRICK ──────────────────────────────────────────────────────
# Copy ONLY requirements.txt first, then install dependencies
# Docker caches each layer — if requirements.txt hasn't changed,
# pip install is skipped on the next build (saves 30-60 seconds)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# --no-cache-dir: don't cache pip downloads inside the image (saves ~50MB)

# Copy the rest of the application code AFTER installing dependencies
# This way, code changes don't invalidate the pip install cache layer
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Size: ~320MB (much better, but still can improve)
```

---

### Step 4 — Multi-stage build (production-grade)

```dockerfile
# Dockerfile — production-grade multi-stage FastAPI Dockerfile

# ═══════════════════════════════════════════════════════════
# STAGE 1: builder
# This stage installs dependencies and compiles anything needed
# It will NOT be in the final image — only its output will
# ═══════════════════════════════════════════════════════════
FROM python:3.11-slim AS builder

# Install build tools needed to compile some Python packages
# (e.g. psycopg2 needs libpq-dev, some packages need gcc)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*    # clean up apt cache immediately to save space

WORKDIR /app

# Copy and install Python dependencies into a specific directory
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt
# --prefix=/install: installs packages into /install instead of system Python
# This lets us copy just /install into the runtime stage


# ═══════════════════════════════════════════════════════════
# STAGE 2: runtime
# This is the final image — minimal, secure, production-ready
# It does NOT contain gcc, apt packages, or build artifacts
# ═══════════════════════════════════════════════════════════
FROM python:3.11-slim AS runtime

# Install only runtime dependencies (not build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \           # PostgreSQL client library (runtime, not dev)
    curl \             # needed for the health check
    && rm -rf /var/lib/apt/lists/*

# ── Create a non-root user for security ──────────────────────────────────────
# Running as root inside a container is a security risk
# If the container is compromised, root inside = more damage potential
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid 1000 --no-create-home appuser
# --gid/--uid 1000: use predictable IDs (easier for volume permission management)

WORKDIR /app

# Copy installed Python packages from the builder stage
COPY --from=builder /install /usr/local
# This brings in all pip-installed packages WITHOUT the build tools

# Copy only the application source code
COPY --chown=appuser:appuser app/ .
# --chown: set file ownership to appuser immediately during copy

# Switch to the non-root user
USER appuser

# Document which port the app listens on (informational only — doesn't open the port)
EXPOSE 8000

# ── Health check ──────────────────────────────────────────────────────────────
HEALTHCHECK \
    --interval=30s \    # check every 30 seconds
    --timeout=10s \     # fail if no response in 10 seconds
    --start-period=10s \# wait 10s after start before first check
    --retries=3 \       # mark unhealthy after 3 consecutive failures
    CMD curl -f http://localhost:8000/health || exit 1
# 'exit 1' = unhealthy, 'exit 0' = healthy

# Start the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
# --workers 2: use 2 worker processes for better performance
```

```bash
# Build the production image
docker build -t myapp:latest .

# Compare image sizes
docker images | grep myapp
# myapp   bad      1.18GB
# myapp   slim     320MB
# myapp   latest   165MB  ← multi-stage result
```

---

### Production Dockerfile for Celery Worker

```dockerfile
# Dockerfile.worker — production Celery worker

FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Non-root user
RUN groupadd --gid 1000 celeryuser && \
    useradd --uid 1000 --gid 1000 --no-create-home celeryuser

WORKDIR /app

COPY --from=builder /install /usr/local
COPY --chown=celeryuser:celeryuser worker/ .

USER celeryuser

# Celery worker — no ports exposed (it pulls tasks, doesn't accept connections)
CMD ["celery", "-A", "tasks", "worker", \
     "--loglevel=info", \
     "--concurrency=4", \
     "--max-tasks-per-child=1000"]
# --max-tasks-per-child=1000: restart worker process after 1000 tasks (prevents memory leaks)
```

---

### Handling secrets safely

```dockerfile
# NEVER do this — secrets baked into the image are visible to anyone
# who pulls the image, even after you remove them from later layers
ENV DATABASE_PASSWORD=mysecretpassword   # ❌ visible in docker history

# CORRECT: pass secrets at runtime via environment variables
# In docker-compose.yml:
# environment:
#   DATABASE_PASSWORD: ${DATABASE_PASSWORD}  # reads from .env at runtime

# Or use Docker secrets for production (Swarm / Kubernetes):
# secrets:
#   db_password:
#     file: ./secrets/db_password.txt
```

```bash
# See what's baked into any image (including deleted files)
docker history myapp:latest

# Check if any secrets leaked into layers
docker run --rm myapp:latest env | grep -i password
# Should return nothing — passwords should not be in env at build time
```

---

### Image tagging and versioning

```bash
# Semantic versioning: MAJOR.MINOR.PATCH
# MAJOR: breaking change
# MINOR: new feature, backward compatible
# PATCH: bug fix

# Tag with a version number
docker build -t myusername/roadmap-api:1.0.0 .
docker build -t myusername/roadmap-api:1.0.0 \
             -t myusername/roadmap-api:latest .   # tag same image twice

# Also tag with git commit hash for traceability
GIT_SHA=$(git rev-parse --short HEAD)    # get short git commit hash
docker build -t myusername/roadmap-api:${GIT_SHA} .
docker build -t myusername/roadmap-api:1.0.1 \
             -t myusername/roadmap-api:latest \
             -t myusername/roadmap-api:${GIT_SHA} .

# List all tags on an image
docker images myusername/roadmap-api
```

---

### Push to Docker Hub

```bash
# Step 1: login to Docker Hub
docker login
# Enter your Docker Hub username and password

# Step 2: push the image
docker push myusername/roadmap-api:1.0.0
docker push myusername/roadmap-api:latest

# Step 3: push ALL tags at once
docker push myusername/roadmap-api --all-tags

# Pull it anywhere to verify
docker pull myusername/roadmap-api:1.0.0
```

### Push to GitHub Container Registry (GHCR)

```bash
# GitHub Container Registry is free for public repos
# Images live at: ghcr.io/your-github-username/image-name

# Step 1: create a GitHub Personal Access Token with 'write:packages' scope
# Settings → Developer settings → Personal access tokens → New token

# Step 2: login to GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin

# Step 3: build with GHCR tag
docker build -t ghcr.io/your-github-username/roadmap-api:latest .

# Step 4: push
docker push ghcr.io/your-github-username/roadmap-api:latest
```

---

### Debugging containers

```bash
# Open an interactive shell inside a running container
docker exec -it roadmap_api bash
# -it: interactive terminal
# bash: the shell to open

# If bash is not available (alpine images use sh)
docker exec -it roadmap_api sh

# Run a specific command without opening a shell
docker exec roadmap_api python --version
docker exec roadmap_api pip list | grep fastapi

# Read logs
docker logs roadmap_api                    # all logs
docker logs roadmap_api --tail 50          # last 50 lines
docker logs roadmap_api --follow           # live follow
docker logs roadmap_api --since 5m        # last 5 minutes
docker logs roadmap_api --since 2024-01-15T10:00:00  # since timestamp

# Inspect full container configuration
docker inspect roadmap_api                 # full JSON config
docker inspect roadmap_api | grep -A5 '"Health"'  # just health status

# Copy a file from a container to your host
docker cp roadmap_api:/app/logs/app.log ./app.log

# Copy a file from your host into a container
docker cp ./new_config.py roadmap_api:/app/config.py

# See processes running inside a container
docker top roadmap_api

# See real-time resource usage
docker stats roadmap_api
```

---

## ⚠️ Common Mistakes

**Mistake 1: COPY . . before installing dependencies**

```dockerfile
# WRONG: code changes invalidate the pip install cache layer
COPY . .                          # if ANY file changes, next layer reruns
RUN pip install -r requirements.txt   # this reinstalls every time — slow!

# CORRECT: copy requirements first, install, then copy code
COPY requirements.txt .
RUN pip install -r requirements.txt  # cached unless requirements.txt changes
COPY . .                              # code changes don't invalidate pip cache
```

**Mistake 2: Not cleaning up apt cache**

```dockerfile
# WRONG: apt cache stays in the layer, adding ~50MB
RUN apt-get update
RUN apt-get install -y gcc

# CORRECT: clean up in the same RUN command (same layer = no extra size)
RUN apt-get update && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*    # delete apt cache in the same layer
```

**Mistake 3: Multiple RUN commands for related operations**

```dockerfile
# WRONG: each RUN creates a new layer — more layers = bigger image
RUN apt-get update
RUN apt-get install -y gcc
RUN apt-get install -y libpq-dev
RUN rm -rf /var/lib/apt/lists/*   # this doesn't remove what previous layers stored!

# CORRECT: chain with && in one RUN command — one layer, truly cleaned up
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*
```

---

## ✅ Exercises

**Exercise 1 — Easy**
Build the naive `Dockerfile.bad` and the optimised multi-stage `Dockerfile`. Compare their sizes with `docker images`. Calculate the percentage size reduction.

**Exercise 2 — Medium**
Add a `HEALTHCHECK` to the Celery worker Dockerfile. Since Celery has no HTTP endpoint, use this check instead:

```bash
celery -A tasks inspect ping -d celery@$HOSTNAME
```

Test it with `docker inspect --format='{{.State.Health.Status}}' roadmap_worker`.

**Exercise 3 — Hard**
Create a `Dockerfile` for a Python script that reads a CSV file from a mounted volume, processes it, and writes output back to the volume. The script must run as a non-root user. The `.dockerignore` must exclude test data files. Build the image, run it with `-v`, and verify the output file appears on your host.

---

## 🏗️ Mini Project — Build and Push a Versioned Image

**Goal:** Build a production-ready versioned image of the FastAPI + ML model app and push it to Docker Hub.

```bash
# Step 1: build with version and git hash tags
VERSION="1.0.0"
GIT_SHA=$(git rev-parse --short HEAD)

docker build \
  -t myusername/roadmap-api:${VERSION} \
  -t myusername/roadmap-api:${GIT_SHA} \
  -t myusername/roadmap-api:latest \
  .

# Step 2: verify the image works locally
docker run -d \
  --name test_api \
  -p 8001:8000 \
  -e DATABASE_URL=postgresql://postgres:password@host.docker.internal:5432/books_db \
  -e REDIS_URL=redis://host.docker.internal:6379/0 \
  myusername/roadmap-api:${VERSION}

# Test it
curl http://localhost:8001/health
# Expected: {"status": "healthy"}

curl http://localhost:8001/books
# Expected: list of books from database

# Step 3: check image size
docker images myusername/roadmap-api

# Step 4: push all tags
docker push myusername/roadmap-api --all-tags

# Step 5: clean up
docker stop test_api && docker rm test_api

# Step 6: verify pull works from a clean state
docker rmi myusername/roadmap-api:${VERSION}  # remove local copy
docker pull myusername/roadmap-api:${VERSION}  # pull from Docker Hub
docker run --rm myusername/roadmap-api:${VERSION} python --version
```

---

## 🔗 What's Next

In **Module 6-3: CI/CD Pipelines**, you will automate everything you did in this module — building, testing, and pushing Docker images — so it happens automatically every time you push code to GitHub.
