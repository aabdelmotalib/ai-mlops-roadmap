---
tags:
  - Intermediate
  - Phase 5
---

# Module 5: Visualising Results & Trends

> **Phase 5 — Analytics & Monitoring**

---

## 🎯 What You Will Learn

- How to choose the right chart type for your data and question
- Advanced matplotlib techniques: subplots, annotations, and custom styles
- Seaborn for statistical visualisation: boxplots, violin plots, pairplots
- Plotly for interactive, shareable web charts
- How to visualise time-series data: trends, seasonality, and anomalies
- How to visualise ML model performance: confusion matrices, ROC curves, feature importance
- How to export charts to PNG, SVG, and PDF for reports

---

## 🧠 Concept Explained

Imagine you've spent three months building pipelines, training models, and collecting data. Now your manager asks: _"So what did we find?"_

You could hand them 10,000 rows of CSV. Or you could show them one well-designed chart that makes the answer obvious in five seconds.

That is the power of data visualisation. Not making things pretty — making things **understood**.

The most common mistake beginners make is choosing a chart first and then filling it with data. The right way is the opposite: **start with your question, then pick the chart that answers it most clearly.**

!!! note "The golden rule of visualisation"
Every element in your chart must earn its place. If removing it doesn't change what the viewer understands, remove it.

---

## 🔍 How It Works

### Choosing the right chart type

```
What are you trying to show?
         │
         ├── Comparing categories (e.g. sales by genre)
         │        └── BAR CHART (horizontal if many categories)
         │
         ├── Showing change over time (e.g. daily scrapes this month)
         │        └── LINE CHART
         │
         ├── Showing distribution (e.g. how are ratings spread?)
         │        ├── HISTOGRAM (raw counts)
         │        ├── BOX PLOT (summary: median, quartiles, outliers)
         │        └── VIOLIN PLOT (shape of the distribution)
         │
         ├── Showing relationship between two numbers (e.g. price vs rating)
         │        └── SCATTER PLOT
         │
         ├── Showing part of a whole (e.g. genre share of catalogue)
         │        └── PIE CHART (use sparingly — bar is usually clearer)
         │
         ├── Showing density across two dimensions (e.g. rating × price)
         │        └── HEATMAP
         │
         └── Showing many variables at once
                  └── PAIRPLOT / SCATTERPLOT MATRIX
```

---

## 🛠️ Step-by-Step Guide

### Step 1 — Install and import libraries

### Step 2 — Load data from PostgreSQL

### Step 3 — Advanced matplotlib charts

### Step 4 — Statistical charts with seaborn

### Step 5 — Interactive charts with plotly

### Step 6 — Time-series visualisation

### Step 7 — ML model performance charts

### Step 8 — Export to PDF report

---

## 💻 Code Examples

### Setup

```python
# Install required libraries
# pip install matplotlib seaborn plotly pandas psycopg2-binary reportlab kaleido

import matplotlib.pyplot as plt          # core plotting
import matplotlib.gridspec as gridspec   # for complex subplot layouts
import seaborn as sns                    # statistical visualisation
import plotly.express as px              # interactive charts (high-level)
import plotly.graph_objects as go        # interactive charts (low-level)
import plotly.io as pio                  # save plotly charts
import pandas as pd                      # data manipulation
import numpy as np                       # numerical operations
import psycopg2                          # PostgreSQL connection

# ── Set a clean matplotlib style ─────────────────────────────────────────────
plt.style.use('seaborn-v0_8-whitegrid')  # clean white background with grid
sns.set_palette('husl')                  # use a colourful, accessible palette

# ── Load data from PostgreSQL ─────────────────────────────────────────────────
def load_data():
    """Load books data from PostgreSQL into a pandas DataFrame."""
    conn = psycopg2.connect(
        host="localhost", database="books_db",
        user="postgres", password="yourpassword"
    )
    df = pd.read_sql("""
        SELECT id, title, author, genre, price, rating,
               in_stock, scraped_at
        FROM books
        ORDER BY id
    """, conn)
    conn.close()
    return df

df = load_data()
print(f"Loaded {len(df)} books")   # confirm data loaded
print(df.dtypes)                    # check column types
```

---

