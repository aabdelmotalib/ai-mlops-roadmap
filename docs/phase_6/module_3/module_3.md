---
tags:
  - Advanced
  - Phase 6
---

# Module 3: CI/CD Pipelines

> **Phase 6 — MLOps & Deployment**

---

## 🎯 What You Will Learn

- What CI/CD is and why it is the foundation of professional software delivery
- The key concepts: pipeline, stage, job, artifact, trigger, runner
- How GitHub Actions works and how to write workflow YAML files
- How to build a complete CI pipeline: lint → test → build → push
- How to manage secrets safely in GitHub Actions
- How to speed up pipelines with dependency caching
- How to test across multiple Python versions using matrix builds
- How to write pytest tests for a FastAPI application

---

## 🧠 Concept Explained

Imagine you work in a car factory. Every time an engineer makes a change to the design, a team of quality control workers manually inspects the blueprints, builds a prototype, tests it, and ships it. This takes days and costs a lot of human effort.

Now imagine a robot that does all of this automatically in 5 minutes, every time a change arrives — without anyone pressing a button.

**That is CI/CD.**

- **CI (Continuous Integration):** Every time you push code, the system automatically checks it — runs tests, lints the code, builds the Docker image. If anything fails, it tells you immediately before the bad code reaches anyone else.
- **CD (Continuous Deployment):** If CI passes, the system automatically deploys the new version to your server.

!!! note "Why this matters"
Without CI/CD, bugs reach production because someone forgot to run the tests.
With CI/CD, broken code physically cannot reach production — the pipeline blocks it.

---

## 🔍 How It Works

```
Developer pushes code to GitHub
           │
           ▼
   GitHub Actions triggered
           │
     ┌─────▼──────┐
     │   Stage 1  │  Checkout code
     │    Setup   │  Set up Python
     └─────┬──────┘  Install dependencies
           │
     ┌─────▼──────┐
     │   Stage 2  │  flake8 (code style)
     │    Lint    │  black --check (formatting)
     └─────┬──────┘  bandit (security scan)
           │ pass ✅ (fail ❌ = pipeline stops here)
     ┌─────▼──────┐
     │   Stage 3  │  pytest (unit tests)
     │    Test    │  pytest --cov (coverage)
     └─────┬──────┘
           │ pass ✅
     ┌─────▼──────┐
     │   Stage 4  │  docker build
     │   Build    │  docker tag
     └─────┬──────┘
           │ pass ✅
     ┌─────▼──────┐
     │   Stage 5  │  docker push to Docker Hub
     │   Deploy   │  (only on main branch)
     └────────────┘
```

---

## 🛠️ Step-by-Step Guide

### Step 1 — Create the GitHub Actions directory

### Step 2 — Write the CI workflow

### Step 3 — Add secrets to GitHub

### Step 4 — Write pytest tests for the FastAPI app

### Step 5 — Add the CD workflow

### Step 6 — Add matrix builds

### Step 7 — Add dependency caching

---

## 💻 Code Examples

### Step 1 — Create the workflow directory

```bash
# GitHub Actions looks for workflow files in this exact location
mkdir -p .github/workflows

# We will create two workflow files:
# ci.yml   — runs on every push and pull request
# cd.yml   — runs on push to main only, deploys the app
```

---

### Step 2 — The complete CI workflow

