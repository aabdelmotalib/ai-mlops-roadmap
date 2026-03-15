---
tags:
  - Intermediate
  - Phase 5
---

# Module 1: SQL for Analytics

> **Phase 5 — Analytics & Monitoring**

---

## 🎯 What You Will Learn

- The difference between writing SQL to _run_ an app vs writing SQL to _understand_ data
- How to summarise millions of rows into meaningful numbers using aggregations
- How to filter those summaries with `HAVING`
- How window functions work — and why they are one of the most powerful tools in analytics
- How to write clean, readable queries using CTEs
- How to work with dates, strings, and pivoted data
- How to read an `EXPLAIN ANALYZE` output and spot slow queries

---

## 🧠 Concept Explained

Imagine you work at a bookshop. Every time someone buys a book, a receipt is printed and filed in a drawer. That drawer is your **operational database** — it records every single transaction so the shop keeps running.

Now imagine your manager walks in at the end of the month and says: _"Which genre made us the most money? Which authors are trending? Are prices going up?"_

To answer those questions, you don't read every receipt one by one. You stack them up, sort them, count them, and summarise them. **That is analytical SQL.**

The same database, the same tables — but a completely different way of thinking about the queries.

!!! note "Operational vs Analytical SQL" - **Operational SQL**: `SELECT * FROM orders WHERE order_id = 123` — fetch one specific thing fast - **Analytical SQL**: `SELECT genre, AVG(price) FROM books GROUP BY genre` — summarise everything to find patterns

---

## 🔍 How It Works

Here is the dataset we will use throughout this module — the `books` table built in Phase 1 and stored in PostgreSQL.

```sql
-- The books table structure we built in Phase 1
CREATE TABLE books (
    id          SERIAL PRIMARY KEY,
    title       TEXT NOT NULL,
    author      TEXT NOT NULL,
    genre       TEXT,
    price       NUMERIC(6,2),
    rating      NUMERIC(3,1),
    in_stock    BOOLEAN,
    scraped_at  TIMESTAMP DEFAULT NOW()
);
```

And a `weather` table from Phase 1 as well:

```sql
CREATE TABLE weather_measurements (
    id          SERIAL PRIMARY KEY,
    city        TEXT NOT NULL,
    temperature NUMERIC(5,2),
    humidity    INTEGER,
    recorded_at TIMESTAMP DEFAULT NOW()
);
```

Here is the overall flow of analytical SQL:

```
Raw table (millions of rows)
        │
        ▼
   Filter rows        ← WHERE clause
        │
        ▼
   Group rows         ← GROUP BY clause
        │
        ▼
   Aggregate groups   ← COUNT, SUM, AVG, MIN, MAX
        │
        ▼
   Filter groups      ← HAVING clause
        │
        ▼
   Sort results       ← ORDER BY clause
        │
        ▼
   Limit output       ← LIMIT clause
```

---

## 🛠️ Step-by-Step Guide

### Step 1 — Connect to your PostgreSQL database

```bash
psql -U postgres -d books_db   # connect to the books database
```

### Step 2 — Insert some sample data to work with

```sql
-- Insert sample books so we have data to analyse
INSERT INTO books (title, author, genre, price, rating, in_stock) VALUES
('Clean Code',            'Robert Martin',  'Technology', 29.99, 4.5, true),
('The Pragmatic Programmer', 'David Thomas', 'Technology', 34.99, 4.7, true),
('Dune',                  'Frank Herbert',  'Science Fiction', 12.99, 4.8, true),
('Foundation',            'Isaac Asimov',   'Science Fiction', 9.99,  4.6, false),
('1984',                  'George Orwell',  'Fiction',    8.99,  4.9, true),
('Animal Farm',           'George Orwell',  'Fiction',    6.99,  4.7, true),
('Sapiens',               'Yuval Harari',   'History',    15.99, 4.4, true),
('Homo Deus',             'Yuval Harari',   'History',    14.99, 4.2, false),
('The Hobbit',            'J.R.R. Tolkien', 'Fantasy',    11.99, 4.8, true),
('Lord of the Rings',     'J.R.R. Tolkien', 'Fantasy',    24.99, 4.9, true);
```

