#!/usr/bin/env bash

# This script automates the process of building the thinkfan-ui RPM package
# within the project's own directory structure.

set -e # Exit immediately if a command exits with a non-zero status.

# --- Configuration ---
PROJECT_ROOT=$(git rev-parse --show-toplevel)
RPM_DIR="$PROJECT_ROOT/linux_packaging/RPM-thinkfan-ui"
SPEC_FILE="$RPM_DIR/thinkfan-ui.spec"

# Define local build directories
TOP_DIR="$RPM_DIR/build"
SOURCES_DIR="$TOP_DIR/SOURCES"
SPECS_DIR="$TOP_DIR/SPECS"
RPMS_DIR="$TOP_DIR/RPMS"

# Extract package name and version from the spec file
VERSION=$(grep -m 1 "Version:" "$SPEC_FILE" | awk '{print $2}')
NAME=$(grep -m 1 "Name:" "$SPEC_FILE" | awk '{print $2}')
ARCHIVE_NAME="$NAME-$VERSION.tar.gz"


# --- Script Logic ---

echo "--- Setting up local RPM build environment in $TOP_DIR ---"
# Clean up previous builds and create fresh directories
rm -rf "$TOP_DIR"
mkdir -p "$SOURCES_DIR" "$SPECS_DIR" "$RPMS_DIR"

echo "--- Creating source archive ---"
# Explicitly change to the project root to ensure git archive includes all files.
# The command is run in a subshell to avoid changing the CWD for the rest of the script.
(cd "$PROJECT_ROOT" && git archive --format=tar.gz --prefix="$NAME-$VERSION/" -o "$RPM_DIR/$ARCHIVE_NAME" HEAD)


echo "--- Copying files to local build directories ---"
mv "$RPM_DIR/$ARCHIVE_NAME" "$SOURCES_DIR/"
cp "$SPEC_FILE" "$SPECS_DIR/"

echo "--- Building RPM package locally ---"
# Use the --define flag to override the default _topdir
rpmbuild -ba "$SPECS_DIR/$(basename "$SPEC_FILE")" --define "_topdir $TOP_DIR"

echo "--- Copying RPM to project directory ---"
find "$RPMS_DIR" -name "*.rpm" -exec cp {} "$PROJECT_ROOT" \;

echo "--- Build complete! RPM located in project root. ---"
exit 0
