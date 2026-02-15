# AutoFinance: Demo Scenarios for Judges

This document contains complete test scenarios to demonstrate AutoFinance capabilities during the hackathon presentation.

---

## 🎬 5-Minute Video Demo Script

### Opening (30 seconds)
"Hi, I'm [name], and this is AutoFinance - a production-ready AI financial control system that showcases the full power of Archestra."

"Most hackathon projects are demos. AutoFinance is different. It's a real system with 13 MCP servers, 12 AI agents in a hierarchical structure, real market data, and multi-channel notifications."

### Live Demo Structure (4 minutes)
1. Scenario 1: Trading Analysis (90 seconds)
2. Scenario 2: Price Alert Setup (60 seconds)
3. Scenario 3: Strategy Simulation (60 seconds)
4. Architecture Showcase (30 seconds)

### Closing (30 seconds)
"AutoFinance demonstrates Archestra's unique capabilities: Agent-to-agent delegation, MCP orchestration, multi-channel triggers, and production-ready architecture. This isn't a prototype - it's a system you could deploy today."

---

## 📋 Scenario 1: Trading Analysis with Agent Delegation

**Goal:** Show hierarchical agent coordination and A2A protocol

**Setup:** Have Archestra web UI open with Portfolio Manager agent chat

**Script:**

```
User: "Should I buy Tesla stock right now? Give me a thorough analysis."

Expected Flow:
1. Portfolio Manager receives request
2. Delegates to Trading Director (A2A call visible in logs)
3. Trading Director invokes 3 specialists:
   - Market Analyzer: Gets current TSLA price, volume, volatility
   - Signal Generator: Provides technical signals (RSI, MACD, trend)
   - Risk Assessor: Checks if trade fits risk policy
4. Trading Director synthesizes results
5. Portfolio Manager presents final recommendation

Sample Response:
"I've consulted my trading team. Here's what we found:

Market Analyzer reports:
- TSLA at $235.67 (-2.3% today)
- Volatility: HIGH (35% implied vol)
- Volume: Above average

Signal Generator shows:
- Signal: HOLD (confidence 65%)
- RSI at 58 (neutral)
- Below 50-day SMA ($242) - bearish
- Recommendation: Wait for break above $242

Risk Assessor notes:
- TSLA would be 8% of portfolio (within 15% limit ✓)
- High volatility requires smaller position
- Current conditions: CAUTION due to market volatility

MY RECOMMENDATION: Wait for clearer technical setup. TSLA is in consolidation phase. If you want exposure, consider a smaller pilot position (5 shares vs 10)."
```

**Why This Impresses Judges:**
- ✅ Agent-to-Agent (A2A) delegation visible
- ✅ Real market data (not simulated)
- ✅ Multiple perspectives synthesized
- ✅ Production-level risk governance
- ✅ Clear decision-making process

**Archestra UI to Show:**
- Chat interface with Portfolio Manager
- Agent delegation logs showing A2A calls
- Individual agent responses in trace view

---

## 📋 Scenario 2: Price Alert with Multi-Channel Notification

**Goal:** Show real-time monitoring and multi-channel notification system

**Setup:** Have Slack workspace open in another window

**Script:**

```
User (in Archestra chat): "Set up an alert: notify me on Slack when Bitcoin goes above $50,000"

Expected Flow:
1. Portfolio Manager receives request
2. Delegates to Operations Director (not a trading operation)
3. Operations Director invokes Alert Manager agent
4. Alert Manager:
   - Validates request format
   - Creates alert via alert-engine MCP server
   - Stores rule: {symbol: BTC-USD, condition: above, threshold: 50000, channel: slack}
   - Confirms alert is active

Sample Response:
"Alert created successfully! ✅

Alert Details:
- Symbol: BTC-USD
- Trigger: Price above $50,000
- Current Price: $45,230
- Notification: Slack (#trading-alerts)
- Status: ACTIVE 🟢

I'm now monitoring Bitcoin price. You'll receive a Slack notification the moment it crosses $50,000."

THEN (for demo, manually trigger or adjust threshold):
User: "Actually, notify me immediately if it's above $45,000 for testing"

Alert Manager updates threshold
Bitcoin price checked → $45,230 > $45,000 → TRIGGER!

Alert Manager invokes Notification Dispatcher agent
Notification sent to Slack
```

