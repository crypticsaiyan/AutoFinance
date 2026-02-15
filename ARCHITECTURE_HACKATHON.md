# AutoFinance Architecture

## 🎯 Core Principles

### 1. Separation of Concerns

**Every server has exactly ONE responsibility:**

| Server | Responsibility | Can Do | Cannot Do |
|--------|---------------|--------|----------|
| Risk | Validate policies | Return approval/rejection | Execute trades, access data |
| Execution | Mutate state | Execute approved actions | Validate risk, make decisions |
| Compliance | Log events | Store audit trail | Validate, execute, decide |
| Analytical | Produce intelligence | Analyze data | Validate, execute |
| Supervisors | Orchestrate | Aggregate, coordinate | Execute directly, bypass risk |

### 2. Zero-Trust Architecture

**No server trusts another server:**

- Execution server MUST verify `approved=True` flag
- Risk server CANNOT call execution
- Supervisors CANNOT bypass risk validation
- All decisions logged to compliance

### 3. MCP-Native Communication

**No imports, only MCP tool calls:**

```python
# ❌ WRONG - Direct import
from execution_server import execute_trade

# ✅ CORRECT - MCP tool call
result = await mcp_client.call_tool(
    "execution",
    "execute_trade",
    {"trade_id": "...", "approved": True}
)
```

---

## 🏛 Three-Layer Architecture

### Layer 1: Intelligence (Analytical Agents)

**Purpose**: Produce insights, no authority

**Trading Domain:**
- `market` - Price data, volatility
- `technical` - Signals, indicators
- `volatility` - Risk scoring
- `news` - Sentiment analysis

**Investing Domain:**
- `fundamental` - Long-term analysis
- `macro` - Market regime
- `portfolio-analytics` - Portfolio metrics

**Characteristics:**
- Stateless (mostly)
- Read-only data access
- No validation authority
- No execution authority
- Pure functions

### Layer 2: Orchestration (Supervisors)

**Purpose**: Aggregate intelligence, build proposals

**Servers:**
- `trading-supervisor` - Orchestrates trading flow
- `investing-supervisor` - Orchestrates investment flow

**Flow Pattern:**
```
1. Receive request
2. Call analytical agents (parallel where possible)
3. Aggregate results
4. Build structured proposal
5. Submit to governance layer
6. Coordinate execution if approved
7. Log everything
```

**Characteristics:**
- Stateless
- No direct execution authority
- Must go through risk validation
- Aggregation logic only

### Layer 3: Governance (Authority & Control)

**Purpose**: Enforce policies, execute actions, audit

**Servers:**
- `risk` - Policy enforcement
- `execution` - State mutation
- `compliance` - Audit trail

**Authority Model:**

```
┌─────────────────────────────────────────────────┐
│            GOVERNANCE LAYER                      │
├─────────────┬──────────────┬────────────────────┤
│    RISK     │  EXECUTION   │   COMPLIANCE       │
│             │              │                    │
│  Validates  │  Executes    │   Logs            │
│  ✓/✗        │  Portfolio   │   Everything      │
│             │  Changes     │                    │
└─────────────┴──────────────┴────────────────────┘
      ↑              ↑               ↑
      │              │               │
      └──────────────┴───────────────┘
              Must go through
            governance for ANY
           portfolio mutation
```

---

## 🔄 Data Flow

### Trading Flow

```
User Request: "Process trade for BTCUSDT"
     ↓
┌────────────────────────────────────────┐
│   Trading Supervisor                    │
│   ┌─────────────────────────────────┐  │
│   │ 1. Gather Intelligence          │  │
│   │    ├─→ Market Server             │  │
│   │    ├─→ Technical Server          │  │
│   │    ├─→ Volatility Server         │  │
│   │    └─→ News Server               │  │
│   │                                  │  │
│   │ 2. Aggregate Signals             │  │
│   │    Calculate confidence          │  │
│   │                                  │  │
│   │ 3. Build Trade Proposal          │  │
│   │    {symbol, action, qty, ...}    │  │
│   └─────────────────────────────────┘  │
└────────────────────────────────────────┘
     ↓
     ├─→ Compliance: log proposal
     ↓
┌────────────────────────────────────────┐
│   Risk Server                           │
│   Validate against policy               │
│   → approved: true/false                │
└────────────────────────────────────────┘
     ↓
     ├─→ Compliance: log risk decision
     ↓
     If approved=true:
     ↓
┌────────────────────────────────────────┐
│   Execution Server                      │
│   1. Verify approved flag               │
│   2. Execute trade                      │
│   3. Update portfolio state             │
│   → execution result                    │
└────────────────────────────────────────┘
     ↓
     ├─→ Compliance: log execution
     ↓
    Done
```

