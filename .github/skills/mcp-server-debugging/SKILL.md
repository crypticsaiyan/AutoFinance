---
name: mcp-server-debugging
description: Debug and troubleshoot MCP servers in the AutoFinance platform. Use when servers fail to start, tools return errors, or communication issues occur.
license: MIT
---

# MCP Server Debugging Skill

This skill provides a systematic approach to debugging MCP servers in the AutoFinance platform.

## Debugging Workflow

### 1. Verify Server Status

First, check if the server is running:

```bash
# Check if server process is running
ps aux | grep -i server.py

# Check server logs
tail -f mcp-servers/<server-name>/logs/server.log

# Test server health endpoint (if available)
curl http://localhost:<port>/health
```

### 2. Check Environment Variables

Verify all required environment variables are set:

```bash
# List all environment variables
env | grep -E "(ALPHA_VANTAGE|FINNHUB|POLYGON|NEWS)"

# Check .env file exists and is loaded
cat .env | grep API_KEY
```

### 3. Test Server Tools

Test individual tools in isolation:

```bash
# Use the test scripts
python tests/test_<server>_server.py

# Or test manually with curl (for SSE servers)
curl http://localhost:<port>/tools/<tool-name>
```

### 4. Verify Dependencies

Check that all Python dependencies are installed:

```bash
# Activate virtual environment
source venv/bin/activate

# Check installed packages
pip list | grep -E "(mcp|asyncio|aiohttp)"

# Install missing dependencies
pip install -r mcp-servers/requirements.txt
```

### 5. Check API Credentials

Verify API credentials are valid and not rate-limited:

```bash
# Test API credentials directly
curl "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&apikey=${ALPHA_VANTAGE_API_KEY}"

# Check rate limits
echo "Check API dashboard for quota usage"
```

### 6. Review Server Logs

Look for common error patterns in logs:

- `Connection refused`: Server not running or wrong port
- `Authentication failed`: Invalid API credentials
- `Rate limit exceeded`: Too many API calls
- `Timeout`: Network issues or slow API
- `JSON decode error`: Malformed API response

### 7. Test Server Communication

Verify SSE/HTTP communication:

```bash
# Test SSE connection
curl -N http://localhost:<port>/sse

# Check for CORS issues
curl -H "Origin: http://localhost:3000" -I http://localhost:<port>
```

## Common Issues and Solutions

### Server Won't Start

```bash
# Check port availability
netstat -tulpn | grep <port>

# Kill existing process
pkill -f server.py

# Start with verbose logging
python mcp-servers/<server-name>/server.py --verbose
```

### Tool Returns Empty Data

1. Check API credentials are valid
2. Verify input parameters are correct
3. Check if market is open (for market data)
4. Review API rate limits
5. Test API endpoint directly

### Import Errors

```bash
# Verify Python path
echo $PYTHONPATH

# Add project root to path
export PYTHONPATH="${PYTHONPATH}:/home/cryptosaiyan/Documents/AutoFinance"

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

### Memory Leaks

```bash
# Monitor memory usage
top -p $(pgrep -f server.py)

# Use memory profiler
python -m memory_profiler mcp-servers/<server-name>/server.py
```

## Debugging Checklist

- [ ] Server process is running
- [ ] Port is not blocked by firewall
- [ ] Environment variables are set
- [ ] API credentials are valid
- [ ] Dependencies are installed
- [ ] Logs show no errors
- [ ] Network connectivity is working
- [ ] Data format is correct
- [ ] Rate limits not exceeded
- [ ] Python version is 3.10+

## Advanced Debugging

For complex issues, use Python debugger:

```python
# Add breakpoint in server code
import pdb; pdb.set_trace()

# Or use ipdb for better interface
import ipdb; ipdb.set_trace()

# Run server in debug mode
python -m pdb mcp-servers/<server-name>/server.py
```
