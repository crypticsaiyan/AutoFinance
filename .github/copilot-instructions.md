# AutoFinance - GitHub Copilot Custom Instructions

## Project Overview

AutoFinance is an AI-powered financial automation platform built with Model Context Protocol (MCP) servers. This project demonstrates advanced financial analysis, real-time market monitoring, and autonomous trading capabilities.

## Architecture

- **MCP Servers**: Multiple specialized servers handling different financial domains (market data, technical analysis, fundamental analysis, risk management, portfolio analytics, etc.)
- **CLI Interface**: Terminal-based dashboard using Textual for real-time visualization
- **SSE Communication**: Server-Sent Events for real-time data streaming
- **Agent Supervisors**: Trader and Investor supervisor agents for autonomous decision-making

## Coding Standards

### Python Style
- Use Python 3.10+ features including type hints and match statements
- Follow PEP 8 with line length of 100 characters
- Use dataclasses for data structures
- Prefer async/await for I/O operations
- Use pathlib for file operations

### Error Handling
- Always use specific exception types
- Include contextual error messages
- Log errors with appropriate severity levels
- Never expose API keys or sensitive data in error messages

### API Keys and Secrets
- All API keys must be stored in environment variables
- Use `.env` files for local development (never commit these)
- Reference keys as `${VARIABLE_NAME}` in configuration files
- Document all required environment variables in README

### MCP Server Development
- Each server must implement standard MCP protocol
- Include comprehensive tool descriptions
- Validate all input parameters
- Return structured JSON responses
- Include rate limiting and error handling

### Testing
- Write unit tests for all MCP server tools
- Include integration tests for server communication
- Use pytest with async support
- Mock external API calls in tests
- Maintain >80% code coverage

## Financial Domain Guidelines

### Market Data
- Always validate ticker symbols before API calls
- Cache market data appropriately (respect rate limits)
- Handle market hours and timezone conversions
- Include data source attribution

### Technical Analysis
- Use numpy for performance-critical calculations
- Vectorize operations when possible
- Document all indicator formulas
- Include parameter validation for technical indicators

### Risk Management
- Always calculate position sizes considering account risk
- Validate portfolio constraints before execution
- Include stop-loss and take-profit calculations
- Log all risk calculations for audit trail

### Compliance
- Never execute trades without proper validation
- Include regulatory checks for order types
- Log all trade decisions with timestamps
- Implement circuit breakers for abnormal market conditions

## CLI Dashboard
- Use Textual widgets for all UI components
- Implement reactive data binding
- Handle keyboard shortcuts gracefully
- Ensure smooth 60fps updates for charts
- Use color coding consistently (green=positive, red=negative)

## Documentation
- All MCP tools must have clear descriptions
- Include example usage in docstrings
- Document rate limits and quotas
- Provide setup instructions for each server

## Security Best Practices
- Validate and sanitize all user inputs
- Use parameterized queries for database operations
- Implement request throttling
- Never log sensitive financial data
- Use HTTPS for all external API calls

## Performance Considerations
- Cache frequently accessed data
- Use connection pooling for database connections
- Implement pagination for large datasets
- Profile code for bottlenecks
- Use async operations for concurrent API calls

## Git Commit Messages
- Use conventional commits format: `type(scope): message`
- Types: feat, fix, docs, test, refactor, perf, chore
- Include issue references where applicable
- Keep subject line under 72 characters

## Dependencies
- Pin major versions in requirements.txt
- Document why each dependency is needed
- Regularly update dependencies for security patches
- Use virtual environments for isolation
