# AutoFinance Deployment Guide

## 🚀 Deployment Options

### Option 1: Local Development

Run each MCP server in a separate terminal for testing and development.

```bash
# Terminal 1: Risk Server
cd mcp-servers/risk
python server.py

# Terminal 2: Execution Server
cd mcp-servers/execution
python server.py

# Terminal 3: Compliance Server
cd mcp-servers/compliance
python server.py

# ... continue for all 12 servers
```

### Option 2: Archestra Orchestration (Recommended)

Configure all servers in Archestra for production orchestration.

#### Step 1: Install Archestra

```bash
npm install -g archestra
```

#### Step 2: Configure MCP Servers

Create `archestra.config.json`:

```json
{
  "servers": {
    "auto-finance-risk": {
      "command": "python",
      "args": ["mcp-servers/risk/server.py"],
      "env": {}
    },
    "auto-finance-execution": {
      "command": "python",
      "args": ["mcp-servers/execution/server.py"],
      "env": {}
    },
    "auto-finance-compliance": {
      "command": "python",
      "args": ["mcp-servers/compliance/server.py"],
      "env": {}
    },
    "auto-finance-market": {
      "command": "python",
      "args": ["mcp-servers/market/server.py"],
      "env": {}
    },
    "auto-finance-technical": {
      "command": "python",
      "args": ["mcp-servers/technical/server.py"],
      "env": {}
    },
    "auto-finance-volatility": {
      "command": "python",
      "args": ["mcp-servers/volatility/server.py"],
      "env": {}
    },
    "auto-finance-news": {
      "command": "python",
      "args": ["mcp-servers/news/server.py"],
      "env": {}
    },
    "auto-finance-trading-supervisor": {
      "command": "python",
      "args": ["mcp-servers/trader-supervisor/server.py"],
      "env": {}
    },
    "auto-finance-fundamental": {
      "command": "python",
      "args": ["mcp-servers/fundamental/server.py"],
      "env": {}
    },
    "auto-finance-macro": {
      "command": "python",
      "args": ["mcp-servers/macro/server.py"],
      "env": {}
    },
    "auto-finance-portfolio-analytics": {
      "command": "python",
      "args": ["mcp-servers/portfolio-analytics/server.py"],
      "env": {}
    },
    "auto-finance-investing-supervisor": {
      "command": "python",
      "args": ["mcp-servers/investor-supervisor/server.py"],
      "env": {}
    }
  }
}
```

#### Step 3: Start Archestra

```bash
archestra start
```

### Option 3: Docker Compose

For containerized deployment.

#### Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  risk:
    build:
      context: ./mcp-servers/risk
    ports:
      - "5001:5000"
    environment:
      - MCP_SERVER_NAME=auto-finance-risk
    restart: unless-stopped

  execution:
    build:
      context: ./mcp-servers/execution
    ports:
      - "5002:5000"
    environment:
      - MCP_SERVER_NAME=auto-finance-execution
    restart: unless-stopped

  compliance:
    build:
      context: ./mcp-servers/compliance
    ports:
      - "5003:5000"
    environment:
      - MCP_SERVER_NAME=auto-finance-compliance
    restart: unless-stopped

  market:
    build:
      context: ./mcp-servers/market
    ports:
      - "5004:5000"
    environment:
      - MCP_SERVER_NAME=auto-finance-market
    restart: unless-stopped

  technical:
    build:
      context: ./mcp-servers/technical
    ports:
      - "5005:5000"
    environment:
      - MCP_SERVER_NAME=auto-finance-technical
    restart: unless-stopped

  volatility:
    build:
      context: ./mcp-servers/volatility
    ports:
      - "5006:5000"
    environment:
      - MCP_SERVER_NAME=auto-finance-volatility
    restart: unless-stopped

  news:
    build:
      context: ./mcp-servers/news
    ports:
      - "5007:5000"
    environment:
      - MCP_SERVER_NAME=auto-finance-news
    restart: unless-stopped

  trader-supervisor:
    build:
      context: ./mcp-servers/trader-supervisor
    ports:
      - "5008:5000"
    environment:
      - MCP_SERVER_NAME=auto-finance-trading-supervisor
    depends_on:
      - risk
      - execution
      - compliance
      - market
      - technical
      - volatility
      - news
    restart: unless-stopped

  fundamental:
    build:
      context: ./mcp-servers/fundamental
    ports:
      - "5009:5000"
    environment:
      - MCP_SERVER_NAME=auto-finance-fundamental
    restart: unless-stopped

  macro:
    build:
      context: ./mcp-servers/macro
    ports:
      - "5010:5000"
    environment:
      - MCP_SERVER_NAME=auto-finance-macro
    restart: unless-stopped

  portfolio-analytics:
    build:
      context: ./mcp-servers/portfolio-analytics
    ports:
      - "5011:5000"
    environment:
      - MCP_SERVER_NAME=auto-finance-portfolio-analytics
    restart: unless-stopped

  investor-supervisor:
    build:
      context: ./mcp-servers/investor-supervisor
    ports:
      - "5012:5000"
    environment:
      - MCP_SERVER_NAME=auto-finance-investing-supervisor
    depends_on:
      - risk
      - execution
      - compliance
      - fundamental
      - macro
      - portfolio-analytics
    restart: unless-stopped
