#!/bin/bash
# Post-tool check to verify successful execution

set -e

# Read JSON input from stdin
INPUT=$(cat)

# Extract tool information
TOOL_NAME=$(echo "$INPUT" | jq -r '.toolName // "unknown"' 2>/dev/null || echo "unknown")
TIMESTAMP=$(date +%Y-%m-%d\ %H:%M:%S)

# Log completion
mkdir -p logs
echo "[$TIMESTAMP] Post-tool check: $TOOL_NAME completed" >> logs/tool-usage.log

# Run specific checks based on tool
case "$TOOL_NAME" in
    "file_edit"|"file_create")
        # Check if Python files have syntax errors
        if ls *.py &>/dev/null; then
            for file in *.py; do
                if ! python3 -m py_compile "$file" 2>/dev/null; then
                    echo "⚠️  Syntax error in $file"
                fi
            done
        fi
        ;;
    "pip_install")
        # Verify package was installed
        echo "Verifying pip packages..."
        pip check > /dev/null 2>&1 || echo "⚠️  Dependency issues detected"
        ;;
esac

# Return success
cat <<EOF
{
  "checked": true,
  "toolName": "$TOOL_NAME",
  "timestamp": "$TIMESTAMP"
}
EOF