### Step 3 — Run your first aggregation

### Step 4 — Add window functions

### Step 5 — Write CTEs for complex queries

### Step 6 — Use date and string functions

### Step 7 — Build a pivot with CASE WHEN

### Step 8 — Run EXPLAIN ANALYZE on a slow query

---

## 💻 Code Examples

### Aggregations: GROUP BY, COUNT, SUM, AVG, MIN, MAX

```sql
-- Count how many books exist per genre
-- GROUP BY collapses all rows with the same genre into one row
SELECT
    genre,                    -- the column we are grouping by
    COUNT(*)        AS total_books,   -- count every row in this group
    AVG(price)      AS avg_price,     -- average price within this group
    MIN(price)      AS cheapest,      -- cheapest book in this genre
    MAX(price)      AS most_expensive,-- most expensive book in this genre
    SUM(price)      AS total_value,   -- sum of all prices in this genre
    ROUND(AVG(rating), 2) AS avg_rating -- average rating, rounded to 2 decimals
FROM books
GROUP BY genre          -- one row per unique genre value
ORDER BY avg_rating DESC; -- show highest-rated genres first
```

```
-- Expected output:
   genre        | total_books | avg_price | cheapest | most_expensive | total_value | avg_rating
----------------+-------------+-----------+----------+----------------+-------------+------------
 Fiction        |           2 |      7.99 |     6.99 |           8.99 |       15.98 |       4.80
 Fantasy        |           2 |     18.49 |    11.99 |          24.99 |       36.98 |       4.85
 Science Fiction|           2 |     11.49 |     9.99 |          12.99 |       22.98 |       4.70
 Technology     |           2 |     32.49 |    29.99 |          34.99 |       64.98 |       4.60
 History        |           2 |     15.49 |    14.99 |          15.99 |       30.98 |       4.30
```

### Filtering aggregations: HAVING

```sql
-- HAVING filters AFTER grouping — WHERE filters BEFORE grouping
-- Use HAVING when your condition involves an aggregated value

-- Find genres where the average price is above $15
SELECT
    genre,
    ROUND(AVG(price), 2) AS avg_price,
    COUNT(*)             AS book_count
FROM books
GROUP BY genre
HAVING AVG(price) > 15      -- only keep groups where avg price > 15
ORDER BY avg_price DESC;

-- WHY HAVING not WHERE?
-- WHERE price > 15 would remove individual cheap books BEFORE grouping
-- HAVING AVG(price) > 15 checks the average AFTER the group is formed
```

```
-- Expected output:
    genre    | avg_price | book_count
-------------+-----------+------------
 Technology  |     32.49 |          2
 Fantasy     |     18.49 |          2
 History     |     15.49 |          2
```

---

### Window Functions

Window functions are the most powerful analytical SQL tool. They let you compute values **across a set of rows related to the current row** — without collapsing those rows into groups.

!!! tip "The key mental model"
`GROUP BY` collapses 10 rows into 1. A window function keeps all 10 rows but **adds a new calculated column** to each one.

#### ROW_NUMBER

```sql
-- Assign a unique sequential number to each book within its genre
-- ordered by price descending (most expensive = rank 1)
SELECT
    title,
    genre,
    price,
    ROW_NUMBER() OVER (
        PARTITION BY genre      -- restart numbering for each genre
        ORDER BY price DESC     -- within each genre, number by price high→low
    ) AS price_rank
FROM books
ORDER BY genre, price_rank;
```

**What ROW_NUMBER does — ASCII before/after:**

