# AutoFinance

**A Hierarchical Financial AI Control Plane**

Built for the WeMakeDevs "2 Fast 2 MCP" Hackathon

---

## 🎯 Project Overview

AutoFinance demonstrates **enterprise-grade distributed AI architecture** using real MCP servers orchestrated by Archestra. This is **NOT a trading bot** — it's a showcase of:

- ✅ Real MCP-native architecture
- ✅ Multi-agent swarm orchestration
- ✅ Tool-level authority boundaries
- ✅ Zero-trust governance enforcement
- ✅ Strict separation between analysis and execution
- ✅ Observability and audit logging
- ✅ Clean distributed architecture

---

## 🏗 Architecture

### Two Independent Domains

**🟢 Trading Domain** (Short-term Tactical)
- Market data analysis
- Technical indicators
- Volatility scoring
- News sentiment
- Trading supervisor

**🔵 Investing Domain** (Long-term Strategic)
- Fundamental analysis
- Macro environment
- Portfolio analytics
- Investing supervisor

### Shared Governance Layer

**🔴 Governance Servers** (Zero-trust enforcement)
- **Risk Server**: Policy validation only
- **Execution Server**: ONLY authority that modifies state
- **Compliance Server**: Audit logging

---

## 📦 MCP Server Architecture

### Shared Governance (3 servers)

#### 1. `auto-finance-risk-server`
**Purpose**: Pure policy validation  
**Tools**:
- `validate_trade` - Validate trading proposals
- `validate_rebalance` - Validate rebalancing proposals
- `get_risk_policy` - Get current policy configuration

**Authority**: VALIDATION ONLY - Cannot execute

#### 2. `auto-finance-execution-server`
**Purpose**: THE ONLY server that modifies portfolio state  
**Tools**:
- `execute_trade` - Execute approved trade
- `apply_rebalance` - Apply approved rebalance
- `get_portfolio_state` - Read portfolio (read-only)
- `update_position_prices` - Mark-to-market updates
- `reset_portfolio` - Reset for testing

**Authority**: EXECUTION ONLY - Does not validate

#### 3. `auto-finance-compliance-server`
**Purpose**: Audit trail and compliance logging  
**Tools**:
- `log_event` - Log compliance event
- `generate_audit_report` - Generate audit report
- `get_recent_events` - Get recent events
- `get_compliance_metrics` - Get compliance KPIs

**Authority**: LOGGING ONLY - Observer pattern

---

### Trading Domain (5 servers)

#### 4. `auto-finance-market-server`
**Tools**: `get_live_price`, `get_candles`, `calculate_volatility`, `set_simulation_mode`

#### 5. `auto-finance-technical-server`
**Tools**: `generate_signal`, `analyze_trend`, `get_support_resistance`, `set_simulation_signal`

#### 6. `auto-finance-volatility-server`
**Tools**: `get_volatility_score`, `compare_volatility`, `get_volatility_forecast`, `set_simulation_volatility`

#### 7. `auto-finance-news-server`
**Tools**: `analyze_sentiment`, `get_market_sentiment`, `analyze_custom_headline`, `set_simulation_sentiment`

#### 8. `auto-finance-trading-supervisor-server`
**Tools**: `process_trade_request`

**Flow**:
1. Calls analytical agents via MCP
2. Aggregates intelligence
3. Builds trade proposal
4. Calls risk server
5. If approved → calls execution server
6. Logs everything via compliance server

---

### Investing Domain (4 servers)

#### 9. `auto-finance-fundamental-server`
**Tools**: `analyze_fundamentals`, `compare_fundamentals`, `get_investment_thesis`, `set_simulation_fundamentals`

#### 10. `auto-finance-macro-server`
**Tools**: `analyze_macro`, `get_sector_outlook`, `assess_portfolio_timing`, `get_correlation_analysis`, `set_simulation_macro`

#### 11. `auto-finance-portfolio-analytics-server`
**Tools**: `evaluate_portfolio`, `calculate_rebalance_proposal`, `get_allocation_summary`, `set_simulation_portfolio`

#### 12. `auto-finance-investing-supervisor-server`
**Tools**: `process_investment_review`

**Flow**:
1. Calls fundamental, macro, portfolio analytics
2. Builds rebalance proposal
3. Calls risk server
4. If approved → calls execution server
5. Logs everything via compliance server

---

## 🔐 Critical Architectural Rules

1. ❌ **No MCP server may directly import another server**
2. ✅ **All communication via MCP tool calls**
3. ✅ **Only execution server modifies portfolio state**
4. ❌ **Risk server cannot execute**
5. ❌ **Supervisors cannot execute**
6. ❌ **Analytical servers cannot validate risk**
7. ✅ **Compliance server only logs**
8. ✅ **Deterministic demo mode exists**
9. ❌ **No circular dependencies**
10. ✅ **Clear structured JSON tool I/O**

---

## 🚀 Quick Start

### Prerequisites

```bash
# Install dependencies
pip install mcp fastmcp

# Or install from requirements
cd mcp-servers
pip install -r requirements.txt
```

### Running Individual Servers

```bash
# Start any MCP server
cd mcp-servers/risk
python server.py

# Start another server in a new terminal
cd mcp-servers/execution
python server.py
```

### Running Orchestrated Demo

```bash
# Run the trading demo
python demo_trading.py

# Run the investing demo
python demo_investing.py

# Run the complete demo
python demo_complete.py
```

---

## 🧪 Demo Scenarios

### Scenario 1: Approved Trade

```python
# Trading supervisor receives request
# → Calls market, technical, volatility, news servers
# → Aggregates signals
# → Builds trade proposal
# → Risk server validates → APPROVED
# → Execution server executes
# → Compliance logs everything
```

