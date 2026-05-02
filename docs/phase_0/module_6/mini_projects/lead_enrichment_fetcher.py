"""
Mini Project: Async Lead Enrichment Fetcher

This is the EXACT pattern used in the Lead Gen Agent (Phase 8, Module 2).

It demonstrates:
1. Fetching data for 5 companies asynchronously
2. Handling errors gracefully with return_exceptions=True
3. Saving results to PostgreSQL
4. Processing 5 items in ~1-2 seconds instead of 5+ seconds

Before running:
1. Install dependencies: pip install aiohttp asyncpg
2. Update DB_CONFIG below with your PostgreSQL credentials
3. Create the enriched_leads table (SQL provided in comments)
4. Run: python3 mini_project.py
"""

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

# PostgreSQL connection details — UPDATE THESE!
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",  # Change this to your username
    "password": "password",  # Change this to your password
    "database": "test_db",  # Change this to your database name
}

# SQL to create the table (run this in psql first):
"""
CREATE TABLE IF NOT EXISTS enriched_leads (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(100),
    domain VARCHAR(100),
    enrichment_data TEXT,
    status VARCHAR(20),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


async def enrich_company(session, company):
    """
    Fetch enrichment data for a single company asynchronously.
    
    In production, this would call real APIs like:
    - LinkedIn API for company info
    - Clearbit API for technology stack
    - Hunter.io for email addresses
    
    Here, we simulate with httpbin.org delays.
    """
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
    """
    Save enriched results to PostgreSQL asynchronously.
    
    In production, this would batch inserts for better performance,
    but for clarity, we insert one at a time.
    """
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
        if 5 / elapsed > 1:
            print(f"🚀 Speedup: ~{5/elapsed:.1f}x faster than sequential processing!")
        print("=" * 70)
    
    except asyncpg.PostgresError as e:
        print(f"❌ Database Error: {e}")
        print("Make sure PostgreSQL is running and DB_CONFIG is correct!")
        print("Update DB_CONFIG at the top of this file with your credentials.")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Check the error above and try again.")


if __name__ == "__main__":
    asyncio.run(main())
