#!/bin/bash
# Check environment variables required for AutoFinance

set -e

echo "Checking required environment variables..."

# List of required API keys
REQUIRED_VARS=(
    "ALPHA_VANTAGE_API_KEY"
    "FINNHUB_API_KEY"
    "POLYGON_API_KEY"
    "NEWS_API_KEY"
)

MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo "⚠️  Warning: Missing environment variables:"
    for var in "${MISSING_VARS[@]}"; do
        echo "  - $var"
    done
    echo ""
    echo "Some MCP servers may not function properly."
    echo "Please set these in your .env file."
else
    echo "✅ All required environment variables are set"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "Create one from .env.example if available"
fi

exit 0
