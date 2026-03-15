---
tags:
  - Advanced
  - Phase 6
---

# Module 5: Production Monitoring & Error Handling

> **Phase 6 — MLOps & Deployment**

---

## 🎯 What You Will Learn

- What changes when your application goes from development to production
- The four golden signals of site reliability engineering
- How to integrate Sentry for error tracking and performance monitoring
- How model drift works and why it silently kills model performance
- How to detect data drift using the Evidently library
- How to build automated retraining triggers
- How to roll back to a previous model when a new one underperforms
- Production logging patterns: structured logs, correlation IDs, request tracing
- The complete production architecture diagram for everything built in this roadmap

---

## 🧠 Concept Explained

There is a huge difference between a model that works on your laptop and a model that works reliably in production at 2am when you are asleep.

On your laptop, you control everything. You know the data. You can fix it immediately if something breaks. In production, the data is live and unpredictable. Users make unexpected requests. The data distribution shifts over time. Memory leaks slowly. And you are not there to see it.

**Production monitoring is the system that watches your application while you sleep and wakes you up only when something is actually wrong.**

!!! note "The hardest part of ML in production"
A web server either works or it doesn't. You know immediately.
An ML model can silently degrade — still returning predictions, never throwing errors,
but becoming increasingly wrong because the world changed.
This is called model drift, and it is invisible without monitoring.

---

## 🔍 How It Works

```
The full production monitoring stack:

User request
    │
    ▼
┌─────────────────────────────────────────────────────┐
│                 FastAPI Application                  │
│                                                      │
│  • Sentry SDK: captures every exception             │
│  • Correlation ID: unique ID per request            │
│  • Structured logs: JSON to Elasticsearch           │
│  • Prometheus metrics: latency, error rate          │
└─────────────────────────────────────────────────────┘
    │                    │                    │
    ▼                    ▼                    ▼
Sentry.io          Prometheus            Elasticsearch
(errors +          (metrics +            (logs +
 performance)       Grafana alerts)       Kibana search)
    │                    │
    ▼                    ▼
Email/Slack alert   PagerDuty alert
when error spikes   when latency > 2s

Separately — model health:
    │
    ▼
┌─────────────────────────────────────────────────────┐
│               Evidently Monitoring                   │
│                                                      │
│  Daily job: compare today's data vs training data   │
│  Detects: feature drift, prediction drift            │
│  If drift detected: trigger Celery retraining job   │
└─────────────────────────────────────────────────────┘
    │
    ▼
Celery task: retrain model → log to MLflow → promote to Production
```

---

## 🛠️ Step-by-Step Guide

### Step 1 — Add Sentry to FastAPI

### Step 2 — Add correlation IDs to requests

### Step 3 — Implement the golden signals

### Step 4 — Understand model drift

### Step 5 — Detect data drift with Evidently

### Step 6 — Build an automated retraining trigger

### Step 7 — Implement rollback strategies

### Step 8 — Production logging with correlation IDs

---

## 💻 Code Examples

### Step 1 — Integrate Sentry into FastAPI

```bash
# Install Sentry SDK
pip install sentry-sdk[fastapi]

# Create a free account at sentry.io
# Create a new project → Python → FastAPI
# Copy the DSN (Data Source Name) — looks like: https://abc123@sentry.io/456789
```

