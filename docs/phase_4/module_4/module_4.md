---
tags:
  - Intermediate
  - Phase 4
---

# Module 4: Logging, Monitoring & Error Handling

When you run Python and `print()` something, it disappears. You can't see it later. But in production, you need history: "What happened at 3:15am when the service crashed?" Logging is how we build that history. Logs are records of everything: requests, errors, performance, decisions. Smart logging answers "Why did that happen?" when you're debugging at 2am.

This module teaches you to log like a professional and handle errors gracefully so systems continue running and operators understand what failed.

---

## 🎯 What You Will Learn

By the end of this module, you will:

- Understand logging vs printing
- Use Python's logging module with levels
- Write structured JSON logs (better for machines)
- Log in background tasks and scheduled jobs
- Use health check endpoints
- Handle errors: try/except, custom exceptions
- Understand fail-fast vs fail-gracefully
- Send alerts to Slack on errors
- Know the observability pillars: logs, metrics, traces
- Build a production logging system

---

## 🧠 Concept Explained: Logging

### Problem: Printing vs Logging

**Printing (Bad for production):**

```python
print("User logged in")
# Where does it go? Terminal? Lost if process restarts.
```

**Logging (Good):**

```python
logger.info("User logged in")
# Goes to file, service, database. Persists forever.
```

### Why Logging Matters

In production, you can't watch the terminal. You need:

1. **History:** What happened over the past hour/day/week?
2. **Search:** Find all errors in database requests
3. **Alerts:** Notify ops when something breaks
4. **Patterns:** Understand systemic problems ("API slow every Tuesday at 9am")

### Log Levels

Think of log levels as importance:

```
DEBUG   - Detailed debugging info (variable values)
INFO    - General info (process started, user created)
WARNING - Something unusual (retried, slow response)
ERROR   - Something failed (API down, invalid input)
CRITICAL - System may crash or lose data (out of memory)
```

### Structured vs Unstructured Logs

**Unstructured (human-readable, hard to parse):**

```
2024-03-15 14:22:33 User alice@example.com logged in from 192.168.1.1
2024-03-15 14:23:15 API call to orders took 2.3 seconds
```

**Structured (machine-readable, easy to query):**

```json
{"timestamp": "2024-03-15T14:22:33Z", "event": "login", "user": "alice@example.com", "ip": "192.168.1.1"}
{"timestamp": "2024-03-15T14:23:15Z", "event": "api_call", "endpoint": "/orders", "duration_ms": 2300}
```

Machines can query structured logs: "Show me all logins from suspicious IPs in the past hour."

---

## 🔍 How It Works

### Logging Flow

```
Your Code
   ↓
logger.info("User logged in")
   ↓
Handler (where to send?)
   ├── File Handler → /var/log/app.log
   ├── Stream Handler → System stdout/stderr
   └── HTTP Handler → Logging service (DataDog, etc.)
   ↓
Formatter (how to format?)
   ├── Plain text: "2024-03-15 14:22:33 INFO User logged in"
   └── JSON: {"timestamp": "...", "level": "INFO", "message": "..."}
   ↓
Output
```

### Error Handling Flow

```
Code attempts action
   ↓
Success? ─ YES ─→ Return result
   ↓ NO
   ↓
Catch exception
   ↓
Log error details
   ↓
Fail-Fast: Stop, return error
OR
Fail-Gracefully: Use default value, continue
   ↓
Return response to user
```

---

## 🛠️ Step-by-Step Guide

### Basic Logging Setup

#### Step 1: Import logging

```python
import logging
```

#### Step 2: Create Logger

```python
logger = logging.getLogger(__name__)
```

#### Step 3: Set Level

```python
logger.setLevel(logging.DEBUG)  # Capture all levels
```

#### Step 4: Add Handler (where to send logs)

```python
# File handler
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.INFO)

# Add to logger
logger.addHandler(file_handler)
```

#### Step 5: Set Formatter

```python
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
file_handler.setFormatter(formatter)
```

#### Step 6: Use Logger

```python
logger.debug("Detailed info")      # Only if DEBUG enabled
logger.info("Process started")     # General info
logger.warning("Slow response")    # Something unusual
logger.error("Could not connect")  # Error occurred
logger.critical("System down")     # Critical problem
```

### Logging Background Tasks

#### Celery Task Logging

