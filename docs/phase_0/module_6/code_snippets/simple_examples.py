"""
Simple Async Examples - Start Here!

These are the 4 simplest examples to understand async.
Run each one separately to see how async works.
"""

import asyncio  # Async orchestrator


# ============================================================================
# EXAMPLE 1: Basic async function
# ============================================================================
# Shows: async def, await, asyncio.run()

async def example_1_basic():
    """Your first async function."""
    print("Starting task...")  # Print before waiting
    await asyncio.sleep(1)  # Pause for 1 second (other tasks run now)
    print("Task done!")  # Print after waiting
    return "Success"


print("EXAMPLE 1: Basic async function")
print("-" * 50)
result = asyncio.run(example_1_basic())
print(f"Result: {result}\n")


# ============================================================================
# EXAMPLE 2: Two tasks run sequentially (wrong way)
# ============================================================================
# Shows: What NOT to do

async def example_2_sequential():
    """Two tasks one after another (takes 2 seconds)."""
    print("Task 1 starting...")
    await asyncio.sleep(1)  # Wait 1 second
    print("Task 1 done!")
    
    print("Task 2 starting...")
    await asyncio.sleep(1)  # Wait 1 second (Task 1 already done, so really waiting)
    print("Task 2 done!")


print("EXAMPLE 2: Sequential (SLOW - takes ~2 seconds)")
print("-" * 50)
asyncio.run(example_2_sequential())
print()


# ============================================================================
# EXAMPLE 3: Two tasks run concurrently (right way)
# ============================================================================
# Shows: How to use gather() to run tasks at the same time

async def task_a():
    """First task."""
    print("  Task A starting...")
    await asyncio.sleep(1)  # Wait 1 second
    print("  Task A done!")
    return "A result"


async def task_b():
    """Second task."""
    print("  Task B starting...")
    await asyncio.sleep(1)  # Wait 1 second (happens at the SAME TIME as Task A!)
    print("  Task B done!")
    return "B result"


async def example_3_concurrent():
    """Two tasks at the same time (takes 1 second)."""
    results = await asyncio.gather(
        task_a(),  # Start but don't wait
        task_b(),  # Start but don't wait
    )
    return results


print("EXAMPLE 3: Concurrent (FAST - takes ~1 second)")
print("-" * 50)
results = asyncio.run(example_3_concurrent())
print(f"Results: {results}\n")


# ============================================================================
# EXAMPLE 4: Three tasks with timing
# ============================================================================
# Shows: How much faster gathering is

async def task_with_timing(name, delay):
    """Task that takes a specific amount of time."""
    print(f"  [{name}] Starting (will take {delay}s)...")
    await asyncio.sleep(delay)  # Simulate work
    print(f"  [{name}] Done!")
    return f"{name}: {delay}s"


async def example_4_speedup():
    """Run 3 tasks: 1s, 2s, 1s."""
    results = await asyncio.gather(
        task_with_timing("Task 1", 1),  # 1 second
        task_with_timing("Task 2", 2),  # 2 seconds
        task_with_timing("Task 3", 1),  # 1 second
    )
    return results


print("EXAMPLE 4: Three tasks (1s + 2s + 1s = 4s sequential, but ~2s concurrent)")
print("-" * 50)
results = asyncio.run(example_4_speedup())
print(f"Results: {results}\n")

print("=" * 50)
print("That's it! You now understand async basics!")
print("=" * 50)
