"""
Exercise 1: Sequential vs Concurrent

Goal: Write an async function that fetches 5 URLs sequentially, then rewrite it 
to fetch them concurrently. Measure the difference.

Expected result: concurrent should be ~5x faster
Sequential: ~5 seconds
Concurrent: ~1 second
"""

import asyncio  # Async orchestrator
import time  # For timing
import aiohttp  # Async HTTP library

URLS = [
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/1",
]


async def fetch_url(session, url):
    """Helper function to fetch a single URL."""
    async with session.get(url) as response:  # Make request
        return response.status  # Return status code


async def sequential_fetch():
    """
    Fetch all URLs one at a time (sequential).
    This should take ~5 seconds.
    """
    print("Sequential fetch starting...")
    start_time = time.time()  # Record start time
    
    async with aiohttp.ClientSession() as session:  # Create session
        for url in URLS:  # Loop through each URL
            status = await fetch_url(session, url)  # Wait for each one to finish
            print(f"  ✓ Fetched {url} - status {status}")
    
    elapsed = time.time() - start_time  # Calculate time
    return elapsed


async def concurrent_fetch():
    """
    Fetch all URLs at the same time (concurrent).
    This should take ~1 second.
    """
    print("Concurrent fetch starting...")
    start_time = time.time()  # Record start time
    
    async with aiohttp.ClientSession() as session:  # Create session
        results = await asyncio.gather(  # Run all at the same time
            *[fetch_url(session, url) for url in URLS]
        )
        for i, status in enumerate(results):
            print(f"  ✓ Fetched URL {i+1} - status {status}")
    
    elapsed = time.time() - start_time  # Calculate time
    return elapsed


async def main():
    """Compare sequential vs concurrent."""
    print("=" * 70)
    print("Exercise 1: Sequential vs Concurrent")
    print("=" * 70)
    
    # Run sequential
    print("\n1. SEQUENTIAL (one at a time):")
    seq_time = await sequential_fetch()
    print(f"   Total time: {seq_time:.2f} seconds")
    
    # Run concurrent
    print("\n2. CONCURRENT (all at the same time):")
    con_time = await concurrent_fetch()
    print(f"   Total time: {con_time:.2f} seconds")
    
    # Show speedup
    print("\n" + "=" * 70)
    speedup = seq_time / con_time
    print(f"SPEEDUP: {speedup:.1f}x faster!")
    print(f"Time saved: {seq_time - con_time:.2f} seconds")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
