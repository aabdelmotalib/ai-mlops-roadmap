---
tags:
  - Intermediate
  - Phase 5
---

# Module 3: Tracking Pipeline Metrics

> **Phase 5 — Analytics & Monitoring**

---

## 🎯 What You Will Learn

- Why tracking pipeline health is different from tracking business data
- What metrics matter most in a data pipeline
- How to log pipeline run statistics to a PostgreSQL metrics table
- How Prometheus works and how to expose metrics from Python
- How to visualise Prometheus metrics in Grafana
- How to set up alerts when something goes wrong
- What SLAs and SLOs mean and how to define them for your pipeline

---

## 🧠 Concept Explained

Imagine you own a factory. The factory produces books (your pipeline processes data). You already have dashboards showing _what_ was produced — how many books, what genres, what prices.

But now you want to know: _Is the factory running well? Did the night shift complete on time? Did any machines break? How long did each step take?_

That is **pipeline metrics** — not about the data itself, but about the health of the process that produces it.

!!! note "Data metrics vs pipeline metrics" - **Data metrics**: "We scraped 150 books today" — about the output - **Pipeline metrics**: "The scrape job ran for 4.2 minutes, processed 155 rows, failed 5, and used 340MB of memory" — about the process itself

Without pipeline metrics, you only find out something broke when someone complains the data is wrong or missing. With pipeline metrics, you know _before_ anyone notices.

---

## 🔍 How It Works

```
Your Python pipeline
        │
        ├── records: start time, end time, rows in, rows out, errors
        │
        ▼
Two places metrics go:

1. PostgreSQL metrics table  ←── simple, queryable, for historical analysis
        │
        └── Metabase dashboard: "How did last week's runs compare?"

2. Prometheus (time-series DB) ←── designed for live metrics, millisecond precision
        │
        └── Grafana dashboard: "Is my pipeline healthy RIGHT NOW?"
                │
                └── Alerting: "Text me if error rate > 5%"
```

---

## 🛠️ Step-by-Step Guide

### Step 1 — Create a metrics table in PostgreSQL

### Step 2 — Instrument your pipeline to log metrics

### Step 3 — Install and run Prometheus with Docker

### Step 4 — Expose metrics from Python with prometheus-client

### Step 5 — Connect Grafana to Prometheus

### Step 6 — Build a pipeline health dashboard in Grafana

### Step 7 — Create an alert rule

---

## 💻 Code Examples

### Step 1 — Create the metrics table

```sql
-- This table records every pipeline run — one row per execution
CREATE TABLE pipeline_runs (
    id              SERIAL PRIMARY KEY,
    pipeline_name   TEXT NOT NULL,           -- which pipeline ran (e.g. 'book_scraper')
    run_id          UUID DEFAULT gen_random_uuid(), -- unique ID for this run
    started_at      TIMESTAMP NOT NULL,      -- when the run began
    finished_at     TIMESTAMP,               -- when it ended (NULL if still running)
    duration_seconds NUMERIC(10, 2),         -- how long it took
    rows_extracted  INTEGER DEFAULT 0,       -- rows read from source
    rows_loaded     INTEGER DEFAULT 0,       -- rows successfully written to destination
    rows_failed     INTEGER DEFAULT 0,       -- rows that failed validation or insert
    status          TEXT DEFAULT 'running',  -- 'running', 'success', 'failed'
    error_message   TEXT,                    -- error details if status = 'failed'
    created_at      TIMESTAMP DEFAULT NOW()  -- when this record was inserted
);

-- Index for fast lookups by pipeline name and time
CREATE INDEX idx_pipeline_runs_name ON pipeline_runs(pipeline_name);
CREATE INDEX idx_pipeline_runs_started ON pipeline_runs(started_at DESC);
```

### Step 2 — Pipeline metrics logger in Python

