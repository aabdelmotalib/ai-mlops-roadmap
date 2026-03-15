---
tags:
  - Beginner
  - Phase 3
---

# Module 5: Integrating ML with Python Apps

You've built fantastic ML models. But they're just Python scripts on your computer. Real-world ML systems need to serve predictions 24/7 to thousands of users. This module teaches you to turn models into production APIs using FastAPI, then package it all in Docker.

---

## 🎯 What You Will Learn

By the end of this module, you will:

- Understand why models need to be served (not just scripts)
- Know the concept of model serving layers
- Use FastAPI to build APIs
- Load saved sklearn models into FastAPI apps
- Create /predict endpoints that validate input with pydantic
- Test endpoints with curl and interactive docs
- Handle errors gracefully
- Containerize with Docker (from Phase 0)
- Build batch prediction endpoints
- Deploy production-ready ML services

---

## 🧠 Concept Explained: From Script to Service

### The Problem with Scripts

**Your current workflow:**

```bash
python predict.py book_title="Python 101" pages=300
# Model runs, outputs prediction
# Done
```

**Problems:**

- Only you can run it
- No one else can access your predictions
- Can't scale (one prediction at a time)
- No monitoring or error handling
- No way to track who made what prediction

### The Solution: API Server

**With an API server:**

```bash
curl http://localhost:8000/predict?title="Python 101"&pages=300
# Returns JSON: {"predicted_price": 29.99}
```

**Benefits:**

- Anyone can access via HTTP
- Scales to millions of requests
- Monitoring and logging
- User authentication
- Load balancing

### The Architecture

```
Client (mobile app, website, another service)
        ↓ (HTTP request)
    FastAPI Server
        ↓
    Load Model from Disk
        ↓
    Validate Input (pydantic)
        ↓
    Make Prediction
        ↓
    Return JSON Response
        ↑ (HTTP response)
```

---

## 🛠️ Step-by-Step Guide

### Step 1: Install FastAPI and Uvicorn

```bash
pip install fastapi uvicorn[standard] pydantic
```

### Step 2: Create Your First API

```python
# main.py
from fastapi import FastAPI
from pydantic import BaseModel

# Create app
app = FastAPI()

# Define request schema (what user sends)
class Item(BaseModel):
    name: str
    price: float

# Define routes
@app.get("/")
def read_root():
    """Health check endpoint"""
    return {"status": "alive"}

@app.post("/predict")
def predict(item: Item):
    """Make prediction"""
    prediction = item.price * 1.1  # Simple rule
    return {"input": item, "prediction": prediction}
```

### Step 3: Run the Server

```bash
uvicorn main.py:app --reload
# Server runs on http://localhost:8000
```

### Step 4: Load Your Trained Model

```python
import joblib
from fastapi import FastAPI

# Load model once when app starts
model = joblib.load('model.pkl')
scaler = joblib.load('scaler.pkl')

app = FastAPI()

@app.post("/predict")
def predict(features: dict):
    # Validate input
    # Transform with scaler
    features_scaled = scaler.transform([features.values()])
    # Predict
    prediction = model.predict(features_scaled)[0]
    return {"prediction": float(prediction)}
```

### Step 5: Validate Input with Pydantic

```python
from pydantic import BaseModel, Field
from typing import Optional

class BookInput(BaseModel):
    pages: int = Field(..., gt=0, description="Number of pages (must be > 0)")
    rating: float = Field(..., ge=0, le=5)
    author_experience: int = Field(default=1, ge=0)

    class Config:
        example = {
            "pages": 300,
            "rating": 4.5,
            "author_experience": 10
        }

@app.post("/predict")
def predict(book: BookInput):
    # pydantic automatically validates
    # Invalid requests return 422 error
    pass
```

### Step 6: Handle Errors

```python
from fastapi import HTTPException

@app.post("/predict")
def predict(book: BookInput):
    try:
        features = prepare_features(book)
        prediction = model.predict(features)[0]
        return {"price": float(prediction)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Step 7: Create Batch Endpoint

```python
from typing import List

class BatchInput(BaseModel):
    books: List[BookInput]

@app.post("/batch-predict")
def batch_predict(batch: BatchInput):
    """Predict for multiple books at once"""
    predictions = []
    for book in batch.books:
        pred = predict(book)
        predictions.append(pred)
    return {"predictions": predictions}
```

### Step 8: Containerize with Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `requirements.txt`:

```
fastapi
uvicorn[standard]
pydantic
scikit-learn
joblib
```

Run:

```bash
docker build -t book-price-api .
docker run -p 8000:8000 book-price-api
```

---

## 💻 Code Examples

### Example 1: Complete Book Price Prediction API

```python
# main.py
import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
import numpy as np
from contextlib import asynccontextmanager

