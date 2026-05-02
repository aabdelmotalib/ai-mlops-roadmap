# Real-world scenario: temperature readings from a week
# Some readings are valid, some are missing (None), some are obviously wrong (negative)
temperatures = [22, None, 25, -999, 35, 28, None, 40, 19, 32]

# Example 1: Filtering Valid Data With if and is not None¶
# Process only valid (non-None) readings
valid_count = 0
for temp in temperatures:
    if temp is not None and temp >= 0:
        print(f"Valid reading: {temp}C")
        valid_count = valid_count + 1 
    if temp is None:
        hard_to_fetch = []
        hard_to_fetch.append(temp)
        print(f"it is hard to get {len(hard_to_fetch)} day")
    else:
        print("Skipping invalid reading.")
print(f"Total Hard readings: {len(hard_to_fetch)} days")
print(f"Total valid readings: {valid_count} days")

print("=" * 50)

# Example 2: Categorizing Data With Nested if Statements¶
for temp in temperatures:
    if temp is None:
        print(f"{temp}C --- MISSING DATA!")
    elif temp < 0:
        print(f"{temp}C --- BAD DATA!")
    elif temp < 15:
        print(f"{temp}C --- COLD!")
    elif temp < 25:
        print(f"{temp}C --- COMFORT!")
    
    elif temp > 25:
        hot_days = []
        hot_days.append(temp)
        print(f"{temp}C --- HOT!")
print(f"Total of hot days {len(hot_days)}")