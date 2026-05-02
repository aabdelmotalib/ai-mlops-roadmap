# Reads input file and adds a prefix

INPUT_FILE = "/data/data.txt"
OUTPUT_FILE = "/output/step1.txt"

with open(INPUT_FILE, "r") as f:
    lines = f.readlines()

processed = [f"STEP1: {line}" for line in lines]

with open(OUTPUT_FILE, "w") as f:
    f.writelines(processed)

print("Processor1 done")