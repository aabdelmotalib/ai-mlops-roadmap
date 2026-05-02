---
tags:
  - Beginner
  - Phase 0
  - Collections
  - Data Structures
---

# Sub-Module: Lists and Loops (Deep Dive)

**Part of Module 1: Python Essentials**  
**Phase 0: Baseline Setup**

---

## 🎯 What You Will Learn

By the end of this sub-module, you will:

- Understand lists as mutable collections and master every list method
- Distinguish between references, shallow copies, and deep copies
- Work with tuples as immutable sequences and use tuple unpacking
- Build and manipulate dictionaries as key-value stores
- Create and use sets for deduplication and membership testing
- Choose the right data structure for different problems
- Iterate through complex data structures using multiple patterns
- Write lambda functions for concise, single-use operations
- Process real-world datasets (student records) using all these tools
- Group, filter, sort, and transform data structures efficiently

---

## 🧠 Concept Explained: Collections and Data Structures

### The Analogy: Different Containers for Different Jobs

Imagine you're packing for a trip and you have different containers to choose from:

- **List**: A shopping trolley. You can add items anywhere, remove them, rearrange them, and the order matters. You can have duplicates.
- **Tuple**: A sealed cardboard box. Once packed, you can't change what's inside. But it's lightweight and safe — perfect for things that shouldn't change.
- **Dictionary**: A real dictionary. You look up a word (key) and get its definition (value). No duplicate keys. Organized for quick lookup.
- **Set**: An unordered bag. You only care if something is IN the bag, not where it is. Great for asking "Do I have this?" and "What's unique?"

Each is designed for different problems. The wrong choice makes your code slow or confusing. The right choice makes it fast and elegant.

### Why This Matters

In data work, you'll constantly:

- Store rows of data (lists of dictionaries)
- Look up values by ID (dictionaries)
- Remove duplicates (sets)
- Keep data safe from modification (tuples)
- Group records by category (dictionaries with lists as values)

Understanding these data structures deeply is what separates a "person who writes Python" from a "Python programmer."

---

## 🔍 How It Works: Data Structures in Memory

### Visual Comparison: How They're Stored Differently

```
LIST (ordered, mutable)
┌───┬───┬───┬───┐
│ A │ B │ C │ D │  ← Position matters
└───┴───┴───┴───┘
  0   1   2   3

TUPLE (ordered, immutable)
(A, B, C, D)  ← Same as list structurally, but sealed
  0  1  2  3

DICT (unordered by default, key→value pairs)
{
  "name": "Alice",    ← Key "name" → Value "Alice"
  "age": 30,          ← Key "age" → Value 30
  "city": "NYC"       ← Key "city" → Value "NYC"
}

SET (unordered, unique items only)
{A, B, C, D}  ← Just a collection, no duplicates, no order
```

### The Reference Trap

This is critical:

```
list_a = [1, 2, 3]
list_b = list_a  # DON'T do this! list_b is a reference, not a copy

list_b.append(4)
print(list_a)  # Output: [1, 2, 3, 4] — list_a changed too!

# Why? Because list_b and list_a point to the SAME list in memory.
# When you modify list_b, you're modifying the original.

# Safe copy:
list_c = list_a.copy()  # Now list_c is independent
list_c.append(5)
print(list_a)  # Output: [1, 2, 3, 4] — list_a unchanged
```

---

## 🛠️ Step-by-Step Guide

### Step 1: Master List Methods

A list is a container where you can add, remove, and rearrange items:

```python
# Create a list
numbers = [3, 1, 4, 1, 5]

# .append() — add to the end
numbers.append(9)
print(numbers)  # [3, 1, 4, 1, 5, 9]

# .insert(index, value) — add at a specific position
numbers.insert(0, 0)  # Insert 0 at position 0
print(numbers)  # [0, 3, 1, 4, 1, 5, 9]

# .extend() — merge another list
numbers.extend([2, 6])  # Add two numbers to the end
print(numbers)  # [0, 3, 1, 4, 1, 5, 9, 2, 6]

# .remove(value) — remove by VALUE (first match only)
numbers.remove(1)  # Remove the first occurrence of 1
print(numbers)  # [0, 3, 4, 1, 5, 9, 2, 6]

# .pop(index) — remove by POSITION and return it
popped = numbers.pop(0)  # Remove and return item at position 0
print(f"Removed: {popped}")  # Removed: 0
print(numbers)  # [3, 4, 1, 5, 9, 2, 6]

# .index(value) — find the position of a value
position = numbers.index(5)
print(f"5 is at position {position}")  # position = 3

# .count(value) — count occurrences
original = [1, 2, 2, 3, 2, 4]
count = original.count(2)
print(f"2 appears {count} times")  # 3 times

# .sort() — sort in place (modifies the list)
original = [3, 1, 4, 1, 5]
original.sort()
print(original)  # [1, 1, 3, 4, 5]

# .reverse() — reverse in place
original = [1, 2, 3]
original.reverse()
print(original)  # [3, 2, 1]

# .copy() — create a shallow copy (independent list)
list_a = [1, 2, 3]
list_b = list_a.copy()  # Independent copy
list_b.append(4)
print(f"list_a: {list_a}")  # [1, 2, 3] — unchanged
print(f"list_b: {list_b}")  # [1, 2, 3, 4] — only list_b changed
```

**Expected output:**

```
[3, 1, 4, 1, 5, 9]
[0, 3, 1, 4, 1, 5, 9]
[0, 3, 1, 4, 1, 5, 9, 2, 6]
[0, 3, 4, 1, 5, 9, 2, 6]
Removed: 0
[3, 4, 1, 5, 9, 2, 6]
5 is at position 3
2 appears 3 times
[1, 1, 3, 4, 5]
[3, 2, 1]
list_a: [1, 2, 3]
list_b: [1, 2, 3, 4]
```

### Step 2: Understand Slicing (Review From Strings Module)

List slicing works exactly like string slicing:

```python
numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# Get elements from index 2 to 5 (not including 5)
print(numbers[2:5])  # [2, 3, 4]

# Get the last 3 elements
print(numbers[-3:])  # [7, 8, 9]

# Get every other element
print(numbers[::2])  # [0, 2, 4, 6, 8]

# Reverse the list
print(numbers[::-1])  # [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
```

**Expected output:**

```
[2, 3, 4]
[7, 8, 9]
[0, 2, 4, 6, 8]
[9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
```

### Step 3: Work With Tuples

Tuples are like immutable lists — once created, they can't be changed:

```python
# Create a tuple (parentheses or just commas)
coordinates = (10, 20)
print(coordinates)

# Access elements like a list
print(coordinates[0])  # 10

# You CAN'T modify a tuple
try:
    coordinates[0] = 15
except TypeError:
    print("Can't modify a tuple!")

# Tuple unpacking — assign each element to a variable
x, y = coordinates
print(f"x={x}, y={y}")

# Multiple assignments
a, b, c = (1, 2, 3)
print(f"a={a}, b={b}, c={c}")

# THE TRAP: Single-element tuple
single_element = (42)  # This is just a number in parentheses
print(type(single_element))  # <class 'int'>

single_element_tuple = (42,)  # This is a tuple (note the comma!)
print(type(single_element_tuple))  # <class 'tuple'>
```

**Expected output:**

```
(10, 20)
10
Can't modify a tuple!
x=10, y=20
a=1, b=2, c=3
<class 'int'>
<class 'tuple'>
```

!!! warning
Always remember: a single-element tuple needs a trailing comma: `(42,)` not `(42)`.

### Step 4: Build and Use Dictionaries

A dictionary is a key-value store where you look up values by their keys:

```python
# Create a dictionary
student = {
    "name": "Alice",
    "age": 20,
    "grade": "A",
    "courses": ["Math", "Physics", "Chemistry"]
}

# Read values by key
print(student["name"])  # Alice
print(student["age"])  # 20

# Modify values
student["age"] = 21
student["grade"] = "A+"
print(student)

# Add new key-value pairs
student["email"] = "alice@example.com"
print(student)

# Delete a key-value pair
del student["courses"]
print(student)

# .get(key, default) — safe lookup without KeyError
# If the key doesn't exist, return the default value
phone = student.get("phone", "not provided")
print(phone)  # not provided

gpa = student.get("gpa", 0.0)
print(gpa)  # 0.0

# .keys() — get all keys
print(student.keys())

# .values() — get all values
print(student.values())

# .items() — get key-value pairs
for key, value in student.items():
    print(f"{key}: {value}")
```

