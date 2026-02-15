# AutoFinance - AI Agent Instructions

This document provides guidance for AI agents working on the AutoFinance platform - an AI-powered financial automation system built with Model Context Protocol (MCP) servers.

## Project Context

AutoFinance is a comprehensive financial automation platform that demonstrates:
- Real-time market data aggregation and analysis
- Technical and fundamental analysis capabilities
- Risk management and portfolio optimization
- Autonomous trading through supervisor agents
- Terminal-based dashboard for real-time monitoring

### Technology Stack
- **Language**: Python 3.10+
- **Framework**: Model Context Protocol (MCP) for server architecture
- **UI**: Textual for CLI dashboard
- **Communication**: Server-Sent Events (SSE) for real-time data
- **Testing**: pytest with async support

## Architecture Overview

```
AutoFinance/
├── mcp-servers/           # MCP servers for different financial domains
│   ├── market/           # Market data (real-time quotes, historical data)
│   ├── technical/        # Technical analysis (RSI, MACD, Bollinger Bands)
│   ├── fundamental/      # Fundamental analysis (earnings, ratios)
│   ├── risk/             # Risk management (position sizing, portfolio risk)
│   ├── portfolio-analytics/  # Portfolio tracking and P&L
│   ├── execution/        # Order execution and management
│   ├── news/             # Financial news aggregation
│   ├── alert-engine/     # Alert system for price/indicator triggers
│   ├── trader-supervisor/    # Autonomous trading agent
│   └── investor-supervisor/  # Long-term investment agent
├── cli/                  # Textual-based dashboard
│   ├── components/       # UI components (charts, portfolio, search)
│   └── data/             # Data fetchers
└── tests/                # Comprehensive test suite
```

## Development Principles

### Code Quality
1. **Type Hints**: Use type hints for all function parameters and returns
2. **Documentation**: Every function needs a clear docstring
3. **Error Handling**: Use specific exceptions with descriptive messages
4. **Async Best Practices**: Use async/await for I/O, never block the event loop
5. **Testing**: Maintain >80% code coverage with pytest

### Financial Domain Specifics
1. **Data Validation**: Always validate ticker symbols, dates, and numerical values
2. **Precision**: Use appropriate decimal precision for financial calculations
3. **Timezone Awareness**: Handle market hours and timezone conversions correctly
4. **Data Attribution**: Always include data source in responses
5. **Security**: Never log API keys, credentials, or sensitive financial data

### MCP Server Guidelines
1. **Tool Naming**: Use clear, descriptive names (e.g., `get_stock_quote`, `calculate_rsi`)
2. **Input Validation**: Validate all parameters before processing
3. **Consistent Responses**: Return JSON with consistent schema
4. **Rate Limiting**: Implement caching and respect API rate limits
5. **Error Context**: Include helpful context in error messages

### CLI Development
1. **Responsive Design**: Support various terminal sizes
2. **Real-Time Updates**: Use reactive properties for automatic UI updates
3. **Keyboard Navigation**: Implement intuitive keyboard shortcuts
4. **Performance**: Target 60fps rendering, optimize data updates
5. **Error States**: Show user-friendly error messages with recovery options

## Common Tasks

### Adding a New MCP Server

1. Create directory: `mcp-servers/new-server/`
2. Implement `server.py` with MCP protocol
3. Add environment variables to `.env.example`
4. Write tests: `tests/test_new_server.py`
5. Update `start_sse_servers.sh` to include new server
6. Document tools and usage in README

### Implementing a Technical Indicator

1. Add calculation function in `mcp-servers/technical/indicators/`
2. Use numpy for vectorized operations
3. Add tool decorator in `server.py`
4. Write unit tests with known values
5. Document formula and parameters
6. Add to technical analysis server tools

### Adding a Dashboard Component

1. Create widget in `cli/components/`
2. Implement reactive properties for data
3. Use Textual composition pattern
4. Add to main dashboard layout
5. Implement keyboard shortcuts
6. Write component tests
7. Document usage and shortcuts

## Testing Requirements

Every code change must include:

1. **Unit Tests**: Test individual functions in isolation
2. **Integration Tests**: Test tool workflows end-to-end
3. **Mock External APIs**: Never make real API calls in tests
4. **Edge Cases**: Test error conditions, empty data, extreme values
5. **Performance Tests**: Benchmark critical calculations

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_market_server.py

# Run in watch mode
ptw
```

## Environment Setup

### Required Environment Variables

```bash
# Market Data APIs
ALPHA_VANTAGE_API_KEY=your_key_here
FINNHUB_API_KEY=your_key_here
POLYGON_API_KEY=your_key_here

# News APIs
NEWS_API_KEY=your_key_here

# Optional for enhanced features
OPENAI_API_KEY=your_key_here  # For LLM-based analysis
```

### Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
pip install -r mcp-servers/requirements.txt
pip install -r cli/requirements.txt

# Start MCP servers
./start_sse_servers.sh

# Run CLI dashboard
cd cli && python main.py
```

## Debugging Strategies

