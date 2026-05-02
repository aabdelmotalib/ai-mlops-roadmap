"""
Benchmark: requests (synchronous) vs aiohttp (asynchronous)
This demonstrates the real performance difference between sync and async.

Run this to see ~7-10x speedup with async!
"""

import asyncio  # Async orchestrator
import time  # For timing
import aiohttp  # Async HTTP library
import requests  # Regular HTTP library

# URLs to fetch (10 URLs, each takes 1 second)
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


def sync_fetch():
    """
    SYNCHRONOUS version (old way).
    Fetches URLs one at a time. Takes ~10 seconds.
    """
    start_time = time.time()  # Record start time
    
    for url in URLS:  # Loop through each URL
        response = requests.get(url)  # Fetch it (BLOCKS until response arrives)
        status = response.status_code  # Get status code
    
    elapsed = time.time() - start_time  # Calculate how long it took
    return elapsed  # Return elapsed time


async def async_fetch():
    """
    ASYNCHRONOUS version (new way).
    Fetches all URLs at the same time. Takes ~1 second.
    """
    start_time = time.time()  # Record start time
    
    async with aiohttp.ClientSession() as session:  # Create session
        # Create a list of fetch tasks
        async def fetch_one(url):  # Helper to fetch a single URL
            async with session.get(url) as response:  # Make request
                status = response.status  # Get status code
                return status  # Return it
        
        # Run all requests at the same time
        await asyncio.gather(
            *[fetch_one(url) for url in URLS]  # Unpack list of tasks
        )
    
    elapsed = time.time() - start_time  # Calculate how long it took
    return elapsed  # Return elapsed time


if __name__ == "__main__":
    print("=" * 70)
    print("BENCHMARK: Fetching 10 URLs (each takes ~1 second)")
    print("=" * 70)
    
    print("\n1. SYNCHRONOUS (old way with requests library):")
    sync_time = sync_fetch()  # Run sync version
    print(f"   Time taken: {sync_time:.2f} seconds")  # Print result
    print(f"   → Fetches one URL at a time (1+1+1+... = ~10 seconds)")  # Explain
    
    print("\n2. ASYNCHRONOUS (new way with aiohttp):")
    async_time = asyncio.run(async_fetch())  # Run async version
    print(f"   Time taken: {async_time:.2f} seconds")  # Print result
    print(f"   → Fetches all URLs at the same time (~1 second)")  # Explain
    
    print("\n" + "=" * 70)
    speedup = sync_time / async_time  # Calculate how much faster
    print(f"SPEEDUP: {speedup:.1f}x faster with async!")  # Show improvement
    print(f"Time saved: {sync_time - async_time:.2f} seconds")  # Show absolute time saved
    print("=" * 70)
