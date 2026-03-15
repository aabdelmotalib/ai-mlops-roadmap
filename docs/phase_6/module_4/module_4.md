---
tags:
  - Advanced
  - Phase 6
---

# Module 4: Experiment Tracking with MLflow

> **Phase 6 — MLOps & Deployment**

---

## 🎯 What You Will Learn

- Why experiment tracking is essential when training ML models
- The core MLflow concepts: run, experiment, artifact, metric, parameter, model registry
- How to install and start the MLflow UI locally
- How to log parameters, metrics, and artifacts manually
- How to use autologging with scikit-learn
- How to register a model and promote it through Staging → Production
- How to load a registered model for inference in a FastAPI app
- How to run MLflow with a PostgreSQL backend for team use

---

## 🧠 Concept Explained

Imagine you are a scientist running experiments to find the best recipe for a new medicine. You try 20 different combinations of ingredients and doses. Without a lab notebook, you cannot remember which combination produced the best result. You cannot reproduce it. You cannot explain it to your team.

**MLflow is the lab notebook for machine learning.**

Every time you train a model, MLflow records what you tried (parameters), what happened (metrics), what you produced (artifacts like model files), and when you ran it. Later you can open the MLflow UI, see all 20 experiments side by side, click on the best one, and reproduce it exactly.

!!! note "Without MLflow — a common disaster"
"We trained 15 models last month. The best one had accuracy 0.94 but nobody
remembers what hyperparameters we used. We deleted the notebook. The model
file is somewhere on someone's laptop."

    With MLflow: every run is recorded. Nothing is lost.

---

## 🔍 How It Works

```
Your training script
        │
        │  mlflow.log_param("n_estimators", 100)
        │  mlflow.log_metric("accuracy", 0.94)
        │  mlflow.log_artifact("model.pkl")
        │
        ▼
   MLflow Tracking Server
        │
        ├── Backend Store (where runs are saved)
        │       ├── Local filesystem (default, good for solo work)
        │       └── PostgreSQL database (good for teams)
        │
        └── Artifact Store (where files are saved)
                ├── Local filesystem: ./mlruns/
                └── S3 / GCS (for teams and production)
        │
        ▼
   MLflow UI (http://localhost:5000)
        │
        ├── List all experiments
        ├── Compare runs side by side
        ├── View charts of metrics over time
        └── Download artifacts
        │
        ▼
   Model Registry
        ├── Register the best model version
        ├── Stages: None → Staging → Production → Archived
        └── Load by stage: mlflow.sklearn.load_model("models:/MyModel/Production")
```

---

## 🛠️ Step-by-Step Guide

### Step 1 — Install MLflow and start the UI

### Step 2 — Log your first experiment manually

### Step 3 — Use autologging with scikit-learn

### Step 4 — Compare runs in the UI

### Step 5 — Register the best model

### Step 6 — Load the registered model in FastAPI

### Step 7 — Set up MLflow with PostgreSQL backend

---

## 💻 Code Examples

### Step 1 — Install and start MLflow

```bash
# Install MLflow and dependencies
pip install mlflow scikit-learn pandas psycopg2-binary

# Start the MLflow tracking server (default: local filesystem)
mlflow ui --port 5000

# Open the UI at http://localhost:5000
# You will see an empty experiments list — runs will appear after training
```

---

### Step 2 — Log your first experiment manually

