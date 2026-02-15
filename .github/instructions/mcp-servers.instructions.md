---
applyTo: "mcp-servers/**/*.py"
---

# MCP Server Development Instructions

## Server Structure
- Each MCP server should be self-contained in its own directory
- Include a `server.py` file as the main entry point
- Implement proper error handling for all tools
- Use type hints for all function parameters and returns

## Tool Implementation
- Every tool must have a clear, descriptive name
- Include comprehensive docstrings explaining:
  - What the tool does
  - Required parameters and their types
  - Expected return values
  - Example usage
- Validate all input parameters before processing
- Return structured JSON responses with consistent schema

## Data Handling
- Never hardcode API keys - use environment variables
- Implement proper data caching to respect API rate limits
- Handle timezone conversions for financial data
- Validate ticker symbols and financial instruments
- Include proper error messages for invalid inputs

## Async Operations
- Use async/await for all I/O operations
- Implement proper connection pooling
- Handle timeouts gracefully
- Use asyncio.gather for concurrent operations

## Testing Requirements
- Write unit tests for each tool
- Mock external API calls
- Test edge cases and error conditions
- Verify JSON response schemas
- Include integration tests for tool interactions

## Logging
- Log all API calls with timestamps
- Include request/response details for debugging
- Never log sensitive data (API keys, credentials)
- Use appropriate log levels (DEBUG, INFO, WARNING, ERROR)

## Financial Data Standards
- Use ISO 4217 currency codes
- Format prices with appropriate decimal precision
- Include data source attribution
- Handle market hours and trading calendars
- Implement proper date/time handling with timezone awareness
