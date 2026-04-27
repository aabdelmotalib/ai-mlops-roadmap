# This is our word and line counter program
# It reads a text file and analyzes it

# Function to count words and lines in a file
def analyze_text_file(filename):
    results = {
        "filename": filename,
        "lines": 0,
        "words": 0,
        "characters": 0
    }
    try:
        with open(filename, "r") as file:
            for line in file:
                results["lines"] += 1
                results["characters"] += len(line)
                words_in_line = line.strip().split()
                results["words"] += len(words_in_line)
        if results["words"] > 0:
            avg = results["characters"] / results["words"]
            results["avg_word_length"] = round(avg, 2)
        else:
            results["avg_word_length"] = 0
        
        with open("analysis_report.txt", "w") as report_file:
            # Write header section with separators
            report_file.write("=" * 50 + "\n")
            report_file.write("TEXT FILE ANALYSIS REPORT\n")
            report_file.write("=" * 50 + "\n\n")
            # Write computed statistics in readable format
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
    # Print header for console output
    print("\n" + "=" * 50)
    print("ANALYSIS RESULTS")
    print("=" * 50)

    # Print each field from results dictionary
    print(f"File: {results['filename']}")
    print(f"Lines: {results['lines']}")
    print(f"Words: {results['words']}")
    print(f"Characters: {results['characters']}")
    print(f"Average word length: {results['avg_word_length']}")

    # Print footer separator
    print("=" * 50)

    # Inform user that report file was generated
    print("Report saved to: analysis_report.txt\n")

# Entry point of the program (only runs if script executed directly)
if __name__ == "__main__":

    # Ask user to input filename to analyze
    filename = input("Enter the text file to analyze: ")

    # Run analysis function and store returned results
    results = analyze_text_file(filename)

    # Display results on screen
    display_results(results)

