scores = [65, 78, 45, 92, 88, 55, 79, 100]

# Expected output:
# Passing grades: [78, 92, 88, 79, 100]
# Count: 5

passing = [score for score in scores if score >= 70]
print(f"Passing grades: {passing}")
print(f"Count: {len(passing)}")


products = [
    {"name": "Laptop", "category": "Electronics", "price": 800},
    {"name": "Mouse", "category": "Electronics", "price": 25},
    {"name": "Desk", "category": "Furniture", "price": 300},
    {"name": "Chair", "category": "Furniture", "price": 150},
    {"name": "Monitor", "category": "Electronics", "price": 250},
]

grouped = {}
for product in products:
    cat = product['category']
    if cat not in grouped:
        grouped[cat] = []
    grouped[cat].append(product['price'])
    print(grouped)
# Calculate average per category
print("Average price per category:")
for category in sorted(grouped.keys()):
    prices = grouped[category]
    print(prices)

    average = sum(prices) / len(prices)
    print(f" {category}: ${average:.2f}")

raw_records = [
    {"id": 3, "name": "Charlie", "score": 92},
    {"id": 1, "name": "Alice", "score": 95},
    {"id": 3, "name": "Charlie", "score": 92},
    {"id": 2, "name": "Bob", "score": 87},
    {"id": 1, "name": "Alice", "score": 95},
]
# Deduplicate by converting to dict with ID as key
unique = {record['id']: record for record in raw_records}
# Sort by ID
sorted_records = sorted(unique.values(), key=lambda r:r['id'])

# Print summary
for record in sorted_records:
    print(f" {record['id']}: {record['name']} ({record['score']})")
