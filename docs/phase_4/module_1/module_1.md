---
tags:
  - Intermediate
  - Phase 4
---

# Module 1: Background Tasks with Celery and RQ

Some work takes time. When you order pizza, the restaurant doesn't make you wait for the entire process—from dough to oven to box—before telling you it's done. Instead, they take your order, give you a ticket, and you can leave. A worker makes your pizza. Later, you come back to collect it. In web development, long tasks work the same way. When a user hits an endpoint, you don't want them waiting 30 seconds while their data scrapes. Instead, you queue the task (like dropping a letter in a mailbox) and return immediately. A worker picks up that task later and completes it in the background.

This module teaches you to architect systems where work happens asynchronously, without blocking the user.

---

## 🎯 What You Will Learn

By the end of this module, you will:

- Understand what a background task is and why you need them
- Know the difference between synchronous and asynchronous execution
- Follow the worker pattern: producer, queue, worker, result
- Install and configure Celery with Redis
- Write tasks using the `@task` decorator
- Call and track tasks with task IDs
- Check results without blocking
- Chain dependent tasks together
- Use RQ as a simpler alternative to Celery
- Know when to choose Celery vs RQ
- Handle retries and timeouts
- Integrate background tasks with FastAPI

---

## 🧠 Concept Explained: Background Tasks

### The Problem with Synchronous Code

When you write regular Python:

```python
def send_email(user_email):
    # This blocks everything until email is sent
    smtp.send(user_email, "Welcome!")
    return "Email sent"

@app.post("/register")
def register(user):
    # User waits 5 seconds for email to send
    send_email(user.email)
    return {"status": "registered"}
```

**Problems:**

- User waits 5 seconds for the response
- If email fails, user sees an error
- If 100 users register at once, 100 emails send sequentially (500 seconds total!)
- User experiences feels slow

### The Solution: Asynchronous Tasks

Instead, split into producer and worker:

```python
# Producer (fast, returns immediately)
@app.post("/register")
def register(user):
    task = send_email.delay(user.email)  # Queue it
    return {"status": "registered", "task_id": task.id}

# Worker (runs later, in background)
@task
def send_email(user_email):
    # This runs when a worker picks it up
    smtp.send(user_email, "Welcome!")
    return "Email sent"
```

**Benefits:**

- User gets response in 10ms
- Email sends in background
- 100 users → all emails sent in parallel
- If email fails, system retries automatically

### Real-World Analogy

Think of a coffee shop:

- **Synchronous (bad):** Barista serves 1 customer at a time, everyone waits
- **Asynchronous (good):** Customers order, get a number, sit down. Baristas make drinks in parallel. When ready, they call your number.

The "result pickup" is checking if your task is done.

---

## 🔍 How It Works

### The Worker Pattern

```
Client                Queue               Worker
  ↓                     ↓                    ↓
POST /task          [Task 1]           Process Task 1
  ↓                 [Task 2]           Process Task 2
Return task_id      [Task 3]           Process Task 3
immediately         [Task 4]           → Store result
  ↓
GET /result?id=1
  ↓
Return result
(either done or still processing)
```

### Celery + Redis Architecture

```
FastAPI App              Redis Queue         Celery Worker
─────────────            ──────────────      ──────────────
@app.post()              [Queue Name]        @celery.task
send_email.delay()  →    [Task 1]       →    def send_email(email)
task_id returned         [Task 2]           ↓
                         [Task 3]           Execute
user_id: "abc-123"       [...]              ↓
                                            Store result
                                            in Redis
                                            ↓
Query result ←── Redis ←─ Result Cache
```

---

## 🛠️ Step-by-Step Guide

### Step 1: Install Celery and Redis

```bash
pip install celery redis
# Redis also needs to run (Docker recommended)
docker run -d -p 6379:6379 redis:7-alpine
```

### Step 2: Configure Celery

```python
# celery_app.py
from celery import Celery

app = Celery('myapp')
app.conf.broker_url = 'redis://localhost:6379/0'
app.conf.result_backend = 'redis://localhost:6379/0'
```

### Step 3: Define a Task

```python
from celery_app import app

@app.task
def send_email(email):
    # This runs in a worker process
    return f"Sent to {email}"
```

### Step 4: Call the Task (from FastAPI)

```python
from fastapi import FastAPI
from celery_app import app

app = FastAPI()

@app.post("/send")
def trigger_send(email: str):
    # Queue the task, get task ID, return immediately
    task = send_email.delay(email)
    return {"task_id": task.id}
```