### Advanced matplotlib: subplots, annotations, custom styles

```python
# ── Multi-panel figure: 4 charts in one figure ───────────────────────────────
fig = plt.figure(figsize=(16, 12))      # large figure to fit 4 panels

# GridSpec gives precise control over subplot layout
# 2 rows, 2 columns, with custom spacing
gs = gridspec.GridSpec(
    2, 2,               # 2 rows, 2 columns
    figure=fig,
    hspace=0.4,         # vertical space between rows
    wspace=0.3          # horizontal space between columns
)

ax1 = fig.add_subplot(gs[0, 0])   # top-left panel
ax2 = fig.add_subplot(gs[0, 1])   # top-right panel
ax3 = fig.add_subplot(gs[1, 0])   # bottom-left panel
ax4 = fig.add_subplot(gs[1, 1])   # bottom-right panel

# ── Panel 1: Bar chart with value annotations ────────────────────────────────
avg_price = df.groupby('genre')['price'].mean().sort_values(ascending=False)
bars = avg_price.plot(kind='bar', ax=ax1, color='steelblue', width=0.7)

# Add value labels on top of each bar
for bar, value in zip(ax1.patches, avg_price.values):
    ax1.annotate(
        f'${value:.2f}',                  # format as dollar amount
        xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),  # above bar
        xytext=(0, 3),                    # 3 pixels above the bar top
        textcoords='offset points',       # offset is in points, not data units
        ha='center', va='bottom',         # centre horizontally, bottom aligned
        fontsize=9
    )

ax1.set_title('Average Price by Genre', fontsize=12, fontweight='bold')
ax1.set_xlabel('')                        # no x-axis label needed (obvious)
ax1.set_ylabel('Average Price ($)')
ax1.tick_params(axis='x', rotation=30)   # rotate x labels to prevent overlap

# ── Panel 2: Scatter plot with a trend line ───────────────────────────────────
ax2.scatter(
    df['price'], df['rating'],
    c=pd.Categorical(df['genre']).codes,  # colour by genre (numeric codes)
    cmap='tab10',                          # colourmap with 10 distinct colours
    alpha=0.7,                             # slight transparency
    s=80                                   # dot size
)

# Add a trend line (linear regression)
z = np.polyfit(df['price'], df['rating'], 1)  # fit a degree-1 polynomial
p = np.poly1d(z)                              # create the polynomial function
x_line = np.linspace(df['price'].min(), df['price'].max(), 100)  # x points
ax2.plot(
    x_line, p(x_line),
    'r--', linewidth=2, alpha=0.8,  # red dashed trend line
    label=f'Trend: y={z[0]:.3f}x + {z[1]:.2f}'
)

ax2.set_title('Price vs Rating with Trend Line', fontsize=12, fontweight='bold')
ax2.set_xlabel('Price ($)')
ax2.set_ylabel('Rating')
ax2.legend(fontsize=9)

# ── Panel 3: Stacked bar showing in_stock split by genre ─────────────────────
stock_counts = df.groupby(['genre', 'in_stock']).size().unstack(fill_value=0)
stock_counts.columns = ['Out of Stock', 'In Stock']   # rename for legend clarity
stock_counts.plot(
    kind='bar',
    stacked=True,          # bars stacked on top of each other
    ax=ax3,
    color=['#ff7f7f', '#7fbfff'],  # red for out of stock, blue for in stock
    width=0.7
)

ax3.set_title('Stock Status by Genre', fontsize=12, fontweight='bold')
ax3.set_xlabel('')
ax3.set_ylabel('Number of Books')
ax3.tick_params(axis='x', rotation=30)
ax3.legend(loc='upper right')

# ── Panel 4: Horizontal bar — top authors by count ────────────────────────────
top_authors = df['author'].value_counts().head(8)   # top 8 authors

top_authors.plot(
    kind='barh',           # horizontal bar chart
    ax=ax4,
    color='mediumpurple',
    width=0.7
)

# Add count labels at the end of each bar
for i, (name, count) in enumerate(top_authors.items()):
    ax4.text(
        count + 0.05,         # just past the end of the bar
        i,                    # vertical position
        str(count),           # the count value as text
        va='center',          # vertically centred
        fontsize=10
    )

ax4.set_title('Top Authors by Book Count', fontsize=12, fontweight='bold')
ax4.set_xlabel('Number of Books')
ax4.invert_yaxis()    # put the most popular author at the top

# ── Add a figure-level title ──────────────────────────────────────────────────
fig.suptitle(
    'Books Database — Analytics Overview',
    fontsize=16, fontweight='bold', y=1.02  # slightly above the top
)

plt.savefig('analytics_overview.png', dpi=150, bbox_inches='tight')
plt.show()
```