**Expected output:**

```
Alice
20
{'name': 'Alice', 'age': 21, 'grade': 'A+', 'courses': ['Math', 'Physics', 'Chemistry']}
{'name': 'Alice', 'age': 21, 'grade': 'A+', 'courses': ['Math', 'Physics', 'Chemistry'], 'email': 'alice@example.com'}
{'name': 'Alice', 'age': 21, 'grade': 'A+', 'email': 'alice@example.com'}
not provided
0.0
dict_keys(['name', 'age', 'grade', 'email'])
dict_values(['Alice', 21, 'A+', 'alice@example.com'])
name: Alice
age: 21
grade: A+
email: alice@example.com
```

### Step 5: Use Dictionary Comprehensions

Just like list comprehensions, you can build dictionaries in one line:

```python
# Build a dictionary from a list
names = ["Alice", "Bob", "Charlie"]
grades = [95, 87, 92]

# Traditional way (verbose)
grade_dict = {}
for name, grade in zip(names, grades):
    grade_dict[name] = grade

print(grade_dict)

# Dictionary comprehension (one line)
grade_dict = {name: grade for name, grade in zip(names, grades)}
print(grade_dict)

# With a condition
high_grades = {name: grade for name, grade in zip(names, grades) if grade >= 90}
print(high_grades)
```

**Expected output:**

```
{'Alice': 95, 'Bob': 87, 'Charlie': 92}
{'Alice': 95, 'Bob': 87, 'Charlie': 92}
{'Alice': 95, 'Charlie': 92}
```

### Step 6: Work With Nested Dictionaries

Dictionaries can contain other dictionaries (and lists inside dicts, etc.):

```python
# A record with nested information
student_data = {
    "name": "Alice",
    "courses": {
        "math": {
            "grade": 95,
            "credits": 3
        },
        "physics": {
            "grade": 88,
            "credits": 4
        }
    }
}

# Access nested values
print(student_data["name"])  # Alice
print(student_data["courses"]["math"]["grade"])  # 95

# Modify nested values
student_data["courses"]["physics"]["grade"] = 92

# Check if a key exists before accessing
if "chemistry" in student_data["courses"]:
    print(student_data["courses"]["chemistry"])
else:
    print("Chemistry course not found")
```

**Expected output:**

```
Alice
95
Chemistry course not found
```

### Step 7: Understand Sets

Sets are collections of unique items with no particular order:

```python
# Create a set
colors = {"red", "green", "blue"}
print(colors)

# Add an item
colors.add("yellow")
print(colors)

# Duplicates are automatically removed
numbers = {1, 2, 2, 3, 3, 3}
print(numbers)  # {1, 2, 3}

# Check membership (very fast!)
if "red" in colors:
    print("Red is in the set")

# Remove an item
colors.discard("blue")  # discard doesn't error if item doesn't exist
print(colors)

# Set operations (union, intersection, difference)
set_a = {1, 2, 3}
set_b = {2, 3, 4}

# Union: all items from both sets
union = set_a | set_b
print(f"Union: {union}")  # {1, 2, 3, 4}

# Intersection: only items in both sets
intersection = set_a & set_b
print(f"Intersection: {intersection}")  # {2, 3}

# Difference: items in set_a but not in set_b
difference = set_a - set_b
print(f"Difference: {difference}")  # {1}
```

**Expected output:**

```
{'red', 'green', 'blue'}
{'red', 'green', 'blue', 'yellow'}
{1, 2, 3}
Red is in the set
{'red', 'green', 'yellow'}
Union: {1, 2, 3, 4}
Intersection: {2, 3}
Difference: {1}
```

### Step 8: Choose the Right Data Structure

Here's a decision guide:

| Need                           | Use        | Why                                  |
| ------------------------------ | ---------- | ------------------------------------ |
| Ordered collection, can modify | List       | Flexible, many methods               |
| Immutable collection           | Tuple      | Safe, hashable (can use as dict key) |
| Fast lookup by key             | Dictionary | O(1) lookup time                     |
| Unique items, membership test  | Set        | Fast `in` operator, automatic dedup  |

