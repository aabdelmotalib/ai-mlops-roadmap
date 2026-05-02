---
tags:
  - Beginner
  - Phase 0
  - Debugging
  - Best Practices
  - Testing
---

# Sub-Module: Debugging and Best Practices

**Part of Module 1: Python Essentials**  
**Phase 0: Baseline Setup**

---

## 🎯 What You Will Learn

By the end of this sub-module, you will:

- Understand Python's error types and how to read tracebacks
- Apply a systematic debugging process to any problem
- Use `print()` debugging for quick problem isolation
- Use the Python debugger (pdb) for deep inspection
- Write robust code with try/except/else/finally
- Follow PEP 8 style guidelines for readable code
- Use code linting (flake8) to catch issues automatically
- Write unit tests with pytest to verify your code works
- Refactor messy code into clean, professional-grade code
- Build confidence that your code is correct before pushing to production

---

## 🧠 Concept Explained: Debugging Is a Skill, Not a Superpower

### The Analogy: A Plumber's Troubleshooting Process

Imagine a plumber is called to a house with a water leak. The plumber doesn't panic or guess randomly. They follow a **process**:

1. **Locate the leak** — Find exactly where the water is coming from
2. **Understand the cause** — Is it a loose fitting? A crack? A broken seal?
3. **Test their diagnosis** — Turn on the water and watch what happens
4. **Apply the fix** — Tighten, replace, or reseal
5. **Verify it works** — Test again to confirm the leak is gone

**Debugging is exactly this same process.** Every time you have a bug, follow these five steps:

1. **Read the error message fully** — Python usually tells you exactly what's wrong
2. **Find the line number** — Go directly to that line
3. **Understand what was supposed to happen** — Review your logic
4. **Test your understanding** — Print variables, inspect state
5. **Apply the fix** — Make the minimum change necessary
6. **Verify it works** — Run all related tests

Debugging is not mysterious. It's a skill you can master with practice.

---

## 🔍 How It Works: Reading Tracebacks

### Anatomy of a Traceback

When Python hits an error, it shows you a traceback. Let's learn to read it:

```python
# Broken code example:
def calculate_average(numbers):
    total = sum(numbers)
    average = total / len(numbers)
    return average

def process_data(data):
    avg = calculate_average(data)
    return avg * 2

# Call it with bad data
result = process_data([])  # Empty list — division by zero!
```

**The traceback you'd see:**

```
Traceback (most recent call last):
  File "script.py", line 15, in <module>
    result = process_data([])
  File "script.py", line 10, in process_data
    avg = calculate_average(data)
  File "script.py", line 3, in calculate_average
    average = total / len(numbers)
ZeroDivisionError: division by zero
```

**How to read it (from bottom to top)**:

- **Bottom line** (`ZeroDivisionError...`): This is THE ERROR. Python tells you the type and reason.
- **Next lines** (from bottom up): The "call stack" — where the error happened and who called it
- **File and line number**: Exactly where to look in your code
- **"most recent call last"**: Means we're reading the stack from earliest to latest function call

**In this example**: Line 15 called `process_data([])`, which called `calculate_average` on line 10, which tried to divide on line 3. That division failed.

---

## 🛠️ Step-by-Step Guide: The Debugging Process

### Step 1: Read the Error Message (Fully!)

```python
# Common mistake: only reading the last line
# Correct approach: read the ENTIRE traceback

# Bad code:
user_input = "25"
age = int(user_input)  # This is fine
salary_str = "hello"  # This is NOT a number!
salary = int(salary_str)  # This will crash
```

**The error you see:**

```
ValueError: invalid literal for int() with base 10: 'hello'
```

The error tells you:

- **What went wrong**: `ValueError` (wrong value for conversion)
- **Which line failed**: `int(salary_str)`
- **Why**: 'hello' is not a valid integer

### Step 2: Find the Line Number and Go There

Always go to the line number the traceback mentions. Don't guess.

```python
# Line 5 (where the error is)
salary = int("hello")
# What happened before this line?
user_input = input("Enter salary: ")
# Is user_input what we expected?
```

### Step 3: Print Variables to Understand State

Use print() statements to see what your variables actually contain:

```python
# Debug version (adding print statements)
user_input = "25"
age = int(user_input)
print(f"DEBUG: age = {age}, type = {type(age)}")

salary_str = "hello"
print(f"DEBUG: salary_str = {salary_str}, type = {type(salary_str)}")

salary = int(salary_str)  # This will crash with our debug info printed
```

**Best practice**: Print the type AND the value:

```python
print(f"DEBUG: {type(x)} x = {x}")
```

### Step 4: Isolate the Problem

Create a minimal version that reproduces the error:

```python
# Full script (complicated)
# Don't debug the whole thing at once

# Minimal reproduction (simple)
numbers = []
total = sum(numbers)
average = total / len(numbers)  # CRASH: empty list
```

This tiny version shows the exact problem without distractions.

### Step 5: Apply the Fix

Once you know the problem, think about the fix:

```python
# Problem: dividing by zero with empty list
# Solution: check if list is empty before dividing

def calculate_average(numbers):
    if len(numbers) == 0:  # New guard clause
        return 0  # Or raise an error, or return None

    total = sum(numbers)
    average = total / len(numbers)
    return average

# Test it
print(calculate_average([]))  # Output: 0
print(calculate_average([1, 2, 3]))  # Output: 2.0
```

---

## 🛠️ Types of Errors (And What They Mean)

### SyntaxError

Python cannot even read the code:

```python
# Missing colon
if x > 5
    print("big")

# Error: SyntaxError: invalid syntax
```

**How to fix**: Check for colons, quotes, parentheses, indentation.

### NameError

Using a variable that doesn't exist:

```python
print(score)  # Never defined 'score'

# Error: NameError: name 'score' is not defined
```

**How to fix**: Check spelling, make sure the variable is assigned before use.

### TypeError

Wrong type for an operation:

```python
x = "hello"
result = x + 5  # Can't add string + integer

# Error: TypeError: can only concatenate str (not "int") to str
```

**How to fix**: Convert to the same type, or check types before operations.

### ValueError

Right type, wrong value:

```python
age = int("not_a_number")

# Error: ValueError: invalid literal for int() with base 10: 'not_a_number'
```

**How to fix**: Validate input before converting.

### IndexError

Asking for a list position that doesn't exist:

```python
numbers = [1, 2, 3]
print(numbers[10])  # Only positions 0, 1, 2 exist

# Error: IndexError: list index out of range
```

**How to fix**: Check the list length, use safe access (`list[i] if i < len(list) else None`).

### KeyError

Asking for a dict key that doesn't exist:

```python
student = {"name": "Alice"}
print(student["age"])  # Key "age" doesn't exist

# Error: KeyError: 'age'
```

**How to fix**: Use `.get(key, default)` instead of `dict[key]`.

### AttributeError

Calling a method that doesn't exist:

```python
numbers = [1, 2, 3]
print(numbers.lowercase())  # Lists don't have a .lowercase() method

# Error: AttributeError: 'list' object has no attribute 'lowercase'
```

**How to fix**: Check the object's actual methods (use `dir(object)` or read docs).

### ImportError

Module not found:

```python
import nonexistent_module

# Error: ModuleNotFoundError: No module named 'nonexistent_module'
```

**How to fix**: Install the module, fix the spelling, or check the import path.

---

## 💻 Code Examples: Debugging in Action

### Example 1: A Real, Broken Script

Let's say you wrote this word counter script and it's not working:

```python
# BROKEN CODE (do not run yet)
def count_words_in_file(filename):
    words_total = 0
    lines_total = 0

    with open(filename, "r") as file:
        content = file.read()

    lines = content.split("\n")
    lines_total = len(lines)

    for line in lines:
        words = line.split(" ")
        words_total = words_total + len(words)

    return words_total, lines_total

# Test it
result = count_words_in_file("sample.txt")
print(result)
```

**You create sample.txt:**

```
Hello world
This is a test

Final line
```

**When you run it, you get:**

```
(18, 5)
```

But you count manually: 9 words, 4 lines (excluding the empty line). Something's wrong!

### Example 2: Debug Using Print Statements

Add print statements to understand what's happening:

```python
def count_words_in_file(filename):
    words_total = 0
    lines_total = 0

    with open(filename, "r") as file:
        content = file.read()

    lines = content.split("\n")
    print(f"DEBUG: lines = {lines}")  # See what we're splitting
    lines_total = len(lines)
    print(f"DEBUG: lines_total = {lines_total}")

    for line in lines:
        words = line.split(" ")
        print(f"DEBUG: line = '{line}' → words = {words}")
        words_total = words_total + len(words)

    return words_total, lines_total

result = count_words_in_file("sample.txt")
print(result)
```

**Output:**

```
DEBUG: lines = ['Hello world', 'This is a test', '', 'Final line']
DEBUG: lines_total = 4
DEBUG: line = 'Hello world' → words = ['Hello', 'world']
DEBUG: line = 'This is a test' → words = ['This', 'is', 'a', 'test']
DEBUG: line = '' → words = ['']  ← EMPTY LINE SPLITS TO ['']!
DEBUG: line = 'Final line' → words = ['Final', 'line']
(18, 5)
```

**Aha!** The empty line splits to `['']` (a list with one empty string), not `[]`. That's why the count is off. We're counting empty strings as words.

### Example 3: Apply the Fix

```python
def count_words_in_file(filename):
    words_total = 0
    lines_total = 0

    with open(filename, "r") as file:
        content = file.read()

    lines = content.split("\n")
    # Count only non-empty lines
    lines_total = len([line for line in lines if line.strip()])

    for line in lines:
        # Skip empty lines when counting words
        if not line.strip():
            continue

        words = line.split(" ")
        words_total = words_total + len(words)

    return words_total, lines_total

result = count_words_in_file("sample.txt")
print(result)  # Output: (9, 4)
```

Now it returns (9, 4) — correct!

### Example 4: Using the Python Debugger (pdb)

For complex issues, use the debugger. Drop this line where you want to pause:

```python
def count_words_in_file(filename):
    words_total = 0
    lines_total = 0

    with open(filename, "r") as file:
        content = file.read()

    lines = content.split("\n")
    lines_total = len(lines)

    for line in lines:
        breakpoint()  # Pause here — Python 3.7+
        # Or: import pdb; pdb.set_trace()

        words = line.split(" ")
        words_total = words_total + len(words)

    return words_total, lines_total
```

When you run it:

```bash
python3 script.py
```

You get a debugger prompt:

```
> script.py(15)count_words_in_file()
-> words = line.split(" ")
(Pdb) p line  # Print the current line variable
'Hello world'
(Pdb) p words  # Print what split produced
['Hello', 'world']
(Pdb) n  # Next — execute this line and move to the next
(Pdb) c  # Continue — resume normal execution
(Pdb) q  # Quit — exit the debugger
(Pdb) l  # List — show code around this point
(Pdb) h  # Help — show all commands
```

---

## ✅ Clean Code: PEP 8 Style Guide

PEP 8 is Python's official style guide. Following it makes code **readable, maintainable, and professional**.

### Before: Messy Code

```python
# Bad style (hard to read)
def countwords(f):
    w=0
    l=0
    with open(f,"r")as file:content=file.read()
    lines=content.split("\n")
    l=len(lines)
    for line in lines:words=line.split(" ");w=w+len(words)
    return w,l
```

### After: Clean Code

```python
# Good style (easy to read)
def count_words_in_file(filename):
    """Count total words and lines in a file."""
    # Initialize counters
    word_count = 0
    line_count = 0

    # Read the file
    with open(filename, "r") as file:
        content = file.read()

    # Split into lines
    lines = content.split("\n")
    line_count = len(lines)

    # Count words in each line
    for line in lines:
        words = line.split(" ")
        word_count = word_count + len(words)

    return word_count, line_count
```

### PEP 8 Key Rules

| Rule                             | Example                                               |
| -------------------------------- | ----------------------------------------------------- |
| Variable names: `snake_case`     | `user_name`, `total_score`                            |
| Function names: `verb_noun`      | `get_data()`, `save_file()`                           |
| Class names: `PascalCase`        | `Student`, `DataProcessor`                            |
| Line length: max 79 characters   | Break long lines                                      |
| Indentation: 4 spaces            | Never mix tabs/spaces                                 |
| Blank lines: 2 between functions | Separate your functions clearly                       |
| Comments: explain WHY not WHAT   | `# Prevent division by zero` not `# Check if len > 0` |
| Docstrings: on every function    | """Describe what the function does."""                |

### Docstrings Example