**Slack Message Received:**
```
🚨 Price Alert Triggered

Bitcoin (BTC-USD) has crossed your threshold!

Current Price: $45,230.00
Your Threshold: $45,000.00
Change: +0.51% today

Triggered at: 2025-02-13 14:23:45 UTC

View Details | Manage Alerts
```

**Why This Impresses Judges:**
- ✅ Real-time event monitoring
- ✅ Multi-channel notification (Slack shown, WhatsApp/SMS available)
- ✅ Production-ready alert system
- ✅ User-friendly interface
- ✅ Demonstrates "always-on" monitoring capability

**Archestra UI to Show:**
- Chat for alert creation
- Alert Manager agent activity
- Notification Dispatcher logs
- Slack desktop app showing received message

---

## 📋 Scenario 3: Strategy Simulation ("What-If" Analysis)

**Goal:** Show risk-free simulation capabilities

**Setup:** Have Archestra chat open

**Script:**

```
User: "I'm thinking about buying 100 shares of Apple. What would happen in different market scenarios?"

Expected Flow:
1. Portfolio Manager receives request
2. Delegates to Operations Director (this is analysis, not execution)
3. Operations Director invokes Strategy Simulator agent
4. Strategy Simulator:
   - Gets current AAPL price via market server
   - Calculates 3 scenarios (bull/base/bear)
   - Computes risk metrics
   - Shows portfolio impact

Sample Response:
"Let me run a simulation for 100 shares of Apple...

CURRENT MARKET DATA:
- AAPL Price: $185.50
- Total Investment: $18,550
- Your Portfolio Value: $150,000
- Position Size: 12.4% of portfolio ✓

SCENARIO ANALYSIS:

📈 BULL CASE (+15% move to $213.33)
   Probability: 20%
   Profit/Loss: +$2,783
   Portfolio Impact: +1.86%
   
📊 BASE CASE (+5% move to $194.78)
   Probability: 50%
   Profit/Loss: +$928
   Portfolio Impact: +0.62%
   
📉 BEAR CASE (-10% move to $166.95)
   Probability: 30%
   Profit/Loss: -$1,855
   Portfolio Impact: -1.24%

RISK METRICS:
✅ Expected Return: +$722 (+3.9%)
✅ Risk/Reward Ratio: 1:1.5 (acceptable)
⚠️  Max Potential Loss: -$1,855 (1.24% of portfolio)
✅ Position Size: 12.4% (within 15% limit)

RECOMMENDATION:
This is a reasonable position size. Base case is slightly positive. Consider:
- Setting stop loss at $175 (-5.7%) to limit downside
- Your overall tech exposure would be 35% - ensure diversification

Would you like me to:
1. Execute this trade (requires Trading Director approval)
2. Adjust position size
3. Compare to alternative stocks"
```

**Why This Impresses Judges:**
- ✅ Risk-free "what-if" analysis
- ✅ Multiple scenarios with probabilities
- ✅ Clear risk metrics
- ✅ Actionable recommendations
- ✅ No risk of accidental execution
- ✅ Production-level decision support

**Archestra UI to Show:**
- Chat interface with clear scenario table
- Strategy Simulator agent activity logs
- Calculated risk metrics

---

## 📋 Scenario 4: Long-Term Investment Strategy

**Goal:** Show investment (not trading) domain expertise

**Script:**

