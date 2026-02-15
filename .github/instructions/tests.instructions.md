---
applyTo: "tests/**/*.py"
---

# Testing Instructions

## Test Structure
- Use pytest as the testing framework
- Organize tests to mirror the source code structure
- Name test files with `test_` prefix
- Group related tests in classes with `Test` prefix

## Test Coverage
- Aim for >80% code coverage
- Test happy paths and edge cases
- Include error condition tests
- Test async functions with pytest-asyncio

## Mocking
- Mock external API calls to avoid rate limits
- Use pytest fixtures for common test data
- Mock datetime for time-dependent tests
- Never make real API calls in tests

## Financial Data Testing
- Use realistic but fake financial data
- Test with various market conditions (bull, bear, sideways)
- Include tests for market hours and holidays
- Verify calculation accuracy with known values

## MCP Server Testing
- Test each tool independently
- Verify JSON response schemas
- Test error handling and validation
- Include integration tests for tool chains

## Performance Testing
- Benchmark performance-critical functions
- Test with large datasets
- Verify memory usage
- Ensure async operations don't block

## Test Data
- Store test fixtures in `tests/fixtures/`
- Use consistent data formats
- Include edge cases (empty data, extreme values)
- Document test data sources

## Assertions
- Use descriptive assertion messages
- Test one concept per test function
- Use pytest's assert introspection
- Include type checking in tests

## Continuous Integration
- Ensure all tests pass before committing
- Run tests locally before pushing
- Check code coverage reports
- Fix failing tests immediately
