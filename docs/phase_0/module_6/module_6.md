# Module 6: Async Python — Handle Multiple Tasks at Once

**Estimated time:** 3-4 hours  
**Prerequisites:** Modules 0-5 (Python basics, Git, Docker, Linux CLI, PostgreSQL basics)  
**Why this matters:** When your Lead Generation Agent talks to APIs, databases, or waits for user input, synchronous code sits idle. Async lets you start 50 lead enrichment calls at the same time instead of one after another. This is the difference between processing 50 leads in 2 seconds vs 100 seconds.

---

## 🎯 What You Will Learn

- **The mindset shift**: Why synchronous code wastes time and how async fixes it
- **Event loop basics**: Python's internal scheduler that keeps everything running smoothly
- **async/await syntax**: The two keywords that unlock concurrent programming
- **asyncio.gather()**: Run multiple tasks in parallel and collect their results
- **aiohttp**: Make HTTP requests without blocking your program
- **asyncpg**: Query PostgreSQL without freezing your entire application
- **FastAPI async routes**: Handle multiple API requests simultaneously
- **Timeouts and cancellation**: Kill tasks that are taking too long
- **Error handling in async code**: One task fails without breaking the others
- **Real-world pattern**: Process 50 leads in parallel just like the Lead Gen Agent does

---

## 🧠 Concept Explained

### The Restaurant Waiter Analogy

Imagine you're managing a restaurant. You have one waiter.

**Synchronous (one task at a time):**

1. Waiter takes a table's order
2. Waiter walks to the kitchen, stands there, and watches the food cook (wasting time)
3. Waiter carries the plate back and delivers it
4. Waiter finally walks to the next table
5. All other customers are frustrated because the waiter is doing nothing while the food cooks

**Asynchronous (smart waiter):**

1. Waiter takes all the orders at every table
2. Waiter drops all the orders with the kitchen at once
3. While the kitchen cooks, the waiter chats with other tables, refills drinks, clears plates
4. When a plate is ready, the waiter picks it up and delivers it immediately
5. Same waiter. Same amount of work. Much faster service. Customers are happy.

### Why This Matters for Your Code

Let's say your Lead Gen Agent needs to:

- Fetch company data from an API (takes 1 second per request)
- Enrich the data with LinkedIn info (takes 1 second per request)
- Save to the database (takes 0.1 seconds per request)

**Synchronous code:**

```
Lead 1: API (1s) → LinkedIn (1s) → Database (0.1s) = 2.1 seconds
Lead 2: API (1s) → LinkedIn (1s) → Database (0.1s) = 2.1 seconds
...
Lead 50: API (1s) → LinkedIn (1s) → Database (0.1s) = 2.1 seconds
Total: 105 seconds for all 50 leads
```

**Asynchronous code:**

```
All 50 leads fire API calls at the same time: ~1 second max (not 50!)
All 50 leads get responses back and fire LinkedIn calls: ~1 second max
All 50 leads save to database in parallel: ~0.1 second max
Total: ~2.2 seconds for all 50 leads (47x faster!)
```

### What We're Actually Doing

You're not adding extra CPUs or threads. You're simply **not wasting time waiting**. When your code says "Hey, wait for this API response," instead of sitting idle, the async system switches to other tasks. When the API responds, it comes back and finishes. Like the waiter checking other tables while the kitchen works.

This is called **concurrency** (doing many things, switching between them) — different from **parallelism** (doing multiple things at the exact same time).

---

## 🔍 How It Works

### The Event Loop: Python's Internal Scheduler

```
┌─────────────────────────────────────────────────────────────────┐
│                       EVENT LOOP (Always Running)               │
│                                                                 │
│  1. Check Task A:  Is it ready to continue? Yes → Resume it    │
│  2. Task A pauses at await → Save state, move on               │
│  3. Check Task B:  Is it ready to continue? No → Skip it       │
│  4. Check Task C:  Is it ready to continue? Yes → Resume it    │
│  5. Task C pauses at await → Save state, move on               │
│  6. Check Task A:  API response arrived! → Resume it           │
│  7. Task A completes → Remove from queue                       │
│  8. Loop back to step 1 until all tasks done                   │
│                                                                 │
│  This all happens in microseconds. No sleeping. Always busy.   │
└─────────────────────────────────────────────────────────────────┘
```

### The Three Core Pieces

**1. async def** — Marks a function that can pause and resume

```python
async def fetch_data():  # This function CAN pause (with await)
    pass

def sync_function():     # This function CANNOT pause
    pass
```

**2. await** — The pause point; "I'm waiting for something, start other tasks"

```python
result = await some_async_function()  # Pause here until result arrives
```

**3. asyncio.run()** — Starts the whole machine; creates the event loop and runs your async code

```python
asyncio.run(main())  # Creates event loop, runs main(), then cleans up
```

### Key Rule You Must Remember

**You can only use `await` inside an `async def` function. Period.**

If you write `await` in a regular function, Python will scream:

```
SyntaxError: 'await' outside async function
```

We'll see this error in the Common Mistakes section.

### asyncio.gather() — The Concurrency Workhorse

This is the most important function in this entire module.

```python
# Sequential (old way) — one after another
result1 = await fetch(url1)  # Wait for it to finish
result2 = await fetch(url2)  # THEN wait for this
result3 = await fetch(url3)  # THEN wait for this
# Total time: ~3 seconds (if each takes 1 second)

# Concurrent (new way) — all at the same time
results = await asyncio.gather(
    fetch(url1),  # Start but don't wait
    fetch(url2),  # Start but don't wait
    fetch(url3),  # Start but don't wait
)
# Total time: ~1 second (all start at once!)
```

---

## 🛠️ Step-by-Step Guide

### Step 1: Install asyncio (Already Built In!)

