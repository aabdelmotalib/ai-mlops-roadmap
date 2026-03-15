---
tags:
  - Intermediate
  - Phase 4
---

# Module 3: Scheduling & Retries

Some jobs need to run on a schedule. Every morning at 6am, fetch the weather. Every hour, sync data. Every week on Monday, generate a report. These are scheduled jobs—they run whether you're awake or not. Scheduling is automation.

But scheduled jobs sometimes fail. Your API is temporarily down. Network hiccups. These jobs need retry logic: attempt once, fail, wait 5 seconds, try again, fail, wait 10 seconds, try again. This is exponential backoff: wait longer each time, avoid overwhelming a struggling system. This module teaches you to schedule reliably and retry intelligently.

---

## 🎯 What You Will Learn

By the end of this module, you will:

- Understand why scheduling matters in automation
- Read and write cron expressions (the standard scheduling language)
- Use crontab to schedule system tasks on Linux/macOS
- Use APScheduler for Python-based scheduling
- Schedule Celery tasks with Celery Beat
- Understand retry strategies: fixed delay, exponential backoff, jitter
- Know when to use each strategy
- Ensure idempotency (safe to re-run jobs)
- Handle missed runs and edge cases
- Monitor scheduled jobs
- Build a weather fetcher that retries on API failure

---

## 🧠 Concept Explained: Scheduling & Retries

### Why Scheduling?

Without scheduling, you need to be involved:

```
Manual: 6:00am - you wake up and manually run script
        ↓ python weather_scraper.py

Scheduled: 6:00am - your computer runs script automatically
           ↓ (you're sleeping, doesn't matter)
```

Scheduling lets systems be fully automated.

### Cron: The Scheduling Language

Cron is the universal scheduling tool on Linux/macOS. Every Unix-like system understands it.

```
*    *    *    *    *    command
│    │    │    │    │
│    │    │    │    └─── Day of week (0=Sun, 1=Mon, ... 6=Sat)
│    │    │    └──────── Month (1-12)
│    │    └───────────── Day of month (1-31)
│    └────────────────── Hour (0-23)
└─────────────────────── Minute (0-59)

Examples:
0 6 * * *     - Every day at 6:00 AM
0 */4 * * *   - Every 4 hours (midnight, 4am, 8am, etc.)
0 6 * * 1     - Every Monday at 6:00 AM
30 2 1 * *    - 1st of each month at 2:30 AM
```

### Retry Strategies

#### Strategy 1: Fixed Delay

Wait the same time between retries:

```
Attempt 1: FAIL
Wait 5 seconds
Attempt 2: FAIL
Wait 5 seconds
Attempt 3: SUCCESS ✓
```

**Problem:** If API is struggling, 5 seconds isn't enough. May overload it more.

#### Strategy 2: Exponential Backoff

Wait longer each time:

```
Attempt 1: FAIL
Wait 2 seconds
Attempt 2: FAIL
Wait 4 seconds (2x)
Attempt 3: FAIL
Wait 8 seconds (2x)
Attempt 4: SUCCESS ✓
```

**Benefit:** Gives struggling system more time to recover.

#### Strategy 3: Jitter

Add randomness to prevent thundering herd:

```
Attempt 1: FAIL
Wait 2 + random(0-1) seconds
Attempt 2: FAIL
Wait 4 + random(0-1) seconds
```

**Why:** If 1000 services retry at exact same time, overwhelming the target.

### Idempotency

A job is idempotent if running it twice gives same result as running once.

**NOT idempotent:**

```python
# This increments counter each time
def increment_counter():
    count = db.get('count')
    db.set('count', count + 1)

# If retried, count goes up twice!
```

**Idempotent:**

```python
# This sets counter to specific value (safe if retried)
def set_daily_count(date):
    count = scrape_today_data()
    db.set(f'count:{date}', count)

# If retried same day, overwrites with same value (safe)
```

---

## 🔍 How It Works

### Cron Flow

```
System Clock          Cron Daemon            Your Job
─────────────         ───────────            ───────
6:00:00 AM ──time?──→ [Check schedule]
                      ↓ Matches entry
                      ↓ "0 6 * * *"
                      ↓ Execute
                                             Run: weather_scraper.py
                                             ↓
                                             Success/Failure
```

