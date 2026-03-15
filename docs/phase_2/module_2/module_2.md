---
tags:
  - Beginner
  - Phase 2
---

# Module 2: dbt Transformations

Your Airflow DAG extracts data from APIs and websites, cleans it with pandas, and loads it into PostgreSQL. Great! But as your pipelines scale, you'll have hundreds of tables, complex transformations, and nobody knows what depends on what.

**dbt (data build tool) solves this.**

dbt is a framework that lets you write SQL to transform raw data into clean, reliable analytics tables. It automatically forms dependencies, tests data quality, and generates documentation. dbt turns your database into a version-controlled, testable codebase.

---

## 🎯 What You Will Learn

By the end of this module, you will:

- Understand what dbt is and where it fits in a data pipeline
- Know the difference between ETL and ELT patterns
- Install dbt-core and the PostgreSQL adapter
- Initialize a dbt project
- Understand project structure (models, tests, seeds)
- Write your first model (a .sql file)
- Know materializations: table, view, incremental, ephemeral
- Use the ref() function to build DAGs automatically
- Write and run data tests
- Generate documentation
- Build a three-model pipeline: staging → intermediate → marts

---

## 🧠 Concept Explained: What Is dbt?

### The Analogy: dbt as a Factory for Data

**Traditional ETL (Extract, Transform, Load):**
It's like a restaurant that goes between the farmer's market, a central kitchen, and the dining room.

- Extract: Go to market, buy ingredients
- Transform: Cook in central kitchen
- Load: Serve to customers

**Modern ELT (Extract, Load, Transform):**
It's like a restaurant that brings ALL ingredients to one kitchen (refrigerator full of raw ingredients), then later decides what to cook.

- Extract: Bring all ingredients
- Load: Put them in the kitchen
- Transform: Cook whatever the customers want right now

**dbt is the chef.** You write SQL recipes. dbt handles the kitchen logistics: timing, dependencies, quality checks.

### Why dbt Matters

**Before dbt**: You write SQL in your data warehouse by hand, nobody knows what depends on what, and if raw data changes, everything breaks.

**With dbt**:

- Transformations are version-controlled (like code)
- Dependencies are automatic (dbt figures out the order)
- You can test data (assert uniqueness, non-nullness, etc.)
- Documentation is generated automatically
- Everybody knows which tables are "gold standard"

---

## 🔍 How It Works: dbt Architecture

```mermaid
graph TB
    A["Raw Data<br/>(In PostgreSQL)"] -->|SELECT *| B["dbt Models<br/>(SQL files)"]
    B -->|ref()| C["Dependency<br/>Resolution"]
    C -->|Execute<br/>in Order| D["Run Models"]
    D -->|Create/Update| E["Transformed Tables<br/>(Staging)"]
    E -->|dbt ref()| F["Intermediate<br/>Models"]
    F -->|dbt ref()| G["Mart Models"]

    H["Tests<br/>(assertions)"] -->|Validate| G
    I["Documentation<br/>Generator"] -->|Reads SQL| J["dbt docs"]

    style A fill:#ffcccc
    style B fill:#ffeecc
    style C fill:#ffffcc
    style D fill:#eeffcc
    style E fill:#ccffcc
    style F fill:#ccffcc
    style G fill:#ccffcc
    style H fill:#ccffee
    style I fill:#e0ccff
```

### Key Concepts

**Model:** A .sql file that produces a table or view. It's just a SELECT statement.

**Materialization:** How the model is stored. Table (physical), View (virtual), Incremental (append-only), or Ephemeral (temporary).

**ref():** A function that automatically creates dependencies. `ref('my_model')` means "use the output of my_model".

**dbt run:** Execute all models in dependency order. dbt figures out what to run when.

**dbt test:** Check assertions like "no nulls in email" or "email is unique".

**dbt docs:** Auto-generate documentation by reading your SQL. No separate documentation to maintain!

---

## 🛠️ Step-by-Step Guide

### Step 1: Install dbt