```python
# app/main.py — FastAPI with Sentry integration

import sentry_sdk                              # error tracking
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from fastapi import FastAPI, Request
import os
import uuid
import time
import logging
import json

# ── Initialise Sentry ─────────────────────────────────────────────────────────
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),    # read from environment variable, never hardcode
    integrations=[
        FastApiIntegration(
            transaction_style="endpoint"   # group transactions by endpoint name
        ),
        SqlalchemyIntegration(),           # also track slow database queries
    ],
    traces_sample_rate=0.1,    # trace 10% of requests for performance monitoring
    # 1.0 = trace everything (expensive), 0.1 = 10% sample (cheaper)
    profiles_sample_rate=0.1,  # profile 10% of transactions (CPU + memory)
    environment=os.getenv("ENVIRONMENT", "development"),  # tag errors by environment
    release=os.getenv("GIT_SHA", "unknown"),  # tag errors by git commit
    # This lets you filter: "show only errors introduced in version abc123"
)

app = FastAPI(title="Book Price Predictor API")

# ── Middleware: add correlation ID to every request ───────────────────────────
@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    """
    Assign a unique correlation ID to every request.
    This ID appears in logs, Sentry errors, and response headers.
    When debugging, search logs/Sentry for the correlation ID to see
    everything that happened during one specific request.
    """
    # Check if the client sent a correlation ID (useful for distributed tracing)
    correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())

    # Store in request state so other parts of the app can access it
    request.state.correlation_id = correlation_id

    # Add to Sentry context — all errors in this request will include this ID
    with sentry_sdk.configure_scope() as scope:
        scope.set_tag("correlation_id", correlation_id)
        scope.set_tag("endpoint", str(request.url.path))

    start_time = time.time()
    response = await call_next(request)     # process the request
    duration_ms = (time.time() - start_time) * 1000

    # Add correlation ID to response headers so client can reference it
    response.headers["X-Correlation-ID"] = correlation_id

    # Structured log entry for every request
    log_entry = {
        "event": "http_request",
        "correlation_id": correlation_id,
        "method": request.method,
        "path": str(request.url.path),
        "status_code": response.status_code,
        "duration_ms": round(duration_ms, 2),
        "client_ip": request.client.host if request.client else "unknown"
    }
    logging.info(json.dumps(log_entry))   # log as JSON for easy parsing

    return response

# ── Error handler: capture unhandled exceptions ───────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch any unhandled exception, log it, and return a clean error response."""
    correlation_id = getattr(request.state, "correlation_id", "unknown")

    # Sentry automatically captures exceptions in route handlers
    # but this catches anything else
    sentry_sdk.capture_exception(exc)

    logging.error(json.dumps({
        "event": "unhandled_exception",
        "correlation_id": correlation_id,
        "error_type": type(exc).__name__,
        "error_message": str(exc)
    }))

    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "correlation_id": correlation_id   # return so users can report it
        }
    )

# ── Example route with Sentry breadcrumbs ─────────────────────────────────────
@app.post("/predict")
async def predict_price(book: dict, request: Request):
    """Predict book price — with Sentry performance tracing."""

    # Add a breadcrumb: Sentry shows these as a trail of events leading to an error
    sentry_sdk.add_breadcrumb(
        category="prediction",
        message=f"Predicting price for genre: {book.get('genre')}",
        level="info"
    )

    try:
        model = get_model()
        prediction = model.predict([[book['genre_encoded'], book['rating'], book['in_stock']]])
        return {"predicted_price": round(float(prediction[0]), 2)}

    except KeyError as e:
        # Capture with extra context
        with sentry_sdk.push_scope() as scope:
            scope.set_context("book_data", book)            # attach the bad input to the error
            scope.set_tag("error_type", "missing_field")
            sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=422, detail=f"Missing field: {e}")
```

---

### Step 2 — The Four Golden Signals

```python
# golden_signals.py — implement the 4 golden signals as Prometheus metrics

from prometheus_client import Counter, Histogram, Gauge
import time

# ── Signal 1: Latency — how long requests take ────────────────────────────────
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint', 'status_code'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0]
    # buckets: track what % of requests take < 10ms, < 50ms, < 100ms, etc.
)

# ── Signal 2: Traffic — how many requests per second ─────────────────────────
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

# ── Signal 3: Errors — what % of requests are failing ────────────────────────
ERROR_COUNT = Counter(
    'http_errors_total',
    'Total HTTP errors (4xx and 5xx)',
    ['method', 'endpoint', 'status_code']
)

# ── Signal 4: Saturation — how full is the system? ───────────────────────────
ACTIVE_REQUESTS = Gauge(
    'http_active_requests',
    'Number of requests currently being processed'
)

# ── ML-specific metrics ───────────────────────────────────────────────────────
PREDICTION_COUNT = Counter(
    'ml_predictions_total',
    'Total number of ML predictions made',
    ['model_version']
)

PREDICTION_LATENCY = Histogram(
    'ml_prediction_duration_seconds',
    'Time to generate one ML prediction',
    ['model_version'],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5]
)

PREDICTION_VALUE = Histogram(
    'ml_predicted_price_distribution',
    'Distribution of predicted prices (to detect prediction drift)',
    buckets=[5, 10, 15, 20, 25, 30, 35, 40, 50, 75, 100]
)
```