### Retry Flow with Exponential Backoff

```
Task        Attempt      Delay        Status
────        ───────      ─────        ──────
Task 1      1            -            FAIL (network error)
            2            2 sec        FAIL (timeout)
            3            4 sec        FAIL (still down)
            4            8 sec        SUCCESS ✓

Task 2      1            -            FAIL
            2            2 sec        FAIL
            3            4 sec        FAIL
            Give up      (max_retries exceeded)
            → Dead Letter Queue
```

---

## 🛠️ Step-by-Step Guide

### Using Cron (Linux/macOS)

#### Step 1: List Current Crontab

```bash
crontab -l
```

#### Step 2: Edit Crontab

```bash
crontab -e
# Opens your default editor
```

#### Step 3: Add Entry

```cron
# Run weather scraper every day at 6:00 AM
0 6 * * * /usr/bin/python3 /home/user/weather_scraper.py

# Run every 4 hours
0 */4 * * * /usr/bin/python3 /home/user/bg_sync.py

# Every Monday at 6:00 AM
0 6 * * 1 /usr/bin/python3 /home/user/weekly_report.py
```

#### Step 4: Verify

```bash
crontab -l
# Should show your entries
```

#### Step 5: Log Cron Output

```cron
# Redirect output and errors to log file
0 6 * * * /usr/bin/python3 /home/user/weather_scraper.py >> /var/log/weather.log 2>&1
```

### Using APScheduler (Python)

#### Step 1: Install

```bash
pip install apscheduler
```

#### Step 2: Create Scheduler

```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.start()
```

#### Step 3: Add Job with Cron Trigger

```python
scheduler.add_job(
    func=weather_fetch,           # Function to run
    trigger='cron',               # Use cron schedule
    hour=6, minute=0,             # 6:00 AM
    id='weather_job'              # Unique ID
)
```

#### Step 4: Add Job with Interval Trigger

```python
scheduler.add_job(
    func=sync_data,
    trigger='interval',           # Run every X seconds/minutes/hours
    hours=4,                      # Every 4 hours
    id='sync_job'
)
```

### Using Celery Beat (for Celery tasks)

#### Step 1: Configure Beat Schedule

```python
from celery.schedules import crontab

app.conf.beat_schedule = {
    'fetch-weather': {
        'task': 'tasks.fetch_weather',  # Task name
        'schedule': crontab(hour=6, minute=0),  # 6:00 AM
    },
    'sync-every-4h': {
        'task': 'tasks.sync_data',
        'schedule': crontab(minute=0, hour='*/4'),  # Every 4 hours
    },
}
```

#### Step 2: Start Beat Scheduler

```bash
celery -A celery_app beat --loglevel=info
```

### Adding Retries

#### Celery Retry (with Exponential Backoff)

