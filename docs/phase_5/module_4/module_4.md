---
tags:
  - Intermediate
  - Phase 5
---

# Module 4: System Monitoring & Logging

> **Phase 5 — Analytics & Monitoring**

---

## 🎯 What You Will Learn

- The difference between system monitoring and application monitoring
- How to monitor Docker containers with `docker stats` and cAdvisor
- How to collect host-level metrics (CPU, RAM, disk) with Node Exporter
- Why centralised logging matters and how log aggregation works
- The ELK/EFK stack — what each piece does and how they connect
- How to ship Python application logs to Elasticsearch
- Log retention, rotation, and practical alerting with Slack

---

## 🧠 Concept Explained

Think of your running application like a building. In Module 5-3, you installed sensors on the _machines inside the building_ — the conveyor belts (pipelines) and assembly lines (Celery tasks). Now you want sensors on the _building itself_ — is the electricity running? Is the roof leaking? Are the pipes hot?

That is **system monitoring** — tracking the health of the infrastructure that your application runs on: CPU, memory, disk, network, container health.

And **centralised logging** is like having every department in the building send their daily reports to one central filing room instead of keeping them in their own desk drawer. When something goes wrong, you go to one place and read everything.

!!! note "Why these matter together" - Your pipeline ran slowly — was it bad code or was the server out of RAM? - Your container crashed — was it a bug or did the disk fill up? - System monitoring tells you _what the machine was doing_ while the app was running. - Centralised logs tell you _what the app was saying_ when it happened.

---

## 🔍 How It Works

```
                    ┌─────────────────────────────────┐
                    │     Your Ubuntu 24 server        │
                    │                                  │
                    │  ┌────────────┐  ┌────────────┐  │
                    │  │ FastAPI    │  │  Celery    │  │
                    │  │ container  │  │  worker    │  │
                    │  └─────┬──────┘  └─────┬──────┘  │
                    │        │ logs           │ logs    │
                    └────────┼───────────────┼─────────┘
                             │               │
                    ┌────────▼───────────────▼─────────┐
                    │         Fluentd / Logstash         │
                    │    (collects and forwards logs)    │
                    └────────────────┬─────────────────┘
                                     │
                    ┌────────────────▼─────────────────┐
                    │          Elasticsearch             │
                    │     (stores and indexes logs)      │
                    └────────────────┬─────────────────┘
                                     │
                    ┌────────────────▼─────────────────┐
                    │             Kibana                 │
                    │   (visualises and searches logs)   │
                    └──────────────────────────────────┘


Separately — metrics (numbers) go to:
  Node Exporter  ──┐
  cAdvisor       ──┼──► Prometheus ──► Grafana
  Your app       ──┘
```

---

## 🛠️ Step-by-Step Guide

### Step 1 — Monitor containers with docker stats

### Step 2 — Run cAdvisor for container metrics

### Step 3 — Run Node Exporter for host metrics

### Step 4 — Add both to Prometheus

### Step 5 — Set up the EFK stack with Docker Compose

### Step 6 — Ship Python logs to Elasticsearch via Fluentd

### Step 7 — Build a Kibana dashboard

### Step 8 — Set up log rotation on Ubuntu 24

---

## 💻 Code Examples

### Step 1 — docker stats (built-in, no setup needed)

```bash
# Real-time container resource usage — like 'top' but for containers
docker stats

# Expected output (updates every second):
# CONTAINER ID   NAME       CPU %   MEM USAGE / LIMIT   MEM %   NET I/O         BLOCK I/O
# a3f2c1d4e5b6   fastapi    2.14%   45.2MiB / 7.5GiB    0.59%   1.2kB / 980B    0B / 0B
# b7e8f9a0c1d2   celery     0.87%   89.1MiB / 7.5GiB    1.16%   4.5kB / 1.1kB   0B / 0B

# Single snapshot (non-interactive) — useful in scripts
docker stats --no-stream

# Only specific container
docker stats fastapi --no-stream

# Formatted output for parsing
docker stats --no-stream --format \
  "{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
```

