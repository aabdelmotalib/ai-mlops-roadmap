---
tags:
  - Beginner
  - Phase 0
  - Strings
  - Text Processing
---

# Sub-Module: Working with Strings

**Part of Module 1: Python Essentials**  
**Phase 0: Baseline Setup**

---

## 🎯 What You Will Learn

By the end of this sub-module, you will:

- Understand how strings work in Python and why they're immutable
- Index and slice strings to extract specific characters and substrings
- Use essential string methods to clean, transform, and search text
- Format strings using `f-strings`, `.format()`, and `%` notation
- Handle multiline strings and raw strings
- Check if text contains certain substrings using membership operators
- Convert between strings and other data types safely
- Use regular expressions to match complex patterns
- Write efficient string operations that scale to large datasets

---

## 🧠 Concept Explained: What Is a String?

### The Analogy: A String Is Like a Cinema Row

Imagine a cinema with numbered seats in a single row. A string in Python is exactly like that:

```
S  t  r  i  n  g
↓  ↓  ↓  ↓  ↓  ↓
0  1  2  3  4  5   (seat numbers / indices)
```

Each character has a position (index) starting from 0. You can:

- **Point to a single seat**: Get character at position 2 → "r"
- **Grab a section of seats**: Get characters from position 0 to 3 → "Stri"
- **Look from the back**: The last seat is position -1, second-to-last is -2

But here's the crucial part: **once the cinema is built, you can't change the seats**. Although you can grab a section and build a new cinema from it. This is what we mean by **strings are immutable** — you can't modify a string in place; you always create a new one.

### Why This Matters

In data work, strings are everywhere:

- File names and paths
- User input (names, emails, addresses)
- CSV data to be cleaned and parsed
- Log files to be analyzed
- Configuration values

Knowing how to manipulate strings efficiently is essential. A single slow string operation on a million rows can make your script unbearably slow.

---

## 🔍 How It Works: Indexing, Slicing, and Immutability

### String Indexing: The Seat Numbers

Here's a visual representation of how Python numbers string positions:

```
Character:  S  t  r  i  n  g
Position:   0  1  2  3  4  5  (from the left, starting at 0)
Negative:  -6 -5 -4 -3 -2 -1  (from the right, ending at -1)
```

### String Slicing: Grabbing Sections of Seats

Slicing uses the syntax `string[start:stop:step]`:

- `start`: Where to begin (included)
- `stop`: Where to end (NOT included — this is important!)
- `step`: How many positions to jump (default is 1)

Example: `"String"[0:3]` means "start at 0, go up to (but not including) 3" → `"Str"`

### The Immutability Rule

```
Original string:  "Hello"
You want:         "Hallo"

Wrong approach:
my_string = "Hello"
my_string[1] = "a"  # Error! Can't modify a string directly

Correct approach:
my_string = "Hello"
my_string = my_string[0] + "a" + my_string[2:]  # Build a new string
# Result: "Hallo"
```

Every time you "change" a string, Python actually makes a brand new string. This seems wasteful, but it has safety benefits.

---

## 🛠️ Step-by-Step Guide

### Step 1: Index Individual Characters

```python
# Create a string
message = "Python"

# Get the first character (index 0)
print(message[0])

# Get the third character (index 2)
print(message[2])

# Get the last character (index -1)
print(message[-1])

# Get the second-to-last character (index -2)
print(message[-2])
```

**Expected output:**

```
P
t
n
o
```

### Step 2: Slice Substrings

```python
message = "Python"

# Get characters from index 0 up to (but not including) 3
print(message[0:3])

# Get characters from index 2 onwards
print(message[2:])

# Get characters up to index 4
print(message[:4])

# Get every second character
print(message[::2])

# Reverse the string
print(message[::-1])
```

**Expected output:**

```
Pyt
thon
Pyth
Pto
nohtyP
```

### Step 3: Use `.strip()` to Remove Whitespace

Raw data often has unwanted spaces. The `.strip()` method removes them from both ends:

```python
# Raw data from a file or user input (notice the spaces!)
messy = "  hello world  "

# Remove spaces from both ends
clean = messy.strip()
print(f"'{clean}'")

# Remove from left side only
left_clean = messy.lstrip()
print(f"'{left_clean}'")

# Remove from right side only
right_clean = messy.rstrip()
print(f"'{right_clean}'")
```

