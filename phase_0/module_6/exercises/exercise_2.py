"""
Exercise 2: Error Handling with gather()

Goal: Fetch 5 URLs, but 2 of them intentionally fail. Use return_exceptions=True 
to handle failures gracefully.

Expected result:
- 3 URLs should succeed (status 200)
- 2 URLs should fail (status 500 and 404)
- All 5 should be processed (no crashing on first error)
"""

import asyncio  # Async orchestrator
import aiohttp  # Async HTTP library

URLS = [
    "https://httpbin.org/status/200",  # OK
    "https://httpbin.org/status/500",  # Server error
    "https://httpbin.org/status/200",  # OK
    "https://httpbin.org/status/404",  # Not found
    "https://httpbin.org/status/200",  # OK
]


async def fetch_safe(session, url):
    """
    Fetch a URL and handle errors gracefully.
    Returns a dict with url, status, and whether it succeeded.
    """
    try:  # Wrap in try/except
        async with session.get(url) as response:  # Make request
            ok = response.status == 200  # Check if 200 (success)
            return {
                "url": url,
                "status": response.status,
                "ok": ok,
            }
    except Exception as e:  # Network or other error
        return {
            "url": url,
            "status": "error",
            "ok": False,
            "error": str(e),
        }


async def main():
    """Main function."""
    print("=" * 70)
    print("Exercise 2: Error Handling with gather()")
    print("=" * 70)
    print(f"\nFetching {len(URLS)} URLs (3 should succeed, 2 should fail):")
    for url in URLS:
        print(f"  • {url}")
    
    async with aiohttp.ClientSession() as session:  # Create session
        # Use return_exceptions=True so failures don't stop the entire gather()
        results = await asyncio.gather(
            *[fetch_safe(session, url) for url in URLS],
            return_exceptions=True,  # This is the key!
        )
    
    # Process results
    print("\n" + "=" * 70)
    print("RESULTS:")
    print("=" * 70)
    
    successful = []  # Track successful results
    failed = []  # Track failed results
    
    for result in results:  # Go through each result
        if isinstance(result, Exception):  # If it's an exception
            print(f"  ❌ Exception: {result}")
            failed.append(result)
        elif result["ok"]:  # If status is 200
            print(f"  ✅ {result['url']}: Status {result['status']}")
            successful.append(result)
        else:  # If status is not 200
            print(f"  ❌ {result['url']}: Status {result['status']}")
            failed.append(result)
    
    # Summary
    print("\n" + "=" * 70)
    print(f"✅ Successful: {len(successful)}/{len(results)}")
    print(f"❌ Failed: {len(failed)}/{len(results)}")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