```python
@celery_app.task
def process_order(order_id):
    logger.info(f"Processing order {order_id}")

    try:
        # Attempt to process
        order = fetch_order(order_id)
        logger.debug(f"Fetched order: {order}")

        result = process_order_logic(order)
        logger.info(f"✓ Order processed successfully: {result}")
        return result

    except OrderNotFound as e:
        logger.warning(f"Order not found: {order_id}")
        raise

    except ProcessingError as e:
        logger.error(f"Processing failed for order {order_id}: {e}")
        raise
```

### Error Handling

#### Try/Except Pattern

```python
try:
    # Attempt risky operation
    response = requests.get(api_url, timeout=5)
    response.raise_for_status()
    return response.json()

except requests.Timeout:
    # Specific exception: network timeout
    logger.warning(f"API timeout after 5 seconds")
    return None  # Fail gracefully

except requests.ConnectionError as e:
    # Specific exception: can't connect
    logger.error(f"Cannot reach API: {e}")
    return None

except Exception as e:
    # Catch-all (bad practice generally, but sometimes needed)
    logger.critical(f"Unexpected error in API call: {e}")
    raise  # Re-raise to caller
```

#### Custom Exceptions

```python
class OrderProcessingError(Exception):
    """Order processing failed"""
    pass

try:
    if order.status != 'pending':
        raise OrderProcessingError(f"Invalid status: {order.status}")

    process(order)

except OrderProcessingError as e:
    logger.error(f"Order error: {e}")
    return {"error": str(e)}
```

### Health Checks

#### FastAPI Health Endpoint

```python
@app.get("/health")
def health_check():
    """System health check"""
    try:
        # Check database
        db.ping()

        # Check cache
        cache.ping()

        # Check external service
        requests.get('external-api.com/ping', timeout=2)

        return {
            "status": "healthy",
            "database": "OK",
            "cache": "OK",
            "external_api": "OK"
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
```

### Alerts on Error

#### Slack Notification

```python
import requests

def send_slack_alert(message, severity="warning"):
    """Send alert to Slack"""
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')

    if not webhook_url:
        logger.warning("Slack webhook not configured")
        return

    color_map = {
        "info": "#36a64f",
        "warning": "#ff9900",
        "error": "#c41e3a"
    }

    payload = {
        "attachments": [
            {
                "color": color_map.get(severity, "#999999"),
                "title": f"{severity.upper()}: {message}",
                "text": f"Occurred at {datetime.now().isoformat()}",
                "footer": "System Alerts"
            }
        ]
    }

    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        logger.info(f"Slack alert sent: {message}")

    except Exception as e:
        logger.error(f"Failed to send Slack alert: {e}")
```

**Use in error handler:**

```python
try:
    critical_operation()
except CriticalError as e:
    logger.critical(f"Critical error: {e}")
    send_slack_alert(f"Critical error occurred: {e}", severity="error")
```

---

## 💻 Code Examples

### Example 1: Comprehensive Logging Setup

```python
# logging_config.py - Centralized logging configuration
import logging
import logging.handlers
import json
import os
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Format logs as JSON for machine parsing"""

    def format(self, record):
        # Create JSON structure
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_data)

def setup_logging():
    """Configure logging for the entire application"""

    # Create logger
    logger = logging.getLogger('myapp')
    logger.setLevel(logging.DEBUG)

    # Create formatters
    json_formatter = JSONFormatter()
    text_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # File handler: structured JSON logs
    json_file_handler = logging.FileHandler('logs/app.json')
    json_file_handler.setLevel(logging.INFO)
    json_file_handler.setFormatter(json_formatter)
    logger.addHandler(json_file_handler)

    # File handler: text logs (for humans)
    text_file_handler = logging.FileHandler('logs/app.log')
    text_file_handler.setLevel(logging.DEBUG)
    text_file_handler.setFormatter(text_formatter)
    logger.addHandler(text_file_handler)

    # Rotating file handler (prevents huge log files)
    rotating_handler = logging.handlers.RotatingFileHandler(
        'logs/app_rotating.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5           # Keep 5 old files
    )
    rotating_handler.setLevel(logging.WARNING)
    rotating_handler.setFormatter(text_formatter)
    logger.addHandler(rotating_handler)

    # Console handler: for development
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(text_formatter)
    logger.addHandler(console_handler)

    return logger

# Usage
logger = setup_logging()

logger.info("Application started")
logger.warning("This is a warning")
logger.error("An error occurred")
```

### Example 2: Logging in Celery Tasks