Good news: `asyncio` is part of Python's standard library. No install needed.

```bash
# You already have it:
python -c "import asyncio; print('asyncio is ready')"
```

### Step 2: Install aiohttp (HTTP Requests Without Blocking)

This is the async version of the `requests` library you used earlier.

```bash
# Activate your virtual environment first
source /path/to/venv/bin/activate

# Then install
pip install aiohttp
```

### Step 3: Install asyncpg (Async PostgreSQL)

For talking to your PostgreSQL database without blocking:

```bash
pip install asyncpg
```

### Step 4: Understand the Execution Flow

When you write:

```python
async def main():
    result = await fetch_something()
    print(result)

asyncio.run(main())
```

Here's what Python does:

1. `asyncio.run(main())` creates an event loop
2. Calls `main()` (which is async, so it returns a coroutine, not a result)
3. Event loop starts running the coroutine
4. When it hits `await fetch_something()`, it pauses `main()`
5. Event loop checks if other tasks are ready — if yes, runs them
6. When `fetch_something()` returns a result, event loop resumes `main()`
7. `main()` continues and prints the result
8. `main()` finishes, event loop closes

### Step 5: Always Use Context Managers with aiohttp

When you open an HTTP session, always close it properly:

```python
# BAD — session might not close properly
session = aiohttp.ClientSession()
data = await session.get(url)
# Oops, forgot to close!

# GOOD — automatically closes when done
async with aiohttp.ClientSession() as session:
    data = await session.get(url)
    # Automatically closed here
```

### Step 6: Always Use Connection Pools with asyncpg

When accessing PostgreSQL, reuse connections:

```python
# BAD — opening a new connection every time (slow)
conn = await asyncpg.connect(...)
await conn.fetch(...)
await conn.close()  # Then immediately open a new one? Wasteful!

# GOOD — connection pool reuses connections
pool = await asyncpg.create_pool(...)
async with pool.acquire() as conn:
    await conn.fetch(...)
# Connection returned to pool, ready for next query
```

---

## 💻 Code Examples

### Example 1: Your First Async Program

```python
import asyncio  # Python's async orchestrator — built in, handles scheduling

async def greet(name, delay):  # async def means this function can pause with await
    await asyncio.sleep(delay)  # Pause here for `delay` seconds; other tasks run now
    print(f"Hello, {name}!")  # After delay, print the greeting
    return f"Greeted {name}"  # Return a result for the caller

async def main():  # Main entry point must be async so it can use await
    result1 = await greet("Alice", 1)  # Pause 1 second, then resume
    result2 = await greet("Bob", 2)  # Pause 2 more seconds
    print(f"Results: {result1}, {result2}")  # Print what we got back

asyncio.run(main())  # Start the event loop, run main(), then shut down
```

**Expected output:**

```
Hello, Alice!
Hello, Bob!
Results: Greeted Alice, Greeted Bob
```

**Timeline (takes 3 seconds total):**

- 0s: `greet("Alice", 1)` starts, pauses at `await`
- 0s: `greet("Bob", 2)` starts, pauses at `await`
- 1s: `greet("Alice", 1)` resumes, prints "Hello, Alice!"
- 3s: `greet("Bob", 2)` resumes, prints "Hello, Bob!"

---

### Example 2: Using asyncio.gather() — The Game Changer

This is the most important pattern you'll use.

```python
import asyncio  # Async orchestrator

async def fetch_data(source_id, delay):  # Simulate fetching from an API
    print(f"[{source_id}] Starting to fetch...")  # Log when we start
    await asyncio.sleep(delay)  # Pause; let other tasks run
    print(f"[{source_id}] Done! Got data.")  # Log when we finish
    return f"Data from source {source_id}"  # Return the result

async def main():  # Entry point
    print("Starting 3 concurrent fetches...")  # Tell the user we're starting

    # asyncio.gather() runs all tasks at the same time and waits for all to complete
    results = await asyncio.gather(
        fetch_data(1, 2),  # Start Task 1 (2 second delay)
        fetch_data(2, 1),  # Start Task 2 (1 second delay) — happens at the same time!
        fetch_data(3, 3),  # Start Task 3 (3 second delay) — also starts now!
    )

    print(f"All done! Got {len(results)} results")  # After all tasks finish
    for result in results:  # Go through each result
        print(f"  → {result}")  # Print it

asyncio.run(main())  # Go!
```

**Expected output:**

```
Starting 3 concurrent fetches...
[1] Starting to fetch...
[2] Starting to fetch...
[3] Starting to fetch...
[2] Done! Got data.
[1] Done! Got data.
[3] Done! Got data.
All done! Got 3 results
  → Data from source 1
  → Data from source 2
  → Data from source 3
```

**Timeline (takes 3 seconds, not 6!):**

- 0s: All three tasks start at the exact same time (not one after another)
- 1s: Task 2 finishes (fastest)
- 2s: Task 1 finishes
- 3s: Task 3 finishes (slowest)
- Main function continues after all three finish

Compare this to running them sequentially: it would take 2+1+3 = 6 seconds!

---

### Example 3: Error Handling with gather()

What if one task fails? By default, gather() fails the entire group. But we can fix that:

```python
import asyncio  # Async orchestrator

async def risky_fetch(task_id):  # Might succeed, might fail
    await asyncio.sleep(1)  # Simulate API call
    if task_id == 2:  # Task 2 intentionally fails
        raise ValueError(f"Task {task_id} failed!")  # Simulate API error
    return f"Success from task {task_id}"  # Return data

async def main():  # Entry point
    print("Running 3 tasks, one will fail...")  # Warn the user

    # return_exceptions=True means: if a task fails, put the exception in results instead of crashing
    results = await asyncio.gather(
        risky_fetch(1),
        risky_fetch(2),  # This one will raise an error
        risky_fetch(3),
        return_exceptions=True,  # Don't stop everything if one fails
    )

    for i, result in enumerate(results, 1):  # Go through each result
        if isinstance(result, Exception):  # Check if it's an error
            print(f"Task {i}: Failed - {result}")  # Print the error message
        else:  # It's successful data
            print(f"Task {i}: {result}")  # Print the success message

asyncio.run(main())  # Go!
```