```python
# train_book_price_model.py
# Train a model to predict book prices and track with MLflow

import mlflow                                    # experiment tracking
import mlflow.sklearn                            # sklearn-specific MLflow helpers
import pandas as pd                              # data manipulation
import numpy as np                               # numerical operations
import psycopg2                                  # PostgreSQL connection
from sklearn.ensemble import RandomForestRegressor  # the model we will train
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score
)
import os

# ── Tell MLflow where to save runs ────────────────────────────────────────────
mlflow.set_tracking_uri("http://localhost:5000")   # use our local MLflow server

# ── Create or select an experiment ───────────────────────────────────────────
# An experiment groups related runs together
mlflow.set_experiment("book-price-prediction")
# If the experiment doesn't exist, MLflow creates it automatically

# ── Load and prepare data ─────────────────────────────────────────────────────
def load_books_data():
    """Load books data from PostgreSQL."""
    conn = psycopg2.connect(
        host="localhost", database="books_db",
        user="postgres", password="yourpassword"
    )
    df = pd.read_sql("SELECT genre, rating, in_stock, price FROM books", conn)
    conn.close()
    return df

def prepare_features(df):
    """Encode categorical features and return X, y."""
    df = df.dropna()                        # drop rows with missing values

    le_genre = LabelEncoder()               # encode 'Fiction' → 0, 'Fantasy' → 1 etc
    df['genre_encoded'] = le_genre.fit_transform(df['genre'])

    df['in_stock_int'] = df['in_stock'].astype(int)   # True → 1, False → 0

    X = df[['genre_encoded', 'rating', 'in_stock_int']]  # features
    y = df['price']                                       # target: price to predict

    return X, y, le_genre

# ── Training function with MLflow tracking ────────────────────────────────────
def train_model(n_estimators: int, max_depth: int, min_samples_split: int):
    """
    Train a RandomForestRegressor with given hyperparameters.
    Logs everything to MLflow.
    """
    df = load_books_data()
    X, y, le_genre = prepare_features(df)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # ── Start an MLflow run ───────────────────────────────────────────────────
    with mlflow.start_run():   # everything inside this block is tracked as one run

        # ── Log hyperparameters ───────────────────────────────────────────────
        mlflow.log_param("n_estimators", n_estimators)       # number of trees
        mlflow.log_param("max_depth", max_depth)              # tree depth limit
        mlflow.log_param("min_samples_split", min_samples_split)  # split threshold
        mlflow.log_param("train_size", len(X_train))          # how much data we used
        mlflow.log_param("test_size", len(X_test))

        # ── Train the model ───────────────────────────────────────────────────
        model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            random_state=42                 # for reproducibility
        )
        model.fit(X_train, y_train)         # train on training data

        # ── Evaluate on test data ─────────────────────────────────────────────
        y_pred = model.predict(X_test)      # predict on unseen test data

        rmse = np.sqrt(mean_squared_error(y_test, y_pred))  # root mean squared error
        mae  = mean_absolute_error(y_test, y_pred)           # mean absolute error
        r2   = r2_score(y_test, y_pred)                      # R² score (0-1, higher=better)

        # ── Log metrics ───────────────────────────────────────────────────────
        mlflow.log_metric("rmse", rmse)      # log each metric by name
        mlflow.log_metric("mae", mae)
        mlflow.log_metric("r2_score", r2)

        # Log feature importances as metrics too
        for feature, importance in zip(X.columns, model.feature_importances_):
            mlflow.log_metric(f"importance_{feature}", importance)

        # ── Log the trained model as an artifact ──────────────────────────────
        mlflow.sklearn.log_model(
            model,
            artifact_path="model",          # folder name inside the run's artifacts
            registered_model_name="BookPricePredictor"  # also register in model registry
        )

        # ── Log the label encoder as a separate artifact ──────────────────────
        import pickle
        with open("genre_encoder.pkl", "wb") as f:
            pickle.dump(le_genre, f)        # save encoder to file
        mlflow.log_artifact("genre_encoder.pkl")  # upload file to MLflow
        os.remove("genre_encoder.pkl")            # clean up local file

        # ── Add tags for easy filtering in the UI ─────────────────────────────
        mlflow.set_tag("model_type", "RandomForestRegressor")
        mlflow.set_tag("dataset", "books_db")
        mlflow.set_tag("author", "your-name")

        print(f"Run complete — RMSE: {rmse:.2f}, MAE: {mae:.2f}, R²: {r2:.3f}")
        print(f"Run ID: {mlflow.active_run().info.run_id}")

        return rmse, r2

# ── Train 3 models with different hyperparameters ─────────────────────────────
print("Training model 1...")
train_model(n_estimators=50,  max_depth=5,    min_samples_split=2)

print("Training model 2...")
train_model(n_estimators=100, max_depth=10,   min_samples_split=2)

print("Training model 3...")
train_model(n_estimators=200, max_depth=None, min_samples_split=5)

print("\nAll runs complete. Open http://localhost:5000 to compare them.")
```

