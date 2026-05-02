# Word counter with improved functionality

def analyze_text_file(filename):
    # Initialize results
    results = {
        "filename": filename,
        "lines": 0,
        "words": 0,
        "characters": 0,
    }

    try:
        # Open and read the file
        with open(filename, "r") as file:
            # Process each line
            for line in file:
                results["lines"] += 1
                results["characters"] += len(line)

                # Count words
                words_in_line = line.strip().split()
                results["words"] += len(words_in_line)

        # Handle empty file
        if results["lines"] == 0:
            print("Warning: The file is empty!")
            return None

        # Calculate average word length
        if results["words"] > 0:
            results["avg_word_length"] = results["characters"] / results["words"]
            results["avg_word_length"] = round(results["avg_word_length"], 2)
        else:
            results["avg_word_length"] = 0

        # Generate report
        with open("analysis_report.txt", "w") as report_file:
            report_file.write("=" * 50 + "\n")
            report_file.write("TEXT FILE ANALYSIS REPORT\n")
            report_file.write("=" * 50 + "\n\n")
            report_file.write(f"File: {results['filename']}\n")
            report_file.write(f"Lines: {results['lines']}\n")
            report_file.write(f"Words: {results['words']}\n")
            report_file.write(f"Characters: {results['characters']}\n")
            report_file.write(f"Average word length: {results['avg_word_length']}\n")
            report_file.write("\n" + "=" * 50 + "\n")

        return results

    except FileNotFoundError:
        print(f"ERROR: The file '{filename}' was not found!")
        return None


def display_results(results):
    if results is None:
        return

    print("\n" + "=" * 50)
    print("ANALYSIS RESULTS")
    print("=" * 50)
    print(f"File: {results['filename']}")
    print(f"Lines: {results['lines']}")
    print(f"Words: {results['words']}")
    print(f"Characters: {results['characters']}")
    print(f"Average word length: {results['avg_word_length']}")
    print("=" * 50)
    print("Report saved to: analysis_report.txt\n")


if __name__ == "__main__":
    filename = input("Enter the text file to analyze: ")
    results = analyze_text_file(filename)
    display_results(results)