### Investing Flow

```
Periodic Review Trigger
     ↓
┌────────────────────────────────────────┐
│   Investing Supervisor                  │
│   ┌─────────────────────────────────┐  │
│   │ 1. Assess Current State         │  │
│   │    ├─→ Execution: get_portfolio  │  │
│   │    └─→ Portfolio Analytics       │  │
│   │                                  │  │
│   │ 2. Analyze Environment           │  │
│   │    ├─→ Macro Server              │  │
│   │    └─→ Fundamental Server (each) │  │
│   │                                  │  │
│   │ 3. Determine Target Allocation   │  │
│   │                                  │  │
│   │ 4. Build Rebalance Proposal      │  │
│   │    {changes: [...]}              │  │
│   └─────────────────────────────────┘  │
└────────────────────────────────────────┘
     ↓
     ├─→ Compliance: log proposal
     ↓
┌────────────────────────────────────────┐
│   Risk Server                           │
│   Validate rebalance                    │
│   Check turnover limits                 │
│   → approved: true/false                │
└────────────────────────────────────────┘
     ↓
     ├─→ Compliance: log risk decision
     ↓
     If approved=true:
     ↓
┌────────────────────────────────────────┐
│   Execution Server                      │
│   Apply rebalance                       │
│   Execute each trade in changes list    │
│   → rebalance result                    │
└────────────────────────────────────────┘
     ↓
     ├─→ Compliance: log execution
     ↓
    Done
```

---

## 🔒 Security Model

### Authority Boundaries

**Risk Server:**
- ✅ Can validate proposals
- ✅ Can read policy configuration
- ❌ CANNOT execute trades
- ❌ CANNOT access portfolio directly
- ❌ CANNOT bypass its own rules

**Execution Server:**
- ✅ Can execute approved actions
- ✅ Can read/write portfolio state
- ❌ CANNOT validate risk
- ❌ CANNOT make trading decisions
- ✅ MUST verify `approved=True` flag

**Supervisors:**
- ✅ Can aggregate intelligence
- ✅ Can build proposals
- ❌ CANNOT execute directly
- ❌ CANNOT bypass risk
- ✅ MUST go through governance

**Analytical Agents:**
- ✅ Can analyze data
- ✅ Can return insights
- ❌ CANNOT execute anything
- ❌ CANNOT validate anything
- ❌ CANNOT access portfolio

### Verification Chain

```
Every portfolio mutation requires:

1. Analytical Intelligence
   └─→ Build understanding

2. Supervisor Aggregation
   └─→ Build proposal

3. Risk Validation
   └─→ Approve/reject

4. Execution Verification
   └─→ Check approved flag
   └─→ Execute ONLY if approved

5. Compliance Logging
   └─→ Audit trail
```

---

## 📊 State Management

### Centralized State

**Only ONE place stores portfolio state:**

```python
# In execution server ONLY
PORTFOLIO_STATE = {
    "cash": 100000.0,
    "positions": {
        "BTCUSDT": {
            "quantity": 1.0,
            "avg_price": 45000,
            "current_price": 48000,
            "current_value": 48000
        }
    },
    "transaction_history": [],
    "last_updated": "2026-02-15T..."
}
```

### Read vs Write Access

| Server | Read Access | Write Access |
|--------|-------------|--------------|
| Execution | ✅ Internal | ✅ Internal |
| Portfolio Analytics | ✅ Via `get_portfolio_state` | ❌ |
| Risk | ❌ No direct access | ❌ |
| Supervisors | ✅ Via `get_portfolio_state` | ❌ |
| Analytical | ❌ No access | ❌ |
| Compliance | ❌ No access | ❌ |

---

## 🎭 Design Patterns

### 1. Observer Pattern (Compliance)

Compliance server observes all important events but never interferes:

```python
# Every significant action logs to compliance
await compliance.log_event(
    event_type="risk_decision",
    agent_name="risk-server",
    action="validate_trade",
    details=result
)
```

### 2. Strategy Pattern (Risk Policies)

Risk policies are configurable strategies:

```python
RISK_POLICY = {
    "max_position_size": 0.15,
    "max_volatility": 0.5,
    "min_confidence": 0.6,
}
```

### 3. Facade Pattern (Supervisors)

Supervisors provide simplified interface to complex swarms:

```python
# Instead of calling 5 servers manually
result = await trading_supervisor.process_trade_request(
    symbol="BTCUSDT",
    quantity=0.5
)
# Supervisor handles all coordination
```

### 4. Mediator Pattern (MCP Protocol)

MCP acts as mediator between all servers:

```
Server A ←→ MCP ←→ Server B
                ↕
              Server C
```

No direct connections, all through MCP.

---

## 🔧 Scalability

### Horizontal Scaling