```
User: "I want to invest for retirement. I have $50,000. Build me a diversified portfolio for 10+ years."

Expected Flow:
1. Portfolio Manager receives request
2. Identifies this as long-term investment (not trading)
3. Delegates to Investment Director (A2A call)
4. Investment Director invokes:
   - Research Analyst: Analyzes multiple quality companies
   - Portfolio Optimizer: Designs allocation strategy
5. Checks macro conditions
6. Proposes balanced portfolio

Sample Response:
"I've consulted my investment team for a long-term retirement portfolio. Here's what we recommend:

INVESTMENT PHILOSOPHY: Quality companies, diversification, long-term focus

PROPOSED ALLOCATION ($50,000):

🏢 U.S. Large Cap Stocks (40% = $20,000)
- Apple (AAPL): $7,500 - Strong moat, consistent growth
- Microsoft (MSFT): $7,500 - Cloud dominance, AI leader
- Berkshire Hathaway (BRK.B): $5,000 - Buffett's quality focus

🌍 International Stocks (20% = $10,000)
- Vanguard FTSE Developed Markets (VEA): $10,000

🏛️ Bonds (25% = $12,500)
- iShares Core U.S. Aggregate Bond (AGG): $12,500

💰 Cash & Alternatives (15% = $7,500)
- High-yield savings / Treasury bills: $7,500

PORTFOLIO CHARACTERISTICS:
✅ Diversification Score: 8.5/10
✅ Expected Annual Return: 7-9%
✅ Risk Level: MODERATE
✅ Tax Efficiency: HIGH (mostly long-term holdings)
✅ Rebalance Frequency: Semi-annually

NEXT STEPS:
1. I can execute these trades immediately (requires approval)
2. Set up automatic rebalancing alerts
3. Schedule quarterly performance reviews

Shall I proceed with execution?"
```

**Why This Impresses Judges:**
- ✅ Demonstrates investment (not just trading) capabilities
- ✅ Long-term thinking
- ✅ Proper diversification
- ✅ Clear allocation strategy
- ✅ Educational for users

---

## 📋 Scenario 5: Risk Governance in Action

**Goal:** Show production-level risk controls

**Script:**

```
User: "I want to buy 2000 shares of this penny stock I heard about: RISKY"

Expected Flow:
1. Portfolio Manager delegates to Trading Director
2. Trading Director invokes Risk Assessor first
3. Risk Assessor flags VIOLATIONS:
   - Position would be 25% of portfolio (exceeds 15% limit)
   - Penny stock = high volatility
   - No fundamental support
4. Trading Director escalates to Risk server validation
5. Risk server DENIES trade

Sample Response:
"I've analyzed this request with my trading team, and I must decline this trade. Here's why:

RISK ASSESSMENT:
❌ Position Size: 25% of portfolio (EXCEEDS 15% limit)
❌ Volatility: EXTREME (80% implied vol)
❌ Liquidity: LOW (high slippage risk)
❌ Fundamental Score: 2/10

GOVERNANCE POLICY VIOLATIONS:
1. Max position size: 15% (yours: 25%)
2. Max volatility: 50% (this: 80%)
3. Min liquidity: $1M daily volume (this: $200K)

RISK SERVER DECISION: ❌ TRADE DENIED

ALTERNATIVE RECOMMENDATION:
If you want speculative exposure:
- Limit position to 5% of portfolio (300 shares max)
- Use trailing stop loss at 15%
- Diversify across 3 speculative plays instead of 1

My job is to protect your capital. This trade has asymmetric risk that violates our governance. I cannot approve it.

Would you like to:
1. Adjust to a smaller position size
2. Explore safer growth opportunities
3. Review our risk policy"
```

**Why This Impresses Judges:**
- ✅ Production-level governance
- ✅ AI that says "NO" when needed
- ✅ Clear policy enforcement
- ✅ Educational explanations
- ✅ Alternative suggestions
- ✅ Risk consciousness

---

## 🎨 Architecture Showcase (30 seconds in video)

**Visual to Show:** ARCHITECTURE_WINNING.md diagram

**Narration:**
"Let me show you how this works under the hood. AutoFinance has 13 MCP servers providing specialized capabilities - market data, risk management, execution, alerts, notifications."

"On top of that, we have 12 AI agents arranged in a 3-level hierarchy:
- Level 1: Portfolio Manager - the CEO
- Level 2: Three directors - Trading, Investment, Operations  
- Level 3: Seven specialists - each with deep expertise