```python
# Example: choosing the right structure

# Storing student records (list of dicts)
records = [
    {"name": "Alice", "grade": "A"},
    {"name": "Bob", "grade": "B"},
]

# Fast ID lookup (dict with ID as key)
by_id = {
    1: "Alice",
    2: "Bob",
    3: "Charlie"
}

# Immutable coordinates (tuple)
point = (10, 20)

# Unique subjects (set)
subjects = {"Math", "Physics", "Chemistry"}
```

### Step 9: Sort a List of Dictionaries

One of the most common operations in data work:

```python
# Data: list of student records
students = [
    {"name": "Alice", "grade": 95},
    {"name": "Bob", "grade": 87},
    {"name": "Charlie", "grade": 92},
    {"name": "Diana", "grade": 88},
]

# Sort by grade (ascending)
sorted_asc = sorted(students, key=lambda student: student["grade"])
for student in sorted_asc:
    print(f"{student['name']}: {student['grade']}")

print("---")

# Sort by grade (descending)
sorted_desc = sorted(students, key=lambda student: student["grade"], reverse=True)
for student in sorted_desc:
    print(f"{student['name']}: {student['grade']}")
```

**Expected output:**

```
Bob: 87
Diana: 88
Charlie: 92
Alice: 95
---
Alice: 95
Charlie: 92
Diana: 88
Bob: 87
```

### Step 10: The Lambda Function

A **lambda** is a tiny, anonymous function for one-time use. It's like a sticky note that says "do this operation" but you don't bother naming it properly:

```python
# Without lambda (traditional approach)
def double(x):
    return x * 2

numbers = [1, 2, 3, 4]
doubled = [double(n) for n in numbers]
print(doubled)  # [2, 4, 6, 8]

print("---")

# With lambda (more concise)
numbers = [1, 2, 3, 4]
doubled = [x * 2 for x in numbers]
# Wait, that's a list comprehension, which is even better!

# Lambdas are useful for operations like sort_key:
students = [
    {"name": "Alice", "age": 20},
    {"name": "Bob", "age": 19},
    {"name": "Charlie", "age": 21},
]

# Sort by age using lambda
sorted_by_age = sorted(students, key=lambda student: student["age"])
for s in sorted_by_age:
    print(f"{s['name']}: {s['age']}")
```

**Expected output:**

```
[2, 4, 6, 8]
---
Bob: 19
Alice: 20
Charlie: 21
```

**When to use lambda**:

```python
# Good: Used once in a specific context
sorted_list = sorted(data, key=lambda x: x["priority"])

# Bad: Too complex or used multiple times
parse_data = lambda x: x.split(",")[0].strip().lower()  # Use a real function instead
```

---

## 💻 Code Examples: Student Records Dataset

### The Running Dataset

We'll use this same dataset throughout — 10 student records with name, grade, and subject:

```python
students = [
    {"name": "Alice", "grade": 95, "subject": "Math"},
    {"name": "Bob", "grade": 87, "subject": "Physics"},
    {"name": "Charlie", "grade": 92, "subject": "Math"},
    {"name": "Diana", "grade": 88, "subject": "Chemistry"},
    {"name": "Eve", "grade": 91, "subject": "Physics"},
    {"name": "Frank", "grade": 85, "subject": "Chemistry"},
    {"name": "Grace", "grade": 96, "subject": "Math"},
    {"name": "Henry", "grade": 89, "subject": "Physics"},
    {"name": "Iris", "grade": 93, "subject": "Chemistry"},
    {"name": "Jack", "grade": 84, "subject": "Math"},
]
```

### Example 1: Sort by Grade (Highest to Lowest)

```python
students = [
    {"name": "Alice", "grade": 95, "subject": "Math"},
    {"name": "Bob", "grade": 87, "subject": "Physics"},
    # ... (rest of data)
]

# Sort by grade in descending order
top_students = sorted(students, key=lambda s: s["grade"], reverse=True)

print("Top students:")
for student in top_students[:3]:  # Show top 3
    print(f"  {student['name']}: {student['grade']}")
```

**Expected output:**

```
Top students:
  Grace: 96
  Alice: 95
  Iris: 93
```

### Example 2: Filter by Subject