---

### Statistical charts with seaborn

```python
# ── Box plot: price distribution per genre ────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Box plot: shows median, quartiles (IQR box), and outliers (dots)
sns.boxplot(
    data=df,
    x='genre',
    y='price',
    palette='pastel',      # soft colours
    order=df.groupby('genre')['price'].median().sort_values(ascending=False).index,
    ax=axes[0]
)

# Overlay individual data points so we can see exact values
sns.stripplot(
    data=df,
    x='genre',
    y='price',
    color='black',
    alpha=0.5,             # transparent so they don't dominate
    size=4,
    ax=axes[0]
)

axes[0].set_title('Price Distribution by Genre\n(box = IQR, line = median, dots = data points)')
axes[0].set_xlabel('Genre')
axes[0].set_ylabel('Price ($)')
axes[0].tick_params(axis='x', rotation=30)

# ── Violin plot: shows the full shape of the distribution ────────────────────
# Violin is like a box plot but shows the density — wider = more data at that value
sns.violinplot(
    data=df,
    x='genre',
    y='rating',
    palette='muted',
    inner='box',           # show the box plot inside the violin
    ax=axes[1]
)

axes[1].set_title('Rating Distribution by Genre\n(width shows density of ratings)')
axes[1].set_xlabel('Genre')
axes[1].set_ylabel('Rating')
axes[1].tick_params(axis='x', rotation=30)

plt.tight_layout()
plt.savefig('statistical_distributions.png', dpi=150, bbox_inches='tight')
plt.show()
```

```python
# ── Pairplot: explore all numeric relationships at once ───────────────────────
# Pairplot creates a grid of scatter plots for every pair of numeric columns
# Diagonal shows the distribution of each variable

numeric_cols = df[['price', 'rating']].copy()
numeric_cols['genre'] = df['genre']   # add genre for colouring

pair_plot = sns.pairplot(
    numeric_cols,
    hue='genre',           # colour points by genre
    diag_kind='kde',       # kernel density estimate on diagonal (smooth histogram)
    plot_kws={'alpha': 0.6},  # slightly transparent scatter points
    height=3               # size of each subplot
)

pair_plot.fig.suptitle('Pairplot: Price and Rating by Genre', y=1.02)
plt.savefig('pairplot.png', dpi=150, bbox_inches='tight')
plt.show()
```

---

### Interactive charts with Plotly

```python
# ── Interactive scatter with full hover info ──────────────────────────────────
fig = px.scatter(
    df,
    x='price',
    y='rating',
    color='genre',                      # colour by genre
    size='price',                       # dot size proportional to price
    hover_name='title',                 # title shown prominently on hover
    hover_data={                        # additional hover fields
        'author': True,
        'price': ':.2f',               # format price to 2 decimal places
        'rating': ':.1f',
        'in_stock': True
    },
    title='Books: Price vs Rating (Interactive)',
    labels={'price': 'Price ($)', 'rating': 'Rating out of 5'},
    template='plotly_white'            # clean white background
)

# Add annotation pointing to the most expensive book
most_expensive = df.loc[df['price'].idxmax()]
fig.add_annotation(
    x=most_expensive['price'],
    y=most_expensive['rating'],
    text=f"Most expensive:<br>{most_expensive['title']}",  # <br> = line break in plotly
    showarrow=True,
    arrowhead=2,
    arrowcolor='red',
    ax=40, ay=-40          # offset of the annotation text from the arrow tip
)

fig.write_html('interactive_scatter.html')   # save as shareable HTML
fig.show()
```

