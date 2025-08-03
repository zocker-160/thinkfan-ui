#!/usr/bin/env python3
import sys
import os

# This script is intended to be run with pkexec to get root privileges.
# It takes the full path to the config file as the first argument
# and the YAML content to write as the second argument.

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: pkexec save_helper.py <file_path> <content>")
        sys.exit(1)

    file_path = sys.argv[1]
    content = sys.argv[2]

    # Security check: Ensure we are only writing to the intended file
    if os.path.abspath(file_path) != "/etc/thinkfan.conf":
        print(f"Error: This helper can only write to /etc/thinkfan.conf, not {file_path}")
        sys.exit(1)

    try:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Successfully wrote to {file_path}")
        sys.exit(0)
    except Exception as e:
        print(f"Failed to write to {file_path}: {e}")
        sys.exit(1)