### Step 2 — cAdvisor (Container Advisor)

```bash
# cAdvisor scrapes detailed container metrics and exposes them for Prometheus
docker run -d \
  --name cadvisor \
  --volume=/:/rootfs:ro \               # read-only access to host filesystem
  --volume=/var/run:/var/run:ro \       # access to Docker socket info
  --volume=/sys:/sys:ro \               # kernel info
  --volume=/var/lib/docker/:/var/lib/docker:ro \  # Docker data
  --publish=8080:8080 \                 # expose cAdvisor web UI
  gcr.io/cadvisor/cadvisor:latest

# Open http://localhost:8080 to see the cAdvisor web UI
# Prometheus metrics available at http://localhost:8080/metrics
```

### Step 3 — Node Exporter (host metrics)

```bash
# Node Exporter exposes CPU, RAM, disk, network metrics of your Ubuntu machine
docker run -d \
  --name node_exporter \
  --net="host" \                  # must use host network to see host metrics
  --pid="host" \                  # must see host process IDs
  -v "/:/host:ro,rslave" \        # read-only access to host filesystem
  quay.io/prometheus/node-exporter:latest \
  --path.rootfs=/host

# Metrics available at http://localhost:9100/metrics
curl http://localhost:9100/metrics | grep node_cpu | head -5
```

### Step 4 — Update Prometheus to scrape cAdvisor and Node Exporter

```yaml
# prometheus.yml — add the new scrape targets
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9090"] # prometheus itself

  - job_name: "pipeline_app"
    static_configs:
      - targets: ["host.docker.internal:8000"] # your Python app

  - job_name: "cadvisor" # container metrics
    static_configs:
      - targets: ["host.docker.internal:8080"]

  - job_name: "node_exporter" # host machine metrics
    static_configs:
      - targets: ["host.docker.internal:9100"]
```

```bash
# Restart Prometheus to pick up the new config
docker restart prometheus

# Verify targets are being scraped at: http://localhost:9090/targets
# All targets should show State: UP
```

**Useful Prometheus queries for system monitoring:**

```promql
# CPU usage percentage across all cores
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Available memory in GB
node_memory_MemAvailable_bytes / 1024 / 1024 / 1024

# Disk usage percentage
100 - ((node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100)

# Container CPU usage
rate(container_cpu_usage_seconds_total{name!=""}[5m]) * 100

# Container memory usage in MB
container_memory_usage_bytes{name!=""} / 1024 / 1024
```

---

### Step 5 — EFK Stack with Docker Compose

```yaml
# docker-compose-efk.yml — Elasticsearch + Fluentd + Kibana

version: "3.8"

services:
  # Elasticsearch: stores and indexes all log data
  elasticsearch:
    image: elasticsearch:8.11.0
    container_name: elasticsearch
    environment:
      - discovery.type=single-node # run as a single node (no cluster)
      - xpack.security.enabled=false # disable auth for local dev
      - ES_JAVA_OPTS=-Xms512m -Xmx512m # limit memory to 512MB heap
    ports:
      - "9200:9200" # REST API port
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data # persist data
    healthcheck:
      test:
        [
          "CMD-SHELL",
          "curl -s http://localhost:9200/_cluster/health | grep -q green",
        ]
      interval: 30s
      timeout: 10s
      retries: 5

  # Kibana: web UI to search and visualise logs in Elasticsearch
  kibana:
    image: kibana:8.11.0
    container_name: kibana
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200 # connect to our ES
    ports:
      - "5601:5601" # Kibana web UI port
    depends_on:
      elasticsearch:
        condition: service_healthy # wait for ES to be ready

  # Fluentd: collects logs from apps and forwards them to Elasticsearch
  fluentd:
    image: fluent/fluentd:v1.16-debian-1
    container_name: fluentd
    volumes:
      - ./fluentd/conf:/fluentd/etc # our fluentd config
    ports:
      - "24224:24224" # TCP port for log forwarding
      - "24224:24224/udp" # UDP port as well
    depends_on:
      elasticsearch:
        condition: service_healthy

volumes:
  elasticsearch_data: # named volume persists data across restarts
```