---

### Step 3 — Autologging with scikit-learn

```python
# autolog_example.py — MLflow can log everything automatically

import mlflow
import mlflow.sklearn

# One line enables automatic logging for ALL sklearn operations
# MLflow automatically logs: all params, all metrics, model, feature names
mlflow.sklearn.autolog(
    log_input_examples=True,    # log a sample of training data
    log_model_signatures=True,  # log input/output schema
    log_models=True             # log the trained model artifact
)

mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("book-price-autolog")

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import cross_val_score

with mlflow.start_run(run_name="gradient-boost-auto"):
    model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1)

    # MLflow autolog captures this automatically:
    model.fit(X_train, y_train)   # logs: n_estimators, learning_rate, etc.
    model.score(X_test, y_test)   # logs: training score

    # You can still add manual logs on top of autolog
    mlflow.set_tag("experiment_type", "gradient_boosting")
    mlflow.log_param("cross_val_folds", 5)

    # Log cross-validation scores
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='r2')
    mlflow.log_metric("cv_r2_mean", cv_scores.mean())
    mlflow.log_metric("cv_r2_std",  cv_scores.std())
```

---

### Step 4 — Comparing runs in the UI

```
In the MLflow UI at http://localhost:5000:

1. Click on the "book-price-prediction" experiment
2. You will see all 3 runs listed as rows
3. Click the checkbox on multiple runs to select them
4. Click "Compare" button
5. You will see:
   - A parallel coordinates chart showing all params and metrics
   - Bar charts comparing each metric across runs
   - A table with all logged values side by side

To find the best model:
1. Click the "RMSE" column header to sort by RMSE ascending
2. The run with the lowest RMSE is your best model
3. Click on that run to see all its details
4. Copy the Run ID — you will need it to register the model
```

---

### Step 5 — Register the best model

```python
# register_best_model.py — find and register the best run

import mlflow
from mlflow.tracking import MlflowClient

mlflow.set_tracking_uri("http://localhost:5000")

client = MlflowClient()    # client for programmatic access to MLflow API

# ── Find the best run by lowest RMSE ─────────────────────────────────────────
experiment = client.get_experiment_by_name("book-price-prediction")

runs = client.search_runs(
    experiment_ids=[experiment.experiment_id],
    order_by=["metrics.rmse ASC"],   # sort by RMSE lowest first
    max_results=1                    # only return the best
)

best_run = runs[0]
best_run_id = best_run.info.run_id
best_rmse = best_run.data.metrics["rmse"]
best_r2 = best_run.data.metrics["r2_score"]

print(f"Best run ID: {best_run_id}")
print(f"Best RMSE: {best_rmse:.2f}")
print(f"Best R²: {best_r2:.3f}")

# ── Register the model in the Model Registry ──────────────────────────────────
model_uri = f"runs:/{best_run_id}/model"    # path to the model artifact

# Register creates a new version in the registry
result = mlflow.register_model(
    model_uri=model_uri,
    name="BookPricePredictor"    # registry model name
)

print(f"Registered model version: {result.version}")

# ── Promote to Staging ────────────────────────────────────────────────────────
client.transition_model_version_stage(
    name="BookPricePredictor",
    version=result.version,
    stage="Staging",                      # Staging = ready for testing
    archive_existing_versions=False       # keep old versions in their current stage
)

print(f"Model version {result.version} promoted to Staging")

# ── After testing, promote to Production ──────────────────────────────────────
# (Run this after verifying the model performs well in staging)
client.transition_model_version_stage(
    name="BookPricePredictor",
    version=result.version,
    stage="Production",                   # Production = live, serving real traffic
    archive_existing_versions=True        # archive old Production versions
)

print(f"Model version {result.version} promoted to Production")
```

```
Model Registry stages:
None → Staging → Production → Archived

None:       Newly registered, not yet reviewed
Staging:    Being tested, not yet live
Production: Live, serving real predictions
Archived:   Replaced by a newer version, kept for rollback
```

---

### Step 6 — Load the registered model in FastAPI