```python
# Get all students in Math
math_students = [s for s in students if s["subject"] == "Math"]

print(f"Math students: {len(math_students)}")
for student in math_students:
    print(f"  {student['name']}: {student['grade']}")
```

**Expected output:**

```
Math students: 3
  Alice: 95
  Charlie: 92
  Grace: 96
  Jack: 84
```

### Example 3: Count Unique Subjects

```python
# Get unique subjects
subjects = {s["subject"] for s in students}
# Using {}  with one iterable = set comprehension

print(f"Subjects: {subjects}")
print(f"Number of unique subjects: {len(subjects)}")

# Count students per subject
subject_counts = {}
for student in students:
    subject = student["subject"]
    subject_counts[subject] = subject_counts.get(subject, 0) + 1
    # .get() returns the current count or 0 if not found

print("\nStudents per subject:")
for subject, count in subject_counts.items():
    print(f"  {subject}: {count}")
```

**Expected output:**

```
Subjects: {'Chemistry', 'Physics', 'Math'}
Number of unique subjects: 3

Students per subject:
  Math: 4
  Physics: 3
  Chemistry: 3
```

### Example 4: Group Students by Subject

```python
# Create a dictionary where keys are subjects and values are lists of students
grouped = {}

for student in students:
    subject = student["subject"]

    # If this subject is new, create an empty list for it
    if subject not in grouped:
        grouped[subject] = []

    # Add this student to the list
    grouped[subject].append(student)

# Print the groups
for subject in sorted(grouped.keys()):  # Sort subjects alphabetically
    print(f"\n{subject}:")
    for student in grouped[subject]:
        print(f"  {student['name']}: {student['grade']}")
```

**Expected output:**

```
Chemistry:
  Diana: 88
  Frank: 85
  Iris: 93

Math:
  Alice: 95
  Charlie: 92
  Grace: 96
  Jack: 84

Physics:
  Bob: 87
  Eve: 91
  Henry: 89
```

### Example 5: Find Top Student Per Subject

```python
grouped_by_subject = {}

# Group students
for student in students:
    subject = student["subject"]
    if subject not in grouped_by_subject:
        grouped_by_subject[subject] = []
    grouped_by_subject[subject].append(student)

# Find top student per subject
print("Top student per subject:")
for subject, student_list in grouped_by_subject.items():
    # Use sorted() with a key to find the highest grade
    top_student = sorted(student_list, key=lambda s: s["grade"], reverse=True)[0]
    print(f"  {subject}: {top_student['name']} ({top_student['grade']})")
```

**Expected output:**

```
Top student per subject:
  Math: Grace (96)
  Physics: Eve (91)
  Chemistry: Iris (93)
```

### Example 6: Remove Duplicates Using Set

```python
# Imagine we have duplicate student records
raw_data = [
    {"name": "Alice", "grade": 95, "subject": "Math"},
    {"name": "Bob", "grade": 87, "subject": "Physics"},
    {"name": "Alice", "grade": 95, "subject": "Math"},  # Duplicate!
    {"name": "Charlie", "grade": 92, "subject": "Math"},
    {"name": "Bob", "grade": 87, "subject": "Physics"},  # Duplicate!
]

# Dicts aren't hashable, so we can't use a set directly
# Instead, convert to tuples for deduplication

# Convert to tuples (which are hashable)
unique_tuples = set(tuple(sorted(d.items())) for d in raw_data)

# Convert back to dicts
unique_students = [dict(t) for t in unique_tuples]

print(f"Original: {len(raw_data)} records")
print(f"After dedup: {len(unique_students)} records")

# OR simpler: use a dict with name as unique key
seen = {}
for student in raw_data:
    seen[student["name"]] = student

unique_students = list(seen.values())
print(f"Using dict trick: {len(unique_students)} records")
```

**Expected output:**

```
Original: 5 records
After dedup: 3 records
Using dict trick: 3 records
```

---

## ⚠️ Common Mistakes

### Mistake 1: Modifying a List While Looping

```python
# Wrong — removing items while looping causes items to be skipped!
numbers = [1, 2, 3, 4, 5]

for num in numbers:
    if num % 2 == 0:  # If even
        numbers.remove(num)  # Don't do this!

print(numbers)  # Output: [1, 3, 5] — but we might miss items!
```

