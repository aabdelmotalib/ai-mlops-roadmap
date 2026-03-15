---
tags:
  - Beginner
  - Phase 2
---

# Module 4: Connecting Databases to ETL Pipelines

You've learned to fetch, transform, and validate data. Now comes the crucial final step: getting that data into your database reliably. This module teaches you to build professional ETL pipelines: Extract data, Transform it, and Load it into PostgreSQL with proper error handling, transactions, and idempotency.

---

## 🎯 What You Will Learn

By the end of this module, you will:

- Understand the ETL pattern step-by-step
- Connect to PostgreSQL with SQLAlchemy and psycopg2
- Read from databases into pandas DataFrames
- Write DataFrames back to database tables
- Implement upserts (insert or update)
- Understand transactions and commits
- Manage database connections safely
- Use .env files to store credentials
- Implement incremental loads
- Build a complete ETL pipeline
- Handle connection pooling and retries

---

## 🧠 Concept Explained: The ETL Pattern

### The Analogy: ETL as Movie Production

**Extract:** Filming scenes (getting raw footage)

- Shoot actors, locations, action
- Raw, unedited, messy footage

**Transform:** Editing (making the footage into a story)

- Cut scenes, add music, color grade
- Rearrange to create narrative

**Load:** Distribution (getting it to audiences)

- Upload to streaming platform
- Make it available for everyone to watch

**In data:**

- **Extract:** Fetch data from sources (APIs, websites, logs)
- **Transform:** Clean, validate, aggregate
- **Load:** Store in database for analytics

### Traditional ETL vs Modern ELT

**ETL:** Extract → Process externally → Load into database
**ELT:** Extract → Load raw → Transform in database with dbt

In this module, we'll use both patterns.

---

## 🔍 How It Works: ETL Architecture

```mermaid
graph TB
    A["Source Data<br/>(API, CSV, DB)"] -->|Extract| B["Python Memory<br/>(DataFrame)"]
    B -->|Transform<br/>(pandas)| C["Cleaned Data"]
    C -->|Validate| D{Validation<br/>OK?}
    D -->|No| E["Dead-Letter<br/>Queue"]
    D -->|Yes| F["Load to<br/>PostgreSQL"]
    F -->|Commit| G["Data Saved"]

    E -->|Log Error| H["Error Handler"]
    F -->|Rollback| H

    style A fill:#ffcccc
    style B fill:#ffeecc
    style C fill:#ffffcc
    style D fill:#ffeecc
    style F fill:#ccffcc
    style G fill:#ccffcc
```

Each component is independent and repeatable.

---

## 🛠️ Step-by-Step Guide

### Step 1: Install Database Libraries

```bash
pip install SQLAlchemy psycopg2-binary python-dotenv pandas
```

### Step 2: Store Database Credentials Safely

Create `.env` file (never commit this!):

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_password
```

In your Python code:

```python
import os
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
}
```

### Step 3: Connect with SQLAlchemy

```python
from sqlalchemy import create_engine

# Create database connection engine (connection pool)
engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    echo=False,  # Set to True to see SQL statements
    pool_size=10,  # How many connections to maintain
    max_overflow=20  # Overflow pool size
)

# Test connection
with engine.connect() as conn:
    result = conn.execute("SELECT 1")
    print("✓ Connection successful")
```

### Step 4: Extract Data

```python
import pandas as pd

# From CSV
def extract_from_csv(filepath: str) -> pd.DataFrame:
    """Load data from CSV file"""
    df = pd.read_csv(filepath)
    print(f"✓ Extracted {len(df)} rows from {filepath}")
    return df

# From API
def extract_from_api(api_url: str) -> pd.DataFrame:
    """Fetch data from API and load into DataFrame"""
    import requests
    response = requests.get(api_url)
    data = response.json()
    df = pd.DataFrame(data)
    print(f"✓ Extracted {len(df)} rows from API")
    return df