**Expected output:**

```
'hello world'
'hello world  '
'  hello world'
```

### Step 4: Change Case With `.lower()`, `.upper()`, `.title()`

```python
text = "PyThOn ProGrAmming"

# Convert to lowercase
print(text.lower())

# Convert to uppercase
print(text.upper())

# Convert to title case (first letter of each word capitalized)
print(text.title())
```

**Expected output:**

```
python programming
PYTHON PROGRAMMING
Python Programming
```

### Step 5: Replace Substrings With `.replace()`

```python
text = "I like Python. Python is great."

# Replace all occurrences
new_text = text.replace("Python", "Java")
print(new_text)

# Replace only the first occurrence (second argument)
new_text = text.replace("Python", "Java", 1)
print(new_text)
```

**Expected output:**

```
I like Java. Java is great.
I like Java. Python is great.
```

### Step 6: Split and Join — The Core Data-Cleaning Combo

**Split**: Turn a string into a list (breaking at a delimiter)

```python
# CSV-style data (pipe-separated)
record = "John  |  Smith  |  john@example.com"

# Split by the pipe character
fields = record.split("|")
print(fields)

# Note: This includes the extra spaces — we'll clean those next
```

**Expected output:**

```
['John  ', '  Smith  ', '  john@example.com']
```

**Join**: Turn a list back into a string

```python
names = ["Alice", "Bob", "Charlie"]

# Join with a comma separator
sentence = ", ".join(names)
print(sentence)

# Join with a different separator
path = "/".join(["home", "user", "documents"])
print(path)
```

**Expected output:**

```
Alice, Bob, Charlie
home/user/documents
```

**The Combo: Clean and Split**

```python
# Real-world messy data
record = "  John  |  Smith  |  john@example.com  "

# Split, then clean each field
fields = record.strip().split("|")
fields = [field.strip() for field in fields]
# This list comprehension applies .strip() to each field

print(fields)
```

**Expected output:**

```
['John', 'Smith', 'john@example.com']
```

### Step 7: Check if Text Contains Something

```python
email = "alice@example.com"

# Check if email contains '@'
if "@" in email:
    print("Valid email format")

# Check if it doesn't contain something
if ".com" in email and "example" in email:
    print("Looks like a real email")

# Check the beginning and end
filename = "data_2024_final.csv"

if filename.startswith("data_"):
    print("This is a data file")

if filename.endswith(".csv"):
    print("This is a CSV file")
```

**Expected output:**

```
Valid email format
Looks like a real email
This is a data file
This is a CSV file
```

### Step 8: Find and Index — Locating Substrings

```python
text = "The quick brown fox jumps over the lazy dog"

# Find the position of a substring (returns -1 if not found)
position = text.find("quick")
print(f"'quick' is at position {position}")

# Using index (similar, but raises an error if not found)
position = text.index("f")
print(f"'f' is at position {position}")

# Count occurrences
count = text.count("o")
print(f"The letter 'o' appears {count} times")
```

**Expected output:**

```
'quick' is at position 4
'f' is at position 16
The letter 'o' appears 4 times
```

### Step 9: Format Strings — Three Methods

#### Method 1: Old-Style `%` Formatting

```python
name = "Alice"
age = 30
score = 95.5

# Using % formatting (understand it to read old code, but don't use it for new code)
message = "Name: %s, Age: %d, Score: %.1f" % (name, age, score)
print(message)
```

**Expected output:**

```
Name: Alice, Age: 30, Score: 95.5
```

#### Method 2: `.format()` Method

```python
name = "Alice"
age = 30
score = 95.5

# Using .format() (middle-era approach)
message = "Name: {}, Age: {}, Score: {}".format(name, age, score)
print(message)

# With named placeholders
message = "Name: {n}, Age: {a}, Score: {s}".format(n=name, a=age, s=score)
print(message)
```

**Expected output:**

```
Name: Alice, Age: 30, Score: 95.5
Name: Alice, Age: 30, Score: 95.5
```

#### Method 3: F-Strings (Modern — Use This!)