---

### Step 3 — Model Drift: the concept

```
What is model drift?

Training data (January):             Live data (July):
Books sold in winter                 Books sold in summer
┌──────────────────────┐             ┌──────────────────────┐
│ Fiction: avg $8.99   │             │ Fiction: avg $12.99  │  ← prices changed
│ Fantasy: avg $18.49  │             │ Fantasy: avg $22.99  │
│ Ratings: avg 4.6     │             │ Ratings: avg 4.2     │  ← user behaviour changed
└──────────────────────┘             └──────────────────────┘

The model was trained on January distributions.
In July, the input distributions are different.
The model still predicts — no errors, no crashes —
but its predictions are increasingly wrong.

Two types of drift:
┌─────────────────┬─────────────────────────────────────────────────────┐
│ Data drift      │ Input feature distributions have changed             │
│ (covariate)     │ e.g. prices shifted, new genres appeared             │
├─────────────────┼─────────────────────────────────────────────────────┤
│ Concept drift   │ The relationship between inputs and outputs changed  │
│                 │ e.g. high rating no longer predicts high price       │
└─────────────────┴─────────────────────────────────────────────────────┘
```

---

### Step 4 — Detect data drift with Evidently

```bash
# Install Evidently
pip install evidently
```

```python
# drift_detection.py — detect data drift in book price predictions

import pandas as pd
import numpy as np
import psycopg2
import mlflow
import json
import logging
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, DataQualityPreset
from evidently.metrics import (
    DatasetDriftMetric,
    ColumnDriftMetric
)
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def load_training_data() -> pd.DataFrame:
    """Load the data the model was originally trained on."""
    conn = psycopg2.connect(
        host="localhost", database="books_db",
        user="postgres", password="yourpassword"
    )
    # Load books from the training period (e.g. first 3 months of data)
    df = pd.read_sql("""
        SELECT genre, rating, CAST(in_stock AS INTEGER) as in_stock, price
        FROM books
        WHERE scraped_at < NOW() - INTERVAL '90 days'
        ORDER BY scraped_at
        LIMIT 500
    """, conn)
    conn.close()
    return df

def load_recent_data() -> pd.DataFrame:
    """Load the most recent data from the last 7 days."""
    conn = psycopg2.connect(
        host="localhost", database="books_db",
        user="postgres", password="yourpassword"
    )
    df = pd.read_sql("""
        SELECT genre, rating, CAST(in_stock AS INTEGER) as in_stock, price
        FROM books
        WHERE scraped_at >= NOW() - INTERVAL '7 days'
        ORDER BY scraped_at
    """, conn)
    conn.close()
    return df

def detect_drift() -> dict:
    """
    Compare training data to recent data.
    Returns a dict with drift results and whether retraining is needed.
    """
    reference_data = load_training_data()   # what the model was trained on
    current_data   = load_recent_data()     # what the model is seeing now

    if len(current_data) < 50:
        logger.warning("Not enough recent data for drift detection (< 50 rows)")
        return {"drift_detected": False, "reason": "insufficient_data"}

    # ── Build Evidently report ────────────────────────────────────────────────
    report = Report(metrics=[
        DatasetDriftMetric(),    # overall: is the dataset drifting?
        ColumnDriftMetric(column_name="price"),    # target variable drift
        ColumnDriftMetric(column_name="rating"),   # feature drift
        DataQualityPreset(),     # check for missing values, outliers, etc.
    ])

    report.run(
        reference_data=reference_data,   # training data (baseline)
        current_data=current_data         # recent data (to compare)
    )

    # ── Save HTML report ──────────────────────────────────────────────────────
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"drift_reports/drift_report_{timestamp}.html"
    report.save_html(report_path)   # human-readable report
    logger.info(f"Drift report saved to {report_path}")

    # ── Extract drift results as JSON ─────────────────────────────────────────
    report_dict = report.as_dict()

    # Find the overall dataset drift result
    dataset_drift_result = report_dict['metrics'][0]['result']
    drift_detected = dataset_drift_result['dataset_drift']         # True or False
    drift_share    = dataset_drift_result['drift_share']           # % of features drifted

    # Find column-level drift
    price_drift = report_dict['metrics'][1]['result']['drift_detected']
    rating_drift = report_dict['metrics'][2]['result']['drift_detected']

    result = {
        "drift_detected": drift_detected,
        "drift_share": drift_share,           # e.g. 0.67 = 67% of features drifted
        "price_drift": price_drift,
        "rating_drift": rating_drift,
        "reference_rows": len(reference_data),
        "current_rows": len(current_data),
        "report_path": report_path,
        "checked_at": datetime.now().isoformat()
    }

    # Log drift metrics to MLflow for tracking over time
    mlflow.set_tracking_uri("http://localhost:5000")
    with mlflow.start_run(experiment_id=None, run_name=f"drift-check-{timestamp}"):
        mlflow.set_experiment("drift-monitoring")
        mlflow.log_metric("drift_share", drift_share)
        mlflow.log_metric("price_drift", int(price_drift))
        mlflow.log_metric("rating_drift", int(rating_drift))
        mlflow.log_artifact(report_path)

    logger.info(f"Drift check complete: drift_detected={drift_detected}, share={drift_share:.2%}")
    return result

# ── Save results to database ──────────────────────────────────────────────────
def save_drift_result(result: dict):
    """Save drift check results to the pipeline_runs table."""
    conn = psycopg2.connect(
        host="localhost", database="books_db",
        user="postgres", password="yourpassword"
    )
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO pipeline_runs
                (pipeline_name, started_at, finished_at, status, error_message)
            VALUES
                ('drift_check', NOW(), NOW(), %s, %s)
        """, (
            'drift_detected' if result['drift_detected'] else 'no_drift',
            json.dumps(result)   # store full result as JSON in error_message column
        ))
        conn.commit()
    conn.close()
```

