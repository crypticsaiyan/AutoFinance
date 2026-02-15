# Archestra MCP Server Configuration Guide

**Quick reference for adding all 13 AutoFinance MCP servers to Archestra**

---

## 🚀 Quick Start: Minimum Viable Configuration

**For a working demo, start with these 5 essential servers:**

1. ✅ market (live data)
2. ✅ risk (validation)
3. ✅ execution (state)
4. ✅ compliance (logging)
5. ✅ technical (signals)

This gives you enough for "Should I buy Apple?" style queries.

---

## 📋 All 13 Server Configurations

Copy-paste these into Archestra's MCP Registry:

### 1. Market Server (CRITICAL - Use Real Data Version)

```
Name: autofinance-market
Connection Type: stdio
Command: python
Args: ["server_real.py"]
Working Directory: /home/cryptosaiyan/Documents/AutoFinance/mcp-servers/market
Environment Variables:
  (none needed - Yahoo Finance is free)
```

**Tools Provided:**
- `get_live_price` - Current stock/crypto prices
- `get_candles` - OHLCV historical data
- `calculate_volatility` - Price volatility
- `get_market_overview` - Multi-symbol snapshot

---

### 2. Risk Server (CRITICAL)

```
Name: autofinance-risk
Connection Type: stdio
Command: python
Args: ["server.py"]
Working Directory: /home/cryptosaiyan/Documents/AutoFinance/mcp-servers/risk
```

**Tools Provided:**
- `validate_trade` - Check trade against policy
- `validate_rebalance` - Check rebalance against policy
- `get_risk_policy` - Read current risk limits

---

### 3. Execution Server (CRITICAL)

```
Name: autofinance-execution
Connection Type: stdio
Command: python
Args: ["server.py"]
Working Directory: /home/cryptosaiyan/Documents/AutoFinance/mcp-servers/execution
```

**Tools Provided:**
- `execute_trade` - Execute approved trade
- `apply_rebalance` - Apply portfolio changes
- `get_portfolio_state` - Read current holdings
- `update_position_prices` - Mark-to-market
- `reset_portfolio` - Reset for testing

---

### 4. Compliance Server (CRITICAL)

```
Name: autofinance-compliance
Connection Type: stdio
Command: python
Args: ["server.py"]
Working Directory: /home/cryptosaiyan/Documents/AutoFinance/mcp-servers/compliance
```

**Tools Provided:**
- `log_event` - Log compliance event
- `generate_audit_report` - Create audit report
- `get_recent_events` - Get recent logs
- `get_compliance_metrics` - Get KPIs

---

### 5. Technical Server

```
Name: autofinance-technical
Connection Type: stdio
Command: python
Args: ["server.py"]
Working Directory: /home/cryptosaiyan/Documents/AutoFinance/mcp-servers/technical
```

**Tools Provided:**
- `generate_signal` - Generate trading signal
- `analyze_trend` - Analyze price trend
- `get_support_resistance` - Get key levels

---

### 6. Volatility Server

```
Name: autofinance-volatility
Connection Type: stdio
Command: python
Args: ["server.py"]
Working Directory: /home/cryptosaiyan/Documents/AutoFinance/mcp-servers/volatility
```

**Tools Provided:**
- `get_volatility_score` - Get volatility assessment
- `compare_volatility` - Compare multiple symbols
- `get_volatility_forecast` - Forecast future volatility

---

### 7. News Server

```
Name: autofinance-news
Connection Type: stdio
Command: python
Args: ["server.py"]
Working Directory: /home/cryptosaiyan/Documents/AutoFinance/mcp-servers/news
Environment Variables:
  NEWS_API_KEY: your_newsapi_key (optional - has simulation mode)
```

**Tools Provided:**
- `analyze_sentiment` - Analyze news sentiment
- `get_market_sentiment` - Aggregate market sentiment
- `analyze_custom_headline` - Test custom headline

---

### 8. Fundamental Server

```
Name: autofinance-fundamental
Connection Type: stdio
Command: python
Args: ["server.py"]
Working Directory: /home/cryptosaiyan/Documents/AutoFinance/mcp-servers/fundamental
```

**Tools Provided:**
- `analyze_fundamentals` - Company fundamental analysis
- `compare_fundamentals` - Compare multiple companies
- `get_investment_thesis` - Generate investment thesis

---

### 9. Macro Server

```
Name: autofinance-macro
Connection Type: stdio
Command: python
Args: ["server.py"]
Working Directory: /home/cryptosaiyan/Documents/AutoFinance/mcp-servers/macro
```