**Fix**: Loop over a copy or build a new list

```python
# Correct option 1: loop over a copy
numbers = [1, 2, 3, 4, 5]
for num in numbers.copy():  # Loop over the copy
    if num % 2 == 0:
        numbers.remove(num)

print(numbers)  # [1, 3, 5]

# Correct option 2: build a new list (better)
numbers = [1, 2, 3, 4, 5]
odds = [n for n in numbers if n % 2 != 0]
print(odds)  # [1, 3, 5]
```

### Mistake 2: The Reference Trap

```python
# Wrong — list_b is a reference, not a copy
list_a = [1, 2, 3]
list_b = list_a  # Both point to the same list!

list_b.append(4)
print(list_a)  # [1, 2, 3, 4] — list_a changed!
```

**Fix**: Use `.copy()` for a shallow copy, or `copy.deepcopy()` for nested structures

```python
# Correct
import copy

list_a = [1, 2, 3]
list_b = list_a.copy()  # True independent copy

list_b.append(4)
print(list_a)  # [1, 2, 3] — unchanged
```

### Mistake 3: KeyError on Missing Dictionary Key

```python
# Wrong — crashes if key doesn't exist
student = {"name": "Alice", "grade": 95}
print(student["age"])  # KeyError: 'age'
```

**Fix**: Use `.get()` with a default value

```python
# Correct
student = {"name": "Alice", "grade": 95}
age = student.get("age", "unknown")
print(age)  # unknown
```

### Mistake 4: Forgetting the Trailing Comma in Single-Element Tuple

```python
# Wrong — this is an integer, not a tuple!
single = (42)
print(type(single))  # <class 'int'>

# Correct — add the trailing comma
single = (42,)
print(type(single))  # <class 'tuple'>
```

### Mistake 5: Using `sort()` vs `sorted()`

```python
# .sort() modifies the list (no return value)
numbers = [3, 1, 2]
result = numbers.sort()  # Returns None!
print(result)  # None
print(numbers)  # [1, 2, 3]

# sorted() returns a new list (doesn't modify original)
numbers = [3, 1, 2]
result = sorted(numbers)
print(result)  # [1, 2, 3]
print(numbers)  # [3, 1, 2] — original unchanged
```

---

## ✅ Exercises

### Exercise 1 (Easy): Filter and Count

**Problem**: You have a list of scores. Filter to keep only passing grades (70+) and count them.

```python
scores = [65, 78, 45, 92, 88, 55, 79, 100]

# Expected output:
# Passing grades: [78, 92, 88, 79, 100]
# Count: 5
```

**Solution**:

```python
scores = [65, 78, 45, 92, 88, 55, 79, 100]

# Filter to passing grades
passing = [s for s in scores if s >= 70]

print(f"Passing grades: {passing}")
print(f"Count: {len(passing)}")
```

### Exercise 2 (Medium): Group and Analyze

**Problem**: You have product data with categories. Group by category and find the average price per category.

```python
products = [
    {"name": "Laptop", "category": "Electronics", "price": 800},
    {"name": "Mouse", "category": "Electronics", "price": 25},
    {"name": "Desk", "category": "Furniture", "price": 300},
    {"name": "Chair", "category": "Furniture", "price": 150},
    {"name": "Monitor", "category": "Electronics", "price": 250},
]

# Expected output:
# Electronics: $358.33
# Furniture: $225.00
```

**Solution**:

```python
products = [
    {"name": "Laptop", "category": "Electronics", "price": 800},
    {"name": "Mouse", "category": "Electronics", "price": 25},
    {"name": "Desk", "category": "Furniture", "price": 300},
    {"name": "Chair", "category": "Furniture", "price": 150},
    {"name": "Monitor", "category": "Electronics", "price": 250},
]

# Group by category
grouped = {}
for product in products:
    cat = product["category"]
    if cat not in grouped:
        grouped[cat] = []
    grouped[cat].append(product["price"])

# Calculate average per category
print("Average price per category:")
for category in sorted(grouped.keys()):
    prices = grouped[category]
    average = sum(prices) / len(prices)
    print(f"  {category}: ${average:.2f}")
```

### Exercise 3 (Hard): Deduplication and Transformation