**Expected output:**

```
Running 3 tasks, one will fail...
Task 1: Success from task 1
Task 2: Failed - Task 2 failed!
Task 3: Success from task 3
```

**Key insight:** Without `return_exceptions=True`, the entire gather() would crash and Task 3 would never run. With it, all three tasks run and we handle each failure individually. This is critical for the Lead Gen Agent — if one API call fails, we don't want to abandon all 50 leads.

---

### Example 4: Fetching Multiple URLs with aiohttp

This is the first realistic example — actually making HTTP requests.

```python
import asyncio  # Async orchestrator
import aiohttp  # Async HTTP library (like requests, but for async)

async def fetch_url(session, url):  # session is shared connection object
    try:  # Wrap in try/except to catch network errors
        async with session.get(url, timeout=5) as response:  # Make GET request, 5 second timeout
            status = response.status  # Get HTTP status (200, 404, etc.)
            data = await response.text()  # Get the response body (pause until data arrives)
            return {"url": url, "status": status, "length": len(data)}  # Return summary
    except asyncio.TimeoutError:  # If request takes > 5 seconds
        return {"url": url, "status": "timeout", "length": 0}  # Return timeout marker
    except Exception as e:  # Any other network error
        return {"url": url, "status": f"error: {e}", "length": 0}  # Return error marker

async def main():  # Entry point
    urls = [  # List of URLs to fetch
        "https://httpbin.org/delay/1",  # Waits 1 second before responding
        "https://httpbin.org/delay/2",  # Waits 2 seconds
        "https://httpbin.org/delay/3",  # Waits 3 seconds
        "https://httpbin.org/delay/1",  # Another 1 second
        "https://httpbin.org/delay/2",  # Another 2 seconds
    ]

    print(f"Fetching {len(urls)} URLs concurrently...")  # Tell user what we're doing

    async with aiohttp.ClientSession() as session:  # Create session, auto-close when done
        results = await asyncio.gather(  # Run all fetches at the same time
            *[fetch_url(session, url) for url in urls],  # Unpack list of coroutines
            return_exceptions=True,  # Handle failures gracefully
        )

    print(f"\nResults:")  # Print header
    for result in results:  # Go through each result
        if isinstance(result, Exception):  # Check if it failed
            print(f"  Error: {result}")  # Print exception
        else:  # It succeeded
            print(f"  {result['url']}: Status={result['status']}, Size={result['length']} bytes")  # Print success

asyncio.run(main())  # Go!
```

**Expected output:**

```
Fetching 5 URLs concurrently...

Results:
  https://httpbin.org/delay/1: Status=200, Size=307 bytes
  https://httpbin.org/delay/2: Status=200, Size=307 bytes
  https://httpbin.org/delay/3: Status=200, Size=307 bytes
  https://httpbin.org/delay/1: Status=200, Size=307 bytes
  https://httpbin.org/delay/2: Status=200, Size=307 bytes
```

**Timeline (takes ~3 seconds, not 9!):**

- 0s: All 5 requests start at the same time
- 3s: All requests finish (the slowest one took 3 seconds)

If we fetched them one at a time, it would be 1+2+3+1+2 = 9 seconds!

---

### Example 5: Setting Timeouts with asyncio.wait_for()

Critical for systems where users are waiting (like your voice agent):

```python
import asyncio  # Async orchestrator
import aiohttp  # Async HTTP library

async def slow_api_call(url, delay):  # Simulate a slow API
    print(f"Calling {url} (will take {delay}s)...")  # Log the call
    async with aiohttp.ClientSession() as session:  # Create session
        async with session.get(url) as response:  # Make request
            await asyncio.sleep(delay)  # Simulate slow response
            return await response.text()  # Return response body

async def main():  # Entry point
    print("Fetching with 2-second timeout...")  # Tell user the timeout

    try:  # Wrap in try/except to catch timeout
        # asyncio.wait_for() adds a timeout to ANY awaitable
        result = await asyncio.wait_for(
            slow_api_call("https://httpbin.org/delay/10", 10),  # Will take 10 seconds
            timeout=2  # But we only wait 2 seconds
        )
        print(f"Got result: {result}")  # Print if it succeeds (it won't)
    except asyncio.TimeoutError:  # If it takes longer than timeout
        print("Error: API call took too long! (timed out after 2 seconds)")  # Tell user

asyncio.run(main())  # Go!
```

**Expected output:**

```
Fetching with 2-second timeout...
Calling https://httpbin.org/delay/10 (will take 10s)...
Error: API call took too long! (timed out after 2 seconds)
```

**Why this matters:** In your voice agent, if you ask "Tell me about Acme Corp" and the lead enrichment API takes 10 seconds, the user hears 10 seconds of silence. Bad experience. With `wait_for()`, you set a 2-second timeout, catch the error, and say "I'm looking that up, let me get back to you." Much better.

---

### Example 6: Async with FastAPI

Remember FastAPI from earlier? Here's how async makes it handle more requests:

