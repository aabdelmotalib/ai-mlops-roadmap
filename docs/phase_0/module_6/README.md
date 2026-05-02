# Quick Start Guide: Module 6 - Async Python

## 📦 What's in This Folder

```
module_6/
├── module_6.md                    ← Main learning material (START HERE!)
├── code_snippets/
│   └── benchmark.py               ← Run this to see async speedup
├── exercises/
│   ├── exercise_1.py              ← Sequential vs Concurrent comparison
│   ├── exercise_2.py              ← Error handling with gather()
│   └── exercise_3.py              ← PostgreSQL async queries
├── mini_projects/
│   └── lead_enrichment_fetcher.py  ← Full realistic example
└── practice/                        ← Your practice files here
```

## ⚡ Quick Setup

```bash
# 1. Activate virtual environment
source ~/.venv/bin/activate

# 2. Install dependencies
pip install aiohttp asyncpg

# 3. Verify installation
python -c "import asyncio, aiohttp, asyncpg; print('All good!')"
```

## 🚀 Try It Now (5 minutes)

```bash
# See async speedup with your own eyes
cd code_snippets
python benchmark.py

# Expected output:
# SPEEDUP: ~7-10x faster with async!
```

## 📚 Learning Path

### Phase 1: Understand (Read module_6.md)

- Waiter analogy
- Event loop concept
- async/await syntax
- asyncio.gather()

### Phase 2: See It Work (Run examples)

```bash
# Sequential vs Concurrent
python exercises/exercise_1.py

# Error handling
python exercises/exercise_2.py

# Database queries
python exercises/exercise_3.py
```

### Phase 3: Build It (Mini project)

```bash
# First, set up PostgreSQL:
# 1. Create table (SQL in lead_enrichment_fetcher.py)
# 2. Update DB_CONFIG in the file
# 3. Run it:
python mini_projects/lead_enrichment_fetcher.py
```

## 🎯 Learning Objectives

By the end, you'll know:

- ✅ How async saves time (waiter analogy)
- ✅ Event loop scheduling
- ✅ async/await syntax
- ✅ asyncio.gather() for concurrency
- ✅ aiohttp for HTTP requests
- ✅ asyncpg for database
- ✅ Error handling in async code
- ✅ The exact pattern used in Lead Gen Agent

## ⚠️ Common Mistakes

1. **Forgot `async` on function?** → Add it: `async def fetch():`
2. **Using `requests` instead of `aiohttp`?** → Blocks event loop!
3. **Didn't use `await` on async call?** → Get coroutine object, not result
4. **Gather failing on first error?** → Add `return_exceptions=True`
5. **Database connection slow?** → Use connection pool, not new connection each time

## 📊 Key Functions Reference

| Function                | What it does               |
| ----------------------- | -------------------------- |
| `asyncio.run()`         | Start async program        |
| `asyncio.gather()`      | Run multiple tasks at once |
| `asyncio.wait_for()`    | Add timeout                |
| `aiohttp.ClientSession` | HTTP client                |
| `asyncpg.create_pool()` | Database pool              |

## 🔗 What's Next

After mastering this module:

1. **Module 7:** Advanced FastAPI patterns
2. **Module 8:** Testing async code
3. **Phase 8, Module 2:** Build the actual Lead Gen Agent

## 💡 One Big Idea

**Async doesn't make your code faster. It makes it smarter about waiting.**

When your code hits `await`, instead of sitting idle, it:

1. Saves state
2. Starts other tasks
3. Checks back later when ready

This is how you process 50 leads in 2 seconds instead of 100 seconds.

---

**Ready? Start with `module_6.md` or jump to `exercises/exercise_1.py` to see speedup!**
