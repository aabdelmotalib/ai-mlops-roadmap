import re 
def extract_and_clean_book(record):
    record = record.strip()
    fields = record.split("|")
    if len(fields) != 3:
        return None
    title = fields[0].strip()
    author = fields[1].strip()
    price_raw = fields[2].strip()
    title = title.title()
    author = author.title()
    price_raw = re.match(r"£(\d+(?:\.\d{2})?)", price_raw)

    if not price_raw:
        return{
            "title": title,
            "author": author,
            "price": None,
            "valid": False,
            "reason": f"Invalid price format: {price_raw}"
        }
    
    price = float(price_raw.group(1))
    return{
        "title": title,
        "author": author,
        "price": price,
        "valid": True,
        "reason": "OK"
    }

# Main program
with open("messy_books.txt", "r") as infile:
    lines = infile.readlines()

clean_books = []
problems = []

for line in lines:
    result = extract_and_clean_book(line)
    if result is None:
        problems.append(f"Skipped (wrong format): {line.strip()}")
    elif result["valid"]:
        clean_books.append(result)
    else:
        problems.append(f"{result["title"]} --- {result["reason"]}")

with open("clean_books.csv", "w") as outfile:
    outfile.write("Title,Author,Price (£)\n")

    for book in clean_books:
        line = f"{book['title']}, {book['author']}, {book['price']:.2f}\n"
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
        print(f" ⚠️ {problem}")
print("\nClean data written to: clean_books.csv")
print("=" * 50)
