"""
Exercise 3: Async Database Queries

Goal: Connect to PostgreSQL using asyncpg, create a connection pool, 
and fetch data asynchronously.

Before running:
1. Create table:
   CREATE TABLE IF NOT EXISTS companies (
       id SERIAL PRIMARY KEY,
       name VARCHAR(100),
       domain VARCHAR(100)
   );
   
2. Insert sample data:
   INSERT INTO companies (name, domain) VALUES
       ('TechCorp', 'techcorp.com'),
       ('DataInc', 'datainc.io'),
       ('CloudSys', 'cloudsys.net');

3. Update DB_CONFIG below with your credentials

4. Run: python3 exercise_3.py
"""

import asyncio  # Async orchestrator
import asyncpg  # Async PostgreSQL

# PostgreSQL connection details — UPDATE THESE!
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",  # Change this to your username
    "password": "password",  # Change this to your password
    "database": "test_db",  # Change this to your database name
}


async def main():
    """Main function."""
    print("=" * 70)
    print("Exercise 3: Async Database Queries with asyncpg")
    print("=" * 70)
    
    try:  # Wrap in try/except for error handling
        # Step 1: Create connection pool
        print("\n1. Creating connection pool...")
        pool = await asyncpg.create_pool(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            min_size=2,  # At least 2 connections ready
            max_size=10,  # At most 10 connections
        )
        print("   ✅ Connection pool created")
        
        # Step 2: Fetch all companies
        print("\n2. Fetching all companies...")
        async with pool.acquire() as conn:  # Get connection from pool
            rows = await conn.fetch("SELECT id, name, domain FROM companies")  # Query
            print(f"   ✅ Found {len(rows)} companies:")
            for row in rows:  # Loop through rows
                print(f"      • {row['name']} ({row['domain']})")
        
        # Step 3: Insert a new company
        print("\n3. Inserting a new company...")
        async with pool.acquire() as conn:  # Get another connection
            result = await conn.execute(  # Execute INSERT
                "INSERT INTO companies (name, domain) VALUES ($1, $2)",
                "AI Innovations",  # Company name
                "aiinnovations.io",  # Domain
            )
            print(f"   ✅ {result}")  # Print result (e.g., "INSERT 0 1")
        
        # Step 4: Query count
        print("\n4. Counting total companies...")
        async with pool.acquire() as conn:  # Reuse pool connection
            count = await conn.fetchval("SELECT COUNT(*) FROM companies")  # Get count
            print(f"   ✅ Total companies: {count}")
        
        # Step 5: Fetch updated list
        print("\n5. Fetching updated list...")
        async with pool.acquire() as conn:  # Get connection
            rows = await conn.fetch("SELECT id, name, domain FROM companies")
            print(f"   ✅ Companies in database:")
            for row in rows:
                print(f"      • [{row['id']}] {row['name']} ({row['domain']})")
        
        # Step 6: Close pool
        print("\n6. Closing connection pool...")
        await pool.close()
        print("   ✅ Pool closed")
        
        print("\n" + "=" * 70)
        print("✅ All operations completed successfully!")
        print("=" * 70)
    
    except asyncpg.PostgresError as e:
        print(f"\n❌ Database Error: {e}")
        print("Make sure:")
        print("  1. PostgreSQL is running")
        print("  2. You created the companies table")
        print("  3. DB_CONFIG has correct credentials")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