```python
@celery_app.task(
    autoretry_for=(requests.RequestException,),  # Exceptions to retry on
    max_retries=3,                                # Max 3 attempts
    default_retry_delay=60,                       # Start with 60 sec
    bind=True                                     # Access self.retry()
)
def fetch_weather(self):
    try:
        response = requests.get('weather-api.com', timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        # Exponential backoff: 60, 120, 240 seconds
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

#### APScheduler Retry (Simpler)

```python
def fetch_with_retry(max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get('weather-api.com', timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if attempt == max_retries:
                raise  # Give up on last attempt

            # Exponential backoff
            wait_time = 2 ** attempt  # 2, 4, 8 seconds
            time.sleep(wait_time)
            print(f"Retry {attempt}/{max_retries} after {wait_time}s")
```

---

## 💻 Code Examples

### Example 1: Cron Job with Logging

```bash
# weather_scraper.py (Python script)
#!/usr/bin/env python3

import requests
import json
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    filename='/var/log/weather.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def fetch_and_store_weather():
    """Fetch weather and save to file"""
    try:
        # Fetch from API
        response = requests.get(
            'https://api.weather.gov/points/40.7128,-74.0060',
            timeout=10
        )
        response.raise_for_status()

        # Parse response
        data = response.json()
        temp = data['properties']['temperature']

        # Store with timestamp
        record = {
            'timestamp': datetime.now().isoformat(),
            'temperature': temp,
            'status': 'success'
        }

        # Append to log file
        with open('/var/log/weather_data.jsonl', 'a') as f:
            f.write(json.dumps(record) + '\n')

        logging.info(f"Successfully stored weather: {temp}°")
        return record

    except requests.RequestException as e:
        # Log error
        error_record = {
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'status': 'failed'
        }
        logging.error(f"Failed to fetch weather: {e}")
        return error_record

if __name__ == "__main__":
    fetch_and_store_weather()
```

**Crontab entry:**

```cron
# Run every day at 6:00 AM
0 6 * * * /usr/bin/python3 /home/user/weather_scraper.py
```

### Example 2: APScheduler with Retries

```python
# app.py - FastAPI with scheduled jobs
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import time
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
scheduler = None

def fetch_weather_with_retry():
    """Fetch weather with exponential backoff"""
    max_retries = 3
    base_delay = 2  # Start with 2 seconds

    for attempt in range(1, max_retries + 1):
        try:
            # Attempt to fetch
            response = requests.get(
                'https://api.weather.gov/points/40.7128,-74.0060',
                timeout=5
            )
            response.raise_for_status()

            # Success
            data = response.json()
            logger.info(f"✓ Weather fetch succeeded on attempt {attempt}")
            return data

        except requests.RequestException as e:
            # Check if this is the last attempt
            if attempt == max_retries:
                logger.error(f"✗ Weather fetch failed after {max_retries} attempts: {e}")
                return None

            # Calculate backoff with jitter
            delay = base_delay * (2 ** (attempt - 1))  # Exponential
            jitter = delay * 0.1  # Add 10% randomness

            import random
            actual_delay = delay + random.uniform(-jitter, jitter)

            logger.warning(
                f"Attempt {attempt} failed: {e}. "
                f"Retrying in {actual_delay:.1f}s..."
            )

            time.sleep(actual_delay)

def sync_data_idempotent():
    """Idempotent job: safe to run multiple times"""
    # Store with today's date as key (safe to overwrite)
    today = datetime.now().strftime('%Y-%m-%d')

    try:
        # Fetch fresh data
        response = requests.get('https://api.example.com/data', timeout=10)
        response.raise_for_status()
        data = response.json()

        # Store with date key (overwrites if run again same day)
        # This is idempotent: running 2x gives same result as 1x
        store_to_cache(f'daily_sync:{today}', data)

        logger.info(f"Synced data for {today}")

    except Exception as e:
        logger.error(f"Sync failed: {e}")

def store_to_cache(key, value):
    """Store in Redis or similar"""
    pass

@app.on_event("startup")
def start_scheduler():
    """Start scheduler when app starts"""
    global scheduler

    scheduler = BackgroundScheduler()

    # Schedule weather fetch every 1 hour
    scheduler.add_job(
        func=fetch_weather_with_retry,
        trigger='interval',
        hours=1,
        id='hourly_weather',
        name='Fetch weather hourly'
    )

    # Schedule data sync every day at 2:00 AM
    scheduler.add_job(
        func=sync_data_idempotent,
        trigger='cron',
        hour=2,
        minute=0,
        id='daily_sync',
        name='Daily data sync'
    )

    scheduler.start()
    logger.info("Scheduler started")

@app.on_event("shutdown")
def stop_scheduler():
    """Stop scheduler when app stops"""
    global scheduler
    if scheduler:
        scheduler.shutdown()

@app.get("/jobs")
def list_jobs():
    """Show all scheduled jobs"""
    if not scheduler:
        return {"error": "Scheduler not started"}

    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run_time": str(job.next_run_time)
        })

    return {"jobs": jobs}
```

### Example 3: Celery Beat with Exponential Backoff

```python
# celery_app.py - Celery with Beat scheduling
import os
from celery import Celery
from celery.schedules import crontab
import requests
import time

celery_app = Celery('myapp')
celery_app.conf.broker_url = 'redis://localhost:6379/0'
celery_app.conf.result_backend = 'redis://localhost:6379/0'

