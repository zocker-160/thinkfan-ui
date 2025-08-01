#!/usr/bin/env bash

# This script ensures that fan control is enabled for the thinkpad_acpi module.

set -e # Exit immediately if a command exits with a non-zero status.

OPTION="options thinkpad_acpi fan_control=1"
CONFIG_DIR="/etc/modprobe.d"
CONFIG_FILE="$CONFIG_DIR/thinkpad_acpi.conf"

# Use grep to search for the exact option string in all files in the directory.
# -q: quiet mode, no output
# -r: recursive search
# -F: treat pattern as a fixed string
# The '|| true' prevents the script from exiting if grep doesn't find a match (exit code 1).
if grep -q -r -F "$OPTION" "$CONFIG_DIR"
then
  # The option is already present in some file, so we do nothing.
  echo "Configuration for 'thinkpad_acpi fan_control=1' already exists. Skipping."
else
  # The option was not found, so we create the configuration file.
  echo "Adding configuration for 'thinkpad_acpi fan_control=1'."
  echo "$OPTION" > "$CONFIG_FILE"
fi

# Reload the kernel module to apply the change immediately.
# First, try to remove the module (if loaded) and then load it again.
# The '|| true' handles cases where the module isn't loaded and can't be removed.
echo "Reloading thinkpad_acpi module to apply settings..."
modprobe -r thinkpad_acpi || true
modprobe thinkpad_acpi

exit 0