**Tools Provided:**
- `analyze_macro` - Analyze macro environment
- `get_sector_outlook` - Get sector outlook
- `assess_portfolio_timing` - Assess timing
- `get_correlation_analysis` - Analyze correlations

---

### 10. Portfolio Analytics Server

```
Name: autofinance-portfolio-analytics
Connection Type: stdio
Command: python
Args: ["server.py"]
Working Directory: /home/cryptosaiyan/Documents/AutoFinance/mcp-servers/portfolio-analytics
```

**Tools Provided:**
- `evaluate_portfolio` - Comprehensive evaluation
- `calculate_rebalance_proposal` - Build rebalance plan
- `get_allocation_summary` - Get allocation breakdown

---

### 11. Alert Engine Server (NEW - Advanced Feature)

```
Name: autofinance-alert-engine
Connection Type: stdio
Command: python
Args: ["server.py"]
Working Directory: /home/cryptosaiyan/Documents/AutoFinance/mcp-servers/alert-engine
```

**Tools Provided:**
- `create_alert` - Create price alert
- `check_alert_condition` - Check if alert triggered
- `list_user_alerts` - List user's alerts
- `delete_alert` - Remove alert
- `get_all_active_alerts` - Get all active alerts
- `reset_alert` - Reset triggered alert

---

### 12. Simulation Engine Server (NEW - Advanced Feature)

```
Name: autofinance-simulation-engine
Connection Type: stdio
Command: python
Args: ["server.py"]
Working Directory: /home/cryptosaiyan/Documents/AutoFinance/mcp-servers/simulation-engine
```

**Tools Provided:**
- `simulate_trade` - Simulate trade outcome
- `simulate_portfolio_rebalance` - Simulate rebalance
- `simulate_strategy` - Backtest strategy
- `calculate_position_size` - Calculate position size

---

### 13. Notification Gateway Server (NEW - Advanced Feature)

```
Name: autofinance-notification-gateway
Connection Type: stdio
Command: python
Args: ["server.py"]
Working Directory: /home/cryptosaiyan/Documents/AutoFinance/mcp-servers/notification-gateway
Environment Variables:
  SLACK_BOT_TOKEN: xoxb-your-token (optional)
  SLACK_DEFAULT_CHANNEL: #trading-alerts (optional)
  TWILIO_ACCOUNT_SID: your_sid (optional)
  TWILIO_AUTH_TOKEN: your_token (optional)
  TWILIO_WHATSAPP_FROM: whatsapp:+14155238886 (optional)
  TWILIO_PHONE_FROM: +15551234567 (optional)
```

**Tools Provided:**
- `send_slack_message` - Send Slack message
- `send_slack_alert` - Send formatted Slack alert
- `send_whatsapp_message` - Send WhatsApp message
- `send_sms` - Send SMS
- `send_email` - Send email
- `send_multi_channel_notification` - Send to multiple channels
- `get_notification_status` - Check channel status

**Note:** Gracefully degrades to simulation mode if credentials not provided.

---

## 🔧 Testing Your Configuration

### Step 1: Test Individual Server

```bash
cd ~/Documents/AutoFinance/mcp-servers/market
python server_real.py

# Should see: MCP server started successfully
# Press Ctrl+C to stop
```

### Step 2: Test in Archestra

1. Add server to MCP Registry
2. Create a simple agent
3. Enable just one tool (e.g., `get_live_price`)
4. Test query: "What's the price of Apple?"

### Step 3: Verify Tools Are Available

In Archestra agent configuration, you should see all tools from each server listed.

---

## 🎯 Recommended Configuration Order

**Day 1 (Core Trading):**
1. market ← Start here
2. risk
3. execution
4. compliance
5. technical

**Test:** "Should I buy 10 shares of Apple?"

**Day 2 (Full System):**
6. volatility
7. news
8. fundamental
9. macro
10. portfolio-analytics

**Test:** "Give me a complete analysis of Tesla"

**Day 3 (Advanced Features):**
11. alert-engine
12. simulation-engine
13. notification-gateway

**Test:** "Notify me on Slack when BTC > $50k"

---

## 🐛 Troubleshooting

### Problem: "Server not responding"

**Solution:**
```bash
# Check if server starts manually
cd mcp-servers/market
python server_real.py

# Look for errors in output
```

### Problem: "Tool not found"

**Solution:**
- Verify server is added to MCP Registry
- Check tools are enabled in agent configuration
- Restart Archestra after adding servers