```python
# metrics_logger.py — a reusable helper for logging pipeline runs
import psycopg2           # PostgreSQL connection
import psycopg2.extras    # for UUID and dict cursor support
from datetime import datetime  # for timestamps
from contextlib import contextmanager  # for the context manager pattern
import time               # for measuring duration
import uuid               # for generating unique run IDs
import logging            # for application logs

logger = logging.getLogger(__name__)  # create a logger for this module

class PipelineMetricsLogger:
    """
    Logs pipeline run statistics to a PostgreSQL table.
    Use as a context manager:

        with PipelineMetricsLogger('my_pipeline') as metrics:
            metrics.rows_extracted = 100
            metrics.rows_loaded = 98
            metrics.rows_failed = 2
    """

    def __init__(self, pipeline_name: str, db_config: dict):
        self.pipeline_name = pipeline_name   # name of this pipeline
        self.db_config = db_config           # PostgreSQL connection details
        self.run_id = str(uuid.uuid4())      # unique ID for this run
        self.started_at = None               # will be set when run starts
        self.rows_extracted = 0              # how many rows we read
        self.rows_loaded = 0                 # how many rows we wrote successfully
        self.rows_failed = 0                 # how many rows failed
        self._start_time = None              # for measuring duration

    def __enter__(self):
        """Called when entering 'with' block — record the start."""
        self.started_at = datetime.now()         # record exact start time
        self._start_time = time.time()           # record start for duration calc
        self._insert_run_record('running')       # insert initial record
        logger.info(f"Pipeline '{self.pipeline_name}' started — run_id: {self.run_id}")
        return self                              # return self so caller can set attributes

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Called when leaving 'with' block — update with final stats."""
        duration = round(time.time() - self._start_time, 2)  # calculate duration

        if exc_type is None:
            # No exception occurred — the pipeline succeeded
            self._update_run_record(
                status='success',
                duration=duration,
                error_message=None
            )
            logger.info(
                f"Pipeline '{self.pipeline_name}' succeeded — "
                f"duration: {duration}s, "
                f"extracted: {self.rows_extracted}, "
                f"loaded: {self.rows_loaded}, "
                f"failed: {self.rows_failed}"
            )
        else:
            # An exception occurred — the pipeline failed
            self._update_run_record(
                status='failed',
                duration=duration,
                error_message=str(exc_val)  # the actual error message
            )
            logger.error(
                f"Pipeline '{self.pipeline_name}' FAILED after {duration}s — "
                f"{exc_type.__name__}: {exc_val}"
            )

        return False  # re-raise any exception (don't suppress it)

    def _insert_run_record(self, status: str):
        """Insert the initial run record into PostgreSQL."""
        with psycopg2.connect(**self.db_config) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO pipeline_runs
                        (pipeline_name, run_id, started_at, status)
                    VALUES (%s, %s, %s, %s)
                """, (self.pipeline_name, self.run_id, self.started_at, status))
                conn.commit()  # commit immediately so the record is visible

    def _update_run_record(self, status: str, duration: float, error_message: str):
        """Update the run record when the pipeline finishes."""
        with psycopg2.connect(**self.db_config) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE pipeline_runs SET
                        finished_at      = NOW(),
                        duration_seconds = %s,
                        rows_extracted   = %s,
                        rows_loaded      = %s,
                        rows_failed      = %s,
                        status           = %s,
                        error_message    = %s
                    WHERE run_id = %s   -- only update THIS run's record
                """, (
                    duration,
                    self.rows_extracted,
                    self.rows_loaded,
                    self.rows_failed,
                    status,
                    error_message,
                    self.run_id
                ))
                conn.commit()  # commit the update
```

```python
# Using the metrics logger in your pipeline
from metrics_logger import PipelineMetricsLogger

DB_CONFIG = {
    "host": "localhost",
    "database": "books_db",
    "user": "postgres",
    "password": "yourpassword"
}

def run_book_scraper_pipeline():
    """The book scraper pipeline — now instrumented with metrics."""

    with PipelineMetricsLogger('book_scraper', DB_CONFIG) as metrics:
        # Step 1: extract data
        raw_books = scrape_books()              # your scraping function
        metrics.rows_extracted = len(raw_books) # record how many we got

        # Step 2: validate and transform
        valid_books = []
        for book in raw_books:
            try:
                validated = validate_book(book)   # your validation function
                valid_books.append(validated)
            except ValueError as e:
                metrics.rows_failed += 1          # count each failed row
                logger.warning(f"Validation failed for book: {e}")

        # Step 3: load to database
        loaded = load_books_to_db(valid_books)    # your load function
        metrics.rows_loaded = loaded              # record successful loads

    # After the 'with' block, the run record is updated automatically
    print("Pipeline complete — metrics logged to pipeline_runs table")

# Run it
run_book_scraper_pipeline()
```

---

### Step 3 — Run Prometheus with Docker