```python
name = "Alice"
age = 30
score = 95.5

# Using f-strings (Python 3.6+, modern and readable)
message = f"Name: {name}, Age: {age}, Score: {score}"
print(message)

# F-strings let you do calculations inside the braces
message = f"In 5 years, {name} will be {age + 5}"
print(message)

# Format numbers with precision
message = f"Score: {score:.0f}%"  # Round to 0 decimal places
print(message)
```

**Expected output:**

```
Name: Alice, Age: 30, Score: 95.5
In 5 years, Alice will be 35
Score: 96%
```

!!! tip
Use f-strings. They're fast, readable, and let you put expressions directly in the {}.

### Step 10: Multiline Strings With Triple Quotes

```python
# Single-line string
single = "This is a single line"

# Multiline string (triple quotes let you break across lines)
multiline = """This is a
multiline string
that spans three lines"""

print(multiline)

# Also useful for docstrings
print("""
REPORT SUMMARY
==============
Total items: 100
Valid items: 95
Invalid items: 5
""")
```

**Expected output:**

```
This is a
multiline string
that spans three lines

REPORT SUMMARY
==============
Total items: 100
Valid items: 95
Invalid items: 5
```

### Step 11: Raw Strings for File Paths

```python
# On Windows, paths look like: C:\Users\Alice\Documents
# The backslash is a special character in Python (escape character)

# Problem: this looks wrong
path = "C:\Users\Alice\Documents"
# Python interprets \U and \A as escape sequences

# Solution 1: Double backslashes
path = "C:\\Users\\Alice\\Documents"
print(path)

# Solution 2: Raw string (r"...") — the best way
path = r"C:\Users\Alice\Documents"
print(path)

# Raw strings are also useful for regular expressions (we'll cover those later)
pattern = r"\d{3}-\d{4}"  # Matches patterns like 123-4567
```

**Expected output:**

```
C:\Users\Alice\Documents
C:\Users\Alice\Documents
```

### Step 12: Convert Between Strings and Numbers

```python
# String to number
age_string = "25"
age = int(age_string)  # Convert to integer
print(type(age))

price_string = "19.99"
price = float(price_string)  # Convert to float
print(type(price))

# Number to string
count = 42
count_string = str(count)
print(count_string)

# Safe conversion with try/except
user_input = "hello"

try:
    number = int(user_input)
    print(number)
except ValueError:
    # If the string is not a valid number
    print(f"'{user_input}' is not a valid number!")
```

**Expected output:**

```
<class 'int'>
<class 'float'>
42
'hello' is not a valid number!
```

### Step 13: Introduction to Regular Expressions

Regular expressions (regex) let you describe patterns instead of exact matches. It's like a metal detector — you describe the "shape" of what you're looking for.

```python
import re  # Import the regex module

# Example: find all numbers in text
text = "I have 5 apples and 12 oranges"

# \d matches any digit
numbers = re.findall(r"\d+", text)
print(numbers)

# Example: find all words
words = re.findall(r"\w+", text)
print(words)
```

**Expected output:**

```
['5', '12']
['I', 'have', '5', 'apples', 'and', '12', 'oranges']
```

**Common regex patterns**:

```python
import re

test_texts = [
    "My email is alice@example.com",
    "Call me at 555-1234",
    "Price: £25.99",
]

for text in test_texts:
    # \w+ matches word characters, \d+ matches digits
    # . matches any character, \s matches whitespace

    # Find email (simplified pattern)
    if re.search(r"\w+@\w+\.\w+", text):
        print(f"Found email in: {text}")

    # Find phone number (pattern: 3 digits, dash, 4 digits)
    if re.search(r"\d{3}-\d{4}", text):
        print(f"Found phone in: {text}")

    # Find price (£ followed by digits and decimal)
    if re.search(r"£\d+\.\d{2}", text):
        print(f"Found price in: {text}")
```

**Expected output:**

```
Found email in: My email is alice@example.com
Found phone in: Call me at 555-1234
Found price in: Price: £25.99
```

**Substitution with regex**:

```python
import re

# Replace all patterns matching
text = "I have 2 cats and 3 dogs"

# Replace all numbers with "X"
new_text = re.sub(r"\d+", "X", text)
print(new_text)

# Replace specific pattern (e.g., phone numbers)
text = "Call: 555-1234 or 555-5678"
clean_text = re.sub(r"\d{3}-\d{4}", "XXX-XXXX", text)
print(clean_text)
```

**Expected output:**

```
I have X cats and X dogs
Call: XXX-XXXX or XXX-XXXX
```

---

## 💻 Code Examples: Cleaning Messy Book Records

### The Running Dataset

We'll use this real-world messy data throughout — a CSV-style file with pipe separators, whitespace problems, and inconsistent formatting:

```
Raw data (messy):
Title  |  Author  |  Price
  The Hobbit  |  J.R.R. TOLKIEN  |  £15.99
  1984|GEORGE ORWELL|£14.50
 Dune | Frank HERBERT  |  £16.75
```

### Example 1: Basic String Cleaning

```python
# Raw record from a file with extra whitespace
record = "  The Hobbit  |  J.R.R. TOLKIEN  |  £15.99  "

# Step 1: Clean the overall whitespace
clean_record = record.strip()

# Step 2: Split on the pipe
fields = clean_record.split("|")

# Step 3: Clean each individual field
title = fields[0].strip()  # Remove whitespace from title
author = fields[1].strip()  # Remove whitespace from author
price = fields[2].strip()  # Remove whitespace from price

# Step 4: Normalize author to title case (not all caps)
author = author.title()

# Step 5: Remove the £ symbol and convert to float
price = float(price.replace("£", ""))

print(f"Title: {title}")
print(f"Author: {author}")
print(f"Price: ${price:.2f}")
```

**Expected output:**

```
Title: The Hobbit
Author: J.R.R. Tolkien
Price: $15.99
```

### Example 2: Processing Multiple Records With the Combo

```python
# Multiple records
records = [
    "  The Hobbit  |  J.R.R. TOLKIEN  |  £15.99  ",
    "  1984|GEORGE ORWELL|£14.50",
    " Dune | Frank HERBERT  |  £16.75",
]

books = []  # Store cleaned data

for record in records:
    # Clean and split
    fields = record.strip().split("|")
    fields = [f.strip() for f in fields]  # Clean each field

    # Extract and normalize
    title = fields[0].strip()
    author = fields[1].title()  # Normalize to Title Case
    price = float(fields[2].replace("£", ""))

    # Store as a dictionary
    books.append({
        "title": title,
        "author": author,
        "price": price
    })

# Print the cleaned results
for book in books:
    print(f"{book['title']} by {book['author']}: ${book['price']:.2f}")
```

**Expected output:**

```
The Hobbit by J.R.R. Tolkien: $15.99
1984 by George Orwell: $14.50
Dune by Frank Herbert: $16.75
```

### Example 3: Validation With Regex

```python
import re

def is_valid_price(price_str):
    """Check if a string looks like a valid price."""
    # Pattern: £ or $, followed by digits, optional decimal point and 2 digits
    pattern = r"[£$]\d+(\.\d{2})?"
    return re.match(pattern, price_str) is not None

def is_valid_isbn(isbn_str):
    """Check if a string looks like an ISBN (simplified)."""
    # ISBNs are often 10 or 13 digits, possibly with hyphens
    pattern = r"\d{10}|\d{13}|\d{3}-\d{10}"
    return re.match(pattern, isbn_str) is not None

# Test validation
prices = ["£15.99", "$20", "15.99", "£abc"]
print("Prices:")
for price in prices:
    status = "✓" if is_valid_price(price) else "✗"
    print(f"  {status} {price}")

isbns = ["978-3-16-148410", "9781234567890", "123abc789"]
print("\nISBNs:")
for isbn in isbns:
    status = "✓" if is_valid_isbn(isbn) else "✗"
    print(f"  {status} {isbn}")
```

**Expected output:**

```
Prices:
  ✓ £15.99
  ✗ $20
  ✗ 15.99
  ✗ £abc

ISBNs:
  ✓ 978-3-16-148410
  ✓ 9781234567890
  ✗ 123abc789
```

### Example 4: Extracting Information With Regex