### MCP Server Issues

1. Check logs: `tail -f mcp-servers/<name>/logs/*.log`
2. Verify environment variables: `env | grep API_KEY`
3. Test API directly: `curl <api_endpoint>`
4. Run server in debug mode: `python server.py --debug`
5. Check port availability: `netstat -tulpn | grep <port>`

### CLI Dashboard Issues

1. Use Textual devtools: `textual console`
2. Enable debug mode: `DEBUG=1 python main.py`
3. Check component logs: `app.log(message)`
4. Profile performance: `textual --profile`
5. Test in isolation: Run individual component tests

### Performance Issues

1. Profile code: `python -m cProfile script.py`
2. Memory profiling: `python -m memory_profiler script.py`
3. Check async operations: Ensure no blocking I/O
4. Monitor API calls: Check for excessive requests
5. Review caching: Verify cache hit rates

## Code Style Guidelines

### Python Style (PEP 8)

```python
# Good
def calculate_rsi(
    prices: np.ndarray,
    period: int = 14
) -> float:
    """
    Calculate Relative Strength Index.
    
    Args:
        prices: Array of closing prices
        period: RSI period (default: 14)
        
    Returns:
        RSI value between 0 and 100
    """
    # Implementation
    pass

# Bad
def calc_rsi(p, per=14):  # No type hints, unclear names
    pass  # No docstring
```

### Async/Await

```python
# Good
async def fetch_quote(symbol: str) -> dict:
    """Fetch quote asynchronously."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# Bad
def fetch_quote(symbol: str) -> dict:
    """Blocking synchronous call."""
    response = requests.get(url)  # Blocks event loop
    return response.json()
```

### Error Handling

```python
# Good
try:
    quote = await fetch_quote(symbol)
except ValueError as e:
    logger.error(f"Invalid symbol: {symbol}")
    raise ValueError(f"Cannot fetch quote for {symbol}: {e}")
except aiohttp.ClientError as e:
    logger.error(f"API error: {e}")
    raise ConnectionError(f"Failed to connect to market data API: {e}")

# Bad
try:
    quote = await fetch_quote(symbol)
except:  # Too broad
    pass  # Silently swallowing errors
```

## Financial Calculations

### Position Sizing

```python
def calculate_position_size(
    account_value: float,
    risk_per_trade: float,
    entry_price: float,
    stop_loss: float
) -> int:
    """
    Calculate position size based on risk.
    
    Args:
        account_value: Total account value
        risk_per_trade: Risk as decimal (0.01 = 1%)
        entry_price: Entry price per share
        stop_loss: Stop loss price
        
    Returns:
        Number of shares to buy
    """
    risk_amount = account_value * risk_per_trade
    risk_per_share = abs(entry_price - stop_loss)
    shares = int(risk_amount / risk_per_share)
    return shares
```

### Portfolio Metrics

```python
def calculate_sharpe_ratio(
    returns: np.ndarray,
    risk_free_rate: float = 0.02
) -> float:
    """
    Calculate Sharpe ratio.
    
    Args:
        returns: Array of periodic returns
        risk_free_rate: Annual risk-free rate
        
    Returns:
        Sharpe ratio (higher is better)
    """
    excess_returns = returns - (risk_free_rate / 252)  # Daily
    return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
```

## Security Considerations

1. **API Keys**: Store in environment variables, never hardcode
2. **Logging**: Never log sensitive data (keys, credentials, PII)
3. **Input Validation**: Sanitize all user inputs
4. **Dependencies**: Regularly update to patch vulnerabilities
5. **Secrets Management**: Use proper secrets management in production

## Communication Guidelines

### Git Commits

Use conventional commits:
```
feat(market): add real-time quote streaming
fix(technical): correct RSI calculation for edge cases
docs(readme): update installation instructions
test(portfolio): add tests for P&L calculation
refactor(cli): improve chart rendering performance
```

### Pull Requests

Include in PR description:
- What changes were made
- Why the changes were necessary
- How to test the changes
- Any breaking changes
- Screenshots (for UI changes)

## Resources

- **MCP Documentation**: https://github.com/anthropics/mcp
- **Textual Documentation**: https://textual.textualize.io/
- **Financial APIs**: Alpha Vantage, Finnhub, Polygon.io
- **Testing**: pytest, pytest-asyncio, pytest-mock

## Getting Help

When stuck:
1. Check project documentation and README files
2. Review existing similar implementations
3. Check test files for usage examples
4. Review MCP server logs for errors
5. Use debugging tools and profilers

## Success Criteria

A well-implemented feature should:
- ✅ Follow code style guidelines
- ✅ Include comprehensive tests (>80% coverage)
- ✅ Have clear documentation
- ✅ Handle errors gracefully
- ✅ Perform efficiently
- ✅ Be secure (no exposed secrets)
- ✅ Work across different environments
- ✅ Include logging for debugging

---

Remember: This project showcases advanced AI-powered financial automation. Every contribution should demonstrate best practices in software engineering, financial domain knowledge, and user experience design.