```python
# save as app.py
from fastapi import FastAPI  # FastAPI framework
import asyncio  # Async orchestrator
import aiohttp  # Async HTTP library

app = FastAPI()  # Create app

# SYNCHRONOUS endpoint (blocks everything while waiting)
@app.get("/sync-data")  # Route for GET /sync-data
def get_sync_data():  # Regular function (NOT async)
    import requests  # Regular requests library (blocking)

    response = requests.get("https://httpbin.org/delay/2")  # Wait 2 seconds (event loop is BLOCKED)
    return {"message": "Got sync data", "status": response.status_code}  # Return response

# ASYNCHRONOUS endpoint (doesn't block, lets other requests run)
@app.get("/async-data")  # Route for GET /async-data
async def get_async_data():  # Async function
    async with aiohttp.ClientSession() as session:  # Async HTTP session
        async with session.get("https://httpbin.org/delay/2") as response:  # Wait 2 seconds (other requests CAN run)
            status = response.status  # Get status code
            return {"message": "Got async data", "status": status}  # Return response

# Run with: uvicorn app:app --reload
```

**What happens if 3 people request at the same time?**

**/sync-data (blocking):**

- Person 1 requests, waits 2 seconds, gets response
- Person 2 requests, WAITS while Person 1's request finishes (1 second wasted)
- Person 3 requests, WAITS while Person 1 & 2 finish (3 seconds wasted)
- Total time: ~6 seconds to serve 3 people

**/async-data (non-blocking):**

- Person 1 requests, pauses at await
- Person 2 requests, pauses at await (no waiting!)
- Person 3 requests, pauses at await (no waiting!)
- After ~2 seconds, all three get responses
- Total time: ~2 seconds to serve 3 people (same as 1 person!)

This is why async is critical for web servers. Every second of waiting is a second you could serve someone else.

---

### Example 7: Querying PostgreSQL Asynchronously with asyncpg

No more blocking database calls:

```python
import asyncio  # Async orchestrator
import asyncpg  # Async PostgreSQL library

async def fetch_companies():  # Async function for database queries
    # Create connection pool (reuses connections instead of opening new ones)
    pool = await asyncpg.create_pool(
        "postgresql://user:password@localhost/companies_db",  # Connection string
        min_size=5,  # At least 5 connections ready
        max_size=20,  # At most 20 connections
    )

    try:  # Wrap in try/finally to ensure cleanup
        # Fetch all companies
        async with pool.acquire() as conn:  # Get a connection from the pool
            rows = await conn.fetch("SELECT id, name, domain FROM companies LIMIT 10")  # Query (non-blocking)
            print(f"Fetched {len(rows)} companies")  # Print how many
            for row in rows:  # Go through each row
                print(f"  {row['id']}: {row['name']} ({row['domain']})")  # Print company info

        # Insert a new company
        async with pool.acquire() as conn:  # Get another connection
            result = await conn.execute(  # Execute INSERT query
                "INSERT INTO companies (name, domain) VALUES ($1, $2)",  # Parameterized query (safe!)
                "Acme Corp",  # First parameter
                "acme.com",  # Second parameter
            )
            print(f"Inserted new company: {result}")  # Print confirmation

        # Query a second time
        async with pool.acquire() as conn:  # Reused connection from pool
            count = await conn.fetchval("SELECT COUNT(*) FROM companies")  # Get single value
            print(f"Total companies in database: {count}")  # Print total

    finally:  # Always cleanup
        await pool.close()  # Close the connection pool

asyncio.run(fetch_companies())  # Go!
```

**Key points:**

- `asyncpg.create_pool()`: Creates a pool of reusable connections (much faster than `open → query → close` every time)
- `pool.acquire()`: Gets a connection from the pool (waits if none available)
- `async with`: Automatically returns connection to pool when done
- `await conn.fetch()`: Non-blocking query (other tasks can run while waiting for database)
- Use `$1, $2` for parameters (prevents SQL injection)

---

### Example 8: Benchmark — requests vs aiohttp

This shows the real performance difference. **Run this yourself!**

```python
import asyncio  # Async orchestrator
import time  # For timing
import aiohttp  # Async HTTP library
import requests  # Regular HTTP library

# URLs to fetch (same 10 URLs, repetition to make time measurement clear)
URLS = [
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/1",
]

# SYNCHRONOUS version (old way)
def sync_fetch():  # Regular function (not async)
    start_time = time.time()  # Record start time

    for url in URLS:  # Loop through each URL
        response = requests.get(url)  # Fetch it (BLOCKS until response arrives)
        status = response.status_code  # Get status code

    elapsed = time.time() - start_time  # Calculate how long it took
    return elapsed  # Return elapsed time

# ASYNCHRONOUS version (new way)
async def async_fetch():  # Async function
    start_time = time.time()  # Record start time

    async with aiohttp.ClientSession() as session:  # Create session
        # Create a list of fetch tasks (all start at the same time with gather)
        async def fetch_one(url):  # Helper to fetch a single URL
            async with session.get(url) as response:  # Make request
                status = response.status  # Get status code
                return status  # Return it

        await asyncio.gather(  # Run all requests at the same time
            *[fetch_one(url) for url in URLS]  # Unpack list of tasks
        )

    elapsed = time.time() - start_time  # Calculate how long it took
    return elapsed  # Return elapsed time

# Run the benchmark
print("=" * 60)
print("BENCHMARK: Fetching 10 URLs (each takes ~1 second)")
print("=" * 60)

print("\n1. SYNCHRONOUS (old way with requests library):")
sync_time = sync_fetch()  # Run sync version
print(f"   Time taken: {sync_time:.2f} seconds")  # Print result
print(f"   → Fetches one URL at a time (1+1+1+... = ~10 seconds)")  # Explain

print("\n2. ASYNCHRONOUS (new way with aiohttp):")
async_time = asyncio.run(async_fetch())  # Run async version
print(f"   Time taken: {async_time:.2f} seconds")  # Print result
print(f"   → Fetches all URLs at the same time (~1 second)")  # Explain

print("\n" + "=" * 60)
speedup = sync_time / async_time  # Calculate how much faster
print(f"SPEEDUP: {speedup:.1f}x faster with async!")  # Show improvement
print(f"Time saved: {sync_time - async_time:.2f} seconds")  # Show absolute time saved
print("=" * 60)
```