```yaml
# .github/workflows/ci.yml
# Runs on every push to any branch and every pull request

name: CI Pipeline # name shown in GitHub Actions UI

# ── Triggers: when does this pipeline run? ────────────────────────────────────
on:
  push:
    branches: ["**"] # every branch push triggers CI
  pull_request:
    branches: [main] # PRs targeting main trigger CI

# ── Jobs: the units of work ───────────────────────────────────────────────────
jobs:
  # ── Job 1: lint ──────────────────────────────────────────────────────────
  lint:
    name: Lint & Format Check
    runs-on: ubuntu-latest # run on a free GitHub-hosted Ubuntu runner

    steps:
      # Step 1: check out your code onto the runner
      - name: Checkout code
        uses: actions/checkout@v4 # official GitHub action to clone your repo

      # Step 2: set up the Python version
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip" # cache pip downloads between runs (faster)

      # Step 3: install linting tools
      - name: Install lint dependencies
        run: |
          pip install flake8 black bandit
          # flake8: checks code style and common errors
          # black: checks code formatting
          # bandit: checks for security issues in Python code

      # Step 4: run flake8
      - name: Run flake8
        run: |
          flake8 app/ --max-line-length=100 --exclude=__pycache__
          # --max-line-length=100: allow lines up to 100 chars (default is 79)
          # --exclude: skip compiled files

      # Step 5: check black formatting (--check = don't change files, just report)
      - name: Check formatting with black
        run: |
          black --check --line-length=100 app/
          # If any file needs reformatting, this step fails

      # Step 6: security scan
      - name: Run bandit security scan
        run: |
          bandit -r app/ -ll
          # -r: recursive (check all files in app/)
          # -ll: only report medium and high severity issues

  # ── Job 2: test ──────────────────────────────────────────────────────────
  test:
    name: Run Tests
    runs-on: ubuntu-latest
    needs:
      lint # only run tests if lint passed
      # this saves time — no point testing badly formatted code

    # Spin up service containers alongside the test runner
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: testuser
          POSTGRES_PASSWORD: testpassword
          POSTGRES_DB: test_books_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
          # wait for PostgreSQL to be ready before running tests

      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      # Cache pip dependencies between runs
      - name: Cache dependencies
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip # where pip stores its cache
          key: ${{ runner.os }}-pip-${{ hashFiles('requirements*.txt') }}
          # key: rebuilds cache if requirements files change
          restore-keys: |
            ${{ runner.os }}-pip-
            # fallback key: use older cache if exact match not found

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
          # requirements-test.txt contains: pytest, pytest-cov, httpx, pytest-asyncio

      - name: Run tests with coverage
        env:
          # Pass test database credentials as environment variables
          DATABASE_URL: postgresql://testuser:testpassword@localhost:5432/test_books_db
          REDIS_URL: redis://localhost:6379/0
          SECRET_KEY: test-secret-key-not-real
        run: |
          pytest tests/ \
            --cov=app \
            --cov-report=xml \
            --cov-report=term-missing \
            --cov-fail-under=70 \
            -v
          # --cov=app: measure coverage for the 'app' directory
          # --cov-report=xml: save coverage to coverage.xml (for upload)
          # --cov-report=term-missing: print which lines are not covered
          # --cov-fail-under=70: fail if coverage drops below 70%
          # -v: verbose output

      # Upload coverage report as an artifact (viewable in GitHub UI)
      - name: Upload coverage report
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: coverage.xml
          retention-days: 7 # keep artifact for 7 days

  # ── Job 3: build ─────────────────────────────────────────────────────────
  build:
    name: Build Docker Image
    runs-on: ubuntu-latest
    needs: test # only build if tests passed

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      # Set up Docker Buildx for advanced build features
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      # Build the image (but don't push — just verify it builds)
      - name: Build Docker image
        uses: docker/build-push-action@v5
        with:
          context: . # build context is repo root
          file: ./Dockerfile # which Dockerfile to use
          push: false # don't push (CI only — push is in CD)
          tags: roadmap-api:${{ github.sha }} # tag with commit SHA
          cache-from: type=gha # use GitHub Actions cache for Docker layers
          cache-to: type=gha,mode=max # save layers to cache
```

---

### Step 3 — Add secrets to GitHub

```
In GitHub:
1. Go to your repository
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add these secrets:
   - DOCKER_USERNAME: your Docker Hub username
   - DOCKER_PASSWORD: your Docker Hub access token
     (Docker Hub → Account Settings → Security → New Access Token)
```

---

### Step 4 — pytest tests for FastAPI

```python
# requirements-test.txt
pytest==7.4.0
pytest-cov==4.1.0
pytest-asyncio==0.23.0
httpx==0.26.0          # required for FastAPI TestClient with async
```

```python
# tests/conftest.py — shared test fixtures

import pytest                               # test framework
from fastapi.testclient import TestClient   # test HTTP client for FastAPI
from sqlalchemy import create_engine        # database connection
from sqlalchemy.orm import sessionmaker
import os

# Import your FastAPI app
from app.main import app, get_db            # your app and DB dependency

# ── Test database setup ───────────────────────────────────────────────────────
TEST_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://testuser:testpassword@localhost:5432/test_books_db"
)

@pytest.fixture(scope="session")
def engine():
    """Create a database engine for the test session."""
    engine = create_engine(TEST_DATABASE_URL)
    yield engine
    engine.dispose()    # close all connections after all tests finish

@pytest.fixture(scope="function")
def db_session(engine):
    """
    Create a fresh database session for each test.
    Rolls back all changes after each test — so tests don't affect each other.
    """
    connection = engine.connect()
    transaction = connection.begin()    # start a transaction
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session    # provide the session to the test

    session.close()
    transaction.rollback()    # undo ALL changes made in this test
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    """
    Create a FastAPI test client that uses the test database session.
    Overrides the real 'get_db' dependency with the test session.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass    # session cleanup handled by db_session fixture

    app.dependency_overrides[get_db] = override_get_db   # swap real DB for test DB
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()    # restore real dependencies after test
```