"When you ask a question, agents delegate to each other using Archestra's A2A protocol. This creates a real chain of command, just like a professional trading firm."

---

## 🏆 Judging Criteria Alignment

### 1. Best Use of Archestra (30%)
✅ **Agent-to-Agent (A2A) Protocol**
   - 12 agents delegating via JSON-RPC 2.0
   - Clear hierarchical structure
   - Visible in demo scenarios

✅ **MCP Gateway & Orchestration**
   - 13 MCP servers coordinated by Archestra
   - Kubernetes embedded orchestration
   - Production-ready deployment

✅ **Multi-Channel Triggers**
   - Slack bot integration
   - WhatsApp notification system
   - SMS alerts via Twilio
   - Real-time price monitoring

### 2. Creativity & Originality (25%)
✅ **Hierarchical Agent Architecture**
   - Not flat agents - real organizational structure
   - CEO → Directors → Specialists pattern
   - Novel approach to AI coordination

✅ **Advanced Features**
   - Alert monitoring system
   - What-if simulation engine
   - Multi-scenario analysis
   - Risk governance enforcement

### 3. Technical Implementation (25%)
✅ **Production-Ready Code**
   - Real market data (no simulations)
   - Proper error handling
   - Logging and compliance
   - Database-backed state

✅ **Clean Architecture**
   - Separation of concerns
   - Zero-trust between MCP servers
   - MCP protocol compliance
   - Scalable design

### 4. User Experience (20%)
✅ **Conversational Interface**
   - Natural language queries
   - Clear explanations
   - Multi-step workflows
   - Proactive suggestions

✅ **Multi-Channel Notifications**
   - Slack for detailed alerts
   - SMS for urgent notifications
   - WhatsApp for mobile-first users

---

## 🎯 Competition Differentiators

**What makes AutoFinance stand out:**

1. **12 Agents vs 3** - Most teams will build basic systems. We built an organization.

2. **Real Data** - While others simulate, we connect to Yahoo Finance, NewsAPI, real markets.

3. **Production-Ready** - Not a demo. This has risk governance, compliance logging, audit trails.

4. **Multi-Channel** - Slack, WhatsApp, SMS, Email. Others will have basic chat.

5. **Advanced Features** - Alert monitoring and strategy simulation show depth.

6. **Clear Architecture** - ARCHITECTURE_WINNING.md shows we understand system design.

7. **Complete Documentation** - README, deployment guides, demo scripts show professionalism.

---

## 📱 Quick Demo Checklist

Before your presentation, ensure:

- [ ] Archestra running at localhost:3000
- [ ] All 13 MCP servers in registry
- [ ] All 12 agents configured with system prompts
- [ ] Slack bot configured with valid token
- [ ] Test alert triggers and receives Slack notification
- [ ] Portfolio Manager chat responds to queries
- [ ] Agent delegation visible in logs/trace view
- [ ] Have backup slides if live demo fails
- [ ] Practice 5-minute script timing
- [ ] Test internet connection for real market data

---

## 🚀 Demo Tips

1. **Start with the "wow" moment:** Show live Slack notification first

2. **Show agent delegation:** Pull up Archestra's trace view to show A2A calls

3. **Be confident:** You built a production system, not a toy

4. **Have backup:** Screenshots/video if live demo fails

5. **Tell the story:** "This is how a real trading firm operates - with hierarchy and governance"

6. **Emphasize real data:** "This is live market data from Yahoo Finance, not simulated"

7. **Show the code:** Judges love seeing actual implementation

8. **End strong:** "AutoFinance showcases everything Archestra can do - and it's ready to deploy today"

---

## 🎬 Post-Demo Q&A Prep

**Expected Questions:**

**Q: "How does this compare to existing trading platforms?"**
A: "Traditional platforms are single-agent or rules-based. AutoFinance is a multi-agent coordination system with real AI decision-making at every level. It's closer to how a real hedge fund operates - with specialists, directors, and a portfolio manager coordinating."