**Problem**: You have a messy list of records with duplicates. Deduplicate, sort by ID, and create a summary.

```python
raw_records = [
    {"id": 3, "name": "Charlie", "score": 92},
    {"id": 1, "name": "Alice", "score": 95},
    {"id": 3, "name": "Charlie", "score": 92},  # Duplicate
    {"id": 2, "name": "Bob", "score": 87},
    {"id": 1, "name": "Alice", "score": 95},  # Duplicate
]

# Expected output:
# 1: Alice (95)
# 2: Bob (87)
# 3: Charlie (92)
```

**Solution**:

```python
raw_records = [
    {"id": 3, "name": "Charlie", "score": 92},
    {"id": 1, "name": "Alice", "score": 95},
    {"id": 3, "name": "Charlie", "score": 92},
    {"id": 2, "name": "Bob", "score": 87},
    {"id": 1, "name": "Alice", "score": 95},
]

# Deduplicate by converting to dict with ID as key
unique = {record["id"]: record for record in raw_records}

# Sort by ID
sorted_records = sorted(unique.values(), key=lambda r: r["id"])

# Print summary
for record in sorted_records:
    print(f"{record['id']}: {record['name']} ({record['score']})")
```

---

## 🏗️ Mini Project: Student Data Processor

### Project Overview

You'll write a Python script that:

1. Starts with a list of 20 student records
2. Removes duplicates by student name
3. Sorts by grade (highest first)
4. Groups students by subject
5. Finds the top student in each subject
6. Writes results to a JSON file

### Step 1: Create the Script

Create `process_students.py`:

```python
import json  # For writing JSON files

# Sample data: 20 student records (some duplicates)
raw_students = [
    {"name": "Alice", "grade": 95, "subject": "Math"},
    {"name": "Bob", "grade": 87, "subject": "Physics"},
    {"name": "Charlie", "grade": 92, "subject": "Math"},
    {"name": "Diana", "grade": 88, "subject": "Chemistry"},
    {"name": "Eve", "grade": 91, "subject": "Physics"},
    {"name": "Frank", "grade": 85, "subject": "Chemistry"},
    {"name": "Grace", "grade": 96, "subject": "Math"},
    {"name": "Henry", "grade": 89, "subject": "Physics"},
    {"name": "Iris", "grade": 93, "subject": "Chemistry"},
    {"name": "Jack", "grade": 84, "subject": "Math"},
    # Duplicates (same students, to test dedup)
    {"name": "Alice", "grade": 95, "subject": "Math"},
    {"name": "Bob", "grade": 87, "subject": "Physics"},
    {"name": "Charlie", "grade": 92, "subject": "Math"},
    {"name": "Diana", "grade": 88, "subject": "Chemistry"},
    {"name": "Eve", "grade": 91, "subject": "Physics"},
    {"name": "Frank", "grade": 85, "subject": "Chemistry"},
    {"name": "Grace", "grade": 96, "subject": "Math"},
    {"name": "Henry", "grade": 89, "subject": "Physics"},
    {"name": "Iris", "grade": 93, "subject": "Chemistry"},
    {"name": "Jack", "grade": 84, "subject": "Math"},
]

print("=" * 60)
print("STUDENT DATA PROCESSOR")
print("=" * 60)

# Step 1: Remove duplicates by using a dict with name as key
# This keeps the last occurrence of each student
unique_students = {}
for student in raw_students:
    # Using name as the key automatically deduplicates
    unique_students[student["name"]] = student

# Convert back to list
students = list(unique_students.values())

print(f"\nRemoved duplicates: {len(raw_students)} → {len(students)} unique students")

# Step 2: Sort by grade (highest first)
students_by_grade = sorted(students, key=lambda s: s["grade"], reverse=True)

print(f"\nTop 3 students by grade:")
for student in students_by_grade[:3]:
    print(f"  {student['name']}: {student['grade']} ({student['subject']})")

# Step 3: Group by subject
grouped_by_subject = {}
for student in students:
    subject = student["subject"]
    if subject not in grouped_by_subject:
        grouped_by_subject[subject] = []
    grouped_by_subject[subject].append(student)

# Step 4: Find the top student per subject
top_per_subject = {}
for subject in grouped_by_subject:
    # Find the student with highest grade in this subject
    top_student = max(
        grouped_by_subject[subject],
        key=lambda s: s["grade"]
    )
    top_per_subject[subject] = top_student

print(f"\nTop student per subject:")
for subject in sorted(top_per_subject.keys()):
    student = top_per_subject[subject]
    print(f"  {subject}: {student['name']} ({student['grade']})")

# Step 5: Prepare data for JSON output
output_data = {
    "all_students": students_by_grade,  # Sorted by grade
    "top_per_subject": top_per_subject,  # Best in each subject
    "summary": {
        "total_students": len(students),
        "subjects": list(grouped_by_subject.keys()),
        "highest_grade": max(students, key=lambda s: s["grade"])["grade"],
        "lowest_grade": min(students, key=lambda s: s["grade"])["grade"],
    }
}

# Step 6: Write to JSON file
with open("students_output.json", "w") as f:
    # indent=2 makes the JSON pretty-printed and readable
    json.dump(output_data, f, indent=2)

print(f"\nResults written to: students_output.json")
print("=" * 60)
```

