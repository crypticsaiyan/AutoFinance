#!/bin/bash
# Error handler for Copilot CLI

set -e

# Read JSON input from stdin
INPUT=$(cat)

# Extract error information
ERROR_MSG=$(echo "$INPUT" | jq -r '.error // "Unknown error"' 2>/dev/null || echo "Unknown error")
TIMESTAMP=$(date +%Y-%m-%d\ %H:%M:%S)

# Log error
mkdir -p logs
echo "[$TIMESTAMP] ERROR: $ERROR_MSG" >> logs/copilot-errors.log

# Check for common issues
if [[ "$ERROR_MSG" =~ "API" ]]; then
    echo "💡 Tip: Check your API credentials in .env file"
elif [[ "$ERROR_MSG" =~ "connection" ]]; then
    echo "💡 Tip: Check your network connection and MCP server status"
elif [[ "$ERROR_MSG" =~ "import" ]]; then
    echo "💡 Tip: Try running 'pip install -r requirements.txt'"
fi

# Return error metadata
cat <<EOF
{
  "handled": true,
  "timestamp": "$TIMESTAMP",
  "errorLogged": true
}
EOF