---

### Step 5 — Automated retraining trigger

```python
# celery_tasks.py — Celery task to retrain the model when drift is detected

from celery import Celery
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient
import pandas as pd
import psycopg2
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np
import logging

logger = logging.getLogger(__name__)

app = Celery('tasks', broker='redis://localhost:6379/0')

@app.task(
    name='retrain_book_price_model',
    max_retries=3,                  # retry up to 3 times if it fails
    default_retry_delay=300,        # wait 5 minutes between retries
    soft_time_limit=600,            # warn at 10 minutes
    time_limit=900                  # kill at 15 minutes
)
def retrain_book_price_model():
    """
    Retrain the book price model on the latest data.
    Called automatically when drift is detected.
    Registers the new model in MLflow and promotes to Production if it's better.
    """
    logger.info("Starting automated model retraining...")

    try:
        # ── Load all current data ─────────────────────────────────────────────
        conn = psycopg2.connect(
            host="localhost", database="books_db",
            user="postgres", password="yourpassword"
        )
        df = pd.read_sql("SELECT genre, rating, in_stock, price FROM books WHERE price > 0", conn)
        conn.close()

        # ── Prepare features ──────────────────────────────────────────────────
        df = df.dropna()
        le = LabelEncoder()
        df['genre_encoded'] = le.fit_transform(df['genre'])
        df['in_stock_int'] = df['in_stock'].astype(int)

        X = df[['genre_encoded', 'rating', 'in_stock_int']]
        y = df['price']

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # ── Get current Production model's performance ────────────────────────
        client = MlflowClient()
        mlflow.set_tracking_uri("http://localhost:5000")

        try:
            prod_versions = client.get_latest_versions("BookPricePredictor", stages=["Production"])
            current_prod_run_id = prod_versions[0].run_id
            current_prod_run = client.get_run(current_prod_run_id)
            current_prod_rmse = current_prod_run.data.metrics.get("rmse", float("inf"))
            logger.info(f"Current Production RMSE: {current_prod_rmse:.2f}")
        except Exception:
            current_prod_rmse = float("inf")   # no current model — any new model is better
            logger.info("No current Production model found")

        # ── Train new model ───────────────────────────────────────────────────
        mlflow.set_experiment("automated-retraining")
        with mlflow.start_run(run_name="auto-retrain"):
            mlflow.log_param("trigger", "drift_detected")
            mlflow.log_param("training_rows", len(X_train))
            mlflow.log_param("n_estimators", 200)
            mlflow.log_param("max_depth", 15)

            new_model = RandomForestRegressor(
                n_estimators=200, max_depth=15, random_state=42
            )
            new_model.fit(X_train, y_train)

            y_pred = new_model.predict(X_test)
            new_rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            new_r2 = r2_score(y_test, y_pred)

            mlflow.log_metric("rmse", new_rmse)
            mlflow.log_metric("r2_score", new_r2)

            mlflow.sklearn.log_model(
                new_model,
                artifact_path="model",
                registered_model_name="BookPricePredictor"
            )

            new_version = client.get_latest_versions("BookPricePredictor", stages=["None"])[0]

            # ── Only promote if new model is better ───────────────────────────
            improvement_threshold = 0.05   # new model must be at least 5% better

            if new_rmse < current_prod_rmse * (1 - improvement_threshold):
                # New model is significantly better → promote to Production
                client.transition_model_version_stage(
                    name="BookPricePredictor",
                    version=new_version.version,
                    stage="Production",
                    archive_existing_versions=True   # archive old production model
                )
                logger.info(
                    f"New model (v{new_version.version}) promoted to Production. "
                    f"RMSE improved: {current_prod_rmse:.2f} → {new_rmse:.2f}"
                )
                return {
                    "action": "promoted_to_production",
                    "new_version": new_version.version,
                    "old_rmse": current_prod_rmse,
                    "new_rmse": new_rmse
                }
            else:
                # New model is not better → archive without promoting
                client.transition_model_version_stage(
                    name="BookPricePredictor",
                    version=new_version.version,
                    stage="Archived"
                )
                logger.info(
                    f"New model did not improve sufficiently. "
                    f"Keeping current Production. "
                    f"Old RMSE: {current_prod_rmse:.2f}, New RMSE: {new_rmse:.2f}"
                )
                return {
                    "action": "kept_existing_production",
                    "old_rmse": current_prod_rmse,
                    "new_rmse": new_rmse
                }

    except Exception as exc:
        logger.error(f"Retraining failed: {exc}")
        raise retrain_book_price_model.retry(exc=exc)   # retry the task
```

