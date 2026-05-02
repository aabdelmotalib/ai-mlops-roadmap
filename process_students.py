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
    unique_students[student['name']] = student

students = list(unique_students.values())
print(f" Removed duplicates: {len(raw_students)} --> {len(students)} unique students")

# Step 2: Sort by grade (highest first)
students_by_grade = sorted(students, key=lambda s: s['grade'], reverse=True)
print(f"\nTop 3 students by grade:")
for student in students_by_grade[:5]:
    print(f"  -{student['name']}: {student['grade']} ({student['subject']})")

# Step 3: Group by subject
grouped_by_subject = {}
for student in students:
    subject = student['subject']
    if subject not in grouped_by_subject:
        grouped_by_subject[subject] = []
    grouped_by_subject[subject].append(student)

# Step 4: Find the top student per subject
top_per_subject = {}
for subject in grouped_by_subject:
    top_student = max(grouped_by_subject[subject], key=lambda s: s['grade'])
    top_per_subject[subject] = top_student

print(f"\nTop student per subject:")
for subject in sorted(top_per_subject.keys()):
    student = top_per_subject[subject]
    print(f" {subject}: {student['name']} ({student['grade']})")

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