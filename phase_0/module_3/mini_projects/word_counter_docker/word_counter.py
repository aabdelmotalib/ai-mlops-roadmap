# Word counter analysis tool
# Reads a file, analyzes it, and writes a report

import sys
import os


def analyze_text_file(filename):
    # Initialize results dictionary
    results = {
        "filename": filename,
        "lines": 0,
        "words": 0,
        "characters": 0,
    }

    try:
        # Open input file (must exist in /input volume)
        with open(filename, "r") as file:
            for line in file:
                results["lines"] += 1
                results["characters"] += len(line)

                words_in_line = line.strip().split()
                results["words"] += len(words_in_line)

        # Compute average word length
        if results["words"] > 0:
            avg = results["characters"] / results["words"]
            results["avg_word_length"] = round(avg, 2)
        else:
            results["avg_word_length"] = 0

        return results

    except FileNotFoundError:
        print(f"ERROR: File not found: {filename}")
        return None


def display_results(results, output_file):
    if results is None:
        return

    print("\n" + "=" * 50)
    print("ANALYSIS RESULTS")
    print("=" * 50)

    print(f"File analyzed: {results['filename']}")
    print(f"Total lines: {results['lines']}")
    print(f"Total words: {results['words']}")
    print(f"Total characters: {results['characters']}")
    print(f"Average word length: {results['avg_word_length']} characters")

    print("=" * 50)
    print(f"Report saved to: {output_file}")
    print("=" * 50 + "\n")


def save_report(results, output_filename):
    if results is None:
        return

    # Ensure output directory exists (CRITICAL for Docker volumes)
    os.makedirs("/output", exist_ok=True)

    with open(output_filename, "w") as report_file:
        report_file.write("=" * 50 + "\n")
        report_file.write("TEXT FILE ANALYSIS REPORT\n")
        report_file.write("=" * 50 + "\n\n")

        report_file.write(f"File: {results['filename']}\n")
        report_file.write(f"Lines: {results['lines']}\n")
        report_file.write(f"Words: {results['words']}\n")
        report_file.write(f"Characters: {results['characters']}\n")
        report_file.write(f"Average word length: {results['avg_word_length']}\n")

        report_file.write("\n" + "=" * 50 + "\n")


if __name__ == "__main__":
    # Validate CLI args
    if len(sys.argv) < 2:
        print("Usage: python word_counter.py /input/file.txt")
        sys.exit(1)

    input_file = sys.argv[1]

    # Analyze file
    results = analyze_text_file(input_file)

    # Build output filename safely
    base_name = os.path.basename(input_file)
    output_file = f"/output/report_{base_name}"

    # Save report
    save_report(results, output_file)

    # Display results
    display_results(results, output_file)