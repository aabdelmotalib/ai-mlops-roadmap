---
tags:
  - Intermediate
  - Phase 4
---

# Module 5: Integrating Multiple Services

> **Phase 4 — Automation & Workflow Integration**

This module teaches you to build production systems from multiple independent services that work together reliably.

---

## 🎯 What You Will Learn

By the end of this module, you will:

- Understand service-oriented architecture
- Design services that do one thing well
- Know 3 communication patterns: sync HTTP, async queues, events
- Configure services with environment variables
- Use service discovery (containers find each other)
- Architect a complete system with FastAPI + Celery + Redis + PostgreSQL
- Use the strangler fig pattern to refactor systems
- Implement circuit breakers to prevent cascade failures
- Build complete systems with Docker Compose
- Debug distributed systems (trace requests across services)
- Test multi-service integrations locally

---

## 🧠 Concept Explained: Services Working Together

### The Restaurant Analogy

Imagine a restaurant:

- **Customers** place orders (FastAPI frontend)
- **Runners** carry plates (message queue)
- **Cooks** prepare food (background workers)
- **Supply store** keeps inventory (database)
- **Manager** ensures everything runs (orchestrator)

If the supply store closes, customers still order (resilient). But orders pile up if cooks are too slow (backpressure matters).

### Problem: Monoliths are Hard to Scale

**Monolith (one program):**

```
[API] [Tasks] [Database] [Cache]
↑
One process, one crash = everything down
Hard to scale (run task workers? Start entire program)
```

**Microservices (many independent programs):**

```
[FastAPI] → [Message Queue] → [Celery Worker]
  ↓                              ↓
[Cache]                      [PostgreSQL]
```

- Each service independent: crash queue ≠ crash API
- Easy to scale: run 10 workers, not 10 entire apps
- Easy to technology-switch: Worker in Python, API in Go

### Service Communication: 3 Patterns

**1. Synchronous (HTTP) — Request/Response**

- Client waits for response
- Good for: fetching current data, simple queries
- Problem: blocks, slow if dependency is slow

**2. Asynchronous (Queues) — Fire and Forget**

- Client sends message, continues
- Good for: long-running work, decoupling
- Problem: result not immediate, harder to debug

**3. Events — Pub/Sub**