### Step 5: Check the Result

```python
from celery.result import AsyncResult

@app.get("/result/{task_id}")
def get_result(task_id: str):
    result = AsyncResult(task_id, app=celery_app)

    if result.state == 'PENDING':
        return {"status": "pending"}
    elif result.state == 'SUCCESS':
        return {"status": "success", "result": result.result}
    else:
        return {"status": result.state}
```

### Step 6: Start the Worker

```bash
celery -A celery_app worker --loglevel=info
```

### Step 7: Task Chaining

```python
from celery import chain

# Chain: do A, then B, then C (passing results forward)
pipeline = chain(
    fetch_data.s(url),      # s() = signature
    clean_data.s(),         # receives fetch_data result as first arg
    save_data.s()
)
result = pipeline.apply_async()
```

### Step 8: Task Groups (Parallel)

```python
from celery import group

# Group: do A, B, C in parallel
parallel_tasks = group(
    send_email.s("alice@example.com"),
    send_email.s("bob@example.com"),
    send_email.s("charlie@example.com")
)
result = parallel_tasks.apply_async()
```

---

## 💻 Code Examples

### Example 1: FastAPI + Celery Complete Setup

```python
# celery_app.py - Initialize Celery
import os
from celery import Celery

# Create Celery app with Redis broker
celery_app = Celery(
    __name__,
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
)

# Configure task settings
celery_app.conf.update(
    task_serializer='json',           # Use JSON for task serialization
    accept_content=['json'],          # Only accept JSON
    result_serializer='json',         # Serialize results as JSON
    timezone='UTC',                   # Use UTC for timestamps
    enable_utc=True,
    task_track_started=True,          # Track when tasks start
    task_time_limit=30 * 60,          # Hard limit: 30 minutes
    task_soft_time_limit=25 * 60,     # Soft limit: 25 minutes
)

# main.py - FastAPI app with tasks
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from celery_app import celery_app
from celery.result import AsyncResult
import time

app = FastAPI(title="Task Queue Demo")

# Task definitions
@celery_app.task(bind=True, max_retries=3)
def scrape_website(self, url: str):
    """Scrape website in background with retry logic"""
    try:
        # Simulate scraping (in real app: use requests/BeautifulSoup)
        import requests
        from bs4 import BeautifulSoup

        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract titles
        titles = [h.text for h in soup.find_all('h1')]
        return {
            "url": url,
            "titles": titles[:5],  # First 5 titles
            "status": "success"
        }

    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60)

@celery_app.task
def process_data(raw_data: str):
    """Process data (called after scrape)"""
    time.sleep(2)  # Simulate processing
    return {
        "processed": raw_data.upper(),
        "word_count": len(raw_data.split())
    }

@celery_app.task
def send_notification(user_email: str, message: str):
    """Send notification (simulated)"""
    print(f"Sending to {user_email}: {message}")
    return {"sent_to": user_email}

# Request/Response models
class ScrapeRequest(BaseModel):
    url: str

class TaskStatus(BaseModel):
    task_id: str
    state: str
    result: dict = None
    error: str = None

# Endpoints
@app.post("/scrape", response_model=dict)
def start_scrape(request: ScrapeRequest):
    """Queue a scraping job, return task ID immediately"""
    task = scrape_website.delay(request.url)
    return {
        "task_id": task.id,
        "message": "Scrape job queued. Check /result/{task_id} for result."
    }

@app.get("/result/{task_id}", response_model=TaskStatus)
def get_result(task_id: str):
    """Check if task is done and get result"""
    result = AsyncResult(task_id, app=celery_app)

    # Task states: PENDING, STARTED, SUCCESS, FAILURE, RETRY, REVOKED
    if result.state == 'PENDING':
        return TaskStatus(task_id=task_id, state='PENDING', result=None)

    elif result.state == 'STARTED':
        return TaskStatus(task_id=task_id, state='STARTED', result=None)

    elif result.state == 'SUCCESS':
        return TaskStatus(
            task_id=task_id,
            state='SUCCESS',
            result=result.result
        )

    elif result.state == 'FAILURE':
        return TaskStatus(
            task_id=task_id,
            state='FAILURE',
            error=str(result.info)
        )

    else:
        return TaskStatus(task_id=task_id, state=result.state)

@app.post("/chain-tasks", response_model=dict)
def start_chain():
    """Chain: scrape → process → notify"""
    from celery import chain

    # Chain of tasks: each feeds result to next
    pipeline = chain(
        scrape_website.s("https://example.com"),
        process_data.s(),
        send_notification.s("admin@example.com", "Processing done!")
    )

    # Apply with array of results
    result = pipeline.apply_async()

    return {
        "task_id": result.id,
        "pipeline": "scrape → process → notify"
    }

@app.post("/parallel-tasks", response_model=dict)
def start_parallel():
    """Parallel: send 3 emails at once"""
    from celery import group

    # Group of tasks: run in parallel
    parallel = group(
        send_notification.s("alice@example.com", "Hello Alice"),
        send_notification.s("bob@example.com", "Hello Bob"),
        send_notification.s("charlie@example.com", "Hello Charlie")
    )

    result = parallel.apply_async()

    return {
        "task_id": result.id,
        "message": "3 emails queued in parallel"
    }

@app.get("/stats")
def get_stats():
    """Show active tasks"""
    inspect = celery_app.control.inspect()
    stats = inspect.stats()
    return {
        "active_workers": len(stats) if stats else 0,
        "active_tasks": inspect.active()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Run it:**

```bash
# Terminal 1: Start Celery worker
celery -A main celery_app worker --loglevel=info