```
BEFORE (raw rows):                    AFTER (with ROW_NUMBER):
┌─────────────────────┬─────────┬───────┐   ┌─────────────────────┬─────────┬───────┬────────────┐
│ title               │ genre   │ price │   │ title               │ genre   │ price │ price_rank │
├─────────────────────┼─────────┼───────┤   ├─────────────────────┼─────────┼───────┼────────────┤
│ Clean Code          │ Tech    │ 29.99 │   │ Pragmatic Programmer│ Tech    │ 34.99 │     1      │
│ Pragmatic Programmer│ Tech    │ 34.99 │   │ Clean Code          │ Tech    │ 29.99 │     2      │
│ The Hobbit          │ Fantasy │ 11.99 │   │ Lord of the Rings   │ Fantasy │ 24.99 │     1      │
│ Lord of the Rings   │ Fantasy │ 24.99 │   │ The Hobbit          │ Fantasy │ 11.99 │     2      │
└─────────────────────┴─────────┴───────┘   └─────────────────────┴─────────┴───────┴────────────┘
                                                         ↑
                                              Rows are NOT collapsed.
                                              Every row kept, new column added.
```

#### RANK and DENSE_RANK

```sql
-- RANK: same value = same rank, but gaps appear after ties
-- DENSE_RANK: same value = same rank, NO gaps after ties

SELECT
    title,
    genre,
    rating,
    RANK()       OVER (ORDER BY rating DESC) AS rank_with_gaps,
    DENSE_RANK() OVER (ORDER BY rating DESC) AS rank_no_gaps
FROM books
ORDER BY rating DESC;
```

**ASCII before/after — RANK vs DENSE_RANK:**

```
BEFORE:                           AFTER:
┌─────────────────┬────────┐      ┌─────────────────┬────────┬────────────────┬──────────────┐
│ title           │ rating │      │ title           │ rating │ rank_with_gaps │ rank_no_gaps │
├─────────────────┼────────┤      ├─────────────────┼────────┼────────────────┼──────────────┤
│ Lord of Rings   │   4.9  │      │ Lord of Rings   │   4.9  │       1        │      1       │
│ 1984            │   4.9  │      │ 1984            │   4.9  │       1        │      1       │
│ The Hobbit      │   4.8  │      │ The Hobbit      │   4.8  │       3 ←gap   │      2 ←no gap│
│ Dune            │   4.8  │      │ Dune            │   4.8  │       3        │      2       │
│ Pragmatic Prog. │   4.7  │      │ Pragmatic Prog. │   4.7  │       5 ←gap   │      3       │
└─────────────────┴────────┘      └─────────────────┴────────┴────────────────┴──────────────┘
```

#### LAG and LEAD

```sql
-- LAG: look at the PREVIOUS row's value
-- LEAD: look at the NEXT row's value
-- Useful for comparing a value to what came before or after

-- Show each book's price and the price of the previous book (by id)
SELECT
    id,
    title,
    price,
    LAG(price)  OVER (ORDER BY id) AS prev_book_price, -- price of previous row
    LEAD(price) OVER (ORDER BY id) AS next_book_price, -- price of next row
    price - LAG(price) OVER (ORDER BY id) AS price_diff -- difference from previous
FROM books
ORDER BY id;
```

**ASCII before/after — LAG:**

```
BEFORE:                    AFTER (LAG added):
┌────┬────────┬───────┐    ┌────┬────────┬───────┬─────────────────┬────────────┐
│ id │ title  │ price │    │ id │ title  │ price │ prev_book_price │ price_diff │
├────┼────────┼───────┤    ├────┼────────┼───────┼─────────────────┼────────────┤
│  1 │ Book A │ 29.99 │    │  1 │ Book A │ 29.99 │      NULL       │    NULL    │
│  2 │ Book B │ 34.99 │    │  2 │ Book B │ 34.99 │      29.99      │   +5.00    │
│  3 │ Book C │ 12.99 │    │  3 │ Book C │ 12.99 │      34.99      │  -22.00    │
│  4 │ Book D │  9.99 │    │  4 │ Book D │  9.99 │      12.99      │   -3.00    │
└────┴────────┴───────┘    └────┴────────┴───────┴─────────────────┴────────────┘
```