```python
# ── Interactive grouped bar chart ─────────────────────────────────────────────
genre_stock = df.groupby(['genre', 'in_stock']).agg(
    count=('id', 'count'),
    avg_price=('price', 'mean')
).reset_index()
genre_stock['stock_label'] = genre_stock['in_stock'].map(
    {True: 'In Stock', False: 'Out of Stock'}   # human-readable labels
)

fig = px.bar(
    genre_stock,
    x='genre',
    y='count',
    color='stock_label',
    barmode='group',           # side-by-side bars (not stacked)
    hover_data=['avg_price'],  # show average price on hover
    title='Books by Genre and Stock Status',
    labels={'count': 'Number of Books', 'genre': 'Genre', 'stock_label': 'Status'},
    color_discrete_map={
        'In Stock': '#2196F3',      # blue for in stock
        'Out of Stock': '#F44336'   # red for out of stock
    }
)

fig.update_layout(
    legend_title_text='Stock Status',
    plot_bgcolor='white',
    bargap=0.15,               # gap between genre clusters
    bargroupgap=0.05           # gap within each genre cluster
)

fig.write_html('genre_stock_chart.html')
fig.show()
```

---

### Time-series visualisation

```python
# ── Simulate time-series data ─────────────────────────────────────────────────
# (In your real project, this comes from weather_measurements table)
dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')  # every day
np.random.seed(42)   # for reproducibility

# Simulate temperature with: trend + seasonality + noise
trend = np.linspace(0, 2, len(dates))                  # slight upward trend
seasonality = 10 * np.sin(2 * np.pi * np.arange(len(dates)) / 365)  # yearly cycle
noise = np.random.normal(0, 1.5, len(dates))           # random day-to-day variation
temperature = 20 + trend + seasonality + noise         # combine all components

ts_df = pd.DataFrame({'date': dates, 'temperature': temperature})
ts_df.set_index('date', inplace=True)   # use date as the index

# ── Plot: raw data + 7-day rolling average + anomalies ───────────────────────
fig, axes = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

# Panel 1: raw temperature + rolling average
axes[0].plot(
    ts_df.index,
    ts_df['temperature'],
    alpha=0.4,                    # raw data slightly transparent
    linewidth=0.8,
    color='steelblue',
    label='Daily temperature'
)

rolling_avg = ts_df['temperature'].rolling(window=7).mean()  # 7-day rolling mean
axes[0].plot(
    ts_df.index,
    rolling_avg,
    linewidth=2,
    color='darkblue',
    label='7-day rolling average'
)

axes[0].set_title('Daily Temperature — 2024 (with 7-day rolling average)')
axes[0].set_ylabel('Temperature (°C)')
axes[0].legend()

# Panel 2: anomaly detection (values > 2 standard deviations from rolling mean)
rolling_std = ts_df['temperature'].rolling(window=30).std()   # 30-day rolling std
upper_bound = rolling_avg + 2 * rolling_std                   # upper anomaly threshold
lower_bound = rolling_avg - 2 * rolling_std                   # lower anomaly threshold

# Shade the normal range
axes[1].fill_between(
    ts_df.index,
    lower_bound, upper_bound,
    alpha=0.2, color='green',
    label='Normal range (±2 std dev)'
)

axes[1].plot(ts_df.index, ts_df['temperature'], linewidth=0.8, color='gray', alpha=0.5)

# Mark anomalies as red dots
anomalies = ts_df[
    (ts_df['temperature'] > upper_bound) | (ts_df['temperature'] < lower_bound)
]
axes[1].scatter(
    anomalies.index,
    anomalies['temperature'],
    color='red', zorder=5,       # zorder=5 puts them on top
    s=50, label=f'Anomalies ({len(anomalies)} points)'
)

axes[1].set_title('Anomaly Detection (values outside ±2 std dev)')
axes[1].set_ylabel('Temperature (°C)')
axes[1].set_xlabel('Date')
axes[1].legend()

plt.tight_layout()
plt.savefig('time_series_analysis.png', dpi=150, bbox_inches='tight')
plt.show()
```

---

### ML model performance charts