```bash
# Create virtual environment
python3 -m venv dbt_env
source dbt_env/bin/activate  # On Windows: dbt_env\Scripts\activate

# Install dbt with PostgreSQL adapter
pip install dbt-core==1.6.0 dbt-postgres==1.6.0
```

### Step 2: Initialize a dbt Project

```bash
# Create a new dbt project interactively
dbt init my_first_project

# Answer prompts:
# adapter: postgres
# host: localhost
# user: postgres
# password: (your postgres password)
# port: 5432
# dbname: postgres
# schema: public
# threads: 4
# keepalives_idle: 0

# Navigate to project
cd my_first_project
```

### Step 3: Understand the Project Structure

```
my_first_project/
├── dbt_project.yml        # Project configuration
├── models/                # SQL transformation files
│   └── example/
│       ├── my_first_dbt_model.sql
│       └── employees.sql
├── tests/                 # YAML files with test assertions
│   └── assert_positive_id.sql
├── seeds/                 # CSV data for loading
├── macros/                # Reusable SQL functions
├── analysis/              # Exploratory queries (not materialized)
└── docs/                  # Documentation files
```

### Step 4: Write Your First Model

Create `models/stg_customers.sql`:

```sql
/* Staging model: clean raw customer data */
SELECT
    customer_id,
    first_name,
    last_name,
    email,
    created_at
FROM
    raw.customers
WHERE
    created_at >= CURRENT_DATE - INTERVAL '1 year'  /* Only recent customers */
    AND email IS NOT NULL  /* Require email to be valid */
```

### Step 5: Understand Materializations

In `dbt_project.yml`:

```yaml
models:
  my_project:
    # All models under staging are created as views (virtual)
    staging:
      +materialized: view # Doesn't take disk space, recalculated each time

    # All models under marts are created as tables (physical)
    marts:
      +materialized: table # Takes disk space, calculated once

    # Incremental: append-only (for immutable event logs)
    incremental_models:
      +materialized: incremental
```

### Step 6: Use ref() for Dependencies

```sql
/* This model depends on stg_customers */
SELECT
    c.customer_id,
    c.first_name,
    COUNT(o.order_id) as total_orders,
    SUM(o.amount) as lifetime_value
FROM
    {{ ref('stg_customers') }} c  /* dbt automatically depends on stg_customers */
LEFT JOIN
    {{ ref('stg_orders') }} o
    ON c.customer_id = o.customer_id
GROUP BY
    1, 2
ORDER BY
    lifetime_value DESC
```

dbt sees `ref('stg_customers')` and automatically:

1. Builds stg_customers first
2. Then builds this model
3. If stg_customers changes, this model reruns

### Step 7: Write Data Tests

Create `models/schema.yml`:

```yaml
version: 2

models:
  - name: stg_customers
    description: Cleaned customer data
    columns:
      - name: customer_id
        description: Unique customer ID
        tests:
          - unique # No duplicates allowed
          - not_null # Every row must have this

      - name: email
        tests:
          - unique # Email must be unique
          - not_null
```

### Step 8: Run dbt

```bash
# Create/update all models in dependency order
dbt run

# Run tests (assertions)
dbt test

# Generate documentation
dbt docs generate

# Launch documentation website
dbt docs serve  # Visit http://localhost:8001
```

---

## 💻 Code Examples

### Example 1: Complete Three-Layer Pipeline

```
models/
├── staging/
│   ├── stg_books.sql
│   └── stg_authors.sql
├── intermediate/
│   └── int_books_by_author.sql
└── marts/
    └── mart_top_authors.sql
```

**models/staging/stg_books.sql:**

```sql
-- Staging layer: clean raw books table (from Module 1-3)
{{
  config(
    materialized='view',  -- View (virtual, calculated on demand)
    unique_key='book_id'
  )
}}

SELECT
    id as book_id,
    TRIM(title) as title,  -- Remove extra spaces
    author_id,
    CAST(price as NUMERIC) as price,  -- Ensure numeric type
    COALESCE(rating, 0) as rating,  -- Replace nulls with 0
    isbn,
    created_at,
    CURRENT_TIMESTAMP as dbt_loaded_at  -- When dbt loaded this
FROM
    public.books
WHERE
    price > 0  -- Only valid prices
    AND deleted_at IS NULL  -- Exclude deleted records
```