#### SUM OVER PARTITION (Running Total)

```sql
-- Running total of prices within each genre
-- Each row shows: how much have we spent SO FAR in this genre?
SELECT
    title,
    genre,
    price,
    SUM(price) OVER (
        PARTITION BY genre      -- reset the running total per genre
        ORDER BY id             -- accumulate in order of insertion
    ) AS running_total_per_genre
FROM books
ORDER BY genre, id;
```

**ASCII before/after — Running SUM:**

```
BEFORE:                              AFTER (running total added):
┌───────────────┬─────────┬───────┐  ┌───────────────┬─────────┬───────┬──────────────────────────┐
│ title         │ genre   │ price │  │ title         │ genre   │ price │ running_total_per_genre  │
├───────────────┼─────────┼───────┤  ├───────────────┼─────────┼───────┼──────────────────────────┤
│ 1984          │ Fiction │  8.99 │  │ 1984          │ Fiction │  8.99 │          8.99            │
│ Animal Farm   │ Fiction │  6.99 │  │ Animal Farm   │ Fiction │  6.99 │         15.98 ← 8.99+6.99│
│ The Hobbit    │ Fantasy │ 11.99 │  │ The Hobbit    │ Fantasy │ 11.99 │         11.99 ← resets!  │
│ Lord of Rings │ Fantasy │ 24.99 │  │ Lord of Rings │ Fantasy │ 24.99 │         36.98            │
└───────────────┴─────────┴───────┘  └───────────────┴─────────┴───────┴──────────────────────────┘
```

---

### CTEs — Common Table Expressions

```sql
-- A CTE is like giving a name to a subquery so you can reference it later
-- Think of it as creating a temporary named result set

-- WITHOUT CTE (hard to read):
SELECT author, total_books, avg_price
FROM (
    SELECT author, COUNT(*) AS total_books, AVG(price) AS avg_price
    FROM books GROUP BY author
) AS author_stats
WHERE total_books > 1
ORDER BY avg_price DESC;

-- WITH CTE (clean and readable):
WITH author_stats AS (
    -- Step 1: calculate per-author statistics
    SELECT
        author,
        COUNT(*)        AS total_books,   -- how many books per author
        ROUND(AVG(price), 2) AS avg_price,-- average price per author
        ROUND(AVG(rating), 2) AS avg_rating -- average rating per author
    FROM books
    GROUP BY author
)
-- Step 2: now use the CTE result like a normal table
SELECT
    author,
    total_books,
    avg_price,
    avg_rating
FROM author_stats
WHERE total_books > 1         -- only authors with more than 1 book
ORDER BY avg_rating DESC;     -- best-rated authors first
```

```
-- Expected output:
     author      | total_books | avg_price | avg_rating
-----------------+-------------+-----------+------------
 J.R.R. Tolkien  |           2 |     18.49 |       4.85
 George Orwell   |           2 |      7.99 |       4.80
 Yuval Harari    |           2 |     15.49 |       4.30
```

#### Chaining multiple CTEs

```sql
-- CTEs can reference each other — like steps in a recipe
WITH
-- Step 1: get genre-level stats
genre_stats AS (
    SELECT
        genre,
        ROUND(AVG(price), 2)  AS avg_price,
        ROUND(AVG(rating), 2) AS avg_rating,
        COUNT(*)              AS book_count
    FROM books
    GROUP BY genre
),
-- Step 2: find which genres are "premium" (avg price above overall average)
overall_avg AS (
    SELECT ROUND(AVG(price), 2) AS overall_avg_price
    FROM books
),
-- Step 3: tag each genre as premium or standard
genre_tier AS (
    SELECT
        g.genre,
        g.avg_price,
        g.avg_rating,
        g.book_count,
        CASE
            WHEN g.avg_price > o.overall_avg_price THEN 'Premium'  -- above average
            ELSE 'Standard'                                         -- at or below average
        END AS price_tier
    FROM genre_stats g
    CROSS JOIN overall_avg o   -- join every genre row with the single average row
)
-- Final query: use the built-up result
SELECT *
FROM genre_tier
ORDER BY avg_rating DESC;
```