```python
# celery_app.py - Celery with structured logging
from celery import Celery
import logging
import requests

# Setup logging
logger = logging.getLogger('celery_tasks')

celery_app = Celery('myapp')
celery_app.conf.broker_url = 'redis://localhost:6379/0'

@celery_app.task(bind=True, max_retries=3)
def scrape_website(self, url: str):
    """Scrape website with logging"""

    logger.info(f"Starting scrape task for {url}")
    task_id = self.request.id

    try:
        logger.debug(f"Task ID: {task_id}, Attempt: {self.request.retries + 1}")

        # Scrape
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.text[:500]  # First 500 chars

        logger.info(
            f"✓ Scrape successful",
            extra={
                'task_id': task_id,
                'url': url,
                'content_length': len(response.text)
            }
        )

        return {'status': 'success', 'data': data}

    except requests.Timeout:
        logger.warning(
            f"⏱ Scrape timeout after 10 sec",
            extra={'task_id': task_id, 'url': url}
        )

        # Retry with exponential backoff
        raise self.retry(exc=Exception("Timeout"), countdown=60)

    except requests.RequestException as exc:
        logger.error(
            f"✗ Scrape failed",
            extra={'task_id': task_id, 'url': url, 'error': str(exc)},
            exc_info=True
        )

        raise self.retry(exc=exc, countdown=30, max_retries=3)

    except Exception as exc:
        logger.critical(
            f"CRITICAL: Unexpected error in scrape task",
            extra={'task_id': task_id, 'url': url},
            exc_info=True
        )
        raise
```

### Example 3: FastAPI with Logging and Health Checks

```python
# main.py - FastAPI app with comprehensive logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
import os
import redis
import psycopg2
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Logged API")

# Dependency tracking
class ServiceHealth(BaseModel):
    database: str
    redis_cache: str
    overall: str

@app.on_event("startup")
def startup():
    """Log application startup"""
    logger.info(
        f"🚀 API starting up",
        extra={
            'environment': os.getenv('ENV', 'development'),
            'version': '1.0.0'
        }
    )

@app.on_event("shutdown")
def shutdown():
    """Log application shutdown"""
    logger.info("🛑 API shutting down")

@app.get("/health", response_model=ServiceHealth)
def health_check():
    """Health check endpoint with detailed status"""
    health_status = ServiceHealth(
        database="unknown",
        redis_cache="unknown",
        overall="starting"
    )

    try:
        # Check database
        conn = psycopg2.connect(
            "dbname=mydb user=postgres host=localhost"
        )
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        health_status.database = "healthy"

        logger.debug("✓ Database health check passed")

    except Exception as e:
        logger.error(f"✗ Database health check failed: {e}")
        health_status.database = "unhealthy"

    try:
        # Check Redis
        r = redis.Redis(host='localhost', port=6379)
        r.ping()
        health_status.redis_cache = "healthy"

        logger.debug("✓ Redis health check passed")

    except Exception as e:
        logger.error(f"✗ Redis health check failed: {e}")
        health_status.redis_cache = "unhealthy"

    # Overall status
    if health_status.database == "healthy" and health_status.redis_cache == "healthy":
        health_status.overall = "healthy"
        logger.info(f"Overall health: HEALTHY")
    else:
        health_status.overall = "degraded"
        logger.warning(f"Overall health: DEGRADED")

    return health_status

class OrderRequest(BaseModel):
    customer_id: int
    amount: float

@app.post("/orders")
def create_order(order: OrderRequest):
    """Create order with error handling"""
    logger.info(f"Creating order for customer {order.customer_id}, amount: ${order.amount}")

    try:
        # Validate
        if order.amount <= 0:
            raise ValueError("Order amount must be positive")

        if order.customer_id <= 0:
            raise ValueError("Invalid customer ID")

        logger.debug(f"Order validation passed")

        # Process
        order_id = save_order_to_db(order)

        logger.info(
            f"✓ Order created successfully",
            extra={
                'order_id': order_id,
                'customer_id': order.customer_id,
                'amount': order.amount
            }
        )

        return {"order_id": order_id, "status": "created"}

    except ValueError as e:
        logger.warning(f"Invalid order request: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(
            f"Failed to create order",
            extra={'customer_id': order.customer_id},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Internal server error")

def save_order_to_db(order: OrderRequest):
    """Save order and return ID"""
    # Simulate database operation
    return 12345
```