```bash
# First create a Prometheus config file
mkdir -p ~/monitoring/prometheus
cat > ~/monitoring/prometheus/prometheus.yml << 'EOF'
# prometheus.yml — tells Prometheus what to scrape

global:
  scrape_interval: 15s      # scrape every 15 seconds
  evaluation_interval: 15s  # evaluate alerting rules every 15 seconds

scrape_configs:
  # Prometheus scrapes itself (for meta-monitoring)
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Scrape our Python pipeline app
  - job_name: 'pipeline_app'
    static_configs:
      - targets: ['host.docker.internal:8000']  # your Python app's metrics endpoint
EOF

# Run Prometheus in Docker
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v ~/monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus:latest
# -v: mount our config file into the container

# Check it's running
docker ps | grep prometheus

# Open Prometheus UI at http://localhost:9090
```

### Step 4 — Expose metrics from Python

```python
# Install the prometheus client library
# pip install prometheus-client

# pipeline_with_prometheus.py — instrument your pipeline with Prometheus metrics

from prometheus_client import (
    Counter,       # counts things that only go up (requests, errors)
    Histogram,     # measures duration distributions
    Gauge,         # measures things that go up and down (queue size, memory)
    start_http_server  # starts a /metrics endpoint on a given port
)
import time
import random  # for demo purposes

# ── Define metrics ────────────────────────────────────────────────────────────
# Counter: total rows processed (always increases)
rows_processed_total = Counter(
    'pipeline_rows_processed_total',    # metric name (snake_case)
    'Total number of rows processed',   # human-readable description
    ['pipeline_name', 'status']         # labels: each combo gets its own counter
)
# Usage: rows_processed_total.labels(pipeline_name='book_scraper', status='success').inc()

# Counter: total pipeline runs
pipeline_runs_total = Counter(
    'pipeline_runs_total',
    'Total number of pipeline runs',
    ['pipeline_name', 'status']  # labels: success or failed
)

# Histogram: pipeline duration in seconds
# Buckets define the range of expected durations in seconds
pipeline_duration_seconds = Histogram(
    'pipeline_duration_seconds',
    'Pipeline run duration in seconds',
    ['pipeline_name'],
    buckets=[1, 5, 10, 30, 60, 120, 300, 600]  # 1s, 5s, 10s... 10 minutes
)

# Gauge: current queue size (changes over time)
pipeline_queue_size = Gauge(
    'pipeline_queue_size',
    'Current number of items waiting to be processed',
    ['pipeline_name']
)

# ── Start the metrics HTTP endpoint ──────────────────────────────────────────
start_http_server(8000)  # Prometheus will scrape http://localhost:8000/metrics
print("Metrics server started on port 8000")

# ── Instrument the pipeline ───────────────────────────────────────────────────
def run_pipeline_with_metrics(pipeline_name: str):
    """Run the pipeline and record Prometheus metrics throughout."""

    start_time = time.time()    # record start for duration calculation

    try:
        # Simulate pipeline work
        pipeline_queue_size.labels(pipeline_name=pipeline_name).set(50)  # 50 items queued

        rows_in = 100           # simulated: 100 rows extracted
        rows_ok = 95            # simulated: 95 rows loaded successfully
        rows_bad = 5            # simulated: 5 rows failed

        time.sleep(random.uniform(2, 8))  # simulate work taking 2-8 seconds

        pipeline_queue_size.labels(pipeline_name=pipeline_name).set(0)  # queue empty

        # Record successful row counts
        rows_processed_total.labels(
            pipeline_name=pipeline_name, status='success'
        ).inc(rows_ok)   # increment by 95 (the rows that succeeded)

        rows_processed_total.labels(
            pipeline_name=pipeline_name, status='failed'
        ).inc(rows_bad)  # increment by 5 (the rows that failed)

        # Record this run as successful
        pipeline_runs_total.labels(
            pipeline_name=pipeline_name, status='success'
        ).inc()          # increment by 1

    except Exception as e:
        # Record this run as failed
        pipeline_runs_total.labels(
            pipeline_name=pipeline_name, status='failed'
        ).inc()
        raise  # re-raise so the error is still visible

    finally:
        # Always record duration, whether success or failure
        duration = time.time() - start_time
        pipeline_duration_seconds.labels(
            pipeline_name=pipeline_name
        ).observe(duration)   # add this duration to the histogram

        print(f"Pipeline '{pipeline_name}' — duration: {duration:.2f}s")

# Run the pipeline every 30 seconds
while True:
    run_pipeline_with_metrics('book_scraper')
    time.sleep(30)   # wait 30 seconds between runs
```

```bash
# After running the script, check the metrics endpoint:
curl http://localhost:8000/metrics | grep pipeline
```