---

### Date and Time Functions

```sql
-- DATE_TRUNC: round a timestamp down to a time unit
-- Useful for grouping data by day, week, month, year

-- How many books were scraped each day?
SELECT
    DATE_TRUNC('day', scraped_at) AS scrape_day, -- truncate to day precision
    COUNT(*)                      AS books_scraped
FROM books
GROUP BY DATE_TRUNC('day', scraped_at)
ORDER BY scrape_day DESC;

-- EXTRACT: pull out one component of a timestamp
-- Useful for "which hour had the most traffic?" type questions
SELECT
    EXTRACT(YEAR  FROM scraped_at) AS year,   -- get just the year number
    EXTRACT(MONTH FROM scraped_at) AS month,  -- get just the month number
    EXTRACT(DOW   FROM scraped_at) AS day_of_week, -- 0=Sunday, 6=Saturday
    COUNT(*) AS count
FROM books
GROUP BY year, month, day_of_week
ORDER BY year, month;

-- AGE: calculate the difference between two timestamps
SELECT
    title,
    scraped_at,
    AGE(NOW(), scraped_at) AS time_since_scrape  -- how long ago was this scraped?
FROM books
ORDER BY scraped_at DESC
LIMIT 5;

-- Weather data: average temperature per month
SELECT
    DATE_TRUNC('month', recorded_at) AS month,    -- group by month
    city,
    ROUND(AVG(temperature), 1)       AS avg_temp, -- average temp that month
    COUNT(*)                         AS readings  -- how many readings that month
FROM weather_measurements
GROUP BY DATE_TRUNC('month', recorded_at), city
ORDER BY month DESC, city;
```

---

### String Functions

```sql
-- CONCAT: join strings together
SELECT
    CONCAT(author, ' — ', title) AS full_label  -- combine author and title
FROM books
ORDER BY author;

-- UPPER / LOWER: change case
SELECT
    UPPER(genre) AS genre_upper,   -- TECHNOLOGY, FICTION etc
    LOWER(title) AS title_lower    -- the hobbit, dune etc
FROM books
LIMIT 5;

-- SPLIT_PART: split a string by a delimiter and get one part
-- Useful for extracting first/last name from a full name
SELECT
    author,
    SPLIT_PART(author, ' ', 1) AS first_name,  -- everything before first space
    SPLIT_PART(author, ' ', 2) AS last_name    -- everything after first space
FROM books;

-- LIKE: pattern matching — % means "anything"
SELECT title, author
FROM books
WHERE title  LIKE '%the%'    -- title contains "the" anywhere
   OR author LIKE 'George%'; -- author name starts with "George"

-- LENGTH: how long is a string?
SELECT
    title,
    LENGTH(title) AS title_length   -- number of characters in title
FROM books
ORDER BY title_length DESC          -- longest titles first
LIMIT 5;
```

---

### Pivoting with CASE WHEN