```

#### Create Dockerfile for each server:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

EXPOSE 5000

CMD ["python", "server.py"]
```

#### Deploy:

```bash
docker-compose up -d
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Risk Policy Configuration
RISK_MAX_POSITION_SIZE=0.15
RISK_MAX_VOLATILITY=0.50
RISK_MIN_CONFIDENCE=0.60
RISK_MAX_SINGLE_TRADE=20000

# Execution Server
EXECUTION_INITIAL_CASH=100000

# Market Server
MARKET_API_KEY=your_binance_api_key
MARKET_SIMULATION_MODE=true
```

### Risk Policy Configuration

Edit `mcp-servers/risk/server.py`:

```python
RISK_POLICY = {
    "max_position_size": 0.15,        # 15% max per position
    "max_volatility": 0.5,            # 50% annualized
    "min_confidence": 0.6,            # 60% minimum
    "max_portfolio_exposure": 0.8,    # 80% max invested
    "max_single_trade_value": 20000,  # $20k per trade
}
```

---

## 🧪 Testing Deployment

### Health Check Script

```python
import asyncio
from mcp.client import MCPClient

async def check_server_health(server_name, tool_name):
    """Check if a server is responding"""
    try:
        client = MCPClient(server_name)
        await client.connect()
        result = await client.call_tool(tool_name, {})
        print(f"✅ {server_name} - OK")
        return True
    except Exception as e:
        print(f"❌ {server_name} - FAILED: {e}")
        return False

async def health_check():
    """Check all servers"""
    servers = [
        ("auto-finance-risk", "get_risk_policy"),
        ("auto-finance-execution", "get_portfolio_state"),
        ("auto-finance-compliance", "get_compliance_metrics"),
        # ... add all servers
    ]
    
    results = await asyncio.gather(*[
        check_server_health(name, tool) 
        for name, tool in servers
    ])
    
    healthy = sum(results)
    total = len(results)
    
    print(f"\n{healthy}/{total} servers healthy")

if __name__ == "__main__":
    asyncio.run(health_check())
```

---

## 📊 Monitoring

### Key Metrics to Monitor

1. **Server Health**
   - Uptime per server
   - Response times
   - Error rates

2. **Business Metrics**
   - Trades per hour
   - Approval rate (from compliance)
   - Execution success rate
   - Average risk score

3. **System Metrics**
   - CPU/Memory per server
   - Network latency between servers
   - Queue depths (if using message queues)

### Prometheus Integration

```python
from prometheus_client import Counter, Histogram, start_http_server

# In each server
trades_total = Counter('trades_total', 'Total trades processed')
trade_latency = Histogram('trade_latency', 'Trade processing time')

@mcp.tool()
def execute_trade(...):
    with trade_latency.time():
        # ... execute trade
        trades_total.inc()
```

### Grafana Dashboard

Visualize:
- Trade volume over time
- Approval vs rejection rates
- Server health status
- Portfolio value over time

---

## 🔒 Security Considerations

### Production Hardening

1. **Authentication**
   ```python
   # Add API key validation
   @mcp.tool()
   def execute_trade(api_key: str, ...):
       if not validate_api_key(api_key):
           raise PermissionError("Invalid API key")
   ```

2. **Rate Limiting**
   ```python
   from ratelimit import limits
   
   @limits(calls=100, period=60)  # 100 calls per minute
   @mcp.tool()
   def process_trade_request(...):
       ...
   ```

3. **Input Validation**
   ```python
   from pydantic import BaseModel, validator
   
   class TradeRequest(BaseModel):
       symbol: str
       quantity: float
       
       @validator('quantity')
       def quantity_positive(cls, v):
           if v <= 0:
               raise ValueError('Quantity must be positive')
           return v
   ```