# Define beat schedule
celery_app.conf.beat_schedule = {
    'fetch-weather-hourly': {
        'task': 'tasks.fetch_weather',
        'schedule': crontab(minute=0),  # Every hour on the hour
        'options': {'expires': 3600}    # Task expires if not executed within 1 hour
    },
    'sync-daily': {
        'task': 'tasks.sync_daily_data',
        'schedule': crontab(hour=2, minute=0),  # 2:00 AM daily
    }
}

@celery_app.task(
    bind=True,
    max_retries=4,
    default_retry_delay=10
)
def fetch_weather(self):
    """Fetch weather with exponential backoff retry"""
    try:
        response = requests.get(
            'https://api.weather.gov/points/40.7128,-74.0060',
            timeout=5
        )
        response.raise_for_status()

        result = response.json()
        return {
            "status": "success",
            "temperature": result['properties'].get('temperature'),
            "attempt": self.request.retries
        }

    except requests.RequestException as exc:
        # Calculate delay: 10, 20, 40, 80 seconds (exponential)
        retry_delay = 10 * (2 ** self.request.retries)

        raise self.retry(
            exc=exc,
            countdown=retry_delay,
            max_retries=4
        )

@celery_app.task(bind=True)
def sync_daily_data(self):
    """Idempotent daily sync"""
    from datetime import date

    try:
        # Use today's date as key (safe to re-run same day)
        today = str(date.today())

        response = requests.get(
            'https://api.example.com/data',
            timeout=10
        )
        response.raise_for_status()

        data = response.json()

        # Idempotent: store with date key
        # Re-running overwrites with same data
        cache_key = f'daily_sync:{today}'
        store_result(cache_key, data)

        return {"status": "completed", "date": today}

    except requests.RequestException as exc:
        # Simpler retry logic for this task
        raise self.retry(exc=exc, countdown=300, max_retries=2)

def store_result(key, value):
    """Store in cache or database"""
    pass
```

**Run Beat scheduler:**

```bash
celery -A celery_app beat --loglevel=info
```

---

## ⚠️ Common Mistakes

### Mistake 1: Not Making Jobs Idempotent

**WRONG:**

```python
# Increments every time (even retries)
count = db.get('count')
db.set('count', count + 1)

# If retried twice, increments twice
```

**RIGHT:**

```python
# Idempotent: always results in same value
today = datetime.now().strftime('%Y-%m-%d')
db.set(f'daily_count:{today}', 42)

# If retried same day, overwrites with same value (safe)
```

### Mistake 2: Forgetting to Handle Timeout

**WRONG:**

```bash
# No timeout! Script hangs forever if API doesn't respond
0 6 * * * /usr/bin/python3 /home/user/scraper.py
```

**RIGHT:**

```bash
# Kill script after 5 min (timeout command)
0 6 * * * timeout 300 /usr/bin/python3 /home/user/scraper.py
```

### Mistake 3: Wrong Retry Strategy

**WRONG:** Immediate retries for external API

```python
# Tries 3x in quick succession
# API is down, will still be down 10ms later
for i in range(3):
    requests.get(api)
```

**RIGHT:** Exponential backoff

```python
# Gives API time to recover
for attempt in range(3):
    try:
        return requests.get(api)
    except:
        time.sleep(2 ** attempt)  # 1s, 2s, 4s
