---
tags:
  - Intermediate
  - Phase 5
---

# Module 2: Building Dashboards

> **Phase 5 — Analytics & Monitoring**

---

## 🎯 What You Will Learn

- What makes a dashboard actually useful vs just pretty
- How to create charts in Python using matplotlib and seaborn
- How to build interactive charts with plotly express
- How to serve a live dashboard using FastAPI and Jinja2 templates
- How to set up Metabase with Docker and connect it to PostgreSQL
- When to use Metabase vs Grafana

---

## 🧠 Concept Explained

Imagine you are the manager of a bookshop. Every morning you walk in and you want to answer three questions instantly: _Are sales up or down? Which genre is moving? Is anything broken?_

You don't want to open a terminal and write SQL. You want to glance at a screen and know. **That is what a dashboard does.**

A dashboard is a live window into your data. It turns the SQL queries you wrote in Module 5-1 into charts, numbers, and tables that update automatically — so humans can understand data at a glance instead of reading rows and columns.

!!! note "What makes a good dashboard" - **One question per panel** — each chart answers exactly one question - **Most important metric first** — top-left is where eyes go first - **No decoration** — every element must carry information - **Right chart for the data** — bar for categories, line for time, scatter for relationships

---

## 🔍 How It Works

There are three levels of dashboard tooling, from simple to powerful:

```
Level 1: Python charts (matplotlib / seaborn / plotly)
         ↓ You write Python, you get a chart image or HTML file
         ↓ Good for: reports, notebooks, one-off analysis

Level 2: FastAPI + Jinja2 web dashboard
         ↓ You build a small web server that queries PostgreSQL
         ↓ and renders charts in a browser page
         ↓ Good for: custom dashboards you control completely

Level 3: Metabase or Grafana
         ↓ A full dashboard application — no code needed for charts
         ↓ Connect to your database, click to build panels
         ↓ Good for: team dashboards, non-technical users
```

---

## 🛠️ Step-by-Step Guide

### Step 1 — Install Python visualisation libraries

```bash
pip install matplotlib seaborn plotly pandas psycopg2-binary   # install all viz libraries
pip install fastapi uvicorn jinja2 python-multipart            # install web framework
```

### Step 2 — Build matplotlib and seaborn charts

### Step 3 — Build interactive plotly charts

### Step 4 — Build the FastAPI dashboard

### Step 5 — Set up Metabase with Docker

### Step 6 — Connect Metabase to PostgreSQL

### Step 7 — Build your first Metabase panels

---

## 💻 Code Examples

### Visualisation with matplotlib and seaborn

```python
import matplotlib.pyplot as plt   # core plotting library
import seaborn as sns              # statistical visualisation built on matplotlib
import pandas as pd                # data manipulation
import psycopg2                    # PostgreSQL connector

# ── Connect to PostgreSQL and load data ──────────────────────────────────────
conn = psycopg2.connect(
    host="localhost",
    database="books_db",
    user="postgres",
    password="yourpassword"
)

# Load books data into a pandas DataFrame
df = pd.read_sql("SELECT * FROM books", conn)  # run SQL, get back a DataFrame
conn.close()                                    # always close the connection

print(df.head())   # preview the first 5 rows
print(df.dtypes)   # check what types each column is
```

```python
# ── Bar chart: average price per genre ───────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 6))   # create a figure with one subplot

# Calculate average price per genre
avg_price = df.groupby('genre')['price'].mean().sort_values(ascending=False)

# Draw the bar chart
avg_price.plot(
    kind='bar',          # bar chart type
    ax=ax,               # draw on our axes
    color='steelblue',   # bar colour
    edgecolor='white',   # white border between bars
    width=0.7            # bar width (0-1)
)

ax.set_title('Average Book Price by Genre', fontsize=14, fontweight='bold')
ax.set_xlabel('Genre', fontsize=12)
ax.set_ylabel('Average Price ($)', fontsize=12)
ax.tick_params(axis='x', rotation=45)    # rotate x labels so they don't overlap
ax.grid(axis='y', alpha=0.3)             # light horizontal gridlines

plt.tight_layout()                        # prevent labels from being cut off
plt.savefig('avg_price_by_genre.png', dpi=150, bbox_inches='tight')  # save to file
plt.show()                                # display in notebook or popup
```

```python
# ── Seaborn: ratings distribution as a histogram ─────────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))

sns.histplot(
    data=df,            # the DataFrame
    x='rating',         # which column to plot
    bins=10,            # how many histogram buckets
    kde=True,           # overlay a smooth density curve
    color='coral',
    ax=ax
)

ax.set_title('Distribution of Book Ratings', fontsize=14)
ax.set_xlabel('Rating (out of 5)')
ax.set_ylabel('Number of Books')

plt.tight_layout()
plt.savefig('ratings_distribution.png', dpi=150, bbox_inches='tight')
plt.show()
```