# Terminal 2: Start FastAPI
python -m uvicorn main:app --reload

# Terminal 3: Test
curl -X POST http://localhost:8000/scrape -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
# Returns: {"task_id": "abc-123", ...}

curl http://localhost:8000/result/abc-123
# Returns: {"task_id": "abc-123", "state": "SUCCESS", "result": {...}}
```

### Example 2: RQ (Simpler Alternative)

```python
# Using RQ instead of Celery (simpler API, fewer features)
from redis import Redis
from rq import Queue
from fastapi import FastAPI

# Create queue
redis_conn = Redis(host='localhost', port=6379)
q = Queue(connection=redis_conn)

app = FastAPI()

def send_email(email):
    """Regular function (not decorated)"""
    return f"Email sent to {email}"

@app.post("/send-rq")
def send_with_rq(email: str):
    """Queue job with RQ"""
    # Enqueue the function
    job = q.enqueue(send_email, email)
    return {"job_id": job.id}

@app.get("/result-rq/{job_id}")
def get_rq_result(job_id: str):
    """Get RQ job result"""
    from rq.job import Job

    job = Job.fetch(job_id, connection=redis_conn)

    if job.is_finished:
        return {"status": "done", "result": job.result}
    elif job.is_failed:
        return {"status": "failed", "error": job.exc_info}
    else:
        return {"status": job.get_status()}
```

**RQ Worker:**

```bash
rq worker
```

---

## ⚠️ Common Mistakes

### Mistake 1: Calling Task Synchronously

**WRONG:**

```python
@app.post("/register")
def register(user):
    # This BLOCKS! Task runs immediately in this process
    result = send_email(user.email)
    return {"status": "done"}
```

**RIGHT:**

```python
@app.post("/register")
def register(user):
    # Queue the task, return immediately
    task = send_email.delay(user.email)
    return {"task_id": task.id}
```

### Mistake 2: Forgetting to Start Worker

Without a worker running, tasks queue up but never execute:

```bash
# You MUST run this separately
celery -A celery_app worker --loglevel=info
```

### Mistake 3: Not Handling Task Failure

**WRONG:**

```python
@celery_app.task
def process_order(order_id):
    # If API fails, task fails silently
    response = requests.get("external-api.com/order")
    return response.json()
```

**RIGHT:**

```python
@celery_app.task(bind=True, max_retries=3)
def process_order(self, order_id):
    try:
        response = requests.get("external-api.com/order", timeout=10)
        response.raise_for_status()
        return response.json()
    except RequestException as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60)
```

---

## ✅ Exercises

### Easy: Basic Task Queue

1. Create a Celery task that sleeps 5 seconds
2. Call it from FastAPI endpoint
3. Return task ID
4. Query result endpoint until done

### Medium: Chained Tasks

1. Create 2 tasks: `fetch_data()` and `process_data()`
2. Chain them with `.s()` syntax
3. Verify result from second task receives output of first task
4. Add error handling if fetch fails

### Hard: Distributed System

1. Run FastAPI + Celery Worker in separate processes
2. Queue 10 long-running tasks
3. Start 2 workers on different machines (or simulated with sleep)
4. Observe tasks distributed across workers
5. Add monitoring endpoint showing which worker processed each task

---

## 🏗️ Mini Project: Async ML Predictions

Convert the book price prediction endpoint from Module 3-5 into an async background job system.

### Requirements

1. POST `/predict-async` accepts book data, queues prediction, returns task ID
2. GET `/result/{task_id}` returns prediction (or "pending" if still processing)
3. Task simulates slow model inference (add sleep)
4. Celery worker processes predictions in background
5. Handle task timeout and retry

### Implementation

```python
# main.py with async predictions
from fastapi import FastAPI
from pydantic import BaseModel
from celery_app import celery_app
from celery.result import AsyncResult
import joblib
import time