```python
# tests/test_books.py — tests for the books API endpoints

import pytest
from fastapi.testclient import TestClient

class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_returns_200(self, client):
        """Health endpoint should always return 200 OK."""
        response = client.get("/health")        # make GET request to /health
        assert response.status_code == 200      # check HTTP status code

    def test_health_returns_healthy_status(self, client):
        """Health endpoint should return status=healthy."""
        response = client.get("/health")
        data = response.json()                  # parse JSON response
        assert data["status"] == "healthy"      # check response body


class TestBooksEndpoint:
    """Tests for the /books endpoint."""

    def test_get_books_returns_200(self, client):
        """GET /books should return 200 OK."""
        response = client.get("/books")
        assert response.status_code == 200

    def test_get_books_returns_list(self, client):
        """GET /books should return a JSON array."""
        response = client.get("/books")
        data = response.json()
        assert isinstance(data, list)           # check it's a list, not a dict

    def test_create_book_returns_201(self, client):
        """POST /books should create a book and return 201 Created."""
        new_book = {
            "title": "Test Book",
            "author": "Test Author",
            "genre": "Fiction",
            "price": 9.99,
            "rating": 4.5
        }
        response = client.post("/books", json=new_book)   # POST with JSON body
        assert response.status_code == 201               # 201 = Created

    def test_create_book_returns_book_data(self, client):
        """POST /books should return the created book's data."""
        new_book = {
            "title": "Another Test Book",
            "author": "Another Author",
            "genre": "Science Fiction",
            "price": 14.99,
            "rating": 4.2
        }
        response = client.post("/books", json=new_book)
        data = response.json()
        assert data["title"] == "Another Test Book"    # check title was saved
        assert data["author"] == "Another Author"       # check author was saved
        assert "id" in data                             # check ID was assigned

    def test_create_book_validates_price(self, client):
        """POST /books should reject negative prices."""
        invalid_book = {
            "title": "Bad Book",
            "author": "Bad Author",
            "price": -5.00        # negative price should be rejected
        }
        response = client.post("/books", json=invalid_book)
        assert response.status_code == 422   # 422 = Unprocessable Entity (validation error)

    def test_get_single_book(self, client):
        """GET /books/{id} should return the correct book."""
        # First create a book
        new_book = {"title": "Find Me", "author": "Author", "price": 9.99}
        create_response = client.post("/books", json=new_book)
        book_id = create_response.json()["id"]    # get the ID of created book

        # Then fetch it by ID
        get_response = client.get(f"/books/{book_id}")
        assert get_response.status_code == 200
        assert get_response.json()["title"] == "Find Me"

    def test_get_nonexistent_book_returns_404(self, client):
        """GET /books/{id} with invalid ID should return 404."""
        response = client.get("/books/999999")    # ID that doesn't exist
        assert response.status_code == 404        # 404 = Not Found
```

```bash
# Run tests locally before pushing
pytest tests/ -v --cov=app --cov-report=term-missing

# Run a specific test file
pytest tests/test_books.py -v

# Run a specific test
pytest tests/test_books.py::TestBooksEndpoint::test_create_book_returns_201 -v
```

---

### Step 5 — The CD workflow

```yaml
# .github/workflows/cd.yml
# Runs only when code is pushed to main branch
# Builds and pushes the Docker image to Docker Hub

name: CD Pipeline — Build & Push

on:
  push:
    branches: [main] # only deploy from main branch
  workflow_run:
    workflows: ["CI Pipeline"] # only run after CI passes
    types: [completed]
    branches: [main]

jobs:
  deploy:
    name: Build and Push Docker Image
    runs-on: ubuntu-latest
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    # Only run if the CI pipeline succeeded

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      # Extract metadata for tagging (branch name, commit SHA, etc.)
      - name: Extract Docker metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ secrets.DOCKER_USERNAME }}/roadmap-api
          tags: |
            type=ref,event=branch          # tag with branch name
            type=sha,prefix=sha-           # tag with commit SHA
            type=raw,value=latest,enable={{is_default_branch}}
            # 'latest' tag only applied on default branch (main)

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      # Login to Docker Hub using secrets (never hardcode credentials!)
      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }} # from GitHub secrets
          password: ${{ secrets.DOCKER_PASSWORD }} # from GitHub secrets

      # Build and push the image
      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./Dockerfile
          push: true # actually push this time
          tags: ${{ steps.meta.outputs.tags }} # all tags from metadata step
          labels: ${{ steps.meta.outputs.labels }} # OCI labels
          cache-from: type=gha # use layer cache to speed up builds
          cache-to: type=gha,mode=max # save layers to cache

      # Post the image digest as a summary
      - name: Image digest
        run: echo "Image pushed with digest ${{ steps.build.outputs.digest }}"
```