**Expected output (approximately):**

```
============================================================
BENCHMARK: Fetching 10 URLs (each takes ~1 second)
============================================================

1. SYNCHRONOUS (old way with requests library):
   Time taken: 10.23 seconds
   → Fetches one URL at a time (1+1+1+... = ~10 seconds)

2. ASYNCHRONOUS (new way with aiohttp):
   Time taken: 1.34 seconds
   → Fetches all URLs at the same time (~1 second)

============================================================
SPEEDUP: 7.6x faster with async!
Time saved: 8.89 seconds
============================================================
```

This is the moment it clicks. The async version is ~7-10x faster for I/O bound tasks. No magic. Just smart scheduling.

---

### Example 9: Full Lead Enrichment Pattern (Preview of Phase 8)

This is what you'll build in the Lead Gen Agent. Here's the pattern:

```python
import asyncio  # Async orchestrator
import aiohttp  # Async HTTP library
import asyncpg  # Async PostgreSQL
import time  # For measuring time

# Simulated company domains to enrich
COMPANIES = [
    {"id": 1, "name": "TechCorp", "domain": "techcorp.com"},
    {"id": 2, "name": "DataInc", "domain": "datainc.io"},
    {"id": 3, "name": "CloudSys", "domain": "cloudsys.net"},
    {"id": 4, "name": "AIStartup", "domain": "aistartup.ai"},
    {"id": 5, "name": "WebDev", "domain": "webdev.com"},
]

async def enrich_company(session, company):  # Fetch external data for one company
    """Enrich a single company with external data (simulated)."""
    url = f"https://httpbin.org/delay/1"  # Simulate API call (takes 1 second)

    try:  # Wrap in try/except for error handling
        async with session.get(url) as response:  # Make request
            if response.status == 200:  # If successful
                # In real life, you'd parse the response and extract useful data
                return {
                    "company_id": company["id"],
                    "name": company["name"],
                    "domain": company["domain"],
                    "enriched": True,  # Mark as successfully enriched
                    "data": f"Tech stack info for {company['name']}",  # Simulated enriched data
                }
            else:  # If API error
                return {
                    "company_id": company["id"],
                    "name": company["name"],
                    "domain": company["domain"],
                    "enriched": False,  # Mark as failed
                    "error": f"API returned {response.status}",  # Error message
                }
    except Exception as e:  # Network error or timeout
        return {
            "company_id": company["id"],
            "name": company["name"],
            "domain": company["domain"],
            "enriched": False,  # Mark as failed
            "error": str(e),  # Error message
        }

async def save_to_database(results):  # Save enriched data to PostgreSQL
    """In real production, this connects to your actual database."""
    # For demo, we just pretend to save
    print(f"\n📦 Saving {len(results)} results to database...")  # Log action

    # In real code:
    # pool = await asyncpg.create_pool("postgresql://...")
    # async with pool.acquire() as conn:
    #     for result in results:
    #         await conn.execute(
    #             "INSERT INTO enriched_leads (company_id, name, domain, data) VALUES ($1, $2, $3, $4)",
    #             result["company_id"], result["name"], result["domain"], result["data"]
    #         )

    for result in results:  # Simulate saving each result
        status = "✅" if result["enriched"] else "❌"  # Success or failure marker
        print(f"  {status} {result['name']}: {result.get('error', 'Saved')}")  # Print status

async def process_leads_concurrent(companies):  # Main orchestration function
    """Process multiple leads concurrently (the fast way)."""
    print(f"🚀 Processing {len(companies)} companies concurrently...")  # Log start
    print(f"   (Each enrichment takes ~1 second)")  # Explain timing
    print(f"   Without async: {len(companies)} seconds")  # Sequential time
    print(f"   With async: ~1 second\n")  # Concurrent time

    start_time = time.time()  # Record start time

    async with aiohttp.ClientSession() as session:  # Create HTTP session
        # Enrich all companies at the same time
        results = await asyncio.gather(
            *[enrich_company(session, company) for company in companies],  # Run all concurrently
            return_exceptions=True,  # Don't fail if one company's enrichment fails
        )

    elapsed = time.time() - start_time  # Calculate elapsed time

    # Print results
    successful = sum(1 for r in results if isinstance(r, dict) and r["enriched"])  # Count successes
    failed = len(results) - successful  # Count failures

    print(f"\n📊 Results:")  # Print header
    print(f"   ✅ Successful: {successful}/{len(results)}")  # Print success count
    print(f"   ❌ Failed: {failed}/{len(results)}")  # Print failure count
    print(f"   ⏱️  Total time: {elapsed:.2f} seconds")  # Print elapsed time

    # Save to database
    await save_to_database(results)

# Run it
asyncio.run(process_leads_concurrent(COMPANIES))  # Execute the entire pipeline
```

**Expected output:**

```
🚀 Processing 5 companies concurrently...
   (Each enrichment takes ~1 second)
   Without async: 5 seconds
   With async: ~1 second

📊 Results:
   ✅ Successful: 5/5
   ❌ Failed: 0/5
   ⏱️  Total time: 1.23 seconds

📦 Saving 5 results to database...
  ✅ TechCorp: Saved
  ✅ DataInc: Saved
  ✅ CloudSys: Saved
  ✅ AIStartup: Saved
  ✅ WebDev: Saved
```

This is the exact pattern you'll use in Phase 8, Module 2 to enrich 50 leads in parallel.

---

## ⚠️ Common Mistakes

### Mistake 1: Forgetting `async` or `await`