```python
# drift_scheduler.py — schedule drift checks and trigger retraining

from celery import Celery
from celery.schedules import crontab
from drift_detection import detect_drift, save_drift_result

app = Celery('tasks', broker='redis://localhost:6379/0')

app.conf.beat_schedule = {
    # Run drift detection every day at 3am
    'check-drift-daily': {
        'task': 'check_and_retrain',
        'schedule': crontab(hour=3, minute=0),   # 3:00 AM every day
    }
}

@app.task(name='check_and_retrain')
def check_and_retrain():
    """Check for drift and trigger retraining if detected."""
    result = detect_drift()
    save_drift_result(result)

    if result['drift_detected'] and result['drift_share'] > 0.3:
        # More than 30% of features drifted → trigger retraining
        from celery_tasks import retrain_book_price_model
        retrain_book_price_model.delay()   # .delay() = async, don't wait for result
        return f"Drift detected ({result['drift_share']:.0%}). Retraining triggered."
    else:
        return f"No significant drift. Drift share: {result.get('drift_share', 0):.0%}"
```

---

### Step 6 — Rollback strategy

```python
# rollback.py — rollback to the previous Production model

from mlflow.tracking import MlflowClient
import mlflow

def rollback_production_model(model_name: str = "BookPricePredictor"):
    """
    Roll back to the previous Production model.
    Called when the current Production model is underperforming.
    """
    client = MlflowClient()
    mlflow.set_tracking_uri("http://localhost:5000")

    # Get all archived versions (these were previously in Production)
    archived_versions = client.get_latest_versions(model_name, stages=["Archived"])

    if not archived_versions:
        print("No archived versions available for rollback")
        return None

    # Sort by version number descending — most recent archived version first
    archived_versions.sort(key=lambda v: int(v.version), reverse=True)
    previous_version = archived_versions[0]   # most recent archived = previous production

    print(f"Rolling back to version {previous_version.version}")

    # Archive the current broken Production model
    current_prod = client.get_latest_versions(model_name, stages=["Production"])
    if current_prod:
        client.transition_model_version_stage(
            name=model_name,
            version=current_prod[0].version,
            stage="Archived"
        )
        print(f"Archived broken version {current_prod[0].version}")

    # Restore the previous version to Production
    client.transition_model_version_stage(
        name=model_name,
        version=previous_version.version,
        stage="Production",
        archive_existing_versions=False   # we already archived it manually above
    )

    print(f"Version {previous_version.version} restored to Production")

    # Trigger model reload in FastAPI
    import requests
    try:
        response = requests.post("http://localhost:8000/reload-model", timeout=10)
        print(f"FastAPI model reload: {response.json()}")
    except Exception as e:
        print(f"Warning: could not reload FastAPI model automatically: {e}")
        print("Manually restart the FastAPI container to load the restored model")

    return previous_version.version

# Usage:
# rollback_production_model()
```