```python
# app/model_loader.py — load the Production model from the MLflow registry

import mlflow.sklearn          # sklearn model loader
import mlflow.pyfunc           # generic model loader
import pandas as pd
import pickle
import logging

logger = logging.getLogger(__name__)

# Global model variable — loaded once at startup, reused for all requests
_model = None
_mlflow_client = None

def load_production_model():
    """
    Load the current Production version of BookPricePredictor from MLflow.
    Called once at app startup.
    """
    global _model

    mlflow.set_tracking_uri("http://localhost:5000")    # or your MLflow server URL

    try:
        # Load by stage name — always gets the current Production version
        # This means: no code change needed when you promote a new version
        model_uri = "models:/BookPricePredictor/Production"

        _model = mlflow.sklearn.load_model(model_uri)   # load as sklearn model
        logger.info("Production model loaded successfully from MLflow")

        # Log which version was loaded (useful for debugging)
        from mlflow.tracking import MlflowClient
        client = MlflowClient()
        versions = client.get_latest_versions("BookPricePredictor", stages=["Production"])
        if versions:
            logger.info(f"Loaded model version: {versions[0].version}")

    except Exception as e:
        logger.error(f"Failed to load model from MLflow: {e}")
        raise   # raise so the app doesn't start with a broken model

    return _model

def get_model():
    """Return the loaded model — loads it if not already loaded."""
    global _model
    if _model is None:
        _model = load_production_model()    # lazy load on first call
    return _model
```

```python
# app/main.py — FastAPI app using the registered model

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
from model_loader import get_model, load_production_model
import numpy as np

app = FastAPI(title="Book Price Predictor API")

# Load model at startup
@app.on_event("startup")
async def startup_event():
    """Load the ML model when the app starts."""
    load_production_model()   # fail fast if model not available

class BookFeatures(BaseModel):
    """Input data for price prediction."""
    genre_encoded: int    # genre as integer (0=Fantasy, 1=Fiction, etc.)
    rating: float         # book rating 0.0-5.0
    in_stock: bool        # whether the book is in stock

    @validator('rating')
    def rating_must_be_valid(cls, v):
        if not 0.0 <= v <= 5.0:
            raise ValueError('rating must be between 0.0 and 5.0')
        return v

class PricePrediction(BaseModel):
    """Output: predicted price."""
    predicted_price: float
    model_version: str = "Production"

@app.post("/predict", response_model=PricePrediction)
async def predict_price(book: BookFeatures):
    """Predict the price of a book given its features."""
    model = get_model()    # get the loaded model

    # Prepare features in the same format as training
    features = np.array([[
        book.genre_encoded,
        book.rating,
        int(book.in_stock)
    ]])

    try:
        prediction = model.predict(features)[0]   # get single prediction
        return PricePrediction(
            predicted_price=round(float(prediction), 2)   # round to 2 decimals
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

@app.post("/reload-model")
async def reload_model():
    """
    Reload the model from MLflow registry.
    Call this endpoint after promoting a new model version to Production.
    """
    global _model
    from model_loader import load_production_model
    load_production_model()
    return {"message": "Model reloaded from Production registry"}
```

---

### Step 7 — MLflow with PostgreSQL backend

```bash
# MLflow can store run data in PostgreSQL instead of local files
# This is better for teams: everyone connects to the same tracking server

# Create the MLflow database in PostgreSQL
psql -U postgres -c "CREATE DATABASE mlflow_db;"

# Start MLflow server with PostgreSQL backend
mlflow server \
  --host 0.0.0.0 \
  --port 5000 \
  --backend-store-uri postgresql://postgres:yourpassword@localhost:5432/mlflow_db \
  --default-artifact-root ./mlflow_artifacts
  # --backend-store-uri: where run metadata is stored
  # --default-artifact-root: where model files and artifacts are stored

# In Docker Compose (from Module 6-1), this is already configured:
# command: mlflow server --host 0.0.0.0 --port 5000
#          --backend-store-uri postgresql://...
#          --default-artifact-root /mlflow/artifacts
```

```python
# In your training scripts, set the tracking URI to the server
mlflow.set_tracking_uri("http://localhost:5000")
# Now all runs go to the PostgreSQL-backed server, not local files
# Everyone on your team can see all experiments
```

