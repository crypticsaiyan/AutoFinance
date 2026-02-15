# AutoFinance CLI Interface

A beautiful, intuitive terminal-based interface for the AutoFinance trading system.

## Features

### 🎨 Landing Page
- Animated ASCII art logo with smooth transitions
- Menu system with keyboard navigation
- Professional terminal aesthetics

### 📊 Live Dashboard
- **Multiple Live Charts**: Display up to 6 stock/crypto charts simultaneously in a grid layout
- **Braille Dot Graphics**: Beautiful charts using Unicode braille characters (via plotille)
- **Real-time Data**: Live price updates from Binance (crypto) and Yahoo Finance (stocks)
- **Technical Indicators**: SMA (Simple Moving Average) with bullish/bearish signals
- **Portfolio Tracker**: Real-time portfolio value with P&L display
- **Favorites Management**: Save and track your favorite symbols

### 💬 Copilot Chat
- **Interactive AI Chat**: Integrated chatbox for natural language queries
- **MCP Tool Access**: Direct access to all 13 MCP servers
- **Command System**: Execute trades, get analysis, manage portfolio via chat
- **Trading Signals**: Get AI-powered trading recommendations

### 🔍 Symbol Search
- **Quick Search**: Find stocks and crypto assets instantly
- **Category Browser**: Browse by industry, sector, or asset class
- **Favorites System**: Star your favorite symbols for quick access

### ⌨️ Keyboard Navigation
- Intuitive keyboard shortcuts for all actions
- Arrow keys for navigation
- Function keys for quick access
- No mouse required!

## Installation

```bash
cd /home/cryptosaiyan/Documents/AutoFinance/cli
pip install -r requirements.txt
```

## Quick Start

```bash
# Run the CLI
python main.py

# Or run dashboard directly
python dashboard.py

# Or just the landing page
python landing.py
```

## Keyboard Shortcuts

### Global
- `Q` - Quit
- `H` - Help
- `R` - Refresh data
- `ESC` - Return to main view

### Navigation
- `1` - Charts View
- `2` - Search View
- `3` - Chat View
- `↑/↓` - Navigate lists
- `←/→` - Navigate tabs
- `ENTER` - Select/Confirm

### Charts View
- View live price charts in grid layout
- Real-time portfolio value
- Quick access to favorites

### Search View
- `S` or `/` - Open search
- Type to search symbols
- `ENTER` - Add to favorites
- `DEL` - Remove from favorites

### Chat View
- Type message and press `ENTER`
- `/tools` - List available MCP tools
- `/call <server> <method>` - Execute MCP tool
- `/clear` - Clear chat history
- `/help` - Show chat commands

## Configuration

Edit `config.yaml` to customize:

```yaml
dashboard:
  default_symbols:
    - "AAPL"
    - "MSFT"
    - "GOOGL"
    - "TSLA"
  grid_columns: 2
  chart_height: 15
  chart_width: 60
  chart_history: 120  # data points

colors:
  logo_base: "bold cyan"
  logo_accent: "bold purple"
  profit: "bold green"
  loss: "bold red"
  # ... more color options
```

## Data Sources

### Binance (Crypto)
- Real-time WebSocket data
- Supports all USDT pairs (BTC, ETH, BNB, etc.)
- Interval: 1m, 5m, 15m, 1h

### Yahoo Finance (Stocks)
- Polling-based updates
- All US stocks and major indices
- Interval: 1m, 5m, 15m, 30m, 1h

## MCP Integration

The chat interface provides direct access to all AutoFinance MCP servers:

- **Market** (9001) - Real-time prices
- **Risk** (9002) - Trade validation
- **Execution** (9003) - Portfolio & trades
- **Compliance** (9004) - Audit logs
- **Technical** (9005) - RSI, MACD, Bollinger
- **Fundamental** (9006) - P/E, ROE, metrics
- **Volatility** (9007) - Volatility analysis
- **Portfolio** (9008) - Analytics
- **News** (9009) - Sentiment analysis
- **Macro** (9010) - Economic indicators
- **Alert** (9011) - Price alerts
- **Simulation** (9012) - Monte Carlo
- **Notification** (9013) - Multi-channel alerts

## Architecture

```
cli/
├── main.py                 # Main entry point
├── landing.py              # Landing page with animation
├── dashboard.py            # Main dashboard
├── config.yaml             # Configuration
├── requirements.txt        # Dependencies
├── components/
│   ├── charts.py          # Live chart rendering (plotille)
│   ├── chatbox.py         # Copilot chat interface
│   ├── portfolio.py       # Portfolio tracker
│   └── search.py          # Symbol search & favorites
├── data/
│   └── fetchers.py        # Binance & yfinance data
└── utils/
    └── keyboard.py        # Keyboard navigation
```

## Examples

### Adding a Symbol to Dashboard

1. Press `2` to open Search
2. Type symbol name (e.g., "AAPL")
3. Press `ENTER` to add to favorites
4. Press `1` to return to Charts
5. Symbol appears in your chart grid!

### Executing a Trade via Chat

1. Press `3` to open Chat
2. Type: `/call execution execute_trade {"symbol": "AAPL", "quantity": 10, "action": "BUY"}`
3. Press `ENTER`
4. Portfolio updates in real-time!

### Getting Technical Analysis

1. Press `3` to open Chat
2. Ask: "What's the RSI for TSLA?"
3. Copilot will call the Technical server and respond

## Troubleshooting

### Charts not updating
- Ensure MCP servers are running: `./start_sse_servers.fish`
- Check internet connection for data sources
- Verify symbols are correct

### Keyboard not responding
- Terminal must support raw mode
- Try running with: `TERM=xterm-256color python main.py`

### Display issues
- Ensure terminal size is at least 120x40
- Use a terminal with Unicode support
- Try: `export LC_ALL=en_US.UTF-8`

## Requirements

- Python 3.10+
- Terminal with Unicode support
- MCP servers running (for chat features)
- Internet connection (for data)

## License

Part of AutoFinance project - WeMakeDevs "2 Fast 2 MCP" Hackathon