---

### The full production architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    The AI & MLOps Engineer Roadmap                          │
│                    Full Production Architecture                             │
└─────────────────────────────────────────────────────────────────────────────┘

Phase 1: DATA INGESTION
┌────────────────┐    ┌─────────────────┐
│  Web Scraper   │    │   REST API      │
│  (requests +   │    │   Client        │
│  BeautifulSoup)│    │                 │
└───────┬────────┘    └────────┬────────┘
        └─────────────────────┘
                    │
                    ▼ raw data

Phase 1-2: STORAGE & VALIDATION
┌─────────────────────────────┐
│      PostgreSQL Database    │
│  books | weather | pipeline │
│  _runs | metrics            │
└──────────────┬──────────────┘
               │ validated, normalised data
               ▼

Phase 2: ORCHESTRATION
┌─────────────────────────────┐
│    Apache Airflow           │
│    DAG: scrape → validate   │
│         → transform → load  │
└──────────────┬──────────────┘
               │ transformed data
               ▼

Phase 2: TRANSFORMATION
┌─────────────────────────────┐
│    dbt models               │
│    stg → int → mart         │
└──────────────┬──────────────┘
               │ analytics-ready data
               ▼

Phase 3: ML TRAINING
┌─────────────────────────────┐     ┌──────────────────┐
│    Training Scripts         │────►│  MLflow Tracking │
│    sklearn models           │     │  Experiments     │
│    Feature engineering      │     │  Model Registry  │
└──────────────┬──────────────┘     └──────────────────┘
               │ Production model
               ▼

Phase 3 + 6: MODEL SERVING
┌─────────────────────────────┐     ┌──────────────────┐
│    FastAPI Application      │────►│  Sentry          │
│    POST /predict            │     │  Error tracking  │
│    GET /health              │     └──────────────────┘
│    POST /reload-model       │
└──────────────┬──────────────┘
               │ prediction requests
               ▼

Phase 4: ASYNC PROCESSING
┌─────────────────────────────┐     ┌──────────────────┐
│    Redis Queue              │────►│  Celery Workers  │
│    Task broker              │     │  Retraining jobs │
│    Result backend           │     │  Drift checks    │
└──────────────┬──────────────┘     └──────────────────┘
               │
               ▼

Phase 5 + 6: MONITORING & ALERTING
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Prometheus  │  │   Grafana    │  │Elasticsearch │  │   Kibana     │
│  Metrics     │─►│  Dashboards  │  │  Log store   │─►│  Log search  │
│  collection  │  │  + Alerts    │  └──────────────┘  └──────────────┘
└──────────────┘  └──────────────┘
                        │
                        ▼
               ┌──────────────┐
               │   Alerts     │
               │  Slack/Email │
               │  PagerDuty   │
               └──────────────┘

Phase 6: DEPLOYMENT
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Docker       │  │ GitHub       │  │ Evidently    │
│ Compose      │  │ Actions      │  │ Drift        │
│ Full stack   │  │ CI/CD        │  │ Detection    │
└──────────────┘  └──────────────┘  └──────────────┘
```

---

## ⚠️ Common Mistakes

**Mistake 1: Not setting SENTRY_DSN as an environment variable**

```python
# WRONG: hardcoded DSN — visible to anyone who reads your code
sentry_sdk.init(dsn="https://abc123@sentry.io/456789")   # ❌

