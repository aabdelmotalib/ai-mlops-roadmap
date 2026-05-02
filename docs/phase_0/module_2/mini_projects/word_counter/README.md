# Word Counter Analysis Tool

A Python tool for analyzing text files. It counts words, lines, and characters, then generates a detailed report.

## Features

- Counts total lines in a file
- Counts total words
- Counts total characters
- Calculates average word length
- Generates a formatted report and saves it to `analysis_report.txt`
- Handles missing files gracefully with error messages

## Usage

```bash
python3 word_counter.py
Then enter the filename when prompted:


Enter the text file to analyze: sample.txt
The program will output analysis results and save a report to analysis_report.txt.

Project Structure¶
word_counter.py - Main script with analysis functions
analysis_report.txt - Generated report (created when you run the program)
.gitignore - Prevents tracking of Python cache files
Example¶
Input file: example.txt


The quick brown fox jumps over the lazy dog
This is a test file
Output:


==================================================
ANALYSIS RESULTS
==================================================
File: example.txt
Lines: 2
Words: 15
Characters: 54
Average word length: 3.6
==================================================
Future Improvements¶
Add support for multiple files
Count sentences
Find the longest word
Generate charts or visualizations