```python
def calculate_average(numbers):
    """
    Calculate the average of a list of numbers.

    Args:
        numbers: A list of integers or floats

    Returns:
        The average as a float, or 0 if the list is empty

    Raises:
        TypeError: If numbers contains non-numeric values
    """
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)
```

---

## 🔧 Tool 1: Linting With flake8

Linting automatically finds style problems and bugs:

```bash
# Install flake8
pip install flake8

# Check a file
flake8 script.py

# Check all files in a directory
flake8 .
```

**Example output:**

```
script.py:5:1: E302 expected 2 blank lines, found 1
script.py:10:80: E501 line too long (92 > 79 characters)
script.py:15:1: F841 local variable 'unused_var' is assigned but never used
```

**Reading the output**: `file:line:column: ERROR message`

Common errors:

- `E302`: Need blank lines between functions
- `E501`: Line too long
- `F841`: Unused variable
- `W293`: Blank line with whitespace

### Auto-fix With black

Black automatically reformats your code to follow PEP 8:

```bash
pip install black

# Auto-format a file
black script.py

# Auto-format a directory
black .
```

---

## 🧪 Tool 2: Testing With pytest

Testing is how professionals verify code works. Even one simple test catches 80% of bugs.

### Write Getaway, Unit Tests

```python
# save_file_word_counter.py
def count_words_in_file(filename):
    """Count words and lines in a file."""
    word_count = 0
    line_count = 0

    with open(filename, "r") as file:
        lines = file.readlines()

    line_count = len(lines)

    for line in lines:
        # Skip empty lines
        if line.strip():
            words = line.split()
            word_count += len(words)

    return word_count, line_count
```

Now write tests in `test_word_counter.py`:

```python
import pytest
from word_counter import count_words_in_file

# Create test files for testing
@pytest.fixture
def temp_file(tmp_path):
    """Create a temporary test file."""
    file = tmp_path / "test.txt"
    file.write_text("Hello world\nThis is a test\n")
    return str(file)

def test_normal_file(temp_file):
    """Test with normal input."""
    words, lines = count_words_in_file(temp_file)
    assert words == 5
    assert lines == 2

def test_empty_file(tmp_path):
    """Test with empty file."""
    file = tmp_path / "empty.txt"
    file.write_text("")
    words, lines = count_words_in_file(str(file))
    assert words == 0
    assert lines == 0

def test_file_not_found():
    """Test with non-existent file."""
    with pytest.raises(FileNotFoundError):
        count_words_in_file("nonexistent_file.txt")
```

### Run Tests

```bash
pip install pytest

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run a specific test
pytest test_word_counter.py::test_normal_file
```

**Output:**

```
test_word_counter.py::test_normal_file PASSED
test_word_counter.py::test_empty_file PASSED
test_word_counter.py::test_file_not_found PASSED

====== 3 passed in 0.12s ======
```

### Why Tests Matter

Once you write tests:

- You can refactor code confidently (tests warn if you broke something)
- You catch bugs before users do
- You document how the code should work
- You sleep better knowing your code works

---

## 💻 Code Example: Before and After Refactoring

### Before: Messy Word Counter

```python
def wc(f):
    w=0;l=0;ls=[]
    try:
        with open(f)as fi:ls=fi.readlines()
    except:
        return None
    l=len(ls)
    for line in ls:
        if len(line.strip())>0:w+=len(line.split())
    return w,l

# No docstring, no error handling, hard to read
result=wc("data.txt")
if result:print(result)
```

### After: Clean Word Counter

```python
def count_words_in_file(filename):
    """
    Count words and lines in a text file.

    Args:
        filename: Path to the file

    Returns:
        Tuple of (word_count, line_count)

    Raises:
        FileNotFoundError: If file doesn't exist
        PermissionError: If file cannot be read
    """
    word_count = 0
    line_count = 0

    # Read file with proper error handling
    try:
        with open(filename, "r", encoding="utf-8") as file:
            lines = file.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filename}")
    except PermissionError:
        raise PermissionError(f"Permission denied: {filename}")

    line_count = len(lines)

    # Count words in non-empty lines
    for line in lines:
        if line.strip():  # Skip empty lines
            words = line.split()
            word_count += len(words)

    return word_count, line_count


# Usage with proper error handling
if __name__ == "__main__":
    try:
        words, lines = count_words_in_file("data.txt")
        print(f"Words: {words}, Lines: {lines}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except PermissionError as e:
        print(f"Error: {e}")
```