```python
from sklearn.datasets import load_iris               # demo dataset
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    confusion_matrix, classification_report,
    roc_curve, auc, RocCurveDisplay
)
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# ── Train a simple model for demo purposes ────────────────────────────────────
iris = load_iris()
X, y = iris.data, iris.target
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)     # train the model
y_pred = model.predict(X_test)  # make predictions

# ── Plot 1: Confusion matrix heatmap ─────────────────────────────────────────
cm = confusion_matrix(y_test, y_pred)   # rows=actual, cols=predicted

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

sns.heatmap(
    cm,
    annot=True,              # show numbers inside cells
    fmt='d',                 # format as integers
    cmap='Blues',            # blue colour scale
    xticklabels=iris.target_names,  # class names on x-axis
    yticklabels=iris.target_names,  # class names on y-axis
    ax=axes[0]
)

axes[0].set_title('Confusion Matrix\n(rows=actual, columns=predicted)')
axes[0].set_xlabel('Predicted Label')
axes[0].set_ylabel('True Label')

# ── Plot 2: Feature importance bar chart ──────────────────────────────────────
importance_df = pd.DataFrame({
    'feature': iris.feature_names,
    'importance': model.feature_importances_   # between 0 and 1
}).sort_values('importance', ascending=True)   # sort for horizontal bar

axes[1].barh(
    importance_df['feature'],
    importance_df['importance'],
    color='steelblue'
)

# Add percentage labels
for i, (feat, imp) in enumerate(zip(importance_df['feature'], importance_df['importance'])):
    axes[1].text(
        imp + 0.005,          # just past the end of the bar
        i,
        f'{imp:.1%}',         # format as percentage
        va='center'
    )

axes[1].set_title('Feature Importance')
axes[1].set_xlabel('Importance Score')
axes[1].set_xlim(0, max(importance_df['importance']) * 1.2)  # room for labels

plt.tight_layout()
plt.savefig('model_performance.png', dpi=150, bbox_inches='tight')
plt.show()

# Print classification report (precision, recall, F1 for each class)
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=iris.target_names))
```

---

### Export charts to PDF

```python
# matplotlib can save a multi-page PDF directly
from matplotlib.backends.backend_pdf import PdfPages

def create_pdf_report(df, output_path='books_report.pdf'):
    """
    Generate a multi-page PDF report from the books dataset.
    Each page is a separate chart.
    """

    with PdfPages(output_path) as pdf:
        # ── Page 1: Title page ────────────────────────────────────────────────
        fig = plt.figure(figsize=(11, 8.5))   # letter paper size
        fig.text(0.5, 0.6, 'Books Database', ha='center', fontsize=32, fontweight='bold')
        fig.text(0.5, 0.5, 'Analytics Report', ha='center', fontsize=20, color='gray')
        fig.text(0.5, 0.35, f'Generated: {pd.Timestamp.now().strftime("%Y-%m-%d")}',
                 ha='center', fontsize=14, color='gray')
        fig.text(0.5, 0.28, f'Total Books: {len(df)}',
                 ha='center', fontsize=14)
        pdf.savefig(fig, bbox_inches='tight')    # save this page
        plt.close(fig)                            # close to free memory

        # ── Page 2: Average price by genre ───────────────────────────────────
        fig, ax = plt.subplots(figsize=(11, 7))
        avg_price = df.groupby('genre')['price'].mean().sort_values(ascending=False)
        avg_price.plot(kind='bar', ax=ax, color='steelblue', width=0.7)
        ax.set_title('Average Price by Genre', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Genre')
        ax.set_ylabel('Average Price ($)')
        ax.tick_params(axis='x', rotation=30)
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)

        # ── Page 3: Ratings distribution ─────────────────────────────────────
        fig, ax = plt.subplots(figsize=(11, 7))
        sns.histplot(data=df, x='rating', bins=10, kde=True, color='coral', ax=ax)
        ax.set_title('Distribution of Book Ratings', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Rating')
        ax.set_ylabel('Count')
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)

        # ── Page 4: Price vs Rating scatter ──────────────────────────────────
        fig, ax = plt.subplots(figsize=(11, 7))
        for genre, group in df.groupby('genre'):
            ax.scatter(group['price'], group['rating'],
                      label=genre, alpha=0.8, s=100)
        ax.set_title('Price vs Rating by Genre', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Price ($)')
        ax.set_ylabel('Rating')
        ax.legend(title='Genre', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)

        # ── Add PDF metadata ──────────────────────────────────────────────────
        metadata = pdf.infodict()
        metadata['Title'] = 'Books Database Analytics Report'
        metadata['Author'] = 'Your Name'
        metadata['Subject'] = 'Data Analysis'
        metadata['Keywords'] = 'books, analytics, python'

    print(f"PDF report saved to: {output_path}")
    return output_path

# Generate the report
create_pdf_report(df, 'books_analytics_report.pdf')
```