### Scenario 2: Rejected Trade (Risk Violation)

```python
# Same flow but:
# → Risk server detects policy violation (e.g., too high volatility)
# → Returns REJECTED
# → Execution never called
# → Compliance logs rejection
```

### Scenario 3: Approved Rebalance

```python
# Investing supervisor runs periodic review
# → Calls fundamental, macro, portfolio analytics
# → Determines rebalancing needed
# → Builds rebalance proposal
# → Risk server validates → APPROVED
# → Execution server applies rebalance
# → Compliance logs everything
```

---

## 📊 Observability

### Compliance Audit Trail

Every action is logged with:
- Event type (proposal, risk_decision, execution, error)
- Agent name
- Action taken
- Detailed metadata
- Timestamp

### Audit Reports

```python
# Generate audit report
compliance.generate_audit_report(
    event_type="risk_decision",
    start_time="2026-02-01T00:00:00Z"
)

# Get compliance metrics
compliance.get_compliance_metrics()
# Returns: approval rates, execution success rates, etc.
```

---

## 🎯 Hackathon Alignment

### How AutoFinance Demonstrates MCP Excellence

#### 1. **MCP-Native Agent Swarms** ✅
- 12 independent MCP servers
- No local cross-imports
- Pure MCP tool communication

#### 2. **Tool Isolation** ✅
- Each server exposes specific tools
- Clear authority boundaries
- No overlapping capabilities

#### 3. **Governance Enforcement** ✅
- Risk validation layer
- Execution authority separation
- Compliance observability

#### 4. **Observability** ✅
- Comprehensive audit logging
- Compliance metrics
- Event tracing

#### 5. **Clean Orchestration** ✅
- Supervisor pattern
- Aggregation logic
- Structured proposals

#### 6. **Scalable Architecture** ✅
- Horizontally scalable
- Stateless analytical agents
- Centralized state management

---

## 🏆 Key Design Decisions

### Why Separation of Concerns?

**Risk Server** validates but cannot execute  
→ Prevents policy bypass

**Execution Server** executes but does not validate  
→ Single source of truth for state

**Analytical Agents** produce intelligence only  
→ No decision authority

**Supervisors** orchestrate but cannot execute directly  
→ Enforced governance path

### Why MCP-Native?

- **Archestra orchestration** ready out of the box
- **Tool-level security** boundaries
- **Language agnostic** - can mix Python, TypeScript, etc.
- **Production-grade** distributed systems pattern

---

## 📁 Project Structure

```
AutoFinance/
├── mcp-servers/
│   ├── risk/                      # Governance
│   │   └── server.py
│   ├── execution/                 # Governance
│   │   └── server.py
│   ├── compliance/                # Governance
│   │   └── server.py
│   ├── market/                    # Trading
│   │   └── server.py
│   ├── technical/                 # Trading
│   │   └── server.py
│   ├── volatility/                # Trading
│   │   └── server.py
│   ├── news/                      # Trading
│   │   └── server.py
│   ├── trader-supervisor/         # Trading
│   │   └── server.py
│   ├── fundamental/               # Investing
│   │   └── server.py
│   ├── macro/                     # Investing
│   │   └── server.py
│   ├── portfolio-analytics/       # Investing
│   │   └── server.py
│   ├── investor-supervisor/       # Investing
│   │   └── server.py
│   └── requirements.txt
├── demo_trading.py                # Trading demo
├── demo_investing.py              # Investing demo
├── demo_complete.py               # Complete demo
├── README.md                      # This file
├── ARCHITECTURE.md                # Detailed architecture
└── DEPLOYMENT.md                  # Deployment guide
```

---

## 🔧 Configuration

### Risk Policy Configuration

Edit `mcp-servers/risk/server.py`:

```python
RISK_POLICY = {
    "max_position_size": 0.15,        # 15% max per position
    "max_volatility": 0.5,            # 50% annualized volatility
    "min_confidence": 0.6,            # 60% minimum confidence
    "max_portfolio_exposure": 0.8,    # 80% max invested
    "max_single_trade_value": 20000,  # $20k per trade
}
```

### Simulation Mode

For deterministic demos:

```python
# Market server
market.set_simulation_mode(
    enabled=True,
    prices={"BTCUSDT": 48000},
    volatility_multiplier=1.5
)

# Technical server
technical.set_simulation_signal(
    symbol="BTCUSDT",
    signal="BUY",
    confidence=0.75
)
```

---

## 📚 Additional Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - Deep dive into architecture
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment guide
- [API_REFERENCE.md](API_REFERENCE.md) - Complete API documentation

---

## 🙋 FAQ

**Q: Is this a real trading bot?**  
A: No. This is an **architecture demonstration**. No real money, no real trading.

**Q: Can I use this for real trading?**  
A: This is a hackathon demo. It would need extensive hardening for production.

**Q: Why so many servers?**  
A: To demonstrate **separation of concerns** and **distributed architecture**. Each server has a single responsibility.

**Q: Does this really work with Archestra?**  
A: Yes! Each server is a proper MCP server that Archestra can register and orchestrate.

---

## 🎓 Learning Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [Archestra GitHub](https://github.com/archestra/archestra)
- [FastMCP](https://github.com/jlowin/fastmcp)

---

## 📝 License

MIT License - Built for WeMakeDevs "2 Fast 2 MCP" Hackathon

---

## 👥 Team

Built by: CryptoSaiyan

Hackathon: WeMakeDevs "2 Fast 2 MCP"

---

**AutoFinance** - Enterprise-grade distributed AI architecture, MCP-native from the ground up.
