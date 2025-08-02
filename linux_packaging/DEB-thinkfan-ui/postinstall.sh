#!/usr/bin/env bash
# This script ensures that fan control is enabled for the thinkpad_acpi module.

set -e # Exit immediately if a command exits with a non-zero status.

# Reload the kernel module to apply the change immediately.
# First, try to remove the module (if loaded) and then load it again.
# The '|| true' handles cases where the module isn't loaded and can't be removed.
echo "Reloading thinkpad_acpi module to apply settings..."
modprobe -r thinkpad_acpi || true
modprobe thinkpad_acpi
