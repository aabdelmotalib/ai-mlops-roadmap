---
tags:
  - Intermediate
  - Phase 4
---

# Module 2: Message Queues (Redis & RabbitMQ)

Think of a coffee shop again. One barista can't handle 100 simultaneous orders if customers all yell at once. So there's a queue: one person at a time steps forward, orders, and moves aside. The barista works through orders in order. When orders get complex (add a second register, third barista), the queue becomes the central coordination point. Message queues work exactly like this: they decouple producers from consumers. One service doesn't care if 10 other services are listening or when they process the message. The queue handles delivery.

This module teaches you to use message queues for scalable, decoupled systems. We'll contrast Redis (simple, fast) with RabbitMQ (complex, guaranteed delivery).

---

## 🎯 What You Will Learn

By the end of this module, you will:

- Understand what a message queue solves
- Know producer-consumer patterns
- Use Redis as a simple queue with redis-py
- Understand Redis Streams for complex workflows
- Use RabbitMQ for guaranteed message delivery
- Know exchanges, queues, and routing
- Implement competing consumers (multiple workers)
- Handle message acknowledgement and retries
- Deal with dead-letter queues
- Choose between Redis and RabbitMQ
- Build a complete producer/consumer system

---

## 🧠 Concept Explained: Message Queues

### The Problem: Direct Communication

When services talk directly:

```
API sends request to Worker
┌──────────┐     REQUEST      ┌────────┐
│   API    │ ─────────────→   │ Worker │
└──────────┘                  └────────┘
                              ↓ (Worker busy, Request blocked!)
```

**Problems:**

- Worker crashes → request lost
- Worker slow → API waits
- 1000 requests → 1000 blocked processes
- Hard to scale or retry

### The Solution: Message Queue

```
┌──────────┐     PUBLISH      ┌──────────┐      SUBSCRIBE      ┌────────┐
│   API    │ ────────────→    │  Queue   │  ───────────────→   │ Worker │
└──────────┘ (returns fast)   └──────────┘                      └────────┘
                              │ Message 1 │
                              │ Message 2 │  ← Can process at own pace
                              │ Message 3 │
```

**Benefits:**

- API returns immediately
- Worker processes at own pace
- Multiple workers handle messages in parallel
- Messages persist if worker crashes

### Coffee Shop Analogy

- **Direct:** Customer yells order → barista stops everything
- **Queue:** Customer writes order on ticket → ticket goes in bin → barista pulls tickets in order, can have multiple baristas

---

## 🔍 How It Works

### Key Concepts