4. **Encryption**
   - Use TLS for all MCP connections
   - Encrypt sensitive data at rest
   - Use secrets management (HashiCorp Vault, AWS Secrets Manager)

### Network Security

```yaml
# Docker network isolation
networks:
  governance:
    driver: bridge
  trading:
    driver: bridge
  investing:
    driver: bridge

services:
  risk:
    networks:
      - governance
  
  market:
    networks:
      - trading
```

---

## 📈 Scaling Strategy

### Horizontal Scaling Tiers

**Tier 1: Analytical Agents (Highly Scalable)**
- Market, Technical, Volatility, News, Fundamental, Macro
- Stateless, read-only
- Scale to 10+ instances per server

**Tier 2: Orchestration (Moderately Scalable)**
- Trading Supervisor, Investing Supervisor
- Mostly stateless
- Scale to 3-5 instances per server

**Tier 3: Governance (Limited Scaling)**
- Risk (3-5 instances, policy is read-only)
- Compliance (3-5 instances with shared log store)
- Execution (1 instance OR shared state architecture)

### Load Balancing

```nginx
# Nginx configuration for MCP servers
upstream market_servers {
    least_conn;
    server market-1:5000;
    server market-2:5000;
    server market-3:5000;
}

server {
    location /mcp/market {
        proxy_pass http://market_servers;
    }
}
```

---

## 🗄 Data Persistence

### Execution Server State

**Option 1: In-Memory (Demo)**
```python
PORTFOLIO_STATE = {...}  # Lost on restart
```

**Option 2: Redis**
```python
import redis
r = redis.Redis(host='localhost', port=6379)

def get_portfolio_state():
    return json.loads(r.get('portfolio_state'))

def update_portfolio_state(state):
    r.set('portfolio_state', json.dumps(state))
```

**Option 3: PostgreSQL**
```python
import psycopg2

def get_portfolio_state():
    conn = psycopg2.connect(...)
    # ... query portfolio table
```

### Compliance Audit Log

**Option 1: In-Memory (Demo)**
```python
AUDIT_LOG = []
```

**Option 2: Database (Production)**
```sql
CREATE TABLE audit_log (
    event_id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    event_type VARCHAR(50),
    agent_name VARCHAR(100),
    action VARCHAR(100),
    details JSONB,
    severity VARCHAR(20)
);

CREATE INDEX idx_timestamp ON audit_log(timestamp);
CREATE INDEX idx_event_type ON audit_log(event_type);
```

---

## 🔄 Backup & Recovery

### Backup Strategy

```bash
# Backup portfolio state
docker exec execution-server python -c "
from server import PORTFOLIO_STATE
import json
print(json.dumps(PORTFOLIO_STATE))
" > backup_$(date +%Y%m%d_%H%M%S).json

# Backup audit log
docker exec compliance-server python -c "
from server import AUDIT_LOG
import json
print(json.dumps(AUDIT_LOG))
" > audit_backup_$(date +%Y%m%d_%H%M%S).json
```

### Recovery

```python
# Restore portfolio state
@mcp.tool()
def restore_portfolio(backup_data: dict):
    global PORTFOLIO_STATE
    PORTFOLIO_STATE = backup_data
    return {"success": True}
```

---

## 🚨 Disaster Recovery

### High Availability Setup

```yaml
# Multi-region deployment
regions:
  - us-east-1
  - us-west-2
  - eu-west-1

# Each region runs full stack
# Active-passive for execution server
# Active-active for analytical servers
```

### Failover Strategy

1. Health monitoring detects failure
2. DNS failover to backup region
3. Restore portfolio state from last backup
4. Resume operations

---

## 📝 Deployment Checklist

- [ ] Install dependencies (`pip install -r requirements.txt`)
- [ ] Configure environment variables
- [ ] Set up database for compliance logs (if production)
- [ ] Set up Redis/database for execution state (if production)
- [ ] Configure Archestra or container orchestration
- [ ] Set up monitoring and alerting
- [ ] Configure backups
- [ ] Test health checks
- [ ] Run integration tests
- [ ] Review security settings
- [ ] Set up log aggregation
- [ ] Document runbooks for common issues
- [ ] Train team on operations

---

## 📚 Additional Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [Archestra GitHub](https://github.com/archestra/archestra)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)

---

**AutoFinance Deployment Guide** - From local development to production deployment.
