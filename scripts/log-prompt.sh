#!/bin/bash
# Log user prompts for analytics and debugging

set -e

# Read JSON input from stdin
INPUT=$(cat)

# Extract relevant information
TIMESTAMP=$(date +%Y-%m-%d\ %H:%M:%S)
PROMPT=$(echo "$INPUT" | jq -r '.userPrompt // "N/A"' 2>/dev/null || echo "N/A")

# Create logs directory if it doesn't exist
mkdir -p logs

# Log the prompt (sanitized)
echo "[$TIMESTAMP] User prompt submitted" >> logs/prompts.log

# Output JSON for Copilot (optional metadata)
cat <<EOF
{
  "logged": true,
  "timestamp": "$TIMESTAMP"
}
EOF