```python
# ❌ WRONG — forgot async
def fetch_data():  # Missing async!
    result = await some_api_call()  # This will crash
    return result

# ✅ RIGHT — added async
async def fetch_data():  # Now it's async
    result = await some_api_call()  # This works
    return result
```

**Error you'll see:**

```
SyntaxError: 'await' outside async function
```

**Fix:** Add `async` before the function definition.

---

### Mistake 2: Using requests in async code (blocks everything!)

```python
import asyncio
import requests  # ❌ WRONG — this is BLOCKING

async def fetch_data():  # This is async
    response = requests.get(url)  # ❌ BLOCKS THE ENTIRE EVENT LOOP
    # All other tasks pause while waiting for response
    return response.text()

# Meanwhile, 49 other leads are stuck waiting for this one request!
```

**Fix:** Use `aiohttp` instead:

```python
import asyncio
import aiohttp  # ✅ RIGHT — this is NON-BLOCKING

async def fetch_data():  # This is async
    async with aiohttp.ClientSession() as session:  # Non-blocking session
        async with session.get(url) as response:  # Non-blocking request
            return await response.text()  # Other tasks can run while waiting
```

---

### Mistake 3: Forgetting to await a coroutine

```python
async def main():
    result = fetch_data()  # ❌ WRONG — forgot await!
    print(result)  # Prints: <coroutine object fetch_data at ...>
    # The function never actually ran!

# ✅ RIGHT — added await
async def main():
    result = await fetch_data()  # Now it runs and waits for result
    print(result)  # Prints actual data
```

**What you'll see:**

```
<coroutine object fetch_data at 0x7f1234567890>
```

**Fix:** Always use `await` when calling an async function.

---

### Mistake 4: Not using gather() when you want concurrency

```python
import asyncio

async def main():
    # ❌ WRONG — sequential (takes 3 seconds)
    result1 = await fetch(url1)  # Wait 1 second
    result2 = await fetch(url2)  # Wait 1 second
    result3 = await fetch(url3)  # Wait 1 second
    # Total: 3 seconds

asyncio.run(main())

# ✅ RIGHT — concurrent (takes 1 second)
async def main():
    results = await asyncio.gather(  # All at the same time
        fetch(url1),
        fetch(url2),
        fetch(url3),
    )
    # Total: 1 second
```

---

### Mistake 5: Ignoring return_exceptions=True when one task fails

```python
async def main():
    # ❌ WRONG — if Task 2 fails, entire gather fails and we lose results from Task 1 & 3
    results = await asyncio.gather(
        task1(),
        task2(),  # If this fails...
        task3(),  # This never runs!
        # return_exceptions=True  # FORGOT THIS
    )

# ✅ RIGHT — handle failures gracefully
async def main():
    results = await asyncio.gather(
        task1(),
        task2(),
        task3(),
        return_exceptions=True,  # Task 2 fails, but Task 1 & 3 still run
    )

    for result in results:
        if isinstance(result, Exception):  # Check if it's an error
            print(f"Task failed: {result}")
        else:
            print(f"Task succeeded: {result}")
```

---

### Mistake 6: Not using context managers (session might not close)

```python
import aiohttp

# ❌ WRONG — session might not close properly
session = aiohttp.ClientSession()
data = await session.get(url)
# If an exception happens here, session is never closed!
# This wastes resources (connection leak)

# ✅ RIGHT — auto-closes even if exception happens
async with aiohttp.ClientSession() as session:
    data = await session.get(url)
    # Even if exception here, session auto-closes
```

---

### Mistake 7: Creating a new database connection for every query

```python
import asyncpg

# ❌ WRONG — slow! Opens/closes connection for each query
for company_id in range(1, 51):
    conn = await asyncpg.connect("postgresql://...")  # Open new connection
    result = await conn.fetch("SELECT * FROM companies WHERE id = $1", company_id)
    await conn.close()  # Close connection
    # Repeat 50 times = 50 open/close cycles (slow!)

# ✅ RIGHT — use connection pool (fast!)
pool = await asyncpg.create_pool("postgresql://...", min_size=5, max_size=20)

for company_id in range(1, 51):
    async with pool.acquire() as conn:  # Reuse connection from pool
        result = await conn.fetch("SELECT * FROM companies WHERE id = $1", company_id)
        # Connection returned to pool, ready for next query (fast!)

await pool.close()  # Close pool when done
```

---

## ✅ Exercises

### Exercise 1: Sequential vs Concurrent (Easy)

**Goal:** Write an async function that fetches 5 URLs sequentially, then rewrite it to fetch them concurrently. Measure the difference.

**Setup:**

```python
import asyncio
import time
import aiohttp

URLS = [
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/1",
]

async def fetch_url(session, url):
    async with session.get(url) as response:
        return response.status
```

**Your task:**

1. Write `async_sequential()` that fetches all URLs one after another using `await`
2. Write `async_concurrent()` that fetches all URLs at the same time using `gather()`
3. Time both and print the difference
4. Expected result: concurrent should be ~5x faster

**Hint:** Use `time.time()` to measure. Sequential should take ~5 seconds, concurrent should take ~1 second.

---

### Exercise 2: Error Handling with gather() (Medium)

**Goal:** Fetch 5 URLs, but 2 of them intentionally fail. Use `return_exceptions=True` to handle failures gracefully.

**Setup:**

```python
import asyncio
import aiohttp

URLS = [
    "https://httpbin.org/status/200",  # OK
    "https://httpbin.org/status/500",  # Server error
    "https://httpbin.org/status/200",  # OK
    "https://httpbin.org/status/404",  # Not found
    "https://httpbin.org/status/200",  # OK
]

async def fetch_safe(session, url):
    try:
        async with session.get(url) as response:
            return {"url": url, "status": response.status, "ok": response.status == 200}
    except Exception as e:
        return {"url": url, "status": "error", "ok": False, "error": str(e)}
```