**Q: "Could this handle real money?"**
A: "Yes. It has production-level risk governance, compliance logging, and audit trails. We'd need to add broker integration (Alpaca API, Interactive Brokers) for real execution, but the decision-making and governance are production-ready."

**Q: "Why 12 agents instead of fewer?"**
A: "Separation of concerns. Each agent has one job. This makes the system more maintainable, testable, and scalable. You can swap out individual agents without affecting others."

**Q: "How do you prevent agents from making bad decisions?"**
A: "Multi-layer validation. Risk Assessor does preliminary checks. Risk server is the final authority. Compliance server logs everything. Portfolio Manager synthesizes multiple perspectives. No single agent can execute a trade alone."

**Q: "What about latency with so many agents?"**
A: "A2A calls are fast JSON-RPC. The hierarchical structure actually reduces latency because agents delegate intelligently instead of everyone querying everything. In practice, response time is 2-4 seconds for complex analyses."

---

## 📧 Video Script Template

```
[0:00-0:30] OPENING
Hi, I'm [name], and this is AutoFinance - a production-ready AI financial control system built for Archestra.

[SHOW: Archestra UI dashboard]

Most hackathon projects are demos. AutoFinance is different.

[0:30-1:00] ARCHITECTURE
[SHOW: ARCHITECTURE_WINNING.md diagram]

AutoFinance has 13 MCP servers and 12 AI agents arranged in a corporate hierarchy - like a real trading firm.

At the top: Portfolio Manager - the CEO who coordinates everything.
Middle layer: Three directors - Trading, Investment, Operations.
Bottom layer: Seven specialists - each an expert in their domain.

[1:00-2:30] DEMO 1 - Trading Analysis
[SHOW: Live Archestra chat]

Let me show you how it works. I'll ask the Portfolio Manager about buying Tesla stock.

[TYPE IN CHAT: "Should I buy Tesla?"]

Watch what happens... Portfolio Manager delegates to Trading Director.
[SHOW: A2A call logs]

Trading Director invokes three specialists:
- Market Analyzer gets live data from Yahoo Finance
- Signal Generator provides technical signals
- Risk Assessor checks compliance

[SHOW: Responses flowing back up]

All of this happens automatically using Archestra's agent-to-agent protocol.

[2:30-3:30] DEMO 2 - Price Alerts
[SHOW: Archestra chat + Slack]

Now watch this - I'll set a price alert.

[TYPE: "Notify me on Slack when Bitcoin crosses $50,000"]

Alert Manager agent creates the rule... stores it in our alert engine... and now it's monitoring 24/7.

[SHOW: Alert trigger, switch to Slack]

There's the notification in Slack! This works for Slack, WhatsApp, SMS, and email.

This is what makes AutoFinance production-ready - real-time monitoring with multi-channel notifications.

[3:30-4:15] DEMO 3 - What-If Analysis
[SHOW: Simulation request]

Before you trade, you should simulate. Watch this:

[TYPE: "What if I buy 100 Apple shares?"]

Strategy Simulator shows three scenarios - bull, base, and bear - with probabilities and risk metrics.

This is risk-free analysis. No real trades until you approve.

[4:15-4:45] WHY IT WINS

AutoFinance demonstrates everything Archestra can do:
✅ Agent-to-agent delegation with 12 coordinated agents
✅ MCP orchestration with 13 specialized servers
✅ Multi-channel triggers with real-time alerts
✅ Production-ready architecture with governance and compliance

This isn't a prototype. This is a system you could deploy today.

[4:45-5:00] CLOSING

AutoFinance shows the future of AI financial systems - not single agents, but coordinated teams working together, just like humans do.

Thank you.

[END]
```

---

## ✅ Final Checklist

Before submitting:
- [ ] All 13 MCP servers tested and working
- [ ] All 12 agents configured in Archestra
- [ ] Slack integration tested with real notifications
- [ ] Live demo rehearsed (5 minutes)
- [ ] Video recorded and uploaded
- [ ] README polished for judges
- [ ] GitHub repo public and accessible
- [ ] All documentation complete
- [ ] Submission form filled out

**You've got this. Go win that $10,000!** 🚀