```
# fluentd/conf/fluent.conf — tells Fluentd what to accept and where to send it

# Accept logs sent to port 24224 (from our Python app via logging handler)
<source>
  @type forward          # accept Fluentd's native protocol
  port 24224             # listen on this port
  bind 0.0.0.0           # accept from any IP
</source>

# Also accept logs from Docker containers using the fluentd log driver
<source>
  @type forward
  port 24224
</source>

# Parse JSON logs (our Python app sends structured JSON)
<filter **>
  @type parser
  key_name log           # the field containing the raw log string
  reserve_data true      # keep the original fields too
  <parse>
    @type json           # parse as JSON
    time_key timestamp   # use 'timestamp' field as the log time
  </parse>
</filter>

# Send everything to Elasticsearch
<match **>
  @type elasticsearch
  host elasticsearch      # hostname of our Elasticsearch container
  port 9200
  logstash_format true    # use logstash-style index names (logstash-YYYY.MM.DD)
  logstash_prefix fluentd # index name prefix
  include_timestamp true  # add @timestamp field
  <buffer>
    flush_interval 5s     # send logs every 5 seconds (not one at a time)
  </buffer>
</match>
```

```bash
# Start the EFK stack
docker-compose -f docker-compose-efk.yml up -d

# Check all three are running
docker-compose -f docker-compose-efk.yml ps

# Open Kibana at http://localhost:5601
# (takes ~30 seconds to start)
```

---

### Step 6 — Ship Python logs to Elasticsearch

```python
# Install the fluent-logger library
# pip install fluent-logger

# structured_logging.py — configure Python logging to send to Fluentd

import logging                    # standard Python logging
import json                       # for JSON formatting
from datetime import datetime     # for timestamps
from fluent import handler        # Fluentd logging handler

def setup_logging(app_name: str, log_level: str = "INFO") -> logging.Logger:
    """
    Set up structured logging that sends to both:
    1. The terminal (for development)
    2. Fluentd → Elasticsearch (for production monitoring)
    """

    logger = logging.getLogger(app_name)
    logger.setLevel(getattr(logging, log_level.upper()))  # e.g. logging.INFO

    # ── Handler 1: terminal output (human-readable) ───────────────────────────
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Format: timestamp | level | logger name | message
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # ── Handler 2: Fluentd (structured JSON) ─────────────────────────────────
    try:
        fluent_handler = handler.FluentHandler(
            app_name,                    # tag prefix for log routing in Fluentd
            host='localhost',            # Fluentd host
            port=24224,                  # Fluentd port
            timeout=3.0,                 # don't hang more than 3 seconds
            verbose=False
        )
        # Tell the Fluentd handler to use a structured formatter
        fluent_handler.setFormatter(handler.FluentRecordFormatter({
            'app':       '%(name)s',     # which application
            'level':     '%(levelname)s',# log level
            'message':   '%(message)s', # the actual message
            'timestamp': '%(asctime)s', # when it happened
            'filename':  '%(filename)s',# which file logged this
            'lineno':    '%(lineno)d'   # which line number
        }))
        logger.addHandler(fluent_handler)
        print(f"Fluentd handler connected for {app_name}")
    except Exception as e:
        # If Fluentd is not running, just log to terminal only
        print(f"Warning: could not connect to Fluentd: {e}. Logging to console only.")

    return logger
```

