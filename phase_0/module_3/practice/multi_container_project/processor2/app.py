# Reads step1 output and converts to uppercase

INPUT_FILE = "/output/step1.txt"
OUTPUT_FILE = "/output/final.txt"

with open(INPUT_FILE, "r") as f:
    lines = f.readlines()

processed = [line.upper() for line in lines]

with open(OUTPUT_FILE, "w") as f:
    f.writelines(processed)

print("Processor2 done")