### Step 2: Run the Script

```bash
python3 process_students.py
```

**Expected output:**

```
============================================================
STUDENT DATA PROCESSOR
============================================================

Removed duplicates: 20 → 10 unique students

Top 3 students by grade:
  Grace: 96 (Math)
  Alice: 95 (Math)
  Iris: 93 (Chemistry)

Top student per subject:
  Chemistry: Iris (93)
  Math: Grace (96)
  Physics: Eve (91)

Results written to: students_output.json
============================================================
```

### Step 3: Examine the JSON Output

The `students_output.json` file will contain:

```json
{
  "all_students": [
    {
      "name": "Grace",
      "grade": 96,
      "subject": "Math"
    },
    ...
  ],
  "top_per_subject": {
    "Chemistry": {
      "name": "Iris",
      "grade": 93,
      "subject": "Chemistry"
    },
    ...
  },
  "summary": {
    "total_students": 10,
    "subjects": ["Math", "Physics", "Chemistry"],
    "highest_grade": 96,
    "lowest_grade": 84
  }
}
```

### Key Points in This Project

```python
# Deduplication using dict:
unique_students = {s["name"]: s for s in students}

# Sorting with custom key:
sorted(students, key=lambda s: s["grade"], reverse=True)

# Grouping into a dict:
grouped = {}
for student in students:
    if student["subject"] not in grouped:
        grouped[student["subject"]] = []
    grouped[student["subject"]].append(student)

# Finding max with a key:
top = max(group, key=lambda s: s["grade"])

# JSON output:
json.dump(data, file, indent=2)
```

All of these are fundamental data structure operations that you'll use constantly in Phase 1, when you load real datasets.

---

## 🔗 What's Next

You've now mastered Python's core data structures — lists, tuples, dictionaries, and sets. You can group data, filter data, sort data, and transform it efficiently.

In the final sub-module of Module 1, **Debugging and Best Practices**, you'll learn how to:

- Read and understand error messages
- Use debugging tools to find problems
- Write clean, professional-grade code
- Test your code with pytest
- Follow Python conventions (PEP 8)

This is the capstone of Python Essentials. After that, you'll be ready for Module 2: Git & Version Control, where you'll learn to save your work and collaborate with others.

---

## 📚 Quick Reference

| Operation        | Code                            | Result             |
| ---------------- | ------------------------------- | ------------------ |
| Create list      | `[1, 2, 3]`                     | List               |
| Create tuple     | `(1, 2, 3)`                     | Immutable tuple    |
| Create dict      | `{"a": 1}`                      | Key-value pairs    |
| Create set       | `{1, 2, 3}`                     | Unique items       |
| List method      | `.append(x)`                    | Add to end         |
| List slice       | `list[1:3]`                     | Items 1-2          |
| Dict lookup      | `dict["key"]`                   | Get value          |
| Safe lookup      | `dict.get("key", default)`      | Get or default     |
| Check membership | `x in list`                     | Boolean            |
| Sort             | `sorted(list, key=lambda x: x)` | New sorted list    |
| Filter           | `[x for x in list if x > 0]`    | Filtered list      |
| Lambda           | `lambda x: x * 2`               | Anonymous function |