---

## ⚠️ Common Mistakes

### Mistake 1: Over-Logging in Production

**WRONG:**

```python
# Logs every variable value (huge log files)
for item in items:
    logger.debug(f"Item: {item}")  # 1 million log lines!
```

**RIGHT:**

```python
# Log once per loop iteration or at key points
logger.debug(f"Processing {len(items)} items")
for item in items:
    if item.is_critical():
        logger.warning(f"Critical item found: {item.id}")
```

### Mistake 2: Catching Everything

**WRONG:**

```python
try:
    dangerous_operation()
except:
    logger.error("Something went wrong")  # What??? How to debug?
```

**RIGHT:**

```python
try:
    dangerous_operation()
except SpecificError as e:
    logger.error(f"Specific error occurred: {e}", exc_info=True)
except Exception as e:
    logger.critical(f"Unexpected error: {e}", exc_info=True)
    raise  # Re-raise so caller knows
```

### Mistake 3: Not Logging Context

**WRONG:**

```python
logger.error("Order processing failed")
# Which order? When? What customer?
```

**RIGHT:**

```python
logger.error(
    "Order processing failed",
    extra={
        'order_id': order.id,
        'customer_id': order.customer_id,
        'timestamp': datetime.now().isoformat()
    }
)
```

---

## ✅ Exercises

### Easy: Basic Logging

1. Create logger with file handler
2. Log at different levels: DEBUG, INFO, WARNING, ERROR
3. View log file
4. Verify logs persisted

### Medium: Error Handling with Logging

1. Create function that fetches API data
2. Add try/except with specific exception types
3. Log errors with full context
4. Return graceful error response

### Hard: Full Application Logging

1. Create FastAPI app with health check endpoint
2. Add structured JSON logging to file
3. Log all requests and responses
4. Test health check with good and degraded services
5. View logs in JSON format

---

## 🏗️ Mini Project: Complete Logging Setup

Build a production-ready logging system for the book price prediction API from earlier phases.

### Requirements

1. Structured JSON logging to file
2. Rotating log files (don't grow unlimited)
3. Log all predictions with input, output, latency
4. Log errors with full stack traces
5. Health check endpoint showing system status
6. Alert to Slack on errors

### Implementation

```python
# main.py - Book Price API with comprehensive logging
from fastapi import FastAPI, HTTPException
import logging
import json
import os
import time
from datetime import datetime
import joblib
from pydantic import BaseModel
import requests

# JSON logging
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
        }
        if record.exc_info:
            log_obj['exception'] = self.formatException(record.exc_info)
        return json.dumps(log_obj)

handler = logging.FileHandler('logs/api.json')
handler.setFormatter(JSONFormatter())
logger = logging.getLogger('book_api')
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# Initialize app and model
app = FastAPI()
model = None

class BookData(BaseModel):
    pages: int
    rating: float
    author_books: int = 1

@app.on_event("startup")
def load_model():
    global model
    logger.info("Loading model on startup")
    model = joblib.load('book_price_model.pkl')

@app.post("/predict")
def predict(book: BookData):
    """Predict with logging"""
    start_time = time.time()

    logger.info(f"Prediction request", extra={
        'pages': book.pages,
        'rating': book.rating
    })

    try:
        # Predict
        import numpy as np
        features = np.array([[book.pages, book.rating, book.author_books]])
        price = model.predict(features)[0]

        latency = time.time() - start_time

        logger.info(f"Prediction successful", extra={
            'pages': book.pages,
            'predicted_price': float(price),
            'latency_ms': latency * 1000
        })

        return {'price': float(price)}

    except Exception as e:
        logger.error(f"Prediction failed", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    """Health check with logging"""
    if model is None:
        logger.error("Model not loaded")
        raise HTTPException(status_code=503, detail="Model not ready")

    logger.info("Health check passed")
    return {"status": "healthy"}
```

---

## 📚 Summary

In this module, you learned:

1. ✅ **Logging fundamentals** – Why logs matter
2. ✅ **Log levels** – DEBUG, INFO, WARNING, ERROR, CRITICAL
3. ✅ **Structured logging** – JSON for machines
4. ✅ **Error handling** – Try/except, custom exceptions
5. ✅ **Health checks** – System status endpoints
6. ✅ **Alerts** – Slack notifications on errors
7. ✅ **Best practices** – Context, not over-logging

Next module: integrating all these pieces into a cohesive production system.