### Problem: "Import errors"

**Solution:**
```bash
# Install dependencies
cd ~/Documents/AutoFinance/mcp-servers
pip install -r requirements.txt

# Verify installation
python -c "import mcp, fastmcp, yfinance"
```

### Problem: "Environment variables not loaded"

**Solution:**
```bash
# Create .env file
cd ~/Documents/AutoFinance/mcp-servers
cp .env.example .env
nano .env

# Add your tokens, then restart servers
```

---

## 📊 Server Dependencies

**Market Server needs:**
- yfinance
- pandas
- numpy

**Notification Gateway needs:**
- slack-sdk (for Slack)
- twilio (for WhatsApp/SMS)
- SMTP credentials (for Email)

**All others:**
- Just mcp and fastmcp

**Install all:**
```bash
cd mcp-servers
pip install -r requirements.txt
```

---

## 🚀 Quick Copy-Paste Commands

### Start All Servers (in separate terminals)

```bash
# Terminal 1
cd ~/Documents/AutoFinance/mcp-servers/market && python server_real.py

# Terminal 2
cd ~/Documents/AutoFinance/mcp-servers/risk && python server.py

# Terminal 3
cd ~/Documents/AutoFinance/mcp-servers/execution && python server.py

# Terminal 4
cd ~/Documents/AutoFinance/mcp-servers/compliance && python server.py

# Terminal 5
cd ~/Documents/AutoFinance/mcp-servers/technical && python server.py

# ... continue for all 13
```

### Or use tmux/screen to manage multiple terminals:

```bash
# Create tmux session
tmux new -s autofinance

# Split into panes (Ctrl+B then %)
# In each pane, start a different server

# Detach: Ctrl+B then D
# Reattach: tmux attach -t autofinance
```

---

## 🎯 Minimal Demo Configuration

**If you only have 1 hour, configure these 3:**

1. **market** - "What's the price of Apple?"
2. **technical** - "Should I buy Apple based on technical analysis?"
3. **risk** - "Is this trade within risk limits?"

**Agent Setup:**
- Create Portfolio Manager agent
- Enable these 3 MCP servers
- Test basic queries

**This is enough to demonstrate:**
- Real data integration
- Agent tool usage
- Basic decision-making

---

## 🏆 Full Production Configuration

**All 13 servers + environment variables:**

```bash
# Create comprehensive .env
cd ~/Documents/AutoFinance/mcp-servers
cat > .env << EOF
# Slack (optional - for notifications)
SLACK_BOT_TOKEN=xoxb-your-token-here
SLACK_DEFAULT_CHANNEL=#trading-alerts

# Twilio (optional - for WhatsApp/SMS)
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
TWILIO_PHONE_FROM=+15551234567

# NewsAPI (optional - has simulation mode)
NEWS_API_KEY=your_newsapi_key

# Other optional services
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_FROM=your.email@gmail.com
EMAIL_PASSWORD=your_app_password
EOF

# Start all servers
./start_all_servers.sh  # (create this script to start all in background)
```

---

## ✅ Configuration Checklist

**Before recording video:**
- [ ] All 13 servers added to Archestra MCP Registry
- [ ] At least 3 agents configured (Portfolio Manager + 2 others)
- [ ] Market server using `server_real.py` (not `server.py`)
- [ ] Test query works: "What's the price of Apple?"
- [ ] Slack integration working (optional but impressive)
- [ ] Alert system tested (optional)

**Minimum for submission:**
- [ ] 5 core servers configured (market, risk, execution, compliance, technical)
- [ ] Portfolio Manager agent working
- [ ] Basic query demo works
- [ ] Video shows agent using MCP server tools

---

## 📞 Quick Reference

**MCP Server Location:**
```
/home/cryptosaiyan/Documents/AutoFinance/mcp-servers/
```

**Critical Files:**
- `requirements.txt` - Install dependencies
- `.env.example` - Environment variable template
- `.env` - Your actual credentials (DON'T COMMIT!)

**Test Command:**
```bash
cd mcp-servers/market && python server_real.py
# Should see: "MCP server started successfully"
```

**Archestra Registry Path:**
Usually: Settings → MCP Registry → Add Server

---

**Need more help?** See [DEPLOYMENT.md](DEPLOYMENT.md) for full Archestra setup.

**Ready to configure agents?** See [AGENT_DEFINITIONS.md](AGENT_DEFINITIONS.md) for system prompts.