```sql
-- A pivot turns row values into column headers
-- SQL doesn't have a native PIVOT — we use CASE WHEN to fake it

-- BEFORE pivot: genres as rows
-- genre       | book_count
-- ------------|------------
-- Fiction     |    2
-- Fantasy     |    2
-- Technology  |    2

-- AFTER pivot: genres as columns
-- fiction_count | fantasy_count | technology_count
-- --------------|---------------|------------------
--       2       |       2       |        2

SELECT
    -- Each CASE WHEN counts books only for that genre — 0 for all others
    SUM(CASE WHEN genre = 'Fiction'      THEN 1 ELSE 0 END) AS fiction_count,
    SUM(CASE WHEN genre = 'Fantasy'      THEN 1 ELSE 0 END) AS fantasy_count,
    SUM(CASE WHEN genre = 'Technology'   THEN 1 ELSE 0 END) AS technology_count,
    SUM(CASE WHEN genre = 'Science Fiction' THEN 1 ELSE 0 END) AS scifi_count,
    SUM(CASE WHEN genre = 'History'      THEN 1 ELSE 0 END) AS history_count
FROM books;

-- More useful pivot: average price per genre, in stock vs out of stock
SELECT
    genre,
    ROUND(AVG(CASE WHEN in_stock = true  THEN price END), 2) AS avg_price_in_stock,
    ROUND(AVG(CASE WHEN in_stock = false THEN price END), 2) AS avg_price_out_of_stock,
    COUNT(CASE WHEN in_stock = true  THEN 1 END)             AS in_stock_count,
    COUNT(CASE WHEN in_stock = false THEN 1 END)             AS out_of_stock_count
FROM books
GROUP BY genre
ORDER BY genre;
```

---

### Query Performance: EXPLAIN ANALYZE

```sql
-- EXPLAIN ANALYZE runs the query and shows you:
-- 1. What plan PostgreSQL chose
-- 2. How long each step actually took
-- 3. How many rows were processed

EXPLAIN ANALYZE
SELECT genre, AVG(price)
FROM books
GROUP BY genre
ORDER BY AVG(price) DESC;
```

```
-- Expected output (read from bottom up):
QUERY PLAN
─────────────────────────────────────────────────────────────────────────
Sort  (cost=1.24..1.26 rows=5 width=36) (actual time=0.05..0.05 rows=5)
  Sort Key: (avg(price)) DESC
  ->  HashAggregate  (cost=1.12..1.17 rows=5 width=36) (actual time=0.04..0.04 rows=5)
        Group Key: genre
        ->  Seq Scan on books  (cost=0.00..1.10 rows=10) (actual time=0.01..0.02 rows=10)
Planning Time: 0.08 ms
Execution Time: 0.12 ms
```

!!! tip "What to look for in EXPLAIN ANALYZE" - **Seq Scan** on a large table = no index being used = potentially slow - **Index Scan** = index is being used = fast - **actual time** much higher than **cost** estimate = statistics are stale, run `ANALYZE books` - **rows** estimate very different from **actual rows** = poor statistics

```sql
-- Add an index to speed up genre queries
CREATE INDEX idx_books_genre ON books(genre);   -- creates an index on the genre column

-- Now run EXPLAIN ANALYZE again — should show Index Scan instead of Seq Scan
EXPLAIN ANALYZE
SELECT * FROM books WHERE genre = 'Fantasy';
```

---

## ⚠️ Common Mistakes

**Mistake 1: Using WHERE instead of HAVING to filter aggregates**

```sql
-- WRONG: this errors because AVG(price) doesn't exist yet at WHERE stage
SELECT genre, AVG(price)
FROM books
WHERE AVG(price) > 15       -- ❌ ERROR: aggregate functions not allowed in WHERE
GROUP BY genre;

-- CORRECT: HAVING runs after GROUP BY, so aggregates are available
SELECT genre, AVG(price)
FROM books
GROUP BY genre
HAVING AVG(price) > 15;     -- ✅ works perfectly
```

**Mistake 2: Selecting a non-aggregated column not in GROUP BY**

```sql
-- WRONG: title is not in GROUP BY and not aggregated
SELECT genre, title, COUNT(*)   -- ❌ ERROR: title must appear in GROUP BY
FROM books
GROUP BY genre;

-- CORRECT: either add title to GROUP BY or aggregate it
SELECT genre, COUNT(*), MIN(title) AS sample_title  -- ✅
FROM books
GROUP BY genre;
```

**Mistake 3: Confusing ROW_NUMBER with RANK**

```sql
-- ROW_NUMBER always gives unique numbers — no ties
-- RANK gives the same number for ties but skips numbers after
-- DENSE_RANK gives the same number for ties and never skips

-- If two books both have rating 4.9:
-- ROW_NUMBER: 1, 2        (always unique)
-- RANK:       1, 1, 3     (skips 2 because two rows tied at 1)
-- DENSE_RANK: 1, 1, 2     (never skips)
```