**Differences**:

- Clear, descriptive names instead of shorthand
- Full docstring explaining what it does
- Proper error handling (catches specific exceptions)
- Comments explaining the why, not the what
- Follows PEP 8 conventions

---

## ⚠️ Common Debugging Mistakes

### Mistake 1: Print Debugging Is Bad

**Wrong thinking**: "I should use a real debugger instead of print"

**Truth**: Print statements are fine for quick debugging. Use whichever tool fits the situation.

### Mistake 2: Catching All Exceptions

```python
# Wrong — hides real problems!
try:
    result = int(user_input)
except:
    result = 0
```

**Better** — catch specific exceptions:

```python
# Correct — only catch what you expect
try:
    result = int(user_input)
except ValueError:
    print("Please enter a number")
    result = 0
```

### Mistake 3: Assuming Variable Values

Don't assume what your variable contains. Print it:

```python
# Wrong — assuming age is a number
age = user_input  # Could be "25" (string) or 25 (number)
result = age + 5  # Might crash!

# Correct — verify first
print(f"age type: {type(age)}, value: {age}")
age = int(age)  # Convert if needed
result = age + 5
```

---

## ✅ Exercises

### Exercise 1 (Easy): Find and Fix the Bug

**Problem**: This function should return the maximum value, but it's broken.

```python
def find_max(numbers):
    max_value = numbers[0]
    for num in numbers:
        if num > max_value:
            max_value = num
    return max_value

# Test
print(find_max([]))  # Crashes!
```

**Solution**: Add a guard clause

```python
def find_max(numbers):
    """Find the maximum value in a list."""
    if not numbers:  # Check for empty list
        raise ValueError("List cannot be empty")

    max_value = numbers[0]
    for num in numbers:
        if num > max_value:
            max_value = num
    return max_value

# Test
try:
    print(find_max([]))
except ValueError as e:
    print(f"Error: {e}")

print(find_max([3, 1, 4, 1, 5]))  # Output: 5
```

### Exercise 2 (Medium): Clean Code Refactoring

**Problem**: Make this code follow PEP 8 and add tests.

```python
def avg(l):
 total=0
 for x in l:total=total+x
 return total/len(l)
```

**Solution**:

```python
# File: average.py
def calculate_average(numbers):
    """Calculate average of a list of numbers."""
    if not numbers:
        raise ValueError("List cannot be empty")
    return sum(numbers) / len(numbers)


# File: test_average.py
import pytest
from average import calculate_average

def test_calculate_average_normal():
    """Test with normal input."""
    assert calculate_average([1, 2, 3]) == 2.0

def test_calculate_average_single():
    """Test with one number."""
    assert calculate_average([5]) == 5.0

def test_calculate_average_empty():
    """Test with empty list."""
    with pytest.raises(ValueError):
        calculate_average([])
```

### Exercise 3 (Hard): Debug a Complex Script

**Problem**: This script reads a CSV file and calculates statistics, but it has bugs.

```python
import csv

def process_csv(filename):
    """Process CSV file and return statistics."""
    total = 0
    count = 0

    with open(filename) as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == "name":  # Skip header
                continue
            price = float(row[2])  # Get price column
            total = total + price
            count = count + 1

    average = total / count
    return {"total": total, "average": average}

# Test
result = process_csv("products.csv")
print(result)
```

**Issues**:

1. No error handling for missing files
2. No error handling for bad data
3. Crashes if CSV is empty/only headers
4. Doesn't handle encoding

**Solution**:

```python
import csv

def process_csv(filename):
    """
    Process CSV file and return price statistics.

    Args:
        filename: Path to CSV file (columns: name, description, price)

    Returns:
        Dict with 'total', 'average', 'count'

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If no valid price rows found
    """
    total = 0
    count = 0

    try:
        with open(filename, encoding="utf-8") as f:
            reader = csv.reader(f)

            # Skip header row
            next(reader, None)

            for row in reader:
                # Skip empty rows
                if not row or len(row) < 3:
                    continue

                try:
                    # Try to parse the price
                    price = float(row[2])

                    # Only count positive prices
                    if price >= 0:
                        total += price
                        count += 1
                except (ValueError, IndexError) as e:
                    # Log but continue processing
                    print(f"Warning: Could not parse price from row: {row}")
                    continue

    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filename}")

    if count == 0:
        raise ValueError("No valid price rows found in CSV")

    average = total / count
    return {
        "total": round(total, 2),
        "average": round(average, 2),
        "count": count
    }


# Test with error handling
try:
    result = process_csv("products.csv")
    print(result)
except (FileNotFoundError, ValueError) as e:
    print(f"Error: {e}")
```