# CORRECT: always read from environment
sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"))              # ✅
# In docker-compose.yml or .env:
# SENTRY_DSN=https://abc123@sentry.io/456789
```

**Mistake 2: Promoting a new model to Production without comparing to current**

```python
# WRONG: always promote the new model, even if it's worse
client.transition_model_version_stage(name="MyModel", version=new_version, stage="Production")

# CORRECT: only promote if the new model is measurably better
if new_rmse < current_rmse * 0.95:   # must be at least 5% better
    client.transition_model_version_stage(...)
else:
    client.transition_model_version_stage(..., stage="Archived")
```

**Mistake 3: Detecting drift but not acting on it**

```python
# WRONG: detect drift, log it, do nothing
result = detect_drift()
logger.info(f"Drift: {result}")   # ❌ information without action

# CORRECT: drift detection triggers a response
result = detect_drift()
if result['drift_detected'] and result['drift_share'] > 0.3:
    retrain_book_price_model.delay()   # ✅ automated response
    alert_slack(f"Drift detected: {result['drift_share']:.0%}. Retraining triggered.")
```

---

## ✅ Exercises

**Exercise 1 — Easy**
Add a `/sentry-test` endpoint to the FastAPI app that intentionally raises a `ZeroDivisionError`. Call the endpoint, then go to sentry.io and find the error. Verify it shows the correlation ID, endpoint, and environment.

**Exercise 2 — Medium**
Write a Python script that loads the last 30 days of prediction logs from the `pipeline_runs` table, calculates the daily average predicted price, plots it as a time series, and flags any day where the average deviates more than 2 standard deviations from the 30-day mean.

**Exercise 3 — Hard**
Extend the `retrain_book_price_model` Celery task to send a Slack notification with the retraining result: whether the model was promoted, the old vs new RMSE, and a link to the MLflow run. Use the Slack Webhooks API.

---

## 🏗️ Mini Project — The Capstone

**This is the final project of the entire AI & MLOps Engineer Roadmap.**

**Goal:** Add Evidently drift detection to the book price model. If drift is detected, trigger a retraining job via Celery. The full automated cycle should run without any human intervention.

```bash
# Step 1: install Evidently
pip install evidently

# Step 2: create the drift reports directory
mkdir -p drift_reports

# Step 3: create the drift detection and retraining code
# (use the code examples from this module)

# Step 4: register the initial model
python train_book_price_model.py

# Step 5: start the Celery worker and beat scheduler
celery -A celery_tasks worker --loglevel=info &
celery -A drift_scheduler beat --loglevel=info &

# Step 6: manually trigger a drift check to test
python -c "from drift_scheduler import check_and_retrain; check_and_retrain()"

# Step 7: verify the full cycle works
# - Check drift_reports/ for the HTML report
# - Check MLflow UI for the new experiment run
# - Check the pipeline_runs table for the drift check record
# - If drift was detected, verify a retraining task appeared in Celery Flower

# Step 8: simulate drift by updating the database
psql -U postgres -d books_db -c "UPDATE books SET price = price * 2;"
# This doubles all prices — creating a major distribution shift

# Step 9: trigger drift check again
python -c "from drift_scheduler import check_and_retrain; check_and_retrain()"

# Drift should now be detected, retraining should be triggered automatically

echo "🎉 Congratulations — you have completed the AI & MLOps Engineer Roadmap!"
```

---

## 🎓 Roadmap Complete

You have reached the end of all 6 phases and 35 modules.

Here is what you can now do:

**Phase 0:** Set up Python, Git, Docker, Linux, and PostgreSQL from scratch.
**Phase 1:** Collect data from APIs and web pages, design schemas, clean data.
**Phase 2:** Build automated ETL pipelines with Airflow, dbt, and validation.
**Phase 3:** Train ML models, engineer features, build prediction APIs with FastAPI.
**Phase 4:** Process tasks asynchronously with Celery, Redis, and scheduled jobs.
**Phase 5:** Build analytics dashboards, track pipeline metrics with Prometheus and Grafana.
**Phase 6:** Containerise everything, set up CI/CD, track experiments with MLflow, monitor production with Sentry and Evidently.

**Your next steps:**

1. Build one complete end-to-end project using everything from Phase 0 to Phase 6
2. Push it to GitHub with a full CI/CD pipeline
3. Write a README explaining the architecture
4. Start applying for junior Data Engineer or ML Engineer roles

_You are ready. 🚀_
