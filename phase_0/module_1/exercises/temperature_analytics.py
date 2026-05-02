# Open the input file and read all lines
with open ("raw_temperatures.txt", "r") as input_file:
    lines =input_file.readlines()

# We'll build a list of only valid temperature values
valid_temps = []

# Loop through each line in the file
for line in lines:
    line = line.strip()
    # Skip empty lines
    if not line:
        continue
    # Try to convert the line to a float
    try:
        temp = float(line)
        if -50 <= temp <= 50:
            valid_temps.append(temp)
    except ValueError:
        pass

# Calculate statistics
if len(valid_temps) > 0: 
    average = sum(valid_temps) / len(valid_temps)

    # Count readings above average using a list comprehension
    above_average = [t for t in valid_temps if t > average]
    above_average_count = len(above_average)

    # Count readings below freezing (0°C)
    below_freezing = [t for t in valid_temps if t < 0]
    below_freezing_count = len(below_freezing)

    # Create a summary report
    summary = f"""TEMPERATURE ANALYTICS REPORT
    =============================
    Total valid readings: {len(valid_temps)}
    Average temperature: {average:.1f}°C
    Readings above average: {above_average_count}
    Readings below freezing: {below_freezing_count}
    Min temperature: {min(valid_temps):.1f}°C
    Max temperature: {max(valid_temps):.1f}°C
    """

    # Write the report to a file
    with open("temperature_report.txt", "w") as output_file:
        output_file.write(summary)
    print(summary)
else:
    print("No valid temperature reading found!")