---

### Step 6 — Matrix builds (test on multiple Python versions)

```yaml
# Add this to the test job in ci.yml to test on Python 3.10, 3.11, 3.12

test:
  name: Run Tests (Python ${{ matrix.python-version }})
  runs-on: ubuntu-latest
  needs: lint

  strategy:
    matrix:
      python-version: ["3.10", "3.11", "3.12"] # test on all three
      # GitHub will create 3 parallel jobs, one per Python version
    fail-fast: false
    # fail-fast: false = don't cancel other matrix jobs if one fails
    # useful to see if the failure is specific to one Python version

  steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }} # uses the matrix value
        cache: "pip"

    # ... rest of test steps same as before ...
```

---

### Caching dependencies

```yaml
# Two ways to cache pip dependencies:

# Method 1: built into setup-python (simplest)
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: "3.11"
    cache: "pip" # automatically caches based on requirements files

# Method 2: explicit cache action (more control)
- name: Cache pip
  uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
    # key changes if any requirements file changes → cache is rebuilt
    restore-keys: |
      ${{ runner.os }}-pip-
      # if exact key not found, restore closest older cache

# Docker layer caching (speeds up docker build in CI)
- name: Build Docker image
  uses: docker/build-push-action@v5
  with:
    cache-from: type=gha # read layers from GitHub Actions cache
    cache-to: type=gha,mode=max # write all layers to cache
    # First run: no cache → slow build
    # Second run: most layers cached → 5x faster build
```

---

## ⚠️ Common Mistakes

**Mistake 1: Storing secrets in the workflow file**

```yaml
# WRONG: hardcoded credentials in the YAML — visible to anyone with repo access
- name: Login to Docker Hub
  run: docker login -u myusername -p mysecretpassword # ❌ never do this

# CORRECT: use GitHub secrets
- name: Login to Docker Hub
  uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKER_USERNAME }} # ✅ from GitHub secrets
    password: ${{ secrets.DOCKER_PASSWORD }} # ✅ from GitHub secrets
```

**Mistake 2: Not pinning action versions**

```yaml
# WRONG: using @main or @latest — action can change and break your pipeline
- uses: actions/checkout@main # ❌ could be different every run
- uses: actions/setup-python@latest # ❌ unpredictable

# CORRECT: pin to a specific version tag
- uses: actions/checkout@v4 # ✅ always the same
- uses: actions/setup-python@v5 # ✅ always the same
```

**Mistake 3: Running CD before CI passes**

```yaml
# WRONG: CD and CI run in parallel — image could be pushed with failing tests
on:
  push:
    branches: [main]   # CI and CD both trigger at same time

# CORRECT: CD depends on CI completing successfully
on:
  workflow_run:
    workflows: ["CI Pipeline"]
    types: [completed]
    branches: [main]
jobs:
  deploy:
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
```

---

## ✅ Exercises

**Exercise 1 — Easy**
Add a step to the CI pipeline that runs `pip check` to verify there are no conflicting package dependencies. This step should run between "install dependencies" and "run tests".

**Exercise 2 — Medium**
Add a `schedule` trigger to the CI workflow that runs the full test suite every day at 02:00 UTC, even if no code was pushed. This catches dependency updates that break your tests.

**Exercise 3 — Hard**
Write a workflow that runs on every pull request and automatically posts a comment showing the test coverage percentage. Use the `pytest-cov` XML output and a GitHub Actions bot comment action to post the result.

---

## 🏗️ Mini Project — Wire Tests into CI

**Goal:** Add tests to the FastAPI app and verify they run automatically on every push.

```bash
# Step 1: create the tests directory
mkdir -p tests
touch tests/__init__.py
touch tests/conftest.py
touch tests/test_books.py
touch tests/test_health.py
```

Use the test code from the examples above. Then:

```bash
# Step 2: run locally to make sure they pass
pytest tests/ -v

# Step 3: push to GitHub
git add .
git commit -m "add: pytest tests and CI pipeline"
git push origin main

# Step 4: watch the pipeline run
# Go to: GitHub repo → Actions tab
# You should see the CI Pipeline running
# All 3 jobs (lint, test, build) should show green checkmarks
```

**Verify the pipeline blocks bad code:**

```bash
# Make a deliberate style error
echo "x=1" >> app/main.py   # no spaces around =

# Push it
git add . && git commit -m "bad code" && git push

# Watch CI fail on the lint step → the build step never runs
# This is exactly what CI is supposed to do
```

---

## 🔗 What's Next

In **Module 6-4: Experiment Tracking with MLflow**, you will learn how to track every ML model training run — logging parameters, metrics, and artifacts — so you can always reproduce your best model and compare runs to find the winner.