**models/staging/stg_authors.sql:**

```sql
-- Staging layer: clean raw authors table
{{
  config(
    materialized='view',
    unique_key='author_id'
  )
}}

SELECT
    id as author_id,
    TRIM(name) as author_name,
    birth_year,
    country,
    created_at,
    CURRENT_TIMESTAMP as dbt_loaded_at
FROM
    public.authors
WHERE
    deleted_at IS NULL
```

**models/intermediate/int_books_by_author.sql:**

```sql
-- Intermediate: aggregate books by author
{{
  config(
    materialized='table',  -- Table (physical, persisted)
    unique_key=['author_id', 'author_name']
  )
}}

SELECT
    a.author_id,
    a.author_name,
    a.country,
    COUNT(b.book_id) as total_books,
    AVG(b.price) as avg_price,
    AVG(b.rating) as avg_rating,
    MIN(b.created_at) as first_book_date,
    MAX(b.created_at) as latest_book_date
FROM
    {{ ref('stg_authors') }} a  -- Depends on stg_authors
LEFT JOIN
    {{ ref('stg_books') }} b  -- Depends on stg_books
    ON a.author_id = b.author_id
GROUP BY
    1, 2, 3
```

**models/marts/mart_top_authors.sql:**

```sql
-- Mart: top authors for reporting (what business users query)
{{
  config(
    materialized='table',
    unique_key='rank'
  )
}}

SELECT
    ROW_NUMBER() OVER (ORDER BY avg_rating DESC) as rank,
    author_name,
    country,
    total_books,
    ROUND(avg_price::NUMERIC, 2) as avg_price,
    ROUND(avg_rating::NUMERIC, 2) as avg_rating
FROM
    {{ ref('int_books_by_author') }}  -- Depends on intermediate model
WHERE
    total_books >= 3  -- Only prolific authors
ORDER BY
    rank
LIMIT 20  -- Top 20 only
```

**models/schema.yml:**

```yaml
version: 2

models:
  - name: stg_books
    description: Cleaned books table
    columns:
      - name: book_id
        tests:
          - unique
          - not_null
      - name: price
        tests:
          - not_null

  - name: stg_authors
    description: Cleaned authors table
    columns:
      - name: author_id
        tests:
          - unique
          - not_null

  - name: int_books_by_author
    description: Books aggregated by author
    columns:
      - name: author_id
        tests:
          - unique
          - relationships:
              to: ref('stg_authors')
              field: author_id

  - name: mart_top_authors
    description: Top 20 authors by rating
```

### Example 2: Incremental Model (Event Log)

```sql
-- Incremental model: append-only events table
{{
  config(
    materialized='incremental',
    unique_key='event_id',
    on_schema_change='fail'
  )
}}

SELECT
    event_id,
    user_id,
    event_type,
    event_timestamp,
    CURRENT_TIMESTAMP as processed_at
FROM
    raw.events

{% if execute %}
  -- Only process events newer than last run
  {% if var('start_time', None) %}
    WHERE event_timestamp > '{{ var("start_time") }}'
  {% endif %}
{% endif %}
```

### Example 3: Custom Test

Create `tests/assert_price_positive.sql`:

```sql
-- Assert that all book prices are positive
SELECT
    book_id,
    price
FROM
    {{ ref('stg_books') }}
WHERE
    price <= 0 OR price IS NULL
HAVING
    COUNT(*) > 0
```

If this query returns any rows, the test fails.

---

## ⚠️ Common Mistakes

### Mistake 1: Circular Dependencies

**WRONG:**

```sql
-- Model A references Model B
SELECT * FROM {{ ref('model_b') }} ...

-- Model B references Model A (CIRCULAR!)
SELECT * FROM {{ ref('model_a') }} ...
```