```

---

## ✅ Exercises

### Easy: Cron Expression Parsing

1. Write cron expressions for:
   - Every Monday at 9am
   - Every 6 hours
   - 1st and 15th of each month at noon

2. Verify with `crontab -e`

### Medium: APScheduler with Retry

1. Create APScheduler job that fetches data from API
2. Add try/except with retry logic
3. Log each attempt
4. Set max retries and give up

### Hard: Complete Scheduled Pipeline

1. Create Celery Beat schedule for weather fetch (hourly)
2. Add exponential backoff on failure
3. Create second scheduled task to process yesterday's data (idempotent)
4. Monitor jobs with `/jobs` endpoint
5. Verify jobs run on schedule, verify retries work

---

## 🏗️ Mini Project: Robust Weather Scheduler

Build a system that fetches weather every hour, retries on failure with exponential backoff, and has a web dashboard showing last fetch time and errors.

### Requirements

1. Fetch weather API every hour (scheduled)
2. If API fails, retry with exponential backoff (2, 4, 8, 16 sec delays)
3. Store results in PostgreSQL with timestamp
4. Give up after 3 retries, log error
5. /weather endpoint shows last successful fetch
6. /schedule-status endpoint shows next run time
7. /errors endpoint shows recent errors

### Implementation

```python
# main.py - FastAPI app with Celery Beat scheduler
from fastapi import FastAPI
from celery import Celery
from celery.schedules import crontab
import requests
import psycopg2
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize apps
app = FastAPI()
celery_app = Celery('weather_app')
celery_app.conf.broker_url = 'redis://localhost:6379/0'
celery_app.conf.result_backend = 'redis://localhost:6379/0'

celery_app.conf.beat_schedule = {
    'fetch-weather-hourly': {
        'task': 'main.fetch_weather_task',
        'schedule': crontab(minute=0),  # Every hour on the hour
    }
}

@celery_app.task(bind=True, max_retries=3)
def fetch_weather_task(self):
    """Celery task with exponential backoff"""
    try:
        # Fetch weather
        response = requests.get(
            'https://api.weather.gov/points/40.7128,-74.0060',
            timeout=5
        )
        response.raise_for_status()
        data = response.json()

        # Store in database
        weather = data['properties']
        store_weather(
            temperature=weather.get('temperature'),
            forecast=weather.get('shortForecast'),
            timestamp=datetime.utcnow()
        )

        logger.info(f"✓ Weather stored: {weather.get('temperature')}°")
        return {"status": "success", "fetch_count": self.request.retries + 1}

    except requests.RequestException as exc:
        # Exponential backoff: 2, 4, 8 seconds
        countdown = 2 ** self.request.retries
        logger.warning(f"Retry in {countdown}s (attempt {self.request.retries + 1})")

        raise self.retry(exc=exc, countdown=countdown)

def store_weather(temperature, forecast, timestamp):
    """Store in PostgreSQL"""
    conn = psycopg2.connect("dbname=weather_db user=postgres")
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO weather (temperature, forecast, timestamp)
        VALUES (%s, %s, %s)
    """, (temperature, forecast, timestamp))

    conn.commit()
    cur.close()
    conn.close()

@app.get("/weather")
def get_latest_weather():
    """Get last successful weather fetch"""
    conn = psycopg2.connect("dbname=weather_db user=postgres")
    cur = conn.cursor()

    cur.execute("""
        SELECT temperature, forecast, timestamp
        FROM weather
        ORDER BY timestamp DESC
        LIMIT 1
    """)

    result = cur.fetchone()
    cur.close()
    conn.close()

    if result:
        return {
            "temperature": result[0],
            "forecast": result[1],
            "timestamp": result[2].isoformat()
        }
    else:
        return {"error": "No weather data yet"}

@app.get("/schedule-status")
def get_schedule_status():
    """Show when next weather fetch is scheduled"""
    from apscheduler.schedulers.background import BackgroundScheduler

    return {
        "next_fetch": "Happens every hour on the hour",
        "last_known": "Check /weather endpoint",
        "retry_policy": "Exponential backoff: 2, 4, 8 seconds"
    }
```

**Run:**

```bash
# Terminal 1: Celery worker
celery -A main worker --loglevel=info

# Terminal 2: Celery Beat scheduler
celery -A main beat --loglevel=info

# Terminal 3: FastAPI
python -m uvicorn main:app --reload
```

---

## 📚 Summary

In this module, you learned:

1. ✅ **Cron expressions** – Universal scheduling language
2. ✅ **Scheduling tools** – crontab, APScheduler, Celery Beat
3. ✅ **Retry strategies** – Fixed, exponential backoff, jitter
4. ✅ **Idempotency** – Safe to re-run jobs
5. ✅ **Error handling** – Graceful failure and recovery
6. ✅ **Monitoring** – Track when jobs run
7. ✅ **Production patterns** – Logging, timeouts, graceful degradation

Next module: comprehensive logging and error handling across all your systems.