```python
# Using structured logging in your FastAPI app
from structured_logging import setup_logging
from fastapi import FastAPI, Request
import time

app = FastAPI()
logger = setup_logging('fastapi_app', log_level='INFO')

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log every HTTP request with timing information."""
    start_time = time.time()                    # record when request arrived

    response = await call_next(request)         # process the request

    duration_ms = round((time.time() - start_time) * 1000, 2)  # calculate duration

    # Log structured data — all fields are searchable in Kibana
    logger.info(
        "HTTP request processed",
        extra={
            'http_method': request.method,      # GET, POST, etc.
            'http_path': str(request.url.path), # /books, /health, etc.
            'status_code': response.status_code, # 200, 404, 500 etc.
            'duration_ms': duration_ms,          # how long it took
            'client_ip': request.client.host     # who made the request
        }
    )

    return response

@app.get("/health")
async def health_check():
    """Health check endpoint — used by monitoring systems."""
    logger.debug("Health check called")  # DEBUG level: only shows in dev
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/books")
async def get_books():
    """Return list of books — logs any errors."""
    try:
        # ... fetch from database ...
        books = []  # placeholder
        logger.info(f"Books endpoint called — returned {len(books)} books")
        return books
    except Exception as e:
        logger.error(
            f"Error fetching books: {e}",
            exc_info=True,              # include full stack trace in log
            extra={'error_type': type(e).__name__}
        )
        raise
```

---

### Step 7 — Set up Kibana

**In your browser at http://localhost:5601:**

1. First visit: click **Explore on my own**
2. Go to **Stack Management → Index Patterns**
3. Click **Create index pattern**
4. Pattern: `fluentd-*` (matches all Fluentd indices)
5. Time field: `@timestamp`
6. Click **Create index pattern**

**Now go to Discover (the magnifying glass icon):**

- Select the `fluentd-*` index pattern
- You should see your Python application logs flowing in
- Use the search bar to filter: `level: ERROR` or `app: fastapi_app`
- Add columns by clicking field names in the left sidebar

**Create a Kibana dashboard:**

1. Go to **Dashboard → Create new dashboard**
2. Add a **Lens** visualisation:
   - X axis: `@timestamp` (date histogram, interval: Auto)
   - Y axis: Count of records
   - Split by: `level.keyword`
   - This shows: log volume over time, coloured by log level
3. Add a second visualisation:
   - Type: **Data table**
   - Rows: `http_path.keyword` (top 10 paths)
   - Metrics: Average of `duration_ms`
   - This shows: which endpoints are slowest
4. Save the dashboard as "FastAPI Request Monitor"

---

### Step 8 — Log rotation on Ubuntu 24

```bash
# Logs grow forever if you don't rotate them — this fills your disk
# logrotate is built into Ubuntu and handles this automatically

# Check your application's log config
cat /etc/logrotate.conf

# Create a custom logrotate config for your app logs
sudo nano /etc/logrotate.d/myapp
```

```
# /etc/logrotate.d/myapp
/var/log/myapp/*.log {
    daily                  # rotate every day
    rotate 14              # keep 14 days of logs
    compress               # compress old logs with gzip
    delaycompress          # don't compress the most recent rotated log
    missingok              # don't error if log file is missing
    notifempty             # don't rotate empty log files
    create 0640 ubuntu ubuntu  # create new empty log file with these permissions
    postrotate
        # Tell your app to reopen its log file after rotation
        kill -HUP $(cat /var/run/myapp.pid) 2>/dev/null || true
    endscript
}
```

```bash
# Test your logrotate config without actually rotating
sudo logrotate --debug /etc/logrotate.d/myapp

# Docker container log rotation — set in daemon.json
sudo nano /etc/docker/daemon.json
```

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "50m",
    "max-file": "5"
  }
}
```

```bash
# Apply Docker log rotation settings
sudo systemctl restart docker
# Each container's logs are now capped at 50MB × 5 files = 250MB max
```

---

### Minimal monitoring stack with Docker Compose

```yaml
# docker-compose-monitoring.yml — complete monitoring stack
# Prometheus + Grafana + cAdvisor + Node Exporter