**Your task:**

1. Use `asyncio.gather(..., return_exceptions=True)` to fetch all URLs
2. Print each result with status (✅ or ❌)
3. Count how many succeeded and how many failed
4. Expected: 3 succeed, 2 fail

**Hint:** Check if result is a dict or an Exception. Print summary at the end.

---

### Exercise 3: Async Database Queries (Hard)

**Goal:** Connect to PostgreSQL using asyncpg, create a connection pool, and fetch data asynchronously.

**Setup:** Assume you have a PostgreSQL database with a `companies` table:

```sql
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    domain VARCHAR(100)
);

INSERT INTO companies (name, domain) VALUES
    ('TechCorp', 'techcorp.com'),
    ('DataInc', 'datainc.io'),
    ('CloudSys', 'cloudsys.net');
```

**Your task:**

1. Install asyncpg: `pip install asyncpg`
2. Create a connection pool with min_size=2, max_size=10
3. Fetch all companies asynchronously
4. Insert a new company asynchronously
5. Query the total count of companies
6. Print all results
7. Close the pool when done

**Hint:** Use `asyncpg.create_pool()`, `pool.acquire()`, and `async with` context manager.

---

## 🏗️ Mini Project: Async Lead Enrichment Fetcher

**Goal:** Build a realistic system that enriches 5 companies' data by fetching external info asynchronously, handling errors per company, and saving results to PostgreSQL.

**What you'll learn:**

- Real-world async concurrency pattern
- Error handling with `return_exceptions=True`
- Combining aiohttp + asyncpg
- Processing 5 items in ~1-2 seconds instead of 5+ seconds

### Part 1: Setup

```bash
pip install aiohttp asyncpg
```

### Part 2: PostgreSQL Table

Run this in psql to create the results table:

```sql
CREATE TABLE IF NOT EXISTS enriched_leads (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(100),
    domain VARCHAR(100),
    enrichment_data TEXT,
    status VARCHAR(20),  -- 'success' or 'failed'
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Part 3: Python Code

```python
import asyncio  # Async orchestrator
import aiohttp  # Async HTTP library
import asyncpg  # Async PostgreSQL
import time  # For timing
import json  # For parsing JSON

# Companies to enrich (hardcoded list)
COMPANIES = [
    {"id": 1, "name": "TechCorp", "domain": "techcorp.com"},
    {"id": 2, "name": "DataInc", "domain": "datainc.io"},
    {"id": 3, "name": "CloudSys", "domain": "cloudsys.net"},
    {"id": 4, "name": "AIStartup", "domain": "aistartup.ai"},
    {"id": 5, "name": "WebDev", "domain": "webdev.com"},
]

# PostgreSQL connection details
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "your_username",  # Change this
    "password": "your_password",  # Change this
    "database": "your_database",  # Change this
}

async def enrich_company(session, company):
    """Fetch enrichment data for a single company asynchronously."""
    url = "https://httpbin.org/delay/1"  # Simulated API call (takes 1 second)

    try:  # Wrap in try/except to catch errors
        async with session.get(url, timeout=5) as response:  # Make request with 5 second timeout
            if response.status == 200:  # If successful
                data = await response.json()  # Parse JSON response
                return {  # Return success result
                    "company_id": company["id"],
                    "company_name": company["name"],
                    "domain": company["domain"],
                    "enrichment_data": f"Tech profile for {company['name']} created on {data.get('date', 'N/A')}",
                    "status": "success",
                    "error_message": None,
                }
            else:  # If API error
                return {  # Return error result
                    "company_id": company["id"],
                    "company_name": company["name"],
                    "domain": company["domain"],
                    "enrichment_data": None,
                    "status": "failed",
                    "error_message": f"API returned status {response.status}",
                }
    except asyncio.TimeoutError:  # If request took too long
        return {  # Return timeout error
            "company_id": company["id"],
            "company_name": company["name"],
            "domain": company["domain"],
            "enrichment_data": None,
            "status": "failed",
            "error_message": "Request timed out (> 5 seconds)",
        }
    except Exception as e:  # Any other error
        return {  # Return generic error
            "company_id": company["id"],
            "company_name": company["name"],
            "domain": company["domain"],
            "enrichment_data": None,
            "status": "failed",
            "error_message": str(e),
        }

async def save_to_database(pool, results):
    """Save enriched results to PostgreSQL asynchronously."""
    print(f"\n💾 Saving {len(results)} results to database...")  # Log action

    async with pool.acquire() as conn:  # Get connection from pool
        for result in results:  # Loop through each result
            await conn.execute(  # Execute INSERT query
                """
                INSERT INTO enriched_leads (company_name, domain, enrichment_data, status, error_message)
                VALUES ($1, $2, $3, $4, $5)
                """,
                result["company_name"],  # Company name
                result["domain"],  # Domain
                result["enrichment_data"],  # Enrichment data
                result["status"],  # Success/failure status
                result["error_message"],  # Error message if failed
            )

            # Print confirmation
            if result["status"] == "success":
                print(f"  ✅ {result['company_name']}: Enriched and saved")
            else:
                print(f"  ❌ {result['company_name']}: {result['error_message']}")