**Producer** = Service that sends messages (the customer ordering)
**Consumer** = Service that processes messages (the barista)
**Queue** = Holds messages until processed (the order bin)
**Message** = Data being passed (the order ticket)
**Acknowledgement** = "Got it" signal (barista checks off completed order)
**Dead Letter Queue** = Failed messages go here (orders that couldn't be made)

### Redis vs RabbitMQ Architecture

**Redis (Simple):**

```
Producer                    Redis List/Stream       Consumer
(LPUSH)     ─message→       [msg1]                 (LPOP/XREAD)
                            [msg2]  ← LPOP ─────  Worker processes
                            [msg3]
```

**RabbitMQ (Robust):**

```
Producer                   Exchange            Queue              Consumer
(publish)   ──message──→  [Routing            [messages]  ─→    (subscribe)
                           Logic]             [persistent
                                              to disk]
                                              Acknowledgement ──→
```

### Message Flow

```
1. Producer sends message to Queue
2. Message stored in Queue (or Exchange first)
3. Consumer receives message
4. Consumer processes
5. Consumer sends ACK (acknowledgement)
6. Queue removes message
7. If no ACK: message sent to Dead Letter Queue or retried
```

---

## 🛠️ Step-by-Step Guide

### Using Redis: Simple Queue

#### Step 1: Install and Run Redis

```bash
# With Docker
docker run -d -p 6379:6379 redis:7-alpine

# Or install locally (macOS)
brew install redis
redis-server
```

#### Step 2: Install redis-py

```bash
pip install redis
```

#### Step 3: Produce Messages

```python
import redis

r = redis.Redis(host='localhost', port=6379)

# Push message to queue
r.lpush('tasks', 'scrape_website:https://example.com')
r.lpush('tasks', 'send_email:albert@example.com')
```

#### Step 4: Consume Messages

```python
import redis

r = redis.Redis(host='localhost', port=6379)

while True:
    # Pop from queue (blocks if empty)
    message = r.brpop('tasks', timeout=1)
    if message:
        task_type, task_data = message[1].decode().split(':')
        process_task(task_type, task_data)
```

#### Step 5: Subscribe Pattern (Pub/Sub)

```python
# Publisher
r.publish('notifications', 'Alert: System down')

# Subscriber
ps = r.pubsub()
ps.subscribe('notifications')

for message in ps.listen():
    if message['type'] == 'message':
        print(f"Received: {message['data']}")
```

### Using RabbitMQ: Guaranteed Delivery

#### Step 1: Install and Run RabbitMQ

```bash
# With Docker
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:4-management

# Access management UI
# http://localhost:15672 (user: guest, password: guest)
```

#### Step 2: Install pika (Python Client)

```bash
pip install pika
```

#### Step 3: Declare Queue and Send

```python
import pika

# Connect
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Declare queue (idempotent: won't error if exists)
channel.queue_declare(queue='tasks', durable=True)

# Send message
channel.basic_publish(
    exchange='',
    routing_key='tasks',
    body='{"task": "scrape", "url": "https://example.com"}',
    properties=pika.BasicProperties(delivery_mode=2)  # Make persistent
)

connection.close()
```

#### Step 4: Receive and Acknowledge

```python
import pika
import json

def callback(channel, method, properties, body):
    # Process message
    task = json.loads(body)
    print(f"Processing: {task}")

    # Do work here...

    # Acknowledge when done
    channel.basic_ack(delivery_tag=method.delivery_tag)

# Connect and consume
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='tasks', durable=True)
channel.basic_consume(queue='tasks', on_message_callback=callback)

channel.start_consuming()
```

#### Step 5: Competing Consumers

Automatically load-balances across multiple workers:

```python
# Worker 1
channel.basic_qos(prefetch_count=1)  # Process 1 message at a time
channel.basic_consume(queue='tasks', on_message_callback=callback)
channel.start_consuming()

# Worker 2, 3, 4 ... (same code)
# Messages automatically distributed: Worker 1 gets msg1, Worker 2 gets msg2, etc.
```

#### Step 6: Dead Letter Queue (RabbitMQ)

```python
# Setup DLQ
channel.queue_declare(queue='tasks')
channel.queue_declare(queue='tasks_dlq')

# If message fails (no ACK after timeout), send to DLQ
channel.queue_bind(
    exchange='dlx',           # Dead Letter Exchange
    queue='tasks_dlq'
)
```

---

## 💻 Code Examples

### Example 1: Complete Producer-Consumer (Redis)

```python
# producer.py - Send tasks to Redis queue
import redis
import json
from datetime import datetime

redis_client = redis.Redis(host='localhost', port=6379)

def queue_scrape_job(url: str, priority: str = 'normal'):
    """Queue a web scraping job"""
    # Create job object
    job = {
        'type': 'scrape',
        'url': url,
        'priority': priority,
        'queued_at': datetime.now().isoformat()
    }

    # Use different queue based on priority
    queue_name = f'jobs:{priority}'

    # Push to Redis list (LPUSH adds to left, RPOP removes from right = FIFO)
    redis_client.lpush(queue_name, json.dumps(job))

    print(f"Queued: {url}")
    return True

def queue_email_job(email: str, subject: str, body: str):
    """Queue an email sending job"""
    job = {
        'type': 'email',
        'email': email,
        'subject': subject,
        'body': body
    }

    redis_client.lpush('jobs:normal', json.dumps(job))

# consumer.py - Process tasks from Redis queue
import redis
import json
import time

redis_client = redis.Redis(host='localhost', port=6379)

def process_scrape_job(url: str):
    """Example: scrape website"""
    print(f"Scraping {url}...")
    # In real app: requests + BeautifulSoup
    time.sleep(2)
    return {"scraped": url, "items": 42}

def process_email_job(email: str, subject: str, body: str):
    """Example: send email"""
    print(f"Sending email to {email}")
    # In real app: SMTP
    return {"sent_to": email}

def worker():
    """Worker process: consume jobs from queue"""
    print("Worker started...")

    while True:
        # Try high priority first, then normal
        for priority in ['high', 'normal', 'low']:
            queue_name = f'jobs:{priority}'

            # BRPOP = blocking right pop (wait if empty)
            result = redis_client.brpop(queue_name, timeout=1)

            if result:
                queue_name, job_data = result
                job = json.loads(job_data)

                try:
                    if job['type'] == 'scrape':
                        result = process_scrape_job(job['url'])
                        print(f"✓ Scraped: {result}")

                    elif job['type'] == 'email':
                        result = process_email_job(
                            job['email'],
                            job['subject'],
                            job['body']
                        )
                        print(f"✓ Email sent: {result}")

                except Exception as e:
                    # Store failed job in error queue
                    error_job = {**job, 'error': str(e)}
                    redis_client.lpush('jobs:failed', json.dumps(error_job))
                    print(f"✗ Job failed: {e}")

if __name__ == "__main__":
    worker()
```

### Example 2: FastAPI + RabbitMQ Producer

```python
# main.py - FastAPI app publishing to RabbitMQ
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pika
import json
from contextlib import contextmanager

app = FastAPI()

class ScrapeJob(BaseModel):
    url: str
    priority: str = "normal"

class EmailJob(BaseModel):
    email: str
    subject: str
    body: str

# Connection pool
@contextmanager
def get_rabbitmq_channel():
    """Context manager for RabbitMQ connection"""
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost')
    )
    channel = connection.channel()

    try:
        yield channel
    finally:
        connection.close()

@app.post("/scrape")
def submit_scrape(job: ScrapeJob):
    """Submit scraping task to RabbitMQ"""
    try:
        with get_rabbitmq_channel() as channel:
            # Declare queue (idempotent)
            channel.queue_declare(
                queue='scrape_jobs',
                durable=True  # Persist on restart
            )

            # Publish message with persistence
            channel.basic_publish(
                exchange='',
                routing_key='scrape_jobs',
                body=json.dumps(job.dict()),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json'
                )
            )

        return {
            "status": "queued",
            "url": job.url,
            "priority": job.priority
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/email")
def submit_email(job: EmailJob):
    """Submit email task to RabbitMQ"""
    try:
        with get_rabbitmq_channel() as channel:
            channel.queue_declare(queue='email_jobs', durable=True)

            channel.basic_publish(
                exchange='',
                routing_key='email_jobs',
                body=json.dumps(job.dict()),
                properties=pika.BasicProperties(delivery_mode=2)
            )

        return {"status": "queued", "email": job.email}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/queue-stats")
def get_queue_stats():
    """Show queue depths"""
    try:
        with get_rabbitmq_channel() as channel:
            # Declare queues (no publish)
            scrape_queue = channel.queue_declare(
                queue='scrape_jobs',
                passive=True  # Don't create, just check
            )
            email_queue = channel.queue_declare(
                queue='email_jobs',
                passive=True
            )

            return {
                "scrape_jobs": scrape_queue.method.message_count,
                "email_jobs": email_queue.method.message_count
            }

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Example 3: RabbitMQ Consumer Worker

```python
# worker.py - Multiple workers process messages
import pika
import json
import time
import os

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
WORKER_ID = os.getenv('WORKER_ID', 'worker-1')

def process_scrape_job(job_data: dict):
    """Process scraping job"""
    print(f"[{WORKER_ID}] Processing scrape: {job_data['url']}")
    time.sleep(2)  # Simulate work
    return {"status": "success", "items_found": 42}

def process_email_job(job_data: dict):
    """Process email job"""
    print(f"[{WORKER_ID}] Sending email to: {job_data['email']}")
    time.sleep(1)  # Simulate work
    return {"status": "sent"}

def scrape_job_callback(channel, method, properties, body):
    """Callback for scrape queue"""
    try:
        job = json.loads(body)
        result = process_scrape_job(job)
        print(f"✓ Success: {result}")

        # Acknowledge: tell RabbitMQ message was processed
        channel.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"✗ Error: {e}")
        # NACK: tell RabbitMQ message wasn't processed (will retry or DLQ)
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def email_job_callback(channel, method, properties, body):
    """Callback for email queue"""
    try:
        job = json.loads(body)
        result = process_email_job(job)
        print(f"✓ Email sent: {result}")

        channel.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"✗ Error: {e}")
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def main():
    """Main worker process"""
    # Connect to RabbitMQ
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(RABBITMQ_HOST)
    )
    channel = connection.channel()

    # Declare queues
    channel.queue_declare(queue='scrape_jobs', durable=True)
    channel.queue_declare(queue='email_jobs', durable=True)

    # Set QoS: process 1 message at a time (fair dispatch)
    channel.basic_qos(prefetch_count=1)

    # Register callbacks
    channel.basic_consume(
        queue='scrape_jobs',
        on_message_callback=scrape_job_callback
    )
    channel.basic_consume(
        queue='email_jobs',
        on_message_callback=email_job_callback
    )

    print(f"[{WORKER_ID}] Started, waiting for messages...")

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
        connection.close()

