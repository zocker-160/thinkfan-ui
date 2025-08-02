#!/bin/bash

# This script finds all files in the current directory tree (excluding .git),
# and compiles their paths and contents into a single output file.

# Define the name for the output file
OUTPUT_FILE="repo_snapshot.txt"

# Ensure the script is run from a directory with content
if [ -z "$(ls -A .)" ]; then
  echo "Error: The current directory is empty. Run this script from your repo's root." >&2
  exit 1
fi

# Clear any previous output file to start fresh
> "$OUTPUT_FILE"

# Use 'find' to locate all files (-type f), excluding the .git directory,
# the output file itself, and this script.
# The 'while' loop reads each found filepath.
find . -type f -not -path "./.git/*" -not -name "$OUTPUT_FILE" -not -name "$(basename "$0")" | sort | while IFS= read -r filepath; do
  # Write a header indicating the start of a file's content, including its path
  echo "########## START FILE: ${filepath} ##########" >> "$OUTPUT_FILE"

  # Append the raw content of the file
  cat "${filepath}" >> "$OUTPUT_FILE"

  # Write a footer to clearly mark the end of the file's content, adding newlines for readability
  echo -e "\n########## END FILE: ${filepath} ##########\n" >> "$OUTPUT_FILE"
done

echo "Operation complete. All file contents have been saved to: ${OUTPUT_FILE}"