# From database query
def extract_from_database(engine, query: str) -> pd.DataFrame:
    """Query database and load into DataFrame"""
    df = pd.read_sql_query(query, engine)
    print(f"✓ Extracted {len(df)} rows from database")
    return df
```

### Step 5: Transform Data

```python
# Use pandas methods from Module 1-4
def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and transform data"""

    # Remove duplicates
    df = df.drop_duplicates()

    # Remove rows with critical nulls
    df = df.dropna(subset=['id', 'title'])

    # Clean string columns
    df['title'] = df['title'].str.strip().str.title()

    # Fix types
    df['price'] = df['price'].astype(float)

    # Standardize values
    df['rating'] = df['rating'].fillna(0).astype(int)

    print(f"✓ Transformed {len(df)} rows")
    return df
```

### Step 6: Write to Database (Simple Insert)

```python
def load_to_database(df: pd.DataFrame, engine, table_name: str):
    """Write DataFrame to database table"""

    try:
        # if_exists options:
        # - 'fail': raise error if table exists (default)
        # - 'replace': drop existing table and recreate
        # - 'append': add to existing table

        df.to_sql(
            table_name,
            engine,
            if_exists='append',  # Add to existing table
            index=False
        )

        print(f"✓ Loaded {len(df)} rows to {table_name}")
        return True

    except Exception as e:
        print(f"✗ Load failed: {str(e)}")
        return False
```

### Step 7: Upsert (Insert or Update)

```python
def upsert_to_database(df: pd.DataFrame, engine, table_name: str, key_column: str):
    """
    Insert new records, update existing ones based on key.
    Idempotent: running twice = same result.
    """

    with engine.connect() as conn:
        with conn.begin():  # Transaction: all or nothing

            for idx, row in df.iterrows():
                # Build INSERT ... ON CONFLICT ... DO UPDATE statement
                columns = list(row.index)

                # Get values
                values_str = ', '.join([f"'{row[col]}'" if isinstance(row[col], str) else str(row[col]) for col in columns])

                # Build SET clause for update
                set_clause = ', '.join([f"{col} = EXCLUDED.{col}" for col in columns if col != key_column])

                query = f"""
                INSERT INTO {table_name} ({', '.join(columns)})
                VALUES ({values_str})
                ON CONFLICT ({key_column}) DO UPDATE SET
                    {set_clause}
                """

                conn.execute(query)

            # Commit happens automatically when exiting 'with' block

    print(f"✓ Upserted {len(df)} rows to {table_name}")
```

### Step 8: Transactions and Rollback

```python
def transactional_load(df: pd.DataFrame, engine, table_name: str):
    """
    Load data in a transaction.
    If any step fails, roll back everything (ACID property).
    """

    with engine.begin() as conn:  # 'begin()' = automatic transaction

        try:
            # All operations below are part of one transaction

            # Step 1: Insert new records
            new_records = df[df['updated_date'].isna()]
            new_records.to_sql(table_name, conn, if_exists='append', index=False)

            # Step 2: Delete old records
            conn.execute(f"DELETE FROM {table_name} WHERE expires_at < NOW()")

            # Step 3: Update statistics
            conn.execute(f"UPDATE {table_name}_stats SET last_updated = NOW()")

            # If we get here, everything worked
            print(f"✓ Transaction complete")

        except Exception as e:
            # Automatically rolls back on exception
            print(f"✗ Transaction failed and rolled back: {str(e)}")
            raise
```

### Step 9: Incremental Loads (Only New Data)

```python
def incremental_load(df: pd.DataFrame, engine, table_name: str, watermark_column: str):
    """
    Only load records newer than last run (incremental).
    Requires a column like 'created_at' or 'updated_at'.
    """

    # Get the last watermark (max value of watermark column)
    query = f"SELECT MAX({watermark_column}) FROM {table_name}"
    result = engine.execute(query).scalar()
    last_watermark = result if result else '2000-01-01'

    print(f"Last watermark: {last_watermark}")

    # Filter: only rows newer than last run
    df_incremental = df[df[watermark_column] > last_watermark]

    print(f"Processing {len(df_incremental)} new rows (of {len(df)} total)")

    # Load only new records
    if len(df_incremental) > 0:
        df_incremental.to_sql(
            table_name,
            engine,
            if_exists='append',
            index=False
        )
        print(f"✓ Loaded {len(df_incremental)} new rows")
    else:
        print(f"✓ No new data to load")
```

---

## 💻 Code Examples

### Example 1: Complete ETL Pipeline

```python
import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load credentials
load_dotenv()
DB_URL = f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

# Step 1: EXTRACT
def extract_books():
    """Extract books from CSV"""
    df = pd.read_csv('books.csv')
    logger.info(f"Extracted {len(df)} books from CSV")
    return df

# Step 2: TRANSFORM
def transform_books(df):
    """Clean and prepare books data"""

    # Remove duplicates
    df = df.drop_duplicates(subset=['isbn'])

    # Remove rows with null required fields
    df = df.dropna(subset=['book_id', 'title'])

    # Clean text fields
    df['title'] = df['title'].str.strip().str.title()
    df['author'] = df['author'].str.strip()

    # Fix price to float
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df = df.dropna(subset=['price'])  # Drop if price conversion failed

    # Fix rating to integer
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df['rating'] = df['rating'].fillna(0).astype(int)

    # Add processing timestamp
    df['loaded_at'] = pd.Timestamp.now()

    logger.info(f"Transformed {len(df)} books")
    return df

# Step 3: LOAD
def load_books(df, engine):
    """Load transformed books to database"""

    try:
        df.to_sql(
            'books',
            engine,
            if_exists='replace',  # Replace table
            index=False,
            chunksize=1000  # Insert 1000 rows at a time (safer)
        )
        logger.info(f"✓ Loaded {len(df)} books to database")
        return True
    except Exception as e:
        logger.error(f"✗ Failed to load: {str(e)}")
        return False

# Main ETL function
def etl_pipeline():
    """Run complete ETL pipeline"""

    logger.info("Starting ETL pipeline...")

    # Create engine
    engine = create_engine(DB_URL)

    try:
        # Extract
        df = extract_books()

        # Transform
        df = transform_books(df)

        # Load
        success = load_books(df, engine)

        if success:
            logger.info("✓ ETL pipeline complete!")
        else:
            logger.error("✗ ETL pipeline failed!")

        return success

    except Exception as e:
        logger.error(f"✗ Pipeline error: {str(e)}", exc_info=True)
        return False

    finally:
        engine.dispose()  # Close all connections

# Run it
if __name__ == '__main__':
    etl_pipeline()
```

### Example 2: Idempotent Upsert

```python
from sqlalchemy import text

def idempotent_upsert(df: pd.DataFrame, engine, table_name: str, unique_key: str):
    """
    Idempotent insert: running twice = same result.
    Uses ON CONFLICT to update if record exists.
    """

    logger.info(f"Upserting {len(df)} records to {table_name}")

    with engine.connect() as conn:
        # Start transaction
        with conn.begin():

            # Build UPSERT query
            columns = list(df.columns)
            insert_cols = ', '.join(columns)

            # VALUES placeholder
            values_placeholder = ', '.join([':' + col for col in columns])

            # UPDATE SET clause (exclude the key column)
            update_cols = ', '.join([f"{col} = EXCLUDED.{col}" for col in columns if col != unique_key])

            query = text(f"""
            INSERT INTO {table_name} ({insert_cols})
            VALUES ({values_placeholder})
            ON CONFLICT ({unique_key}) DO UPDATE SET
                {update_cols},
                updated_at = NOW()
            """)

            # Execute for each row (could be batched for better performance)
            for idx, row in df.iterrows():
                params = {col: row[col] for col in columns}
                conn.execute(query, params)

            logger.info(f"✓ Upserted {len(df)} records")

# Usage
df_update = pd.DataFrame([
    {'book_id': 1, 'title': 'Python 101', 'author': 'John', 'price': 29.99},
    {'book_id': 2, 'title': 'Web Dev 101', 'author': 'Sarah', 'price': 24.99}
])

engine = create_engine(DB_URL)
idempotent_upsert(df_update, engine, 'books', 'book_id')
```

### Example 3: Incremental Load with Watermark

```python
def incremental_load_with_watermark(api_url: str, engine, table_name: str):
    """
    Fetch only new records based on timestamp.
    Example: only fetch books created in the last hour.
    """

    # Get last load time
    query = "SELECT MAX(created_at) FROM books"
    last_load = pd.read_sql_query(query, engine).iloc[0, 0]

    if last_load is None:
        last_load = pd.Timestamp('2000-01-01')

    logger.info(f"Last load: {last_load}")

    # API call: only fetch recent books
    params = {
        'created_after': last_load.isoformat()
    }

    response = requests.get(api_url, params=params)
    new_books = response.json()

    if len(new_books) == 0:
        logger.info("No new data to load")
        return

    # Transform new data
    df = pd.DataFrame(new_books)
    df = transform_books(df)  # Apply same cleaning

    # Load only new records (upsert handles duplicates)
    idempotent_upsert(df, engine, table_name, 'book_id')

    logger.info(f"✓ Loaded {len(df)} new records (incremental)")
```

---

## ⚠️ Common Mistakes

### Mistake 1: No Error Handling

**WRONG:**

```python
df.to_sql('books', engine)  # What if this fails?
# Pipeline crashes, no rollback, data lost
```

**RIGHT:**

```python
try:
    df.to_sql('books', engine)
except Exception as e:
    logger.error(f"Load failed: {e}")
    # Handle gracefully
    return False
```

### Mistake 2: Loading Entire Dataset Every Time

**WRONG:**

```python
# Every run loads all 1 million rows
df = pd.read_csv('all_books.csv')  # Huge file!
df.to_sql('books', engine, if_exists='replace')
```

**RIGHT:**

```python
# Only load new records
last_updated = get_last_watermark(engine)
df = pd.read_csv('books.csv')
df_new = df[df['updated_at'] > last_updated]
df_new.to_sql('books', engine, if_exists='append')
```

### Mistake 3: Storing Credentials in Code

**WRONG:**

```python
# NEVER do this!
engine = create_engine(
    "postgresql://postgres:MyPassword123@localhost/mydb"
)
```

**RIGHT:**

```python
from dotenv import load_dotenv
import os

load_dotenv()
password = os.getenv('DB_PASSWORD')
engine = create_engine(
    f"postgresql://postgres:{password}@localhost/mydb"
)
```

---

## ✅ Exercises

### Easy: Extract and Load

Write a script that:

1. Creates a simple DataFrame
2. Connects to PostgreSQL
3. Loads the DataFrame to a table

### Medium: ETL with Transform

Build an ETL that:

1. Reads books CSV
2. Cleans price and rating columns
3. Removes duplicates
4. Loads to database

### Hard: Idempotent Pipeline

Create a pipeline that:

1. Extracts data from an API
2. Transforms (cleans) it
3. Upserts to database (idempotent)
4. Logs everything
5. Can be run multiple times safely

---

## 🏗️ Mini Project: Complete ETL Pipeline

Build a production-ready ETL system for books data.

### Requirements

1. **Extract:** Read from `books.csv`
2. **Transform:**
   - Remove duplicates (by ISBN)
   - Clean title and author
   - Validate price and rating
   - Add timestamp
3. **Load:** Upsert to PostgreSQL
4. **Error handling:** Rollback on failure
5. **Logging:** Log every step
6. **Idempotency:** Safe to run twice

### Implementation

```python
import pandas as pd
from sqlalchemy import create_engine, text
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load config
load_dotenv()
DB_URL = f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

class BooksETL:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        self.stats = {'extracted': 0, 'transformed': 0, 'loaded': 0}

    def extract(self, csv_file: str) -> pd.DataFrame:
        """Extract books from CSV"""
        df = pd.read_csv(csv_file)
        self.stats['extracted'] = len(df)
        logger.info(f"✓ Extracted {len(df)} rows from {csv_file}")
        return df

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform/clean books data"""

        # Remove duplicates by ISBN
        df = df.drop_duplicates(subset=['isbn'], keep='first')

        # Clean titles
        df['title'] = df['title'].str.strip().str.title()

        # Validate price
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df = df[df['price'] > 0]  # Remove invalid prices

        # Validate rating
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
        df['rating'] = df['rating'].fillna(0).astype(int)
        df = df[(df['rating'] >= 0) & (df['rating'] <= 5)]

        # Add metadata
        df['loaded_at'] = pd.Timestamp.now()

        self.stats['transformed'] = len(df)
        logger.info(f"✓ Transformed {len(df)} rows")
        return df

    def load(self, df: pd.DataFrame, table_name: str) -> bool:
        """Load data to PostgreSQL (idempotent upsert)"""

        try:
            with self.engine.begin() as conn:

                for idx, row in df.iterrows():
                    # Build UPSERT
                    query = text(f"""
                    INSERT INTO {table_name} (book_id, title, author, price, rating, isbn, loaded_at)
                    VALUES (:book_id, :title, :author, :price, :rating, :isbn, :loaded_at)
                    ON CONFLICT (isbn) DO UPDATE SET
                        title = EXCLUDED.title,
                        author = EXCLUDED.author,
                        price = EXCLUDED.price,
                        rating = EXCLUDED.rating,
                        loaded_at = EXCLUDED.loaded_at
                    """)

                    params = {
                        'book_id': row['book_id'],
                        'title': row['title'],
                        'author': row['author'],
                        'price': row['price'],
                        'rating': row['rating'],
                        'isbn': row['isbn'],
                        'loaded_at': row['loaded_at']
                    }

                    conn.execute(query, params)

                self.stats['loaded'] = len(df)
                logger.info(f"✓ Loaded {len(df)} rows to {table_name}")
                return True

        except Exception as e:
            logger.error(f"✗ Load failed: {str(e)}", exc_info=True)
            return False

    def run(self, csv_file: str, table_name: str) -> bool:
        """Run complete ETL pipeline"""

        logger.info("=" * 50)
        logger.info("Starting Books ETL Pipeline")
        logger.info("=" * 50)

        try:
            # Extract
            df = self.extract(csv_file)

            # Transform
            df = self.transform(df)

            # Load
            success = self.load(df, table_name)

            if success:
                logger.info("=" * 50)
                logger.info("ETL Pipeline Complete!")
                logger.info(f"Extracted: {self.stats['extracted']}")
                logger.info(f"Transformed: {self.stats['transformed']}")
                logger.info(f"Loaded: {self.stats['loaded']}")
                logger.info("=" * 50)
                return True
            else:
                logger.error("Pipeline failed at load step")
                return False

        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}", exc_info=True)
            return False

        finally:
            self.engine.dispose()

# Run it
if __name__ == '__main__':
    etl = BooksETL(DB_URL)
    etl.run('books.csv', 'books')
```

---

## 🔗 What's Next

Your data is now flowing reliably!

- **Module 2-5 (Orchestration)**: Schedule with Airflow
- **Advanced:** Multi-table joins, slowly-changing dimensions

Professional ETL is the foundation of analytics and data science.

---

## 📚 Summary

In this module, you learned:

1. ✅ **ETL pattern** – Extract → Transform → Load
2. ✅ **SQLAlchemy** – Python database connections
3. ✅ **Credentials** – Store safely in .env
4. ✅ **Extract** – From CSV, API, database
5. ✅ **Transform** – Clean with pandas
6. ✅ **Load** – Write to database
7. ✅ **Upserts** – Insert or update
8. ✅ **Transactions** – All-or-nothing operations
9. ✅ **Incremental** – Only load new data
10. ✅ **Complete pipeline** – Production-ready code

ETL is the lifeblood of data engineering. Master it.

---

**Congratulations! Your data now moves reliably from source to database. 🎉**
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