```
# Expected output (Prometheus text format):
# HELP pipeline_rows_processed_total Total number of rows processed
# TYPE pipeline_rows_processed_total counter
pipeline_rows_processed_total{pipeline_name="book_scraper",status="success"} 285.0
pipeline_rows_processed_total{pipeline_name="book_scraper",status="failed"} 15.0

# HELP pipeline_duration_seconds Pipeline run duration in seconds
# TYPE pipeline_duration_seconds histogram
pipeline_duration_seconds_bucket{pipeline_name="book_scraper",le="1.0"} 0.0
pipeline_duration_seconds_bucket{pipeline_name="book_scraper",le="5.0"} 1.0
pipeline_duration_seconds_bucket{pipeline_name="book_scraper",le="10.0"} 3.0
pipeline_duration_seconds_count{pipeline_name="book_scraper"} 3.0
pipeline_duration_seconds_sum{pipeline_name="book_scraper"} 17.42
```

---

### Step 5 — Run Grafana and connect to Prometheus

```bash
# Run Grafana in Docker
docker run -d \
  --name grafana \
  -p 3001:3000 \
  grafana/grafana:latest
# port 3001 on host → port 3000 in container (3000 might be taken by Metabase)

# Open Grafana at http://localhost:3001
# Default login: admin / admin
# It will ask you to change the password on first login
```

**Connect Grafana to Prometheus (in the browser):**

1. Click the hamburger menu → **Connections → Data sources**
2. Click **Add data source**
3. Choose **Prometheus**
4. Set URL to: `http://host.docker.internal:9090`
5. Click **Save & test** — should say "Data source is working"

---

### Step 6 — Grafana dashboard panels

**Panel 1: Total rows processed (counter)**

- Add panel → choose **Stat** visualisation
- Query: `sum(pipeline_rows_processed_total{status="success"})`
- Title: "Total Rows Processed (Success)"

**Panel 2: Error rate percentage**

- Add panel → choose **Gauge** visualisation
- Query:

```
sum(pipeline_rows_processed_total{status="failed"})
/
sum(pipeline_rows_processed_total)
* 100
```

- Title: "Error Rate (%)"
- Set thresholds: green < 5%, orange < 10%, red >= 10%

**Panel 3: Pipeline duration over time**

- Add panel → choose **Time series** visualisation
- Query: `pipeline_duration_seconds_sum / pipeline_duration_seconds_count`
- Title: "Average Pipeline Duration (seconds)"

**Panel 4: Rows processed per minute (rate)**

- Add panel → choose **Time series**
- Query: `rate(pipeline_rows_processed_total[5m]) * 60`
- Title: "Rows Processed per Minute"

---

### Step 7 — Create an alert rule in Grafana

```
In Grafana:
1. Click the panel with Error Rate
2. Click Edit → Alert tab
3. Click "Create alert rule"
4. Condition: WHEN last() OF query IS ABOVE 5
   (alert when error rate exceeds 5%)
5. Evaluate every: 1m  For: 5m
   (alert only if condition is true for 5 consecutive minutes)
6. Annotations:
   Summary: "Pipeline error rate is {{ $values.A }}%"
   Description: "The book_scraper pipeline error rate has exceeded 5%"
7. Save the alert
```

---

### SLAs and SLOs

```python
# SLA (Service Level Agreement): a promise to stakeholders
# SLO (Service Level Objective): the internal target you set to meet the SLA

# Example SLOs for our book scraper pipeline:
SLO_CONFIG = {
    'book_scraper': {
        # 99% of runs must complete within 10 minutes
        'max_duration_seconds': 600,
        'duration_percentile': 99,

        # Error rate must stay below 2%
        'max_error_rate_percent': 2.0,

        # Pipeline must run at least once every 25 hours (scheduled every 24h)
        'max_gap_between_runs_hours': 25,

        # At least 95% of runs must succeed
        'min_success_rate_percent': 95.0
    }
}

# SQL query to check SLO compliance:
SLO_COMPLIANCE_QUERY = """
WITH recent_runs AS (
    -- Look at runs from the last 7 days
    SELECT
        pipeline_name,
        status,
        duration_seconds,
        rows_failed,
        rows_extracted,
        started_at
    FROM pipeline_runs
    WHERE started_at >= NOW() - INTERVAL '7 days'
      AND pipeline_name = 'book_scraper'
),
stats AS (
    SELECT
        COUNT(*)                                          AS total_runs,
        COUNT(*) FILTER (WHERE status = 'success')        AS successful_runs,
        ROUND(AVG(duration_seconds), 2)                   AS avg_duration,
        PERCENTILE_CONT(0.99) WITHIN GROUP
            (ORDER BY duration_seconds)                   AS p99_duration,
        ROUND(
            100.0 * SUM(rows_failed) / NULLIF(SUM(rows_extracted), 0),
            2
        )                                                 AS error_rate_percent
    FROM recent_runs
)
SELECT
    total_runs,
    successful_runs,
    ROUND(100.0 * successful_runs / NULLIF(total_runs, 0), 2) AS success_rate,
    avg_duration,
    p99_duration,
    error_rate_percent,
    -- SLO status checks
    CASE WHEN p99_duration <= 600 THEN '✅ Met' ELSE '❌ Breached' END AS duration_slo,
    CASE WHEN error_rate_percent <= 2.0 THEN '✅ Met' ELSE '❌ Breached' END AS error_slo
FROM stats;
"""
```

