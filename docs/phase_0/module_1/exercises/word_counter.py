# This is our mini project: a word and line counter
# It reads a text file and generates a report about its contents

# Function to count words and lines in a file
def analyze_text_file(filename):
    # We'll store our results in a dictionary
    # Keys are stat names, values are the results
    results = {
        "filename": filename,
        "lines": 0,
        "words": 0,
        "chars": 0
    }
    try:
        with open(filename, "r") as file:
            for line in file:
                # Increment line count (we've read one more line)
                results["lines"] += 1
                # Count characters in this line (including spaces and newlines)
                results["chars"] += len(line)
                # Strip whitespace and split by spaces to get words
                words_in_line = line.strip() .split()
                results["words"] += len(words_in_line)
        # Calculate average word length (only if we have words)
        if results["words"] > 0:
            results['avg_word_length'] = results["chars"] / results["words"]
            results["avg_word_length"] = round(results["avg_word_length"], 2)
        else:
            results["avg_word_length"] = 0

    # Open a file for writing the report
        with open("analyze_text_file.txt", "w") as report_file:
            # Write a title for the report
            report_file.write("=" * 50 + "\n")
            report_file.write("TEXT FILE ANALYSIS REPORT \n")
            report_file.write("=" * 50 + "\n\n")
            # Write each statistic to the report file
            report_file.write(f"File: {results['filename']}\n")
            report_file.write(f"Lines: {results['lines']}\n")
            report_file.write(f"Words: {results['words']}\n")
            report_file.write(f"Characters: {results['chars']}\n")
            report_file.write(f"Average word length: {results['avg_word_length']} chars \n")
            report_file.write("\n" + "=" * 50 + "\n")
        return results
    except FileNotFoundError:
        # If the file doesn't exist, tell the user
        print(f"ERROR: The file '{filename}' was not found!")
        print("Please make sure the file exists and you have the correct filename.")
        # Return None to indicate failure
        return None

# Function to display the results nicely
def display_results(results):
    # Check if we got valid results
    if results is None:
        return
    # Print a header
    print("\n" + "=" * 50)
    print("ANALYSIS RESULTS")
    print("=" * 50)

    # Print each statistic
    print(f"File analyzed: {results['filename']}")
    print(f"Total lines: {results['lines']}")
    print(f"Total words: {results['words']}")
    print(f"Total characters: {results['chars']}")
    print(f"Average word length: {results['avg_word_length']} characters")

    # Print footer
    print("=" * 50)
    print("Report saved to: analysis_report.txt")
    print("=" * 50 + "\n")


# MAIN PROGRAM: This is where everything happens

# Ask the user for the filename
filename = input("Enter the text file to analyze: ")
results = analyze_text_file(filename)
display_results(results)