```python
# ── Seaborn: heatmap of average rating by genre and in_stock status ───────────
pivot = df.pivot_table(
    values='rating',      # the value to aggregate
    index='genre',        # rows of the heatmap
    columns='in_stock',   # columns of the heatmap
    aggfunc='mean'        # how to aggregate (mean rating)
)

fig, ax = plt.subplots(figsize=(8, 5))

sns.heatmap(
    pivot,
    annot=True,            # show the number inside each cell
    fmt='.2f',             # format numbers to 2 decimal places
    cmap='YlOrRd',         # colour map: yellow → orange → red
    linewidths=0.5,        # lines between cells
    ax=ax
)

ax.set_title('Average Rating by Genre and Stock Status')
ax.set_xlabel('In Stock')
ax.set_ylabel('Genre')

plt.tight_layout()
plt.savefig('rating_heatmap.png', dpi=150, bbox_inches='tight')
plt.show()
```

```python
# ── Seaborn: scatter plot — price vs rating ───────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 6))

sns.scatterplot(
    data=df,
    x='price',       # x axis: price
    y='rating',      # y axis: rating
    hue='genre',     # colour points by genre
    size='price',    # size points by price (bigger price = bigger dot)
    sizes=(50, 300), # min and max dot size
    alpha=0.8,       # slight transparency to see overlapping points
    ax=ax
)

ax.set_title('Price vs Rating (coloured by Genre)')
ax.set_xlabel('Price ($)')
ax.set_ylabel('Rating (out of 5)')
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')  # legend outside plot

plt.tight_layout()
plt.savefig('price_vs_rating.png', dpi=150, bbox_inches='tight')
plt.show()
```

---

### Interactive Charts with Plotly Express

```python
import plotly.express as px   # high-level plotly interface — much simpler than raw plotly

# ── Interactive bar chart ─────────────────────────────────────────────────────
avg_by_genre = df.groupby('genre').agg(
    avg_price=('price', 'mean'),
    avg_rating=('rating', 'mean'),
    book_count=('id', 'count')
).reset_index()  # turn the GroupBy index back into a regular column

fig = px.bar(
    avg_by_genre,
    x='genre',                      # x axis
    y='avg_price',                  # y axis
    color='avg_rating',             # colour bars by avg rating
    hover_data=['book_count'],      # show book count when hovering
    title='Average Price per Genre (coloured by Rating)',
    labels={                        # rename columns for the chart
        'avg_price': 'Average Price ($)',
        'genre': 'Genre',
        'avg_rating': 'Avg Rating'
    },
    color_continuous_scale='Viridis'  # colour scale
)

fig.update_layout(
    plot_bgcolor='white',    # white background
    showlegend=True
)

fig.write_html('interactive_genre_chart.html')  # save as interactive HTML file
fig.show()                                       # open in browser
```

```python
# ── Interactive scatter plot ──────────────────────────────────────────────────
fig = px.scatter(
    df,
    x='price',
    y='rating',
    color='genre',         # colour by genre
    size='price',          # size by price
    hover_name='title',    # show title on hover
    hover_data=['author'], # also show author on hover
    title='Books: Price vs Rating',
    labels={'price': 'Price ($)', 'rating': 'Rating'}
)

fig.write_html('interactive_scatter.html')
fig.show()
```

---

### FastAPI Dashboard

Create this file structure:

```
dashboard/
├── main.py           ← FastAPI app
├── templates/
│   └── index.html    ← Jinja2 HTML template
└── static/
    └── style.css     ← optional styling
```