app = FastAPI()
model = joblib.load('book_price_model.pkl')
scaler = joblib.load('scaler.pkl')

class BookData(BaseModel):
    pages: int
    rating: float
    author_books: int = 1

@celery_app.task(bind=True)
def predict_price_async(self, pages: int, rating: float, author_books: int):
    """Background task: predict book price"""
    import numpy as np

    try:
        # Simulate slow inference
        time.sleep(3)

        # Prepare features
        features = np.array([[pages, rating, author_books]])
        features_scaled = scaler.transform(features)

        # Predict
        price = model.predict(features_scaled)[0]

        return {
            "pages": pages,
            "rating": rating,
            "predicted_price": float(price),
            "confidence": "high" if 100 <= pages <= 600 else "medium"
        }

    except Exception as exc:
        # Retry up to 2 times with 10 second delay
        raise self.retry(exc=exc, countdown=10, max_retries=2)

@app.post("/predict-async")
def predict_async(book: BookData):
    """Queue prediction, return task ID"""
    task = predict_price_async.delay(
        book.pages,
        book.rating,
        book.author_books
    )
    return {
        "task_id": task.id,
        "message": "Prediction queued"
    }

@app.get("/prediction-result/{task_id}")
def get_prediction(task_id: str):
    """Get prediction result"""
    result = AsyncResult(task_id, app=celery_app)

    if result.state == 'PENDING':
        return {"status": "processing"}
    elif result.state == 'SUCCESS':
        return {"status": "ready", "prediction": result.result}
    elif result.state == 'FAILURE':
        return {"status": "failed", "error": str(result.info)}
    else:
        return {"status": result.state}
```

**Test:**

```bash
# Terminal 1: Worker
celery -A main celery_app worker --loglevel=info

# Terminal 2: API
python -m uvicorn main:app --reload

# Terminal 3: Test
curl -X POST http://localhost:8000/predict-async \
  -H "Content-Type: application/json" \
  -d '{"pages": 300, "rating": 4.5}'

# Copy task_id, then:
curl http://localhost:8000/prediction-result/{task_id}
```

---

## 📚 Summary

In this module, you learned:

1. ✅ **Background tasks** – Why queuing work matters
2. ✅ **Producer/Worker pattern** – Asynchronous architecture
3. ✅ **Celery + Redis** – Production task queue system
4. ✅ **Task chaining** – Sequential dependent tasks
5. ✅ **Task groups** – Parallel execution
6. ✅ **RQ** – Simpler queue alternative
7. ✅ **Retries** – Automatic failure recovery
8. ✅ **Result checking** – Non-blocking status queries
9. ✅ **Integration** – FastAPI + Celery + Redis

You can now build systems where long-running work doesn't block users. Next module: message queues for more complex workflows.
j) ## 🔗 What's Next (link to next module)

3. CODE QUALITY
   - Every code block must be complete and runnable as-is.
   - Every single line must have an inline comment.
   - Use Python unless the module is specifically about another tool.
   - Show expected output after each code block in a separate
     code block labeled `# Expected output`.

4. DIAGRAMS
   - Include at least one Mermaid diagram OR ASCII diagram.
   - Diagrams must show data flow, not just boxes with names.

5. ADMONITIONS — use MkDocs Material admonitions:
   - !!! tip for shortcuts and best practices
   - !!! warning for things that often break
   - !!! note for important context
   - !!! danger for things that can cause data loss or bugs

6. CROSS-LINKS
   - Reference earlier modules when building on prior concepts.
   - Example: "Remember virtual environments from Module 1?"

7. LENGTH
   - Do not summarise. Be thorough.
   - Each section should be detailed enough that a beginner
     can follow without searching anything else.
     ============================================================
     PROMPT END
     -->

!!! note "Module content coming soon"
Use the AI prompt in the comment above to generate the full
content for this module. Paste it into Claude, ChatGPT, or
any AI assistant.