---

## ⚠️ Common Mistakes

**Mistake 1: Using pie charts when you have more than 5 slices**

```python
# WRONG: 8-slice pie chart is impossible to read
df['genre'].value_counts().plot(kind='pie')  # hard to compare thin slices

# CORRECT: horizontal bar chart is always clearer for comparison
df['genre'].value_counts().sort_values().plot(
    kind='barh', color='steelblue'
)
plt.xlabel('Number of Books')
plt.title('Books by Genre')
```

**Mistake 2: Not handling missing values before plotting**

```python
# WRONG: NaN values cause gaps in line charts and errors in seaborn
df.plot(x='date', y='rating')   # gap where NaN appears

# CORRECT: decide how to handle NaN before plotting
df_clean = df.dropna(subset=['rating'])  # option 1: drop NaN rows
# OR
df['rating'] = df['rating'].fillna(df['rating'].median())  # option 2: fill with median
df_clean.plot(x='date', y='rating')  # now clean
```

**Mistake 3: Overloading one chart with too much information**

```python
# WRONG: trying to show 6 lines on one chart
for genre in df['genre'].unique():
    subset = df[df['genre'] == genre]
    plt.plot(subset['date'], subset['price'], label=genre)
# Result: spaghetti chart nobody can read

# CORRECT: use facets (one small chart per genre) or limit to 3-4 lines
g = sns.FacetGrid(df, col='genre', col_wrap=3, height=3)  # one subplot per genre
g.map(plt.plot, 'date', 'price')
```

---

## ✅ Exercises

**Exercise 1 — Easy**
Using seaborn, create a box plot showing the distribution of book prices for books that are in stock vs out of stock (two side-by-side boxes). Add a title and axis labels.

**Exercise 2 — Medium**
Using plotly express, build an animated scatter plot where each frame shows one genre at a time, plotting price on the x-axis and rating on the y-axis. The animation should cycle through all genres.

**Exercise 3 — Hard**
Write a function `generate_report(df, model, X_test, y_test)` that produces a 5-page PDF report containing: a title page, genre price analysis, rating distribution, price vs rating scatter, and the ML model confusion matrix. The function should accept any sklearn model and return the path to the saved PDF.

---

## 🏗️ Mini Project — End-to-End Summary Report

**Goal:** Build a Jupyter-style summary report using plotly figures saved as HTML, showing the full end-to-end results from all previous phases.