---

## ⚠️ Common Mistakes

**Mistake 1: Not recording metrics for failed runs**

```python
# WRONG: if the pipeline crashes, no metrics are recorded
def run_pipeline():
    rows = extract()
    loaded = load(rows)
    record_metrics(rows, loaded)  # never reached if load() crashes

# CORRECT: use try/finally to always record metrics
def run_pipeline():
    start = time.time()
    rows_extracted = 0
    rows_loaded = 0
    try:
        rows = extract()
        rows_extracted = len(rows)
        rows_loaded = load(rows)
    finally:
        duration = time.time() - start
        record_metrics(rows_extracted, rows_loaded, duration)  # always runs
```

**Mistake 2: Confusing Counter and Gauge**

```python
# Counter: only goes UP — use for totals (rows processed, errors)
# WRONG: using Counter for queue size (which goes up AND down)
queue_size = Counter('queue_size', 'Queue size')
queue_size.inc(50)   # add 50
queue_size.dec(10)   # ❌ ERROR: Counter has no dec() method

# CORRECT: use Gauge for values that go up and down
queue_size = Gauge('queue_size', 'Queue size')
queue_size.set(50)   # set to 50
queue_size.dec(10)   # now 40 ✅
```

**Mistake 3: Using high-cardinality labels**

```python
# WRONG: using book_id as a label — creates millions of time series in Prometheus
rows_processed.labels(book_id='12345').inc()   # ❌ one series per book = explosion

# CORRECT: labels should have low cardinality (few unique values)
rows_processed.labels(
    pipeline_name='book_scraper',   # ✅ few pipelines
    status='success'                 # ✅ only 'success' or 'failed'
).inc()
```

---

## ✅ Exercises

**Exercise 1 — Easy**
Write a SQL query against the `pipeline_runs` table that shows the last 10 runs for the `book_scraper` pipeline, including: run_id, started_at, duration_seconds, rows_loaded, rows_failed, and status.

**Exercise 2 — Medium**
Add a `pipeline_queue_size` Gauge metric to the Prometheus instrumentation. Simulate it starting at 100, decreasing by 10 every second, reaching 0 when the pipeline finishes. Verify the metric appears at `http://localhost:8000/metrics`.

**Exercise 3 — Hard**
Write a Python function called `check_slo_compliance(pipeline_name, days=7)` that queries the `pipeline_runs` table and returns a dictionary showing whether each SLO is met or breached. Print a formatted compliance report to the terminal.

---

## 🏗️ Mini Project — Pipeline Metrics Dashboard

**Goal:** Connect everything from this module into one working system.

**Part 1 — PostgreSQL metrics**
Wrap your Airflow DAG from Phase 2 with the `PipelineMetricsLogger`. After 3 DAG runs, query the `pipeline_runs` table and verify rows are being logged correctly.

**Part 2 — Prometheus metrics**
Add the prometheus-client instrumentation to your Celery tasks from Phase 4. Expose metrics on port 8000.

**Part 3 — Grafana dashboard**
Build a 4-panel Grafana dashboard with:

- Panel 1: Total successful rows (Stat)
- Panel 2: Error rate gauge (Gauge with colour thresholds)
- Panel 3: Pipeline duration trend (Time series)
- Panel 4: Rows per minute rate (Time series)

**Part 4 — Alert**
Add an alert that fires when the error rate exceeds 5% for 5 consecutive minutes.

---

## 🔗 What's Next

In **Module 5-4: System Monitoring & Logging**, you will zoom out from pipeline metrics to monitor the machines and containers your pipelines run on — using Node Exporter, cAdvisor, and centralised log aggregation.