**Stateless servers can scale horizontally:**
- Market server → 10 instances
- Technical server → 5 instances
- Volatility server → 5 instances
- Risk server → 3 instances (policy is read-only)

**Stateful server (Execution) options:**
1. Single instance (simple)
2. Multiple instances with shared state (Redis/DB)
3. Sharded by asset (BTCUSDT on instance 1, ETHUSDT on instance 2)

### Load Distribution

```
            ┌─────────────┐
            │  Archestra  │
            │  Load Bal   │
            └─────────────┘
                   ↓
      ┌────────────┼────────────┐
      ↓            ↓            ↓
┌──────────┐ ┌──────────┐ ┌──────────┐
│ Market-1 │ │ Market-2 │ │ Market-3 │
└──────────┘ └──────────┘ └──────────┘
```

---

## 📈 Performance Considerations

### Parallel Intelligence Gathering

Supervisors call analytical agents in parallel:

```python
# ✅ GOOD - Parallel
results = await asyncio.gather(
    market.get_price(symbol),
    technical.generate_signal(symbol),
    volatility.get_score(symbol),
    news.analyze_sentiment(symbol)
)

# ❌ BAD - Sequential
market_data = await market.get_price(symbol)
technical_data = await technical.generate_signal(symbol)
volatility_data = await volatility.get_score(symbol)
news_data = await news.analyze_sentiment(symbol)
```

### Caching Strategies

- **Market data**: Cache 1-5 seconds
- **Technical signals**: Cache 1 minute
- **Fundamental data**: Cache 1 hour
- **Macro analysis**: Cache 4 hours
- **Risk policy**: Cache indefinitely (until config change)

---

## 🧪 Testing Strategy

### Unit Tests (Per Server)

Each server has isolated unit tests:
- Risk server: Policy validation logic
- Execution server: State mutation logic
- Supervisors: Aggregation logic

### Integration Tests (MCP Flows)

Test complete flows:
- Approved trade end-to-end
- Rejected trade end-to-end
- Approved rebalance end-to-end
- Error handling

### Simulation Mode

Deterministic testing:
```python
# Set fixed signals for testing
technical.set_simulation_signal(
    symbol="BTCUSDT",
    signal="BUY",
    confidence=0.75
)

# Test produces identical results every time
```

---

## 🛡 Error Handling

### Failure Modes

1. **Analytical agent fails**
   - Supervisor catches exception
   - Uses fallback/default data
   - Logs error to compliance
   - Continues with reduced confidence

2. **Risk validation fails**
   - Return rejection
   - Log to compliance
   - Do NOT execute

3. **Execution fails**
   - Log failure to compliance
   - Return error to supervisor
   - State remains unchanged
   - Retry NOT automatic (requires manual review)

### Circuit Breaker Pattern

```python
if consecutive_failures > 3:
    # Stop calling failing service
    # Use cached data or fallback
    # Alert monitoring
```

---

## 📝 Audit Trail

### Event Types

- `proposal` - Trade/rebalance proposals
- `risk_decision` - Approval/rejection
- `execution` - Execution results
- `error` - Errors encountered
- `system` - System events

### Compliance Queries

```python
# Get all rejections
report = compliance.generate_audit_report(
    event_type="risk_decision"
)

# Filter by time
report = compliance.generate_audit_report(
    start_time="2026-02-01T00:00:00Z",
    end_time="2026-02-15T23:59:59Z"
)

# Get metrics
metrics = compliance.get_compliance_metrics()
# → approval_rate, success_rate, etc.
```

---

## 🚀 Deployment Architecture

### Archestra Orchestration

```yaml
mcp_servers:
  - name: auto-finance-risk
    command: python mcp-servers/risk/server.py
    
  - name: auto-finance-execution
    command: python mcp-servers/execution/server.py
    
  - name: auto-finance-compliance
    command: python mcp-servers/compliance/server.py
    
  # ... all other servers
```

### Docker Deployment

```dockerfile
# Each server gets its own container
FROM python:3.11-slim
COPY mcp-servers/risk/ /app/
RUN pip install -r requirements.txt
CMD ["python", "server.py"]
```

---

## 📖 Extension Points

### Adding New Analytical Agent

1. Create new MCP server
2. Implement tool(s)
3. Register with Archestra
4. Update supervisor to call new agent
5. Update aggregation logic

### Adding New Risk Rule

1. Edit `mcp-servers/risk/server.py`
2. Update `RISK_POLICY` dict
3. Add validation logic
4. No changes to other servers needed

### Adding New Asset Class

1. Update market server (data source)
2. Update technical server (apply indicators)
3. No changes to governance layer needed

---

**AutoFinance Architecture** - Enterprise-grade separation of concerns for distributed AI systems.