async def main():
    """Main orchestration function."""
    print("=" * 70)
    print("🚀 ASYNC LEAD ENRICHMENT FETCHER")
    print("=" * 70)
    print(f"\n📋 Companies to enrich: {len(COMPANIES)}")
    for company in COMPANIES:
        print(f"   • {company['name']} ({company['domain']})")

    print(f"\n⏱️  Expected time: ~1-2 seconds (all concurrent)")
    print("   Sequential would take: ~5-10 seconds\n")

    start_time = time.time()  # Record start time

    try:  # Wrap everything in try/except for cleanup
        # Step 1: Create connection pool to PostgreSQL
        pool = await asyncpg.create_pool(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            min_size=2,  # At least 2 connections
            max_size=10,  # At most 10 connections
        )

        # Step 2: Enrich all companies concurrently
        async with aiohttp.ClientSession() as session:  # Create HTTP session
            print("🌐 Fetching enrichment data for all companies concurrently...")
            results = await asyncio.gather(  # Run all requests at the same time
                *[enrich_company(session, company) for company in COMPANIES],
                return_exceptions=True,  # Don't fail if one company's enrichment fails
            )

        # Step 3: Save results to database
        await save_to_database(pool, results)

        # Step 4: Close pool
        await pool.close()

        # Step 5: Print summary
        elapsed = time.time() - start_time  # Calculate total time
        successful = sum(1 for r in results if isinstance(r, dict) and r["status"] == "success")
        failed = len(results) - successful

        print(f"\n" + "=" * 70)
        print(f"📊 SUMMARY")
        print(f"=" * 70)
        print(f"✅ Successful: {successful}/{len(results)}")
        print(f"❌ Failed: {failed}/{len(results)}")
        print(f"⏱️  Total time: {elapsed:.2f} seconds")
        print(f"🚀 Speedup: ~{5/elapsed:.1f}x faster than sequential processing!")
        print("=" * 70)

    except Exception as e:  # Catch connection errors
        print(f"❌ Error: {e}")
        print("Make sure PostgreSQL is running and DB_CONFIG is correct!")

# Run it
if __name__ == "__main__":
    asyncio.run(main())
```

### Part 4: Run It

```bash
# Make sure PostgreSQL is running
sudo systemctl start postgresql

# Update DB_CONFIG in the script with your credentials
# Then run:
python3 mini_project.py
```

### Expected Output

```
======================================================================
🚀 ASYNC LEAD ENRICHMENT FETCHER
======================================================================

📋 Companies to enrich: 5
   • TechCorp (techcorp.com)
   • DataInc (datainc.io)
   • CloudSys (cloudsys.net)
   • AIStartup (aistartup.ai)
   • WebDev (webdev.com)

⏱️  Expected time: ~1-2 seconds (all concurrent)
   Sequential would take: ~5-10 seconds

🌐 Fetching enrichment data for all companies concurrently...

💾 Saving 5 results to database...
  ✅ TechCorp: Enriched and saved
  ✅ DataInc: Enriched and saved
  ✅ CloudSys: Enriched and saved
  ✅ AIStartup: Enriched and saved
  ✅ WebDev: Enriched and saved

======================================================================
📊 SUMMARY
======================================================================
✅ Successful: 5/5
❌ Failed: 0/5
⏱️  Total time: 1.45 seconds
🚀 Speedup: ~3.4x faster than sequential processing!
======================================================================
```

### Challenge Extension (Optional)

Make it more realistic:

1. Intentionally fail one company's API call (change its URL to httpbin.org/status/500)
2. Set timeout to 1 second and see which requests timeout
3. Add a delay between saving each result to simulate slow database
4. Print progress as each company completes (not just at the end)

---

## 🔗 What's Next

You've just learned the async pattern that powers the entire Lead Gen Agent system.

**Next modules in Phase 0:**

- **Module 7:** Advanced FastAPI patterns (middleware, dependencies, background tasks)
- **Module 8:** Testing async code (pytest, mocking, fixtures)

**Then in Phase 1-3:** You'll apply async to real systems:

- Voice agent that handles concurrent calls
- Lead enrichment pipeline processing 100+ companies
- Real-time WebSocket connections

**Then in Phase 8, Module 2:** You'll build the complete Lead Gen Agent using the exact async pattern you learned here.

### Key Takeaways to Remember

1. **Async is about scheduling, not speed.** Your CPU isn't faster. You're just not wasting time waiting.

2. **`asyncio.gather()` is your best friend.** Most concurrency patterns use it.

3. **Always use `return_exceptions=True` when one failure shouldn't stop everything.** Critical for production systems.

4. **Use `aiohttp` not `requests`. Use `asyncpg` not `psycopg2`.** The sync versions block the event loop.

5. **Test with `asyncio.run()` locally, but in production use FastAPI or a proper async framework** that manages the event loop for you.

**You now have the superpower to handle 50+ concurrent API calls like they're nothing.** The Lead Gen Agent waits for you.

---

## 📚 Reference: Common Async Functions

| Function                | Purpose                            | Example                                     |
| ----------------------- | ---------------------------------- | ------------------------------------------- |
| `asyncio.run()`         | Start async program from sync code | `asyncio.run(main())`                       |
| `asyncio.gather()`      | Run multiple tasks concurrently    | `await asyncio.gather(task1, task2, task3)` |
| `asyncio.sleep()`       | Non-blocking delay                 | `await asyncio.sleep(2)`                    |
| `asyncio.wait_for()`    | Add timeout to any awaitable       | `await asyncio.wait_for(task(), timeout=5)` |
| `aiohttp.ClientSession` | HTTP client                        | `async with aiohttp.ClientSession() as s:`  |
| `asyncpg.create_pool()` | Database connection pool           | `pool = await asyncpg.create_pool(...)`     |
| `asyncpg.fetch()`       | Run SELECT query                   | `rows = await conn.fetch("SELECT ...")`     |
| `asyncpg.execute()`     | Run INSERT/UPDATE/DELETE           | `await conn.execute("INSERT ...")`          |

---

**You did it. You now understand async. 🎉**

Questions? Head to Phase 0, Module 7 to deepen your FastAPI skills, or jump straight to Phase 8 to build the Lead Gen Agent.
