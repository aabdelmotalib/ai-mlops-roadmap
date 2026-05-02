# Script that reads from /data and writes to /output
import os

# Read input data
with open('/data/data.txt', 'r') as f:
    lines = f.readlines()

# Process it
processed = [f"Processed: {line.strip()}\n" for line in lines]

# Write output
with open('/output/result.txt', 'w') as f:
    f.writelines(processed)

print("Processing complete!")
