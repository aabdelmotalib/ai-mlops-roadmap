# This is our word and line counter program
# It reads a text file and analyzes it

# Function to count words and lines in a file
def analyze_text_file(filename):
    # Initialize a dictionary to store results
    results = {
        "filename": filename,
        "lines": 0,
        "words": 0,
        "characters": 0,
    }

    try:
        # Open the file and read it
        with open(filename, "r") as file:
            # Loop through each line
            for line in file:
                # Count the line
                results["lines"] += 1

                # Count characters
                results["characters"] += len(line)

                # Count words by splitting
                words_in_line = line.strip().split()
                results["words"] += len(words_in_line)

        # Calculate average word length
        if results["words"] > 0:
            results["avg_word_length"] = results["characters"] / results["words"]
            results["avg_word_length"] = round(results["avg_word_length"], 2)
        else:
            results["avg_word_length"] = 0

        # Write report to file
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
        # Handle file not found error
        print(f"ERROR: The file '{filename}' was not found!")
        return None


# Function to display results nicely
def display_results(results):
    # If no results, exit
    if results is None:
        return

    # Print formatted results
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


# Main program
if __name__ == "__main__":
    # Get filename from user
    filename = input("Enter the text file to analyze: ")

    # Analyze it
    results = analyze_text_file(filename)

    # Display results
    display_results(results)
