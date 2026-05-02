room_temps = {
    "Office": [22, 23, 24, 25, 26, 27, 28],
    "Lab": [19, 30, 21, 22, 21, 20, 19],
    "Server": [25, 26, 31, 27, 28, 29, 30],
}

# Track which room has the highest average
highest_avg_room = None
highest_avg_temp = 0

# Process each room
for room_name, temperatures in room_temps.items():
    # Calculate average temperature for this room
    avg_temp = sum(temperatures) / len(temperatures)

    # Check if this room's average is the highest so far
    if avg_temp > highest_avg_temp:
        highest_avg_temp = avg_temp
        highest_avg_room = room_name

    # Count acceptable readings (20-28°C)
    acceptable_count = 0
    for temp in temperatures:
        if 20 <= temp <= 28:
            # Between 20 and 28 inclusive
            acceptable_count = acceptable_count + 1

    print(f"{room_name}: Average {avg_temp:.1f}°C, {acceptable_count} acceptable readings")

    # Flag any readings above 30°C
    for temp in temperatures:
        if temp > 30:
            print(f"⚠️ WARNING: {room_name} reached {temp}°C!")

print(f"\nHighest average: {highest_avg_room} ({highest_avg_temp:.1f}°C)")