```python
import re

# Extract all numbers (like prices, quantities)
text = "Order: 3 copies of book (ISBN: 978-3-16-148410) at £15.99 each"

prices = re.findall(r"£\d+\.\d{2}", text)
print(f"Prices found: {prices}")

isbns = re.findall(r"\d{3}-\d{2}-\d{2}-\d{6}", text)
print(f"ISBNs found: {isbns}")

numbers = re.findall(r"\d+", text)
print(f"All numbers: {numbers}")
```

**Expected output:**

```
Prices found: ['£15.99']
ISBNs found: ['978-3-16-148410']
All numbers: ['3', '978', '3', '16', '148410', '15', '99']
```

## ⚠️ Common Mistakes

### Mistake 1: Forgetting That Strings Are Immutable

```python
# Wrong approach
name = "alice"
name[0] = "A"  # Error! Can't modify a string directly

# TypeError: 'str' object does not support item assignment
```

**Fix**: Create a new string

```python
# Correct
name = "alice"
name = name[0].upper() + name[1:]  # Build a new string
print(name)  # Output: Alice
```

### Mistake 2: Off-by-One Error in Slicing

```python
text = "Python"

# Wrong — this gets up to (but NOT including) position 3
result = text[0:3]
print(result)  # Output: Pyt (not Pyth)

# Correct — go up to position 4
result = text[0:4]
print(result)  # Output: Pyth
```

### Mistake 3: Assuming `split()` Cleans Whitespace

```python
record = "  apple  |  banana  |  cherry  "

# Wrong — each field still has whitespace!
fields = record.split("|")
print(fields)  # Output: ['  apple  ', '  banana  ', '  cherry  ']

# Correct — clean AFTER splitting
fields = record.split("|")
fields = [f.strip() for f in fields]
print(fields)  # Output: ['apple', 'banana', 'cherry']
```

### Mistake 4: Using `.index()` Without Checking

```python
text = "Hello"

# Wrong — if 's' is not in text, this crashes!
position = text.index("s")  # ValueError: substring not found

# Correct — use .find() which returns -1 if not found
position = text.find("s")
if position != -1:
    print(f"Found at {position}")
else:
    print("Not found")
```

### Mistake 5: Forgetting `r""` for File Paths

```python
# Wrong — backslash is interpreted as escape character
path = "C:\Users\alice\data.csv"
# This might become: C:\Users\alice\data.csv (or have issues)

# Correct — use raw string
path = r"C:\Users\alice\data.csv"
print(path)  # Output: C:\Users\alice\data.csv
```

---

## ✅ Exercises

### Exercise 1 (Easy): Extract and Clean

**Problem**: You have email addresses with extra whitespace. Clean them and extract the domain.

```python
emails = [
    "  alice@example.com  ",
    "bob@COMPANY.ORG  ",
    "  charlie@test.co.uk",
]

# For each email:
# 1. Remove whitespace
# 2. Convert to lowercase
# 3. Extract the domain (the part after @)

# Expected output:
# alice@example.com — domain: example.com
# bob@company.org — domain: company.org
# charlie@test.co.uk — domain: test.co.uk
```

**Solution**:

```python
emails = [
    "  alice@example.com  ",
    "bob@COMPANY.ORG  ",
    "  charlie@test.co.uk",
]

for email in emails:
    # Clean: remove whitespace and normalize to lowercase
    clean_email = email.strip().lower()

    # Extract domain: everything after the @
    domain = clean_email.split("@")[1]

    print(f"{clean_email} — domain: {domain}")
```

### Exercise 2 (Medium): Parse and Validate

**Problem**: You have phone numbers in various formats. Normalize them and validate that they're real.

```python
phones = [
    "555-1234",
    "555.1234",
    "5551234",
    "555-12-34",
    "(555) 1234",
]

# Expected output (only valid formats accepted):
# 555-1234 → VALID
# 555.1234 → VALID
# 5551234 → VALID
# 555-12-34 → INVALID
# (555) 1234 → INVALID
```

**Solution**:

```python
import re

phones = [
    "555-1234",
    "555.1234",
    "5551234",
    "555-12-34",
    "(555) 1234",
]

for phone in phones:
    # Pattern: 3 digits, then separator, then 4 digits
    # Separator can be: dash, dot, or nothing
    if re.match(r"\d{3}[-.]?\d{4}", phone):
        print(f"{phone} → VALID")
    else:
        print(f"{phone} → INVALID")
```