**RIGHT:**

```
Think in layers:
1. Staging (cleans raw data, no dependencies)
2. Intermediate (depends on staging)
3. Marts (depends on intermediate)

Never have Model A → B → A
```

### Mistake 2: Materializing Everything as Tables

**WRONG:**

```yaml
models:
  my_project:
    +materialized: table # All models become tables!
    # Takes disk space even if only one table uses them
```

**RIGHT:**

```yaml
models:
  my_project:
    staging:
      +materialized: view # Staging = ephemeral transformations
    intermediate:
      +materialized: view # Intermediate = not often queried directly
    marts:
      +materialized: table # Marts = physical tables for reporting
```

### Mistake 3: Not Testing Data

**WRONG:**

```yaml
# No tests defined
models:
  - name: my_model
    description: Some model
    # That's it! No assertions!
```

**RIGHT:**

```yaml
models:
  - name: my_model
    description: Some model
    columns:
      - name: id
        tests:
          - unique
          - not_null
      - name: email
        tests:
          - unique
```

---

## ✅ Exercises

### Easy: First Model

Create a staging model that:

1. Selects all columns from a raw table
2. Removes rows where a key column is NULL
3. Materializes as a view
4. Has a unique test on the ID column

Expected: `SELECT * FROM raw_table WHERE id IS NOT NULL`

### Medium: Multi-Layer Pipeline

Create 3 models:

1. `stg_products`: Clean raw products
2. `int_products_by_category`: Aggregate by category
3. `mart_top_products`: Top 10 products by sales

With tests and proper materializations.

### Hard: Incremental Model

Create an incremental model that:

1. Loads event data
2. Only processes new events since last run
3. Has tests for uniqueness
4. Is materialized as incremental

Expected: `dbt run` on day 1 loads 1000 events, day 2 loads only 100 new events.

---

## 🏗️ Mini Project: Books Data Mart

Build a complete dbt project with models for the books database from Phase 1.

### Requirements

1. **Staging models** (views):
   - `stg_books.sql` - clean books table
   - `stg_authors.sql` - clean authors table

2. **Intermediate models** (views):
   - `int_books_by_author.sql` - books aggregated by author
   - `int_books_by_category.sql` - books aggregated by category

3. **Mart models** (tables):
   - `mart_top_authors.sql` - top 10 authors by rating
   - `mart_popular_books.sql` - top 20 books by rating/price ratio

4. **Tests:**
   - Unique tests on all IDs
   - Not-null tests on critical columns
   - Relationship tests (book.author_id → author.author_id)

5. **Documentation:**
   - Description for each model
   - Tests documented in schema.yml

### Step 1: Initialize Project

```bash
dbt init books_project
cd books_project
```

### Step 2: Create Staging Models

**models/staging/stg_books.sql:**

```sql
{{
  config(
    materialized='view',
    unique_key='book_id'
  )
}}

SELECT
    id as book_id,
    TRIM(title) as title,
    author_id,
    CAST(price as NUMERIC(8,2)) as price,
    COALESCE(rating, 0) as rating,
    COALESCE(pages, 0) as pages,
    isbn,
    created_at
FROM
    public.books
WHERE
    price > 0
    AND rating >= 0
    AND rating <= 5
```

**models/staging/stg_authors.sql:**

```sql
{{
  config(
    materialized='view',
    unique_key='author_id'
  )
}}

SELECT
    id as author_id,
    TRIM(name) as author_name,
    TRIM(COALESCE(country, 'Unknown')) as country,
    birth_year
FROM
    public.authors
WHERE
    id IS NOT NULL
```

### Step 3: Create Intermediate Models

**models/intermediate/int_books_by_author.sql:**

```sql
{{
  config(
    materialized='view',
    unique_key=['author_id', 'author_name']
  )
}}

SELECT
    a.author_id,
    a.author_name,
    a.country,
    COUNT(b.book_id) as total_books,
    AVG(b.price) as avg_price,
    AVG(b.rating) as avg_rating,
    MAX(b.rating) as max_rating,
    MIN(b.rating) as min_rating
FROM
    {{ ref('stg_authors') }} a
LEFT JOIN
    {{ ref('stg_books') }} b
    ON a.author_id = b.author_id
GROUP BY
    1, 2, 3
```