```python
# main.py — the FastAPI dashboard application
from fastapi import FastAPI, Request           # FastAPI core
from fastapi.templating import Jinja2Templates # HTML template engine
from fastapi.staticfiles import StaticFiles    # serve CSS/JS files
import psycopg2                                # PostgreSQL connector
import psycopg2.extras                         # dict cursor for easier data access
import plotly.express as px                    # chart generation
import plotly.io as pio                        # convert charts to HTML
import pandas as pd                            # data manipulation
import json                                    # for JSON responses

app = FastAPI(title="Books Dashboard")         # create the FastAPI app

# Tell FastAPI where to find HTML templates
templates = Jinja2Templates(directory="templates")

def get_db_connection():
    """Create and return a PostgreSQL connection."""
    return psycopg2.connect(
        host="localhost",
        database="books_db",
        user="postgres",
        password="yourpassword"
    )

@app.get("/")
async def dashboard(request: Request):
    """Render the main dashboard page."""
    conn = get_db_connection()                 # open database connection
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)  # dict results

    # ── Metric 1: total books scraped ────────────────────────────────────────
    cursor.execute("SELECT COUNT(*) AS total FROM books")
    total_books = cursor.fetchone()['total']   # get the count value

    # ── Metric 2: average price by genre (for bar chart) ─────────────────────
    cursor.execute("""
        SELECT genre, ROUND(AVG(price), 2) AS avg_price, COUNT(*) AS count
        FROM books
        GROUP BY genre
        ORDER BY avg_price DESC
    """)
    genre_data = cursor.fetchall()             # list of rows

    # ── Metric 3: ratings distribution (for histogram) ───────────────────────
    cursor.execute("SELECT rating FROM books WHERE rating IS NOT NULL")
    ratings = [row['rating'] for row in cursor.fetchall()]  # list of rating values

    conn.close()                               # always close the connection

    # ── Build charts as HTML strings ─────────────────────────────────────────
    # Bar chart: avg price by genre
    df_genre = pd.DataFrame(genre_data, columns=['genre', 'avg_price', 'count'])
    bar_fig = px.bar(
        df_genre, x='genre', y='avg_price',
        title='Average Price by Genre',
        labels={'avg_price': 'Avg Price ($)', 'genre': 'Genre'},
        color='avg_price',
        color_continuous_scale='Blues'
    )
    bar_chart_html = pio.to_html(
        bar_fig,
        full_html=False,    # only the chart div, not a full HTML page
        include_plotlyjs='cdn'  # load plotly from CDN, not embed it
    )

    # Histogram: ratings distribution
    df_ratings = pd.DataFrame({'rating': ratings})
    hist_fig = px.histogram(
        df_ratings, x='rating',
        title='Ratings Distribution',
        labels={'rating': 'Rating', 'count': 'Number of Books'},
        nbins=10,
        color_discrete_sequence=['coral']
    )
    hist_chart_html = pio.to_html(hist_fig, full_html=False, include_plotlyjs=False)

    # ── Pass everything to the HTML template ─────────────────────────────────
    return templates.TemplateResponse("index.html", {
        "request": request,          # FastAPI requires this to be passed
        "total_books": total_books,  # number to display
        "bar_chart": bar_chart_html, # HTML string for the bar chart
        "hist_chart": hist_chart_html  # HTML string for the histogram
    })
```

```html
<!-- templates/index.html — the dashboard HTML template -->
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Books Dashboard</title>
    <style>
      body {
        font-family: Arial, sans-serif;
        margin: 0;
        background: #f5f5f5;
      }
      .header {
        background: #2c3e50;
        color: white;
        padding: 20px 40px;
      }
      .container {
        max-width: 1200px;
        margin: 30px auto;
        padding: 0 20px;
      }
      .metric-card {
        background: white;
        border-radius: 8px;
        padding: 20px;
        display: inline-block;
        margin: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        min-width: 150px;
        text-align: center;
      }
      .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2c3e50;
      }
      .metric-label {
        color: #666;
        font-size: 0.9rem;
        margin-top: 5px;
      }
      .chart-row {
        display: flex;
        gap: 20px;
        margin-top: 20px;
        flex-wrap: wrap;
      }
      .chart-card {
        background: white;
        border-radius: 8px;
        padding: 20px;
        flex: 1;
        min-width: 300px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      }
    </style>
  </head>
  <body>
    <div class="header">
      <h1>📚 Books Dashboard</h1>
      <p>Live data from your PostgreSQL database</p>
    </div>

    <div class="container">
      <!-- Metric cards row -->
      <div>
        <!-- total_books comes from FastAPI — Jinja2 renders it here -->
        <div class="metric-card">
          <div class="metric-value">{{ total_books }}</div>
          <div class="metric-label">Total Books</div>
        </div>
      </div>

      <!-- Charts row -->
      <div class="chart-row">
        <div class="chart-card">
          <!-- bar_chart is an HTML string — the | safe filter prevents escaping -->
          {{ bar_chart | safe }}
        </div>
        <div class="chart-card">{{ hist_chart | safe }}</div>
      </div>
    </div>
  </body>
</html>
```

```bash
# Run the FastAPI dashboard
cd dashboard
uvicorn main:app --reload --port 8080   # start server, reload on code changes

# Then open: http://localhost:8080
```

---

### Metabase with Docker

```bash
# Step 1: pull and run Metabase
docker run -d \
  --name metabase \
  -p 3000:3000 \
  -e "MB_DB_TYPE=postgres" \
  -e "MB_DB_DBNAME=metabase" \
  -e "MB_DB_PORT=5432" \
  -e "MB_DB_USER=postgres" \
  -e "MB_DB_PASS=yourpassword" \
  -e "MB_DB_HOST=host.docker.internal" \
  metabase/metabase:latest
# -d: run in background (detached)
# -p 3000:3000: expose port 3000
# host.docker.internal: lets Docker container reach your local PostgreSQL

# Wait ~60 seconds for Metabase to start, then open:
# http://localhost:3000

# Check if it's ready:
docker logs metabase --tail 20   # show last 20 log lines
```