---

## ⚠️ Common Mistakes

**Mistake 1: Not setting the experiment name**

```python
# WRONG: all runs go to the Default experiment — hard to find later
with mlflow.start_run():
    mlflow.log_metric("accuracy", 0.94)

# CORRECT: always set the experiment name first
mlflow.set_experiment("book-price-prediction")
with mlflow.start_run(run_name="rf-n100-depth10"):   # descriptive run name
    mlflow.log_metric("accuracy", 0.94)
```

**Mistake 2: Logging metrics outside of a run context**

```python
# WRONG: no active run — MLflow creates a random unnamed run
mlflow.log_metric("accuracy", 0.94)   # ❌ logged to an unnamed auto-created run

# CORRECT: always log inside a with mlflow.start_run() block
with mlflow.start_run():
    mlflow.log_metric("accuracy", 0.94)   # ✅ logged to the named run
```

**Mistake 3: Promoting to Production without testing in Staging**

```python
# WRONG: skip staging, go straight to production
client.transition_model_version_stage(
    name="MyModel", version=5, stage="Production"   # ❌ untested model goes live
)

# CORRECT: promote to Staging, test, THEN promote to Production
client.transition_model_version_stage(
    name="MyModel", version=5, stage="Staging"      # ✅ test here first
)
# ... run integration tests against the Staging model ...
# ... if tests pass ...
client.transition_model_version_stage(
    name="MyModel", version=5, stage="Production"   # ✅ only after testing
)
```

---

## ✅ Exercises

**Exercise 1 — Easy**
Enable `mlflow.sklearn.autolog()` and train a `LinearRegression` and a `Ridge` model on the books dataset. Compare both runs in the MLflow UI. Which one has a better R² score?

**Exercise 2 — Medium**
Write a function `find_best_run(experiment_name, metric, lower_is_better=True)` that queries the MLflow tracking server, finds the run with the best metric value, and returns the run ID and metric value.

**Exercise 3 — Hard**
Add a `/model-info` endpoint to the FastAPI app that returns: the currently loaded model version, the run ID it came from, the RMSE and R² it was trained with, and the date it was promoted to Production. Load all this information from the MLflow tracking server using `MlflowClient`.

---

## 🏗️ Mini Project — Track 3 Models, Register the Best

**Goal:** Train 3 models with different hyperparameters, compare in MLflow, register the best, load it in FastAPI.

```python
# mini_project.py

import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
# ... (use your books data from earlier phases)

mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("mini-project-comparison")

# Train model 1: Random Forest
with mlflow.start_run(run_name="random-forest"):
    mlflow.sklearn.autolog()
    model1 = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
    model1.fit(X_train, y_train)

# Train model 2: Gradient Boosting
with mlflow.start_run(run_name="gradient-boosting"):
    mlflow.sklearn.autolog()
    model2 = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
    model2.fit(X_train, y_train)

# Train model 3: Ridge Regression
with mlflow.start_run(run_name="ridge-regression"):
    mlflow.sklearn.autolog()
    model3 = Ridge(alpha=1.0)
    model3.fit(X_train, y_train)

# Find and register the best model
client = MlflowClient()
experiment = client.get_experiment_by_name("mini-project-comparison")
best_runs = client.search_runs(
    experiment_ids=[experiment.experiment_id],
    order_by=["metrics.mean_squared_error ASC"],
    max_results=1
)
best_run_id = best_runs[0].info.run_id

result = mlflow.register_model(
    f"runs:/{best_run_id}/model",
    "BestBookPriceModel"
)

client.transition_model_version_stage(
    name="BestBookPriceModel",
    version=result.version,
    stage="Production"
)

print(f"Best model (version {result.version}) promoted to Production")
print(f"Update FastAPI to load: models:/BestBookPriceModel/Production")
```

---

## 🔗 What's Next

In **Module 6-5: Production Monitoring & Error Handling** — the final module of the entire roadmap — you will learn how to keep your deployed application healthy: tracking errors with Sentry, detecting model drift with Evidently, and building automated retraining triggers. This is the capstone that ties every phase together.