if __name__ == "__main__":
    main()
```

---

## ⚠️ Common Mistakes

### Mistake 1: Not Acknowledging Messages

**WRONG:**

```python
message = redis_client.brpop('tasks')
process(message)
# If process crashes, message lost forever
```

**RIGHT:**

```python
message = redis_client.brpop('tasks')
try:
    process(message)
    # Only push to processed queue after success
    redis_client.lpush('processed', message)
except Exception as e:
    # Push to failed queue for retry
    redis_client.lpush('failed', message)
```

### Mistake 2: Choosing Wrong Tool

**WRONG:** Using Redis for mission-critical financial transactions

- Redis keeps messages in memory
- If crashed, messages gone
- No guarantee of delivery

**RIGHT:** Using RabbitMQ for financial

- Messages on disk
- Acknowledgement required
- Dead letter queues for failed jobs

### Mistake 3: Not Handling Slow Consumers

**WRONG:**

```python
# One worker can't keep up, queue grows unbounded
result = redis_client.brpop('tasks')  # Takes 10 seconds per task
```

**RIGHT:**

```python
# Start multiple workers in parallel
# Each handles different messages simultaneously
# Use prefetch_count=1 in RabbitMQ for fair distribution
channel.basic_qos(prefetch_count=1)
```

---

## ✅ Exercises

### Easy: Redis Queue

1. Producer: push 5 messages to Redis list
2. Consumer: pop and process all messages
3. Verify all processed in order

### Medium: RabbitMQ Publisher-Subscriber

1. FastAPI endpoint publishes message to RabbitMQ
2. Run 2 consumer workers
3. Verify messages distributed across workers
4. Add acknowledgement

### Hard: Multi-Step Pipeline

1. Producer publishes to `step1_queue`
2. Worker reads from `step1_queue`, processes, publishes to `step2_queue`
3. Another worker reads from `step2_queue`, processes
4. Verify end-to-end pipeline completes
5. Simulate worker crash and verify message not lost (RabbitMQ persistence)

---

## 🏗️ Mini Project: Data Pipeline with Queues

Build a multi-step data processing pipeline where Redis queues data between steps.

### Requirements

1. **Step 1:** Scrape website → publish to `raw_data` queue
2. **Step 2:** Clean data → read from `raw_data`, write to `clean_data` queue
3. **Step 3:** Save to DB → read from `clean_data`, save to PostgreSQL
4. FastAPI endpoint to trigger pipeline
5. Status endpoint showing queue depths

### Implementation

```python
# main.py - FastAPI app
from fastapi import FastAPI
import redis
import json
from pydantic import BaseModel