**Setting up Metabase (in the browser):**

1. Go to `http://localhost:3000`
2. Click **Get started**
3. Create your admin account
4. On the **Add your data** screen:
   - Database type: **PostgreSQL**
   - Host: `host.docker.internal`
   - Port: `5432`
   - Database name: `books_db`
   - Username: `postgres`
   - Password: your password
5. Click **Connect database**

**Creating your first chart:**

1. Click **+ New → Question**
2. Pick your `books` table
3. Click **Summarize**
4. Choose **Average of Price**
5. Group by **Genre**
6. Click **Visualize**
7. Click **Save** → give it a name → **Save to a new dashboard**

---

### Metabase vs Grafana

```
┌─────────────────────┬──────────────────────────────┬──────────────────────────────┐
│ Feature             │ Metabase                     │ Grafana                      │
├─────────────────────┼──────────────────────────────┼──────────────────────────────┤
│ Best for            │ Business analytics, SQL data │ Time-series, ops metrics     │
│ Data sources        │ PostgreSQL, MySQL, MongoDB   │ Prometheus, InfluxDB, Loki   │
│ Audience            │ Non-technical users          │ Engineers, DevOps teams      │
│ Chart building      │ Click-and-point GUI          │ Panel builder (more complex) │
│ Alerting            │ Basic email alerts           │ Advanced multi-channel alerts│
│ Free tier           │ Open source self-hosted      │ Open source self-hosted      │
│ When to choose it   │ "Show me our sales data"     │ "Alert me when CPU > 90%"    │
└─────────────────────┴──────────────────────────────┴──────────────────────────────┘
```

!!! tip "Rule of thumb"
Use **Metabase** when your audience is humans asking business questions about stored data.
Use **Grafana** when your audience is engineers watching live system metrics.

---

## ⚠️ Common Mistakes

**Mistake 1: Too many charts on one dashboard**
A dashboard with 20 panels answers no question clearly. Start with 3–5 panels that each answer one specific question. Add more only when there is a clear need.

**Mistake 2: Using the wrong chart type**

```
Bar chart    → comparing categories (genres, authors)
Line chart   → showing change over time (sales per month)
Scatter plot → showing relationship between two numbers
Pie chart    → showing part-of-whole (use sparingly — bar is usually clearer)
Heatmap      → showing density across two dimensions
```

**Mistake 3: Not closing database connections**

```python
# WRONG: if an error happens before conn.close(), connection stays open
conn = psycopg2.connect(...)
data = cursor.execute("SELECT...")  # if this fails, conn never closes
conn.close()

# CORRECT: use a context manager — connection closes even if an error happens
with psycopg2.connect(...) as conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT ...")
        data = cursor.fetchall()
# connection automatically closed here, even if an error occurred above
```

---

## ✅ Exercises

**Exercise 1 — Easy**
Using matplotlib, create a horizontal bar chart showing the top 5 most expensive books. Label each bar with the price value.

**Exercise 2 — Medium**
Build a plotly line chart that shows how many books were scraped per day over the last 30 days. Make it interactive so hovering shows the exact count and date.

**Exercise 3 — Hard**
Extend the FastAPI dashboard to add a third panel: a table showing the top 10 books by rating, with columns for title, author, genre, price, and rating. Style the table with alternating row colours using Jinja2 and CSS.

---

## 🏗️ Mini Project — Metabase 2-Panel Dashboard

**Goal:** Set up Metabase with Docker and build a 2-panel dashboard from your books database.

**Panel 1: Average Price by Genre (bar chart)**

1. New Question → books table
2. Summarize → Average of Price → Group by Genre
3. Visualize as Bar chart

**Panel 2: Books by Rating Range (pie chart)**

```sql
-- Custom SQL question in Metabase
SELECT
    CASE
        WHEN rating >= 4.8 THEN 'Excellent (4.8-5.0)'
        WHEN rating >= 4.5 THEN 'Great (4.5-4.7)'
        WHEN rating >= 4.0 THEN 'Good (4.0-4.4)'
        ELSE 'Average (below 4.0)'
    END AS rating_category,
    COUNT(*) AS book_count
FROM books
GROUP BY rating_category
ORDER BY book_count DESC;
```

**Save both to a dashboard named "Books Overview".**

---

## 🔗 What's Next

In **Module 5-3: Tracking Pipeline Metrics**, you will go beyond visualising data and start monitoring the health of your pipelines themselves — tracking rows processed, errors, and duration using Prometheus and Grafana.
