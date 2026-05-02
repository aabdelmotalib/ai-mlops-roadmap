#!/bin/bash
# script_with_volumes.sh
# Create directories
mkdir -p input output
# Create some sample data
cat > input/data.txt << 'EOF'
Line 1 of data
Line 2 of data
Line 3 of data
EOF
# Create a Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.9
WORKDIR /app
COPY process.py .
CMD ["python", "process.py"]
EOF
# Create the processing script
cat > process.py << 'EOF'
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
EOF
# Build image
docker build -t data_processor .
# Run with volumes
docker run \
  -v "$PWD"/input:/data \
  -v "$PWD"/output:/output \
  data_processor

# Check the results on your machine
cat output/result.txt