**models/intermediate/int_books_by_category.sql:**

```sql
{{
  config(
    materialized='view'
  )
}}

SELECT
    bc.category_id,
    c.name as category_name,
    COUNT(DISTINCT b.book_id) as book_count,
    AVG(b.price) as avg_price,
    AVG(b.rating) as avg_rating
FROM
    public.book_categories bc
INNER JOIN
    public.categories c ON bc.category_id = c.id
LEFT JOIN
    {{ ref('stg_books') }} b ON bc.book_id = b.book_id
GROUP BY
    1, 2
```

### Step 4: Create Mart Models

**models/marts/mart_top_authors.sql:**

```sql
{{
  config(
    materialized='table',
    unique_key='rank'
  )
}}

SELECT
    ROW_NUMBER() OVER (ORDER BY avg_rating DESC, total_books DESC) as rank,
    author_name,
    country,
    total_books,
    ROUND(avg_price::NUMERIC, 2) as avg_price,
    ROUND(avg_rating::NUMERIC, 2) as avg_rating
FROM
    {{ ref('int_books_by_author') }}
WHERE
    total_books >= 1
LIMIT 10
```

**models/marts/mart_popular_books.sql:**

```sql
{{
  config(
    materialized='table',
    unique_key='rank'
  )
}}

SELECT
    ROW_NUMBER() OVER (ORDER BY popularity_score DESC) as rank,
    title,
    author_name,
    price,
    rating,
    (rating * price) as popularity_score
FROM
    {{ ref('stg_books') }} b
LEFT JOIN
    {{ ref('stg_authors') }} a ON b.author_id = a.author_id
WHERE
    price > 0
ORDER BY
    popularity_score DESC
LIMIT 20
```

### Step 5: Add Tests

**models/schema.yml:**

```yaml
version: 2

models:
  - name: stg_books
    description: Cleaned books from raw table
    columns:
      - name: book_id
        description: Unique book identifier
        tests:
          - unique
          - not_null
      - name: title
        tests:
          - not_null
      - name: price
        tests:
          - not_null

  - name: stg_authors
    description: Cleaned authors from raw table
    columns:
      - name: author_id
        tests:
          - unique
          - not_null

  - name: int_books_by_author
    columns:
      - name: author_id
        tests:
          - relationships:
              to: ref('stg_authors')
              field: author_id

  - name: mart_top_authors
    description: Top 10 authors by rating
    columns:
      - name: rank
        tests:
          - unique
          - not_null
```

### Step 6: Run dbt

```bash
# Run all models
dbt run

# Run tests
dbt test

# Generate docs
dbt docs generate
dbt docs serve

# View documentation at http://localhost:8001
```

---

## 🔗 What's Next

Your data is now clean, tested, and documented!

- **Module 2-3 (Validation)**: Ensure quality at every step
- **Module 2-4 (Database ETL)**: Load data properly
- **Module 2-5 (Orchestration)**: Tie it all together with Airflow

dbt is the SQL engineer. Let it do the work.

---

## 📚 Summary

In this module, you learned:

1. ✅ **ELT pattern** – Load first, transform later
2. ✅ **dbt installation** – Set up locally
3. ✅ **Project structure** – Models, tests, docs
4. ✅ **Writing models** – SQL SELECT statements
5. ✅ **ref() function** – Automatic dependencies
6. ✅ **Materializations** – View vs Table
7. ✅ **Testing** – Data assertions
8. ✅ **Documentation** – Auto-generated
9. ✅ **Three-layer pipeline** – Staging → Intermediate → Marts
10. ✅ **Running dbt** – Execute, test, generate docs

dbt transforms your data warehouse into a version-controlled codebase. This is professional data engineering.

---

**Congratulations! Your data transformations are now automated and tested. 🎉**
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
