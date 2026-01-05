#!/bin/bash
# Validate AGENTS.md generation

set -e

AGENTS_FILE="${1:-AGENTS.md}"

echo "Validating AGENTS.md generation..."

# Check if file exists
if [ ! -f "$AGENTS_FILE" ]; then
    echo "✗ AGENTS.md file not found at: $AGENTS_FILE"
    exit 1
fi

echo "✓ AGENTS.md file exists"

# Check file is not empty
if [ ! -s "$AGENTS_FILE" ]; then
    echo "✗ AGENTS.md file is empty"
    exit 1
fi

echo "✓ AGENTS.md file is not empty"

# Check for required sections
REQUIRED_SECTIONS=("Overview" "Project Structure" "Coding Conventions" "AI Agent Guidelines")

for section in "${REQUIRED_SECTIONS[@]}"; do
    if grep -q "## $section" "$AGENTS_FILE"; then
        echo "✓ Found section: $section"
    else
        echo "✗ Missing section: $section"
        exit 1
    fi
done

# Check file size (should be reasonable)
FILE_SIZE=$(wc -c < "$AGENTS_FILE")
if [ "$FILE_SIZE" -lt 500 ]; then
    echo "⚠ Warning: AGENTS.md seems too small ($FILE_SIZE bytes)"
fi

if [ "$FILE_SIZE" -gt 50000 ]; then
    echo "⚠ Warning: AGENTS.md seems too large ($FILE_SIZE bytes)"
fi

echo "✓ File size: $FILE_SIZE bytes"

# Validate markdown syntax (basic check)
if head -1 "$AGENTS_FILE" | grep -q "^#"; then
    echo "✓ Valid Markdown header"
else
    echo "⚠ Warning: File doesn't start with Markdown header"
fi

echo ""
echo "✓ AGENTS.md validation complete!"