```python
# summary_report.py — generate an HTML report with interactive plotly charts

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import psycopg2
from datetime import datetime

def build_summary_report(output_path='summary_report.html'):
    """
    Build a complete HTML report with interactive plotly charts
    covering all phases of the pipeline.
    """

    # ── Load all data sources ─────────────────────────────────────────────────
    conn = psycopg2.connect(
        host="localhost", database="books_db",
        user="postgres", password="yourpassword"
    )

    books_df    = pd.read_sql("SELECT * FROM books", conn)
    pipeline_df = pd.read_sql("SELECT * FROM pipeline_runs ORDER BY started_at", conn)
    conn.close()

    # ── Chart 1: Books by genre ───────────────────────────────────────────────
    genre_counts = books_df['genre'].value_counts().reset_index()
    genre_counts.columns = ['genre', 'count']
    fig1 = px.bar(
        genre_counts, x='genre', y='count',
        title='Phase 1 Result: Books Scraped by Genre',
        color='count', color_continuous_scale='Blues'
    )

    # ── Chart 2: Pipeline run history ────────────────────────────────────────
    fig2 = px.scatter(
        pipeline_df,
        x='started_at', y='duration_seconds',
        color='status',
        size='rows_loaded',
        hover_data=['pipeline_name', 'rows_failed'],
        title='Phase 2 Result: Pipeline Run History',
        color_discrete_map={'success': 'green', 'failed': 'red'}
    )

    # ── Chart 3: Price distribution ───────────────────────────────────────────
    fig3 = px.histogram(
        books_df, x='price', nbins=15, color='genre',
        title='Phase 1 Data: Price Distribution by Genre',
        barmode='overlay', opacity=0.7
    )

    # ── Chart 4: Rating vs Price with genre ───────────────────────────────────
    fig4 = px.scatter(
        books_df, x='price', y='rating',
        color='genre', size='price',
        hover_name='title', hover_data=['author'],
        title='Phase 1 Data: Rating vs Price by Genre',
        trendline='ols'   # adds ordinary least squares trend line
    )

    # ── Assemble the HTML report ──────────────────────────────────────────────
    report_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Convert each figure to an HTML div (no full page, no plotly.js repeated)
    chart1_html = fig1.to_html(full_html=False, include_plotlyjs='cdn')
    chart2_html = fig2.to_html(full_html=False, include_plotlyjs=False)
    chart3_html = fig3.to_html(full_html=False, include_plotlyjs=False)
    chart4_html = fig4.to_html(full_html=False, include_plotlyjs=False)

    # Build the full HTML page
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI & MLOps Roadmap — Summary Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }}
            h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
            h2 {{ color: #34495e; margin-top: 40px; }}
            .metric-row {{ display: flex; gap: 20px; margin: 20px 0; }}
            .metric {{ background: #f8f9fa; padding: 20px; border-radius: 8px;
                       border-left: 4px solid #3498db; flex: 1; }}
            .metric-value {{ font-size: 2rem; font-weight: bold; color: #2c3e50; }}
            .metric-label {{ color: #666; font-size: 0.9rem; }}
            .chart-container {{ margin: 30px 0; }}
            .footer {{ text-align: center; color: #999; margin-top: 50px; font-size: 0.8rem; }}
        </style>
    </head>
    <body>
        <h1>🚀 AI & MLOps Roadmap — End-to-End Summary Report</h1>
        <p style="color: #666;">Generated: {report_timestamp}</p>

        <h2>📊 Key Metrics</h2>
        <div class="metric-row">
            <div class="metric">
                <div class="metric-value">{len(books_df)}</div>
                <div class="metric-label">Total Books Scraped (Phase 1)</div>
            </div>
            <div class="metric">
                <div class="metric-value">{len(pipeline_df)}</div>
                <div class="metric-label">Pipeline Runs (Phase 2)</div>
            </div>
            <div class="metric">
                <div class="metric-value">
                    {round(pipeline_df[pipeline_df['status']=='success'].shape[0] / max(len(pipeline_df),1) * 100)}%
                </div>
                <div class="metric-label">Pipeline Success Rate</div>
            </div>
            <div class="metric">
                <div class="metric-value">{books_df['genre'].nunique()}</div>
                <div class="metric-label">Unique Genres Found</div>
            </div>
        </div>

        <h2>📚 Phase 1: Data Collection Results</h2>
        <div class="chart-container">{chart1_html}</div>
        <div class="chart-container">{chart3_html}</div>
        <div class="chart-container">{chart4_html}</div>

        <h2>⚙️ Phase 2: Pipeline Health</h2>
        <div class="chart-container">{chart2_html}</div>

        <div class="footer">
            Report generated by the AI & MLOps Roadmap pipeline system
        </div>
    </body>
    </html>
    """

    # Write the HTML file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)              # write the complete HTML string

    print(f"Report saved to: {output_path}")
    print(f"Open in browser: file://{output_path}")
    return output_path

# Generate the report
build_summary_report('summary_report.html')
```

```bash
# Open the report in your browser
xdg-open summary_report.html   # Ubuntu command to open in default browser
```

---

## 🔗 What's Next

You have now completed all 5 modules of **Phase 5: Analytics & Monitoring**. You can query data analytically, build dashboards, track pipeline health, monitor your infrastructure, and communicate results through charts and reports.

In **Phase 6: MLOps & Deployment**, you will take everything you've built and make it production-ready — containerising your services with Docker Compose, setting up CI/CD pipelines, tracking ML experiments with MLflow, and building a system that can monitor itself in production.