---

## ✅ Exercises

**Exercise 1 — Easy**
Write a query that returns the total number of books and the average rating for each author. Only show authors who have written more than 1 book. Order by average rating descending.

**Exercise 2 — Medium**
Using a window function, add a column to the books table showing each book's price as a percentage of the total price of all books in its genre. Round to 2 decimal places.

**Exercise 3 — Hard**
Write a CTE-based query that:

1. Calculates the average rating per genre
2. Ranks genres by average rating using DENSE_RANK
3. For each book, shows its genre's rank alongside the book's own rating
4. Only returns books whose personal rating is above their genre's average

---

## 🏗️ Mini Project — 5 Analytical SQL Queries

Write these 5 queries against your books database. Each answers a real business question.

```sql
-- Query 1: Top 5 authors by average rating
-- Business question: "Who are our best-reviewed authors?"
WITH author_ratings AS (
    SELECT
        author,
        ROUND(AVG(rating), 2) AS avg_rating,
        COUNT(*)              AS book_count
    FROM books
    GROUP BY author
    HAVING COUNT(*) >= 1          -- include all authors
)
SELECT
    author,
    avg_rating,
    book_count,
    RANK() OVER (ORDER BY avg_rating DESC) AS rating_rank  -- rank by rating
FROM author_ratings
ORDER BY rating_rank
LIMIT 5;                          -- top 5 only

-- Query 2: Price trend by genre (in stock vs out of stock)
-- Business question: "Are our most expensive books going out of stock?"
SELECT
    genre,
    ROUND(AVG(CASE WHEN in_stock THEN price END), 2) AS avg_price_available,
    ROUND(AVG(CASE WHEN NOT in_stock THEN price END), 2) AS avg_price_unavailable,
    COUNT(CASE WHEN in_stock THEN 1 END)     AS available_count,
    COUNT(CASE WHEN NOT in_stock THEN 1 END) AS unavailable_count
FROM books
GROUP BY genre
ORDER BY avg_price_available DESC NULLS LAST; -- most expensive genres first

-- Query 3: Books ranked within their genre by price
-- Business question: "What is the most expensive book in each genre?"
SELECT
    genre,
    title,
    price,
    ROW_NUMBER() OVER (
        PARTITION BY genre
        ORDER BY price DESC
    ) AS price_rank_in_genre
FROM books
ORDER BY genre, price_rank_in_genre;

-- Query 4: Running total of inventory value per genre
-- Business question: "How much total value do we hold per genre, cumulatively?"
SELECT
    genre,
    title,
    price,
    SUM(price) OVER (
        PARTITION BY genre
        ORDER BY price DESC
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW  -- include all rows up to this one
    ) AS cumulative_value
FROM books
ORDER BY genre, price DESC;

-- Query 5: Books with above-average rating in their genre
-- Business question: "Which individual books outperform their genre average?"
WITH genre_avg AS (
    SELECT genre, AVG(rating) AS genre_avg_rating
    FROM books
    GROUP BY genre
)
SELECT
    b.title,
    b.author,
    b.genre,
    b.rating                          AS book_rating,
    ROUND(g.genre_avg_rating, 2)      AS genre_avg,
    ROUND(b.rating - g.genre_avg_rating, 2) AS above_average_by
FROM books b
JOIN genre_avg g ON b.genre = g.genre          -- join each book to its genre average
WHERE b.rating > g.genre_avg_rating            -- only books above their genre average
ORDER BY above_average_by DESC;                -- biggest overperformers first
```

---

## 🔗 What's Next

In **Module 5-2: Building Dashboards**, you will take these SQL queries and turn them into visual charts and interactive dashboards using Python, FastAPI, and Metabase. The queries you wrote here are the backbone of every dashboard panel.