### Exercise 3 (Hard): Data Extraction and Transformation

**Problem**: Extract structured data from a messy log line and transform it.

```python
log_line = "2024-03-17 14:35:42 | User: alice_smith | Action: login | Status: SUCCESS"

# Extract:
# 1. Date and time
# 2. Username
# 3. Action performed
# 4. Status

# Then output as: [YYYY-MM-DD] alice_smith performed login (SUCCESS)
```

**Solution**:

```python
import re

log_line = "2024-03-17 14:35:42 | User: alice_smith | Action: login | Status: SUCCESS"

# Extract each field
date_match = re.search(r"(\d{4}-\d{2}-\d{2})", log_line)
date = date_match.group(1) if date_match else "UNKNOWN"

user_match = re.search(r"User: (\w+)", log_line)
user = user_match.group(1) if user_match else "UNKNOWN"

action_match = re.search(r"Action: (\w+)", log_line)
action = action_match.group(1) if action_match else "UNKNOWN"

status_match = re.search(r"Status: (\w+)", log_line)
status = status_match.group(1) if status_match else "UNKNOWN"

# Format the output
output = f"[{date}] {user} performed {action} ({status})"
print(output)
```

---

## 🏗️ Mini Project: Book Data Cleaner

### Project Overview

You'll write a Python script that:

1. Reads a messy text file of book records (pipe-separated: Title|Author|Price)
2. Cleans every field using string methods
3. Validates prices and authors with regex
4. Writes clean data to a new CSV file
5. Generates a report of what was cleaned

### Step 1: Create the Input File

Create `messy_books.txt`:

```
  The Hobbit  |  J.R.R. TOLKIEN  |  £15.99
  1984|GEORGE ORWELL|£14.50
 Dune | Frank HERBERT  |  £16.75
  Harry Potter  |  JOANNE ROWLING  |  £12.99
  To Kill a MockingBird  |  HARPER LEE|£13.75
  the caThe Catch-22|JOSEPH HELLER|£18.50
  Foundation  |  ISAAC ASIMOV  |  invalid_price
```

### Step 2: Write the Cleaner Script

Create `clean_books.py`:

```python
import re  # For regex validation

def extract_and_clean_book(record):
    """
    Take a messy book record and return clean data.
    Returns a dict with cleaned fields and validation status.
    """

    # Step 1: Clean overall whitespace
    record = record.strip()

    # Step 2: Split on pipe
    fields = record.split("|")
    if len(fields) != 3:
        # Skip records that don't have exactly 3 fields
        return None

    # Step 3: Clean each field
    title = fields[0].strip()  # Remove whitespace
    author = fields[1].strip()  # Remove whitespace
    price_raw = fields[2].strip()  # Remove whitespace

    # Step 4: Normalize title (capitalize first letter of each word)
    title = title.title()

    # Step 5: Normalize author (from ALL CAPS to Title Case)
    author = author.title()

    # Step 6: Validate and extract price
    # Pattern: £ followed by digits, optional decimal and 2 digits
    price_match = re.match(r"£(\d+(?:\.\d{2})?)", price_raw)

    if not price_match:
        # Price didn't match the pattern — this record is invalid
        return {
            "title": title,
            "author": author,
            "price": None,  # Invalid price
            "valid": False,
            "reason": f"Invalid price format: {price_raw}"
        }

    # Extract the price value
    price = float(price_match.group(1))

    # Step 7: Return cleaned record
    return {
        "title": title,
        "author": author,
        "price": price,
        "valid": True,
        "reason": "OK"
    }

# Main program

# Step 1: Read the messy file
with open("messy_books.txt", "r") as infile:
    lines = infile.readlines()

# Step 2: Process each record
clean_books = []  # Will store valid books
problems = []  # Will store invalid records

for line in lines:
    result = extract_and_clean_book(line)

    if result is None:
        problems.append(f"Skipped (wrong format): {line.strip()}")
    elif result["valid"]:
        clean_books.append(result)
    else:
        problems.append(f"{result['title']} — {result['reason']}")

# Step 3: Write clean data to CSV
with open("clean_books.csv", "w") as outfile:
    # Write header
    outfile.write("Title,Author,Price (£)\n")

    # Write each book
    for book in clean_books:
        # Use f-string to format the line
        line = f"{book['title']},{book['author']},{book['price']:.2f}\n"
        outfile.write(line)

# Step 4: Generate a report
print("=" * 50)
print("BOOK DATA CLEANING REPORT")
print("=" * 50)
print(f"Total records processed: {len(lines)}")
print(f"Valid books written: {len(clean_books)}")
print(f"Problems found: {len(problems)}")

if problems:
    print("\nProblems encountered:")
    for problem in problems:
        print(f"  ⚠️  {problem}")

print("\nClean data written to: clean_books.csv")
print("=" * 50)
```