---

## 🏗️ Mini Project: Refactored Word Counter (The Capstone)

This is the capstone of the entire Python Essentials section. You'll take a basic script and refactor it to professional standards.

### Part 1: Original (Messy) Version

```python
# word_counter_v1.py (MESSY)
f=input("File: ")
w=0;l=0
with open(f)as file:
 for line in file:
  l=l+1
  w=w+len(line.split())
print(str(w)+" words, "+str(l)+" lines")
```

### Part 2: Refactored Version

Create `word_counter.py`:

```python
"""
A professional word counter utility.

This module provides tools to count words and lines in text files,
with proper error handling and clean code practices.
"""

def count_words_in_file(filename):
    """
    Count words and lines in a text file.

    This function reads a file and counts the total number of words
    and lines. Empty lines are counted, but lines with only whitespace
    are skipped when counting words.

    Args:
        filename (str): Path to the file to analyze

    Returns:
        dict: A dictionary with keys 'words' and 'lines'

    Raises:
        FileNotFoundError: If the file does not exist
        PermissionError: If the file cannot be read
        UnicodeDecodeError: If the file is not valid UTF-8 text

    Example:
        >>> result = count_words_in_file("sample.txt")
        >>> print(f"Words: {result['words']}, Lines: {result['lines']}")
        Words: 150, Lines: 25
    """
    word_count = 0
    line_count = 0

    try:
        # Open file with explicit encoding
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                # Count every line
                line_count += 1

                # Count words only in non-empty lines
                if line.strip():
                    words = line.split()
                    word_count += len(words)

    except FileNotFoundError:
        raise FileNotFoundError(f"File '{filename}' was not found")
    except PermissionError:
        raise PermissionError(f"Permission denied reading '{filename}'")
    except UnicodeDecodeError:
        raise UnicodeDecodeError(
            "utf-8",
            filename,
            0,
            1,
            "File is not valid UTF-8 text"
        )

    return {"words": word_count, "lines": line_count}


def display_results(filename):
    """
    Count and display word/line statistics for a file.

    Args:
        filename (str): Path to the file
    """
    try:
        result = count_words_in_file(filename)
        words = result["words"]
        lines = result["lines"]
        print(f"{filename}: {words} words, {lines} lines")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except PermissionError as e:
        print(f"Error: {e}")
    except UnicodeDecodeError as e:
        print(f"Error: File is not valid text")


if __name__ == "__main__":
    # When run as a script
    filename = input("Enter filename: ")
    display_results(filename)
```

### Part 3: Tests

Create `test_word_counter.py`:

```python
"""
Unit tests for the word counter module.
"""

import pytest
import tempfile
from pathlib import Path
from word_counter import count_words_in_file


@pytest.fixture
def normal_file(tmp_path):
    """Create a test file with normal content."""
    file = tmp_path / "normal.txt"
    file.write_text("Hello world\nThis is a test\n")
    return str(file)


@pytest.fixture
def empty_file(tmp_path):
    """Create an empty test file."""
    file = tmp_path / "empty.txt"
    file.write_text("")
    return str(file)


@pytest.fixture
def whitespace_file(tmp_path):
    """Create a file with only whitespace."""
    file = tmp_path / "whitespace.txt"
    file.write_text("\n\n   \n")
    return str(file)


class TestCountWords:
    """Test suite for count_words_in_file function."""

    def test_normal_file(self, normal_file):
        """Test with normal input file."""
        result = count_words_in_file(normal_file)
        assert result["words"] == 5  # "Hello", "world", "This", "is", "a", "test"
        assert result["lines"] == 2

    def test_empty_file(self, empty_file):
        """Test with empty file."""
        result = count_words_in_file(empty_file)
        assert result["words"] == 0
        assert result["lines"] == 0

    def test_whitespace_only(self, whitespace_file):
        """Test with whitespace only."""
        result = count_words_in_file(whitespace_file)
        assert result["words"] == 0
        assert result["lines"] == 4  # 4 lines, but no words

    def test_nonexistent_file(self):
        """Test with non-existent file."""
        with pytest.raises(FileNotFoundError):
            count_words_in_file("nonexistent_file_xyz.txt")


class TestPEP8Compliance:
    """Test that the module follows PEP 8 standards."""

    def test_has_module_docstring(self):
        """Check module has a docstring."""
        import word_counter
        assert word_counter.__doc__ is not None

    def test_function_has_docstring(self):
        """Check function has a docstring."""
        assert count_words_in_file.__doc__ is not None
```