- Service publishes "order created" event
- Multiple services react (email service, inventory service)
- Good for: loosely coupled workflows
- Problem: harder to trace (who's listening?)

---

## 🔍 How It Works

### Complete System Architecture

```mermaid
graph TB
    User["👤 User / Client"]
    API["FastAPI API"]
    Queue["Redis Queue"]
    Worker["Celery Worker"]
    DB["PostgreSQL DB"]
    Cache["Redis Cache"]
    Logs["Log Aggregator"]

    User -->|HTTP Request| API
    API -->|1. Publish Job| Queue
    API -->|2. Return Task ID| User
    Queue -->|Get Job| Worker
    Worker -->|Fetch Model| Cache
    Worker -->|Save Result| DB
    Worker -->|Emit Log| Logs
    API -->|Check Status| DB
    DB -->|Return Result| API
    API -->|Response| User

    style API fill:#4A90E2,color:#fff
    style Worker fill:#50C878,color:#fff
    style Queue fill:#F5A623,color:#fff
    style DB fill:#7B68EE,color:#fff
    style Cache fill:#FF6B6B,color:#fff
```

### Request Flow: Synchronous to Asynchronous

```
1. User POST /analyze
   ↓
2. API validates input
   ↓
3. API publishes job to Redis Queue
   ↓
4. API returns task_id immediately (< 100ms)
   ↓
5. Client polls /task/{task_id}/status
   ↓
6. Celery Worker picks up job from queue
   ↓
7. Worker processes (might take minutes)
   ↓
8. Worker saves result to PostgreSQL
   ↓
9. Client gets result on next poll
```

### Environment Variables: Service Configuration

Each service needs to know where others are:

```
API Service:
- DATABASE_URL=postgresql://user:pass@db:5432/mydb
- REDIS_URL=redis://cache:6379
- CELERY_BROKER=redis://queue:6379

Worker Service:
- DATABASE_URL=postgresql://user:pass@db:5432/mydb
- REDIS_URL=redis://cache:6379
- CELERY_BROKER=redis://queue:6379
```

In Docker, `db`, `cache`, `queue` are hostnames (service names).

### Service Discovery

**Problem:** `localhost:5432` doesn't work in Docker. Services live in containers with different hostnames.

**Solution:** Docker Compose networking.

When you define services in `docker-compose.yml`, Docker creates a network. Services can reach each other by service name:

```yaml
services:
  api:
    image: my-api
  db:
    image: postgres
```

From `api`, you can `postgresql://db:5432` (not localhost:5432).

---

## 🛠️ Step-by-Step Guide

### Step 1: Design the System

Ask 3 questions per service:

1. **What does it do?** (one responsibility)
2. **Who calls it?** (dependencies)
3. **Can it fail without crashing others?** (isolation)

Example:

| Service  | Does                              | Used By      | Isolated?                     |
| -------- | --------------------------------- | ------------ | ----------------------------- |
| API      | Accept requests, return responses | Users        | Yes (queue decouples)         |
| Worker   | Process tasks                     | Queue        | Yes (crashes don't block API) |
| Database | Store data                        | API + Worker | Yes (connection pooling)      |

### Step 2: Choose Communication Pattern

- **Fast responses needed?** → HTTP (sync)
- **Long-running work?** → Queues (async)
- **Multiple services react?** → Events (pub/sub)

Example workflow:

```
HTTP: API → Database (read current user)
Queue: API → Worker → Database (process order, slow)
Event: Order created → Email service, Inventory service, Analytics
```

### Step 3: Configure with Environment Variables

**Development (.env):**

```
DATABASE_URL=postgresql://user:pass@localhost:5432/mydb
REDIS_URL=redis://localhost:6379
```

**Docker (docker-compose.yml):**

```yaml
services:
  api:
    environment:
      DATABASE_URL: postgresql://user:pass@db:5432/mydb
      REDIS_URL: redis://cache:6379
```

### Step 4: Handle Failures

Expect failures:

- Database down → return 503 "Service Unavailable"
- Worker slow → return 202 "Accepted, still processing"
- External API down → use cached value or default

Use:

- **Timeouts:** Don't wait forever
- **Retries:** Transient failures (network hiccup) vs permanent (bad input)
- **Circuit breakers:** Stop calling a failing service for a time
- **Fallbacks:** Reduced functionality vs crash

### Step 5: Trace Requests

Across services, track request:

```
Request ID: abc-123
API: "Received order POST"
  Queue: "Published job xyz to queue"
  Worker: "Job xyz started"
  Worker: "Saved result to DB"
  API: "Customer retrieved result"
```

Tool: Add request ID to all logs so you can grep: `grep "abc-123" logs/*`

---

## 💻 Code Examples

### Example 1: Multi-Service Docker Compose Setup

```yaml
# docker-compose.yml - Complete system orchestration
version: "3.8"

services:
  # PostgreSQL database - stores all persistent data
  db:
    image: postgres:15-alpine
    environment:
      # Set database name, user, password for postgres
      POSTGRES_DB: mydb
      POSTGRES_USER: dbuser
      POSTGRES_PASSWORD: dbpass
    ports:
      # Expose port 5432 so we can connect locally for testing
      - "5432:5432"
    volumes:
      # Persist data even if container stops (maps /var/lib/postgresql/data to local ./pgdata)
      - ./pgdata:/var/lib/postgresql/data
    healthcheck:
      # Check if postgres is responding to ping
      test: ["CMD-SHELL", "pg_isready -U dbuser"]
      # Run check every 10 seconds
      interval: 10s
      # Timeout each check after 5 seconds
      timeout: 5s
      # Start accepting requests after 5 successful pings
      start_period: 5s

  # Redis - in-memory cache and message queue
  cache:
    image: redis:7-alpine
    ports:
      # Expose redis port 6379
      - "6379:6379"
    healthcheck:
      # Check if redis responds to a ping command
      test: ["CMD", "redis-cli", "ping"]
      # Run check every 10 seconds
      interval: 10s
      # Timeout each check after 5 seconds
      timeout: 5s

  # FastAPI application - handles HTTP requests
  api:
    build:
      # Build from Dockerfile in ./api directory
      context: ./api
      dockerfile: Dockerfile
    environment:
      # Tell API where to find the database (use service name 'db' as hostname)
      DATABASE_URL: postgresql://dbuser:dbpass@db:5432/mydb
      # Tell API where to find Redis cache (use service name 'cache' as hostname)
      CACHE_URL: redis://cache:6379/0
      # Tell API where to find Celery broker (Redis queue)
      CELERY_BROKER_URL: redis://cache:6379/1
    ports:
      # Expose API on port 8000 for testing
      - "8000:8000"
    depends_on:
      # Wait for database and cache to be healthy before starting API
      db:
        condition: service_healthy
      cache:
        condition: service_healthy
    command:
      # Start the FastAPI server
      - uvicorn
      - main:app
      - --host
      - "0.0.0.0"
      - --port
      - "8000"
      - --reload

  # Celery Worker - processes background tasks from queue
  worker:
    build:
      # Build from Dockerfile in ./worker directory
      context: ./worker
      dockerfile: Dockerfile
    environment:
      # Worker needs same database URL as API
      DATABASE_URL: postgresql://dbuser:dbpass@db:5432/mydb
      # Worker reads jobs from same Redis queue
      CELERY_BROKER_URL: redis://cache:6379/1
      # Worker optionally uses Redis as result backend
      CELERY_RESULT_BACKEND: redis://cache:6379/2
    depends_on:
      # Wait for all services to be healthy
      db:
        condition: service_healthy
      cache:
        condition: service_healthy
      api:
        condition: service_started
    command:
      # Start Celery worker with 2 concurrent processes
      - celery
      - -A
      - celery_app
      - worker
      - --loglevel=info
      - --concurrency=2
```

### Example 2: FastAPI Service Configuration

```python
# main.py - API service that publishes jobs and reads results
from fastapi import FastAPI, HTTPException
from celery import Celery
import os
import psycopg2
import redis
import json
import logging
from datetime import datetime

# Configure logging with request ID tracking
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Order API")

# Initialize Celery client
celery_app = Celery('tasks')
celery_app.conf.broker_url = os.getenv('CELERY_BROKER_URL')

# Initialize Redis cache client
cache = redis.Redis.from_url(os.getenv('CACHE_URL'))

# Get database connection string from environment
DATABASE_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    """Get fresh database connection (for thread safety)"""
    return psycopg2.connect(DATABASE_URL)

@app.on_event("startup")
def startup():
    """Initialize database on startup"""
    logger.info("API starting up, testing database connection...")

    try:
        # Try to connect to database
        conn = get_db_connection()
        conn.close()
        logger.info("✓ Database connected successfully")

    except Exception as e:
        # If database is down, log error but don't crash API
        logger.error(f"⚠ Database not yet available: {e}")

@app.get("/health")
def health_check():
    """Health check for orchestrator"""
    health = {
        'api': 'healthy',
        'database': 'unknown',
        'cache': 'unknown',
        'queue': 'unknown'
    }

    # Check database
    try:
        conn = get_db_connection()
        conn.close()
        health['database'] = 'healthy'
    except:
        health['database'] = 'unhealthy'

    # Check cache
    try:
        cache.ping()
        health['cache'] = 'healthy'
    except:
        health['cache'] = 'unhealthy'

    # Check if queue is accessible (by checking redis)
    try:
        # Try to read from Celery stats
        celery_app.control.inspect().stats()
        health['queue'] = 'healthy'
    except:
        health['queue'] = 'unhealthy'

    # Overall status
    if all(v == 'healthy' for v in health.values()):
        return {"status": "healthy", "service": health}
    else:
        return {"status": "degraded", "service": health}

@app.post("/orders")
def create_order(customer_id: int, amount: float):
    """Create order and queue for processing"""
    # Generate request ID for tracing across services
    request_id = f"{datetime.now().isoformat()}-{customer_id}"

    logger.info(f"[{request_id}] Order request", extra={
        'customer_id': customer_id,
        'amount': amount
    })

    try:
        # Validate input
        if amount <= 0:
            raise ValueError("Amount must be positive")

        # Save order to database with "pending" status
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO orders (customer_id, amount, status, request_id) VALUES (%s, %s, %s, %s) RETURNING id",
            (customer_id, amount, 'pending', request_id)
        )
        order_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        logger.info(f"[{request_id}] Order saved to DB", extra={'order_id': order_id})

        # Publish background job to queue
        # This returns immediately while worker processes asynchronously
        task = celery_app.send_task(
            'tasks.process_order',
            args=(order_id, request_id),
            queue='default'
        )

        logger.info(f"[{request_id}] Job published to queue", extra={
            'task_id': str(task.id)
        })

        # Return task ID so client can poll for status
        return {
            'order_id': order_id,
            'task_id': str(task.id),
            'status': 'submitted',
            'message': 'Order received, processing in background'
        }

    except Exception as e:
        logger.error(f"[{request_id}] Failed to create order", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/orders/{order_id}/status")
def get_order_status(order_id: int, task_id: str = None):
    """Get order status and task progress"""
    logger.info(f"Status check for order {order_id}, task {task_id}")

    try:
        # Fetch from database
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, status, amount FROM orders WHERE id = %s",
            (order_id,)
        )
        result = cur.fetchone()
        cur.close()
        conn.close()

        if not result:
            raise ValueError(f"Order {order_id} not found")

        # If task_id provided, check task progress in Celery
        task_status = None
        if task_id:
            from celery.result import AsyncResult
            async_result = AsyncResult(task_id, app=celery_app)
            task_status = {
                'state': async_result.state,
                'progress': async_result.info if async_result.state == 'PROGRESS' else None
            }

        return {
            'order_id': result[0],
            'status': result[1],
            'amount': result[2],
            'task': task_status
        }

    except Exception as e:
        logger.error(f"Failed to fetch order {order_id}", exc_info=True)
        raise HTTPException(status_code=404, detail=str(e))
```

### Example 3: Celery Worker Service

```python
# celery_app.py - Background worker that processes queued jobs
from celery import Celery
import os
import psycopg2
import logging
from datetime import datetime

# Setup logging with service name
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('celery_worker')

# Initialize Celery app with Redis broker
celery_app = Celery('tasks')
celery_app.conf.broker_url = os.getenv('CELERY_BROKER_URL')

# Get database URL for worker
DATABASE_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    """Get fresh database connection (workers need separate connections)"""
    return psycopg2.connect(DATABASE_URL)

@celery_app.task(bind=True, max_retries=3)
def process_order(self, order_id: int, request_id: str):
    """Process order in background task with retries"""

    logger.info(f"[{request_id}] Worker received task", extra={
        'task_id': self.request.id,
        'order_id': order_id,
        'attempt': self.request.retries + 1
    })

    try:
        # Simulate some processing logic (could be ML prediction, API call, etc)
        import time
        time.sleep(2)  # Simulate 2-second processing

        # Update order status to "processing"
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE orders SET status = %s WHERE id = %s",
            ('processing', order_id)
        )
        conn.commit()

        # Simulate processing
        result = {"calculated_price": 99.99, "discount": 0.10}

        # Update order with result
        cur.execute(
            "UPDATE orders SET status = %s, result = %s WHERE id = %s",
            ('completed', str(result), order_id)
        )
        conn.commit()
        cur.close()
        conn.close()

        logger.info(f"[{request_id}] Order processed successfully", extra={
            'order_id': order_id,
            'result': result
        })

        return {'status': 'success', 'order_id': order_id, 'result': result}

    except Exception as exc:
        logger.warning(f"[{request_id}] Processing failed, attempt {self.request.retries + 1}/3", extra={
            'error': str(exc)
        })

        # Retry with exponential backoff (2^attempt seconds)
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
```

### Example 4: .env Configuration Files

```bash
# .env - Development environment variables
# Copy this to .env.local and modify for your machine

# API Settings
API_PORT=8000
API_RELOAD=true

# Database Connection
DATABASE_URL=postgresql://dbuser:dbpass@localhost:5432/mydb

# Cache (Redis)
CACHE_URL=redis://localhost:6379/0

# Message Queue (Celery with Redis)
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Logging
LOG_LEVEL=DEBUG
```

```bash
# .env.docker - Docker environment (inside containers)
# Services use Docker hostnames instead of localhost

# Database Connection
DATABASE_URL=postgresql://dbuser:dbpass@db:5432/mydb

# Cache (Redis)
CACHE_URL=redis://cache:6379/0

# Message Queue
CELERY_BROKER_URL=redis://cache:6379/1
CELERY_RESULT_BACKEND=redis://cache:6379/2

# Logging
LOG_LEVEL=INFO
```

---

## ⚠️ Common Mistakes

### Mistake 1: Using localhost in Docker

**WRONG:**

```python
# In API service running in Docker container
DATABASE_URL=postgresql://user:pass@localhost:5432/mydb
# ❌ localhost = the container itself (where postgres isn't running)
```

**RIGHT:**

```python
# Use service name from docker-compose.yml
DATABASE_URL=postgresql://user:pass@db:5432/mydb
# ✓ db = hostname that Docker DNS resolves to postgres service
```

### Mistake 2: Not Setting Up Health Checks

**WRONG:**

```yaml
services:
  api:
    depends_on:
      - db
    # ❌ Waits for container to start, not for database to be ready
```

**RIGHT:**

```yaml
services:
  api:
    depends_on:
      db:
        condition: service_healthy
    # ✓ Waits for database to actually accept connections
```

### Mistake 3: Blocking API on Slow Work

**WRONG:**

```python
@app.post("/predict")
def process_async():
    # ❌ Process synchronously - client waits, ties up connection
    result = slow_analysis(data)
    return result
```

**RIGHT:**

```python
@app.post("/predict")
def process_async():
    # ✓ Publish to queue, return immediately
    task = celery_app.send_task('analyze')
    return {'task_id': str(task.id), 'status': 'submitted'}
```

---

## ✅ Exercises

### Easy: Docker Compose Basics

1. Create `docker-compose.yml` with PostgreSQL and Redis
2. Start services with `docker-compose up`
3. Connect to each service manually:
   - `psql postgresql://user:pass@localhost:5432`
   - `redis-cli` or Python `redis.Redis()`
4. Verify both services respond

### Medium: Multi-Service API and Worker

1. Create simple FastAPI app that publishes tasks
2. Create Celery worker that processes tasks
3. Run both in Docker Compose
4. Test full flow: POST request → worker processes → retrieve result

### Hard: Complete Order Processing System

1. Design schema: orders table with status column
2. Create API: POST /orders, GET /orders/{id}/status
3. Create worker: process order (slow operation), update status
4. Use environment variables for connection strings
5. Verify request tracing (request ID appears in all logs)

---

## 🏗️ Mini Project: Order Processing System

Build a complete order processing system with API, worker, database, and queue.

### Requirements

1. **API Service:** Accept order POST, return task ID
2. **Worker Service:** Process orders asynchronously
3. **Database:** Store orders with status progression (pending → processing → completed)
4. **Health Checks:** Both services report health
5. **Logging:** Request ID tracked across all services
6. **Docker Compose:** Run everything with `docker-compose up`
7. **Communication:** API → Redis Queue → Worker → PostgreSQL

### Directory Structure

```
project/
├── docker-compose.yml          # Orchestration config
├── .env                         # Environment variables
├── api/
│   ├── Dockerfile
│   ├── main.py                 # FastAPI application
│   └── requirements.txt
├── worker/
│   ├── Dockerfile
│   ├── celery_app.py           # Celery specification
│   ├── tasks.py                # Task definitions
│   └── requirements.txt
└── postgres/
    └── init.sql                # Database schema
```

### API Implementation (api/main.py)

```python
# main.py - FastAPI order processing API
from fastapi import FastAPI, HTTPException
from celery import Celery
from pydantic import BaseModel
import os
import psycopg2
import json
import uuid

# Initialize app
app = FastAPI()

# Celery setup
celery_app = Celery('tasks')
celery_app.conf.broker_url = os.getenv('CELERY_BROKER_URL')

# Database
def get_db():
    return psycopg2.connect(os.getenv('DATABASE_URL'))

class Order(BaseModel):
    customer_name: str
    items: list
    total: float

@app.on_event("startup")
def startup():
    """Create tables if they don't exist"""
    conn = get_db()
    cur = conn.cursor()

    # Create orders table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id SERIAL PRIMARY KEY,
        customer_name VARCHAR(255),
        items TEXT,
        total FLOAT,
        status VARCHAR(50) DEFAULT 'pending',
        result TEXT,
        request_id VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    cur.close()
    conn.close()

@app.post("/orders")
def create_order(order: Order):
    """Create order and queue for processing"""
    request_id = str(uuid.uuid4())

    conn = get_db()
    cur = conn.cursor()

    # Save order with pending status
    cur.execute(
        "INSERT INTO orders (customer_name, items, total, status, request_id) "
        "VALUES (%s, %s, %s, %s, %s) RETURNING id",
        (order.customer_name, json.dumps(order.items), order.total, 'pending', request_id)
    )
    order_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    # Publish task to worker
    task = celery_app.send_task(
        'tasks.process_order',
        args=(order_id, request_id)
    )

    return {
        'order_id': order_id,
        'task_id': str(task.id),
        'request_id': request_id,
        'status': 'submitted'
    }

@app.get("/orders/{order_id}")
def get_order(order_id: int):
    """Get order status"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        raise HTTPException(status_code=404)

    return {
        'id': row[0],
        'customer_name': row[1],
        'total': row[4],
        'status': row[5],
        'result': row[6]
    }

@app.get("/health")
def health():
    """Health check"""
    try:
        conn = get_db()
        conn.close()
        return {'status': 'healthy'}
    except:
        return {'status': 'unhealthy'}
```

### Worker Implementation (worker/tasks.py)

```python
# tasks.py - Celery tasks executed by workers
from celery import Celery
import os
import psycopg2
import json
import time

# Celery setup
celery_app = Celery('tasks')
celery_app.conf.broker_url = os.getenv('CELERY_BROKER_URL')

def get_db():
    return psycopg2.connect(os.getenv('DATABASE_URL'))

@celery_app.task(bind=True, max_retries=3)
def process_order(self, order_id, request_id):
    """Process order in background"""
    print(f"[{request_id}] Processing order {order_id}")

    try:
        # Simulate processing (could be payment, fulfillment, etc)
        time.sleep(3)

        # Calculate discount (example business logic)
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT total FROM orders WHERE id = %s", (order_id,))
        total = cur.fetchone()[0]

        # Apply 10% discount
        discount_amount = total * 0.1
        final_price = total - discount_amount

        # Update order
        result = {
            'discount_applied': discount_amount,
            'final_price': final_price
        }

        cur.execute(
            "UPDATE orders SET status = %s, result = %s WHERE id = %s",
            ('completed', json.dumps(result), order_id)
        )
        conn.commit()
        cur.close()
        conn.close()

        print(f"[{request_id}] ✓ Order completed")
        return {'status': 'success'}

    except Exception as exc:
        print(f"[{request_id}] Error: {exc}, retrying...")
        raise self.retry(exc=exc, countdown=5)
```

### Docker Compose (docker-compose.yml)

```yaml
version: "3.8"

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: orders_db
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin"]
      interval: 10s
      timeout: 5s

  cache:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s

  api:
    build: ./api
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://admin:password@db:5432/orders_db
      CELERY_BROKER_URL: redis://cache:6379/0
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_healthy
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  worker:
    build: ./worker
    environment:
      DATABASE_URL: postgresql://admin:password@db:5432/orders_db
      CELERY_BROKER_URL: redis://cache:6379/0
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_healthy
    command: celery -A tasks worker --loglevel=info
```

### To Run

```bash
# Start all services
docker-compose up

# In another terminal, test the API
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"customer_name": "Alice", "items": ["Book", "Pen"], "total": 29.99}'

# Get order status
curl http://localhost:8000/orders/1
```

---

## 📚 Summary

In this module, you learned:

1. ✅ **Service-oriented thinking** – Each service does one thing
2. ✅ **Communication patterns** – Sync (HTTP), async (queues), events
3. ✅ **Environment configuration** – Services find each other via config
4. ✅ **Service discovery** – Docker DNS resolves service names
5. ✅ **Full architecture** – FastAPI + Celery + Redis + PostgreSQL
6. ✅ **Failure handling** – Timeouts, retries, circuit breakers
7. ✅ **Docker Compose** – Orchestrate multiple services
8. ✅ **Request tracing** – Follow requests across services

**Congratulations!** You've now built production-grade distributed systems. You understand how tech companies scale applications to handle millions of users with independent, resilient services.

**This completes Phase 4: Automation & Workflow Integration!**