# Load model at startup
model = None
scaler = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model when server starts, clean up on shutdown"""
    global model, scaler

    print("Loading model...")
    model = joblib.load('book_price_model.pkl')
    scaler = joblib.load('scaler.pkl')
    print("✓ Model loaded")

    yield  # Server runs here

    print("Shutting down...")

# Create app with lifespan
app = FastAPI(
    title="Book Price Predictor",
    description="Predict book prices using ML",
    lifespan=lifespan
)

# Request/response schemas
class BookData(BaseModel):
    """Single book prediction request"""
    pages: int = Field(..., gt=0, le=1000, description="Pages (1-1000)")
    rating: float = Field(..., ge=0, le=5, description="Rating (0-5)")
    author_books: int = Field(default=1, ge=0, description="Author's previous books")

    class Config:
        example = {
            "pages": 300,
            "rating": 4.5,
            "author_books": 10
        }

class PredictionResponse(BaseModel):
    """Prediction response"""
    input: BookData
    predicted_price: float
    confidence: str  # "low", "medium", "high"

class BatchRequest(BaseModel):
    """Batch prediction request"""
    books: List[BookData]

class BatchResponse(BaseModel):
    """Batch response"""
    count: int
    predictions: List[PredictionResponse]

@app.get("/")
def read_root():
    """Health check and info"""
    return {
        "service": "Book Price Predictor API",
        "version": "1.0",
        "status": "operational"
    }

@app.get("/health")
def health():
    """Detailed health check"""
    try:
        # Test model is loaded
        if model is None:
            raise Exception("Model not loaded")

        # Quick test prediction
        test_input = np.array([[300, 4.0, 5]])
        test_scaled = scaler.transform(test_input)
        test_pred = model.predict(test_scaled)[0]

        return {
            "status": "healthy",
            "model": "loaded",
            "test_prediction": float(test_pred)
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.post("/predict", response_model=PredictionResponse)
def predict(book: BookData):
    """Predict price for a single book"""
    try:
        # Prepare features (must match training order)
        features = np.array([
            [book.pages, book.rating, book.author_books]
        ])

        # Scale
        features_scaled = scaler.transform(features)

        # Predict
        price = model.predict(features_scaled)[0]

        # Confidence (based on input reasonableness)
        if 100 <= book.pages <= 600 and 3.0 <= book.rating <= 4.5:
            confidence = "high"
        elif 50 <= book.pages <= 800 and 2.0 <= book.rating <= 5.0:
            confidence = "medium"
        else:
            confidence = "low"

        return PredictionResponse(
            input=book,
            predicted_price=float(price),
            confidence=confidence
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )

@app.post("/batch-predict", response_model=BatchResponse)
def batch_predict(batch: BatchRequest):
    """Predict prices for multiple books"""
    try:
        predictions = []

        for book in batch.books:
            pred = predict(book)
            predictions.append(pred)

        return BatchResponse(
            count=len(predictions),
            predictions=predictions
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/interactive-docs")
def docs():
    """Point to interactive documentation"""
    return {
        "docs_url": "http://localhost:8000/docs",
        "description": "Swagger UI interactive documentation"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Example 2: Docker Deployment

`Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app and model
COPY main.py .
COPY *.pkl ./

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

`requirements.txt`:

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.4.0
scikit-learn==1.3.2
joblib==1.3.2
```

Build and run:

```bash
# Build
docker build -t book-api:1.0 .

# Run
docker run -d -p 8000:8000 --name book-api book-api:1.0

# Test
curl http://localhost:8000/health

# Stop
docker stop book-api
```

### Example 3: Test Endpoint with curl

```bash
# Single prediction
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "pages": 350,
    "rating": 4.2,
    "author_books": 5
  }' | python -m json.tool

# Batch prediction
curl -X POST "http://localhost:8000/batch-predict" \
  -H "Content-Type: application/json" \
  -d '{
    "books": [
      {"pages": 300, "rating": 4.0},
      {"pages": 400, "rating": 4.5},
      {"pages": 200, "rating": 3.5}
    ]
  }' | python -m json.tool
```

---

## ⚠️ Common Mistakes

### Mistake 1: Loading Model for Every Request

**WRONG:**

```python
@app.post("/predict")
def predict(data: PredictInput):
    model = joblib.load('model.pkl')  # Load EVERY time!
    # Slow and wasteful
    prediction = model.predict(...)
    return prediction
```

**RIGHT:**

```python
# Load once at startup
model = joblib.load('model.pkl')

@app.post("/predict")
def predict(data: PredictInput):
    # Use already-loaded model
    prediction = model.predict(...)
    return prediction
```

### Mistake 2: Not Validating Input

**WRONG:**

```python
@app.post("/predict")
def predict(data: dict):
    # User could send garbage data
    features = [data['pages'], data['rating']]  # KeyError if missing!
    prediction = model.predict([features])
    return prediction
```

**RIGHT:**

```python
class BookData(BaseModel):
    pages: int = Field(..., gt=0, le=1000)
    rating: float = Field(..., ge=0, le=5)

@app.post("/predict")
def predict(book: BookData):
    # pydantic validates automatically
    features = [book.pages, book.rating]
    prediction = model.predict([features])
    return prediction
```

### Mistake 3: Model Mismatch with Scaler

**WRONG:**

```python
# Train with scaler
scaler.fit(X_train)
model.fit(scaler.transform(X_train), y_train)

# But in API, forget to scale
@app.post("/predict")
def predict(data: BookData):
    features = [data.pages, data.rating]
    # Using raw features, not scaled!
    prediction = model.predict([features])  # Wrong!
    return prediction
```

**RIGHT:**

```python
@app.post("/predict")
def predict(data: BookData):
    features = [[data.pages, data.rating]]
    features_scaled = scaler.transform(features)  # Scale first
    prediction = model.predict(features_scaled)  # Then predict
    return prediction
```

---

## ✅ Exercises

### Easy: Basic API

1. Create FastAPI app with /predict endpoint
2. Accept pages and rating as input
3. Return a prediction (even if hardcoded)
4. Test with curl

### Medium: Complete API with Model

1. Create API that loads a trained model
2. Validate input with pydantic
3. Handle errors gracefully
4. Test /health and /predict endpoints

### Hard: Batch Prediction with Docker

1. Build complete API with single + batch endpoints
2. Containerize with Docker
3. Run in container
4. Test from outside container
5. Check health endpoint

---

## 🏗️ Mini Project: Complete ML Service

Build production-ready book price prediction API with batch processing and containerization.

### Project Structure

```
book-api/
├── main.py                      # FastAPI app
├── train_model.py              # Model training script
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container definition
├── docker-compose.yml          # Multi-container setup
├── book_price_model.pkl        # Trained model
├── scaler.pkl                  # Feature scaler
├── README.md                   # Documentation
└── tests/                      # API tests
    └── test_api.py
```

### Requirements

1. FastAPI app with /predict and /batch-predict endpoints
2. Load saved model and scaler
3. Validate input with pydantic
4. Handle errors and edge cases
5. Interactive API docs at /docs
6. Containerize with Docker
7. Health check endpoint
8. Batch processing endpoint

### Implementation

```python
# main.py - Complete Production API
import os
import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
import numpy as np
from contextlib import asynccontextmanager

# Model files
MODEL_PATH = os.getenv('MODEL_PATH', 'book_price_model.pkl')
SCALER_PATH = os.getenv('SCALER_PATH', 'scaler.pkl')

model = None
scaler = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load resources on startup"""
    global model, scaler

    try:
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        print(f"✓ Loaded model from {MODEL_PATH}")
    except FileNotFoundError as e:
        print(f"✗ Error loading model: {e}")
        raise

    yield

    print("✓ Shutdown complete")