### Part 4: Run and Verify

```bash
# Check style
flake8 word_counter.py

# Auto-format
black word_counter.py

# Run tests
pytest test_word_counter.py -v

# Test manually
python3 word_counter.py
```

**Expected test output:**

```
test_word_counter.py::TestCountWords::test_normal_file PASSED
test_word_counter.py::TestCountWords::test_empty_file PASSED
test_word_counter.py::TestCountWords::test_whitespace_only PASSED
test_word_counter.py::TestCountWords::test_nonexistent_file PASSED
test_word_counter.py::TestPEP8Compliance::test_has_module_docstring PASSED
test_word_counter.py::TestPEP8Compliance::test_function_has_docstring PASSED

====== 6 passed in 0.15s ======
```

### What You've Accomplished

This script demonstrates:

1. **Error handling**: Try/except for file operations
2. **Docstrings**: On every function
3. **PEP 8 compliance**: Proper naming, spacing, length
4. **Testing**: Multiple test cases covering normal, edge, and error cases
5. **Readability**: Comments explaining WHY, not WHAT
6. **Robustness**: Handles missing files, encoding issues, empty files

This is professional-grade code. It's what you'll see in real projects.

---

## 🔗 What's Next

**Congratulations!** You have now completed the entirety of **Module 1: Python Essentials**. You have learned:

- Variables, data types, and operations
- Control flow (if/elif/else, loops, comprehensions)
- String manipulation and regular expressions
- Data structures (lists, tuples, dicts, sets)
- Functions and modules
- File I/O and error handling
- Debugging techniques and best practices
- Testing with pytest
- Clean code principles

**Next up: Module 2: Git & Version Control**

You now understand how to write Python code. But in a real project, you need to:

- Save your work so you never lose it
- Track changes over time
- Collaborate with others
- Know exactly what changed and why

Git & Version Control teaches you to do all of this. You'll learn:

- Initialize a repository
- Commit your changes with messages
- Branch to work on features
- Merge branches back together
- Push to GitHub to share your code

This is the bridge between "scripts you write on your computer" and "professional projects that teams work on together."

---

## 📚 Debugging Quick Reference

| Task                    | Tool      | Command                           |
| ----------------------- | --------- | --------------------------------- |
| Read error              | Traceback | Always read fully, from bottom up |
| Add debug output        | print()   | `print(f"DEBUG: {variable}")`     |
| Find issues             | flake8    | `flake8 script.py`                |
| Auto-format code        | black     | `black script.py`                 |
| Interactive debugging   | pdb       | `breakpoint()` in code            |
| Check specific behavior | pytest    | `pytest test_file.py -v`          |

| Error Type  | Cause              | Fix                                      |
| ----------- | ------------------ | ---------------------------------------- |
| SyntaxError | Bad syntax         | Check colons, quotes, indentation        |
| NameError   | Undefined variable | Check spelling, initialize before use    |
| TypeError   | Wrong type         | Convert types or check before operations |
| ValueError  | Wrong value        | Validate input before operations         |
| IndexError  | Bad list position  | Check list length                        |
| KeyError    | Missing dict key   | Use `.get()` instead of `dict[key]`      |

---

## 📖 Summary: The Complete Python Essentials

From zero to professional-grade Python programmer in one module:

```
Variables & Types → Functions → Control Flow → Strings → Lists & Dicts
        ↓
    File I/O → Debugging & Best Practices → Testing

Result: You can write robust, tested, documented Python code.
```

Every concept built on the previous one. Every skill connects to real data work. You're ready for Phase 1.