app = FastAPI()
redis_client = redis.Redis(host='localhost', port=6379)

class ScrapeRequest(BaseModel):
    url: str

@app.post("/pipeline/start")
def start_pipeline(req: ScrapeRequest):
    """Kick off 3-step pipeline"""

    # Step 1: Enqueue scraping job
    job = {
        'step': 1,
        'url': req.url,
        'status': 'queued'
    }
    redis_client.lpush('step1:scrape', json.dumps(job))

    return {
        "status": "pipeline started",
        "url": req.url,
        "tracking": "use /stats to monitor"
    }

@app.get("/stats")
def pipeline_stats():
    """Show queue depths"""
    return {
        "step1_scrape": redis_client.llen('step1:scrape'),
        "step2_clean": redis_client.llen('step2:clean'),
        "step3_save": redis_client.llen('step3:save'),
        "completed": redis_client.llen('completed')
    }

# worker_step1.py - Scraper
import redis, json, requests, time
redis_client = redis.Redis()

while True:
    job_data = redis_client.brpop('step1:scrape', timeout=1)
    if job_data:
        job = json.loads(job_data[1])

        # Scrape
        response = requests.get(job['url'])
        scraped_data = {'title': response.text[:100], 'url': job['url']}

        # Pass to step 2
        redis_client.lpush('step2:clean', json.dumps(scraped_data))

# worker_step2.py - Cleaner
import redis, json
redis_client = redis.Redis()

while True:
    data_raw = redis_client.brpop('step2:clean', timeout=1)
    if data_raw:
        data = json.loads(data_raw[1])

        # Clean
        data['title'] = data['title'].strip().upper()

        # Pass to step 3
        redis_client.lpush('step3:save', json.dumps(data))

# worker_step3.py - Saver
import redis, json, psycopg2
redis_client = redis.Redis()
conn = psycopg2.connect("dbname=mydb user=postgres")

while True:
    data_clean = redis_client.brpop('step3:save', timeout=1)
    if data_clean:
        data = json.loads(data_clean[1])

        # Save to DB
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO scraped_data (title, url) VALUES (%s, %s)",
            (data['title'], data['url'])
        )
        conn.commit()

        redis_client.lpush('completed', json.dumps(data))
```

---

## 📚 Summary

In this module, you learned:

1. ✅ **Message queues** – Decoupling producers and consumers
2. ✅ **Redis** – Simple, fast, in-memory queues
3. ✅ **RabbitMQ** – Robust, persistent, guaranteed delivery
4. ✅ **Producer-consumer pattern** – Scalable architecture
5. ✅ **Competing consumers** – Load distribution
6. ✅ **Acknowledgements** – Message reliability
7. ✅ **Dead letter queues** – Failed message handling
8. ✅ **When to choose each** – Redis vs RabbitMQ tradeoffs

Next module: scheduling recurring jobs and advanced retries.