### Step 3: Run and Test

```bash
python3 clean_books.py
```

**Expected output:**

```
==================================================
BOOK DATA CLEANING REPORT
==================================================
Total records processed: 7
Valid books written: 5
Problems found: 2

Problems encountered:
  ⚠️  Skipped (wrong format): the caThe Catch-22|JOSEPH HELLER|£18.50
  ⚠️  Foundation — Invalid price format: invalid_price

Clean data written to: clean_books.csv
==================================================
```

Examine `clean_books.csv`:

```
Title,Author,Price (£)
The Hobbit,J.R.R. Tolkien,15.99
1984,George Orwell,14.50
Dune,Frank Herbert,16.75
Harry Potter,Joanne Rowling,12.99
To Kill A Mockingbird,Harper Lee,13.75
```

### Key Points in This Project

```python
# String methods we used:
record.strip()              # Remove whitespace
fields = record.split("|")  # Split on delimiter
title.title()               # Normalize capitalization

# Regex validation:
price_match = re.match(r"£(\d+(?:\.\d{2})?)", price_raw)
# This pattern matches £ followed by numbers and decimals

# File I/O from Python Essentials:
with open("file.txt", "r") as f:
    lines = f.readlines()

# List operations:
clean_books.append(record)  # Add to list

# Formatting in f-strings:
f"{book['price']:.2f}"  # Format as 2 decimal places
```

All of this combines what you learned in Python Essentials with the string techniques from this module.

---

## 🔗 What's Next

You've now mastered string manipulation — a crucial skill for cleaning and processing real data.

In the next sub-module of Module 1, **Lists and Loops (Deep Dive)**, you'll learn how to:

- Master list methods and understand the shallow copy trap
- Work with tuples, dictionaries, and sets
- Use lambda functions for concise operations
- Group and transform data structures efficiently

You'll recognize that the book cleaning you just did produces dictionaries. In the Deep Dive module, you'll learn to work with complex dictionaries and lists of records — the exact structure used when loading data in Phase 1.

---

## 📚 Quick Reference

| Task           | Code                       | Example                                 |
| -------------- | -------------------------- | --------------------------------------- |
| Index          | `s[i]`                     | `"hello"[1]` → `"e"`                    |
| Slice          | `s[start:stop:step]`       | `"hello"[1:4]` → `"ell"`                |
| Lowercase      | `.lower()`                 | `"HELLO".lower()` → `"hello"`           |
| Remove spaces  | `.strip()`                 | `"  hello  ".strip()` → `"hello"`       |
| Replace        | `.replace(old, new)`       | `"hello".replace("l", "r")` → `"herro"` |
| Split          | `.split(delim)`            | `"a,b".split(",")` → `["a", "b"]`       |
| Join           | `sep.join(list)`           | `",".join(["a", "b"])` → `"a,b"`        |
| Find position  | `.find(sub)`               | `"hello".find("l")` → `2`               |
| Check contains | `sub in s`                 | `"e" in "hello"` → `True`               |
| Format         | `f"{var}"`                 | `f"Hello {name}"` → `Hello Alice`       |
| Regex search   | `re.search(pattern, s)`    | `re.search(r"\d+", "a1b2")`             |
| Regex replace  | `re.sub(pattern, repl, s)` | `re.sub(r"\d", "X", "a1b2")` → `aXbX`   |