app = FastAPI(
    title="Book Price Prediction API",
    description="ML service for predicting book prices",
    version="1.0.0",
    lifespan=lifespan
)

# Schemas
class BookInput(BaseModel):
    pages: int = Field(..., gt=0, le=1000)
    rating: float = Field(..., ge=0, le=5)
    author_books: int = Field(default=1, ge=0)

class PredictionOutput(BaseModel):
    predicted_price: float
    currency: str = "USD"

class BatchRequest(BaseModel):
    books: List[BookInput]

class BatchOutput(BaseModel):
    count: int
    predictions: List[PredictionOutput]

# Endpoints
@app.get("/")
def root():
    return {"message": "Book Price Predictor API", "version": "1.0"}

@app.get("/health")
def health():
    """Health check"""
    if model is None or scaler is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "healthy"}

@app.post("/predict", response_model=PredictionOutput)
def predict(book: BookInput):
    """Predict price for single book"""
    try:
        features = np.array([[book.pages, book.rating, book.author_books]])
        features_scaled = scaler.transform(features)
        price = model.predict(features_scaled)[0]

        return PredictionOutput(predicted_price=float(price))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch-predict", response_model=BatchOutput)
def batch_predict(batch: BatchRequest):
    """Predict prices for multiple books"""
    predictions = []

    for book in batch.books:
        result = predict(book)
        predictions.append(result)

    return BatchOutput(count=len(predictions), predictions=predictions)

@app.get("/docs")
def documentation():
    return {"swagger_ui": "/docs", "openapi_schema": "/openapi.json"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py .
COPY *.pkl ./

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and test
docker build -t book-api .
docker run -p 8000:8000 book-api

# In another terminal:
curl http://localhost:8000/health
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"pages":300,"rating":4.5}'
```

---

## 🔗 What's Next

You've now completed Phase 3 — AI & ML Basics! You can:

- ✅ Understand ML concepts
- ✅ Engineer features
- ✅ Use pre-trained models
- ✅ Build models with scikit-learn
- ✅ Deploy as production APIs

---

## 📚 Summary

In this module, you learned:

1. ✅ **Model serving** – Why APIs matter
2. ✅ **FastAPI basics** – Building fast APIs
3. ✅ **Loading models** – Using saved models in apps
4. ✅ **Pydantic validation** – Input validation
5. ✅ **Error handling** – Robust APIs
6. ✅ **Batch processing** – Multiple predictions
7. ✅ **Docker** – Containerization for deployment
8. ✅ **Interactive docs** – Auto-generated API documentation
9. ✅ **Production patterns** – Real-world ML services

---

**Congratulations! You're now a full-stack ML engineer. 🎉**

You can build models AND deploy them to production. That's rare and valuable.
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
