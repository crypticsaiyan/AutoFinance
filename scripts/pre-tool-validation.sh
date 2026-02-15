#!/bin/bash
# Pre-tool validation to ensure safe execution

set -e

# Read JSON input from stdin
INPUT=$(cat)

# Extract tool information
TOOL_NAME=$(echo "$INPUT" | jq -r '.toolName // "unknown"' 2>/dev/null || echo "unknown")
TIMESTAMP=$(date +%Y-%m-%d\ %H:%M:%S)

# Log tool usage
mkdir -p logs
echo "[$TIMESTAMP] Pre-tool validation: $TOOL_NAME" >> logs/tool-usage.log

# Validate specific tools
case "$TOOL_NAME" in
    "file_edit"|"file_create")
        # Check if we're in a safe directory
        if [[ ! "$PWD" =~ /AutoFinance ]]; then
            echo "⚠️  Warning: Tool $TOOL_NAME used outside project directory"
        fi
        ;;
    "bash"|"shell")
        # Log shell command usage
        echo "[$TIMESTAMP] Shell command requested" >> logs/shell-commands.log
        ;;
esac

# Return success
cat <<EOF
{
  "validated": true,
  "toolName": "$TOOL_NAME",
  "timestamp": "$TIMESTAMP"
}
EOF