version: "3.8"

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - "--config.file=/etc/prometheus/prometheus.yml"
      - "--storage.tsdb.retention.time=30d" # keep 30 days of metrics

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123 # change in production!
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - prometheus

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: cadvisor
    ports:
      - "8081:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
    privileged: true # needs elevated access to read container stats

  node_exporter:
    image: quay.io/prometheus/node-exporter:latest
    container_name: node_exporter
    network_mode: host # must use host network to see host metrics
    pid: host
    volumes:
      - /:/host:ro,rslave
    command:
      - "--path.rootfs=/host"

volumes:
  prometheus_data: # persist Prometheus data
  grafana_data: # persist Grafana dashboards and settings
```

```bash
# Start the full monitoring stack
docker-compose -f docker-compose-monitoring.yml up -d

# Verify all 4 services are running
docker-compose -f docker-compose-monitoring.yml ps

# Services now available:
# Prometheus: http://localhost:9090
# Grafana:    http://localhost:3001
# cAdvisor:   http://localhost:8081
```

---

## ⚠️ Common Mistakes

**Mistake 1: Running Elasticsearch with too little memory**

```bash
# WRONG: default Elasticsearch wants 1–2GB RAM — on a 16GB machine this is fine
# but on low memory it kills the container silently

# CORRECT: limit heap size in docker-compose
environment:
  - ES_JAVA_OPTS=-Xms512m -Xmx512m   # 512MB min and max heap size
  # Do not set higher than half your available RAM
```

**Mistake 2: Logging sensitive data**

```python
# WRONG: logging credentials, personal data, or secrets
logger.info(f"User logged in: username={username}, password={password}")  # ❌ NEVER

# CORRECT: log only what you need for debugging, never secrets
logger.info(f"User logged in: user_id={user_id}")  # ✅ ID only, not password
```

**Mistake 3: Not watching disk space when logging**

```bash
# Logs fill disks fast — check disk usage regularly
df -h /var/log       # how full is the log partition?
du -sh /var/log/*    # which log directory is biggest?

# Set up a disk space alert in Grafana:
# node_filesystem_avail_bytes{mountpoint="/"} < 5e9
# (alert when less than 5GB free)
```

---

## ✅ Exercises

**Exercise 1 — Easy**
Run `docker stats --no-stream` on your machine and write a bash one-liner that extracts only the container name and memory usage columns, and saves them to a `memory_snapshot.txt` file.

**Exercise 2 — Medium**
Add a `GET /metrics/summary` endpoint to your FastAPI app that queries the `pipeline_runs` table and returns a JSON summary of the last 24 hours: total runs, success rate, average duration, and total rows processed.

**Exercise 3 — Hard**
Write a Python script that queries Elasticsearch directly using the `elasticsearch` Python client, retrieves all ERROR-level log entries from the last hour, groups them by `http_path`, and prints a sorted count of which endpoints are generating the most errors.

---

## 🏗️ Mini Project — Minimal Monitoring Stack

**Goal:** Get cAdvisor + Prometheus + Grafana running and monitoring your application containers.

**Step 1:** Start the `docker-compose-monitoring.yml` stack above.

**Step 2:** Add your Python app and its containers to the Prometheus config.

**Step 3:** In Grafana, import the official **Docker & System Monitoring** dashboard (Dashboard ID: `893`) — this gives you a pre-built system dashboard in seconds.

**Step 4:** Add a FastAPI request log panel: connect Grafana to your Fluentd/Elasticsearch, create a Logs panel showing the last 100 error-level log entries.

**Step 5:** Create one alert: when any container's memory usage exceeds 80% of the limit, send a Slack webhook notification.

---

## 🔗 What's Next

In **Module 5-5: Visualising Results & Trends**, you will step back from infrastructure and focus on communicating data insights through charts, reports, and visual storytelling — choosing the right chart for the right question.
