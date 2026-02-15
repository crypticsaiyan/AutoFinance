# AutoFinance CLI

Terminal-based unified trading dashboard with real-time charts, AI copilot, and portfolio tracking.

## Features

🔥 **Unified Dashboard** - Everything on one screen:
- Live chart grid (2x2) with Binance WebSocket & yfinance data
- AI Copilot chatbox with MCP tool access (right panel)
- Real-time portfolio P&L (header bar)
- Single input field (TAB to toggle chat/search modes)

📊 **Multi-Source Data**:
- Cryptocurrencies via Binance WebSocket (BTCUSDT, ETHUSDT, etc.)
- Stocks via yfinance polling (AAPL, MSFT, GOOGL, etc.)
- Braille-dot charts with SMA indicators

🤖 **AI Copilot Integration**:
- Connected to 13 MCP servers (market, execution, risk, etc.)
- Chat commands: `/tools`, `/call <server> <tool> {...}`
- Portfolio updates automatically when executing trades

## Quick Start

### 1. Installation

```fish
cd cli
./install.fish
```

This creates a virtual environment and installs all dependencies:
- rich (Terminal UI)
- plotille (Braille charts)
- yfinance (Stock data)
- python-binance (Crypto WebSocket)
- Other utilities

### 2. Start MCP Servers

```fish
cd ..
./start_sse_servers.fish
```

This launches 13 MCP servers on ports 9001-9013:
- alert-engine, compliance, execution
- fundamental, market, news
- portfolio-analytics, risk, technical
- volatility, simulation-engine
- trader-supervisor, investor-supervisor

### 3. Launch Dashboard

```fish
cd cli
./run.fish
```

Or manually:
```fish
source venv/bin/activate.fish
python main.py
```

## Usage

### Landing Menu

When you start, you'll see an animated ASCII art logo with options:
- `d` - Launch unified dashboard
- `h` - Help & info
- `q` - Quit

### Unified Dashboard

The dashboard shows everything simultaneously:

```
┌─────────────────────────────────────────────────────────────────┐
│ AutoFinance | Portfolio: $XXX,XXX (+X.X%) | Status: Live       │
├──────────────────────────────┬──────────────────────────────────┤
│                              │                                  │
│  ┌─────────┐  ┌─────────┐   │  ┌────────────────────────────┐ │
│  │ BTC/USD │  │ ETH/USD │   │  │ Copilot Chat               │ │
│  │  Chart  │  │  Chart  │   │  │                            │ │
│  └─────────┘  └─────────┘   │  │ > /tools                   │ │
│                              │  │ Available tools:           │ │
│  ┌─────────┐  ┌─────────┐   │  │ - market/get_price         │ │
│  │ AAPL    │  │ MSFT    │   │  │ - execution/execute_trade  │ │
│  │  Chart  │  │  Chart  │   │  │ ...                        │ │
│  └─────────┘  └─────────┘   │  └────────────────────────────┘ │
│                              │                                  │
├──────────────────────────────┴──────────────────────────────────┤
│ [CHAT] > _                                                      │
└─────────────────────────────────────────────────────────────────┘
```

**Left Panel (58%)**: Live chart grid
- 2x2 grid showing 4 symbols
- Braille-dot line charts with SMA indicators
- Auto-refreshes from WebSocket/polling

**Right Panel (42%)**: Copilot chat
- Scrollable chat history (50 width)
- Command interface for MCP tools
- Real-time responses

**Header Bar**: Portfolio summary
- Total value
- P&L percentage (green/red)
- Live connection status

**Footer**: Single input field
- **CHAT mode** (default): Send messages to copilot
- **SEARCH mode** (TAB key): Add symbols to chart grid

### Keyboard Controls

#### Global
- `TAB` - Toggle input mode (chat ↔ search)
- `Ctrl+C` - Exit dashboard
- `Ctrl+L` - Clear chat history
- `q` - Quit (when not typing)

#### Input Field
- `Enter` - Send message (CHAT) or add symbol (SEARCH)
- `Backspace` - Delete character
- `Arrow Up/Down` - Navigate input history
- `Esc` - Clear current input

#### Chart Controls
- `r` - Refresh all data
- `c` - Cycle colors
- `+/-` - Zoom in/out (future)

### Copilot Commands

#### List Available Tools
```
/tools
```

Shows all MCP servers and their tools.

#### Call a Tool
```
/call <server> <tool> <json_args>
```

Examples:
```
/call market get_price {"symbol": "AAPL"}
/call execution execute_trade {"symbol": "BTCUSDT", "side": "BUY", "quantity": 0.1}
/call portfolio get_positions {}
```

#### Natural Language
Just type questions:
```
What's the current price of Bitcoin?
Buy 100 shares of AAPL
Show my portfolio
```

The copilot will parse your intent and call the appropriate MCP tools.

### Adding Symbols

1. Press `TAB` to enter SEARCH mode (footer shows `[SEARCH]`)
2. Type symbol name: `AAPL`, `BTCUSDT`, `GOOGL`, etc.
3. Press `Enter` to add to chart grid
4. Press `TAB` again to return to CHAT mode

**Symbol Types**:
- Stocks: `AAPL`, `MSFT`, `GOOGL`, `TSLA`
- Crypto: `BTCUSDT`, `ETHUSDT`, `BNBUSDT` (Binance pairs)
- Forex: `EURUSD`, `GBPUSD` (via yfinance)

Maximum 4 symbols visible at once (2x2 grid).

### Favorites

Press `f` to open favorites manager (future feature):
- Save frequently-watched symbols
- Quick-load watchlists
- Export/import lists

### Configuration

Edit `config.yaml`:

```yaml
# Default symbols on startup
default_symbols:
  - BTCUSDT
  - ETHUSDT
  - AAPL
  - MSFT

# MCP server ports
mcp_servers:
  market: 9001
  execution: 9002
  portfolio: 9003
  # ... etc.

# Chart settings
chart:
  width: 45
  height: 11
  grid_columns: 2
  update_interval: 1.0  # seconds
  
# Data sources
binance:
  testnet: false
  stream_type: "kline_1m"
  
yfinance:
  interval: "1m"
  period: "1d"
```

## Architecture

### Components

**dashboard.py** - Main unified interface
- Single-screen layout with split panels
- Keyboard event loop
- Rendering coordination

**components/charts.py** - Chart rendering
- `LiveChart`: Individual braille-dot chart
- `ChartGrid`: 2x2 grid layout with panels
- SMA indicator calculations

**components/chatbox.py** - Copilot interface
- `CopilotChat`: Message history & rendering
- `MCPToolExecutor`: HTTP JSON-RPC client
- Command parser (`/tools`, `/call`)

**components/portfolio.py** - Portfolio tracking
- Real-time P&L calculation
- Position fetching from MCP portfolio server
- Price updates trigger recalculations

**components/search.py** - Symbol management
- `SymbolSearch`: Input field for adding symbols
- `FavoritesManager`: Persistent watchlists

**data/fetchers.py** - Data layer
- `BinanceFetcher`: WebSocket streaming (crypto)
- `YFinanceFetcher`: Polling (stocks/other)
- `DataManager`: Unified callback system

**utils/keyboard.py** - Input handling
- Raw terminal mode
- Non-blocking character reading
- Escape sequence parsing

### Data Flow

```
User Input
    ↓ (KeyboardHandler)
Dashboard
    ↓
    ├─→ Charts ← DataManager ← BinanceFetcher/YFinanceFetcher
    ├─→ Chat → MCPToolExecutor → HTTP → MCP Servers
    └─→ Portfolio → MCP Portfolio Server
```

**Real-time Updates**:
1. Data fetchers push to callbacks
2. Dashboard triggers re-render
3. Rich Live display updates

**Chat Execution**:
1. User sends message → CopilotChat
2. Parse command or natural language
3. Execute MCP tool via HTTP
4. Update portfolio if needed
5. Display response in chat panel

### MCP Integration

All 13 MCP servers communicate via HTTP JSON-RPC 2.0:

```python
# Example: Get price
POST http://localhost:9001/execute
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "get_price",
    "arguments": {"symbol": "AAPL"}
  },
  "id": 1
}
```

Response:
```json
{
  "jsonrpc": "2.0",
  "result": {"price": 150.23, "change": 2.1},
  "id": 1
}
```

## Troubleshooting

### Import Errors
```fish
cd cli
python test_imports.py
```

If failures:
```fish
source venv/bin/activate.fish
pip install -r requirements.txt
```

### MCP Servers Not Running
```fish
cd /home/cryptosaiyan/Documents/AutoFinance
./start_sse_servers.fish
```

Check ports:
```fish
lsof -i :9001-9013
```

### Virtual Environment Issues
Delete and recreate:
```fish
rm -rf venv
./install.fish
```

### Chart Not Updating
1. Check data source (Binance/yfinance)
2. Verify symbol format (BTCUSDT vs BTC-USD)
3. Press `r` to force refresh

### Terminal Display Issues
- Use terminal with Unicode support (Alacritty, Kitty, iTerm2)
- Font must support Braille characters (U+2800-U+28FF)
- Minimum size: 120x40 characters

## Development

### Project Structure
```
cli/
├── main.py              # Entry point
├── landing.py           # Landing menu
├── dashboard.py         # Unified dashboard
├── config.yaml          # Configuration
├── requirements.txt     # Dependencies
├── install.fish         # Installer
├── run.fish             # Launcher
├── test_imports.py      # Import validator
├── components/
│   ├── charts.py        # Chart rendering
│   ├── chatbox.py       # Copilot interface
│   ├── portfolio.py     # Portfolio tracker
│   └── search.py        # Symbol search
├── data/
│   └── fetchers.py      # Data sources
└── utils/
    └── keyboard.py      # Input handling
```

### Running Tests
```fish
# Test imports
python test_imports.py

# Test chart rendering
python -c "from components.charts import LiveChart; print('OK')"

# Test data fetchers
python -c "from data.fetchers import BinanceFetcher; print('OK')"

# Test copilot
python -c "from components.chatbox import CopilotChat; print('OK')"
```

### Adding New Features

**New Symbol Source**:
1. Add fetcher class in `data/fetchers.py`
2. Implement callback system
3. Register with DataManager
4. Update config.yaml

**New Chat Command**:
1. Add parser in `components/chatbox.py`
2. Implement handler method
3. Update help text

**New Chart Indicator**:
1. Add calculation in `components/charts.py`
2. Render in `LiveChart.render()`
3. Add config option

## Credits

Built with:
- [Rich](https://github.com/Willmcwilliam/rich) - Terminal UI framework
- [plotille](https://github.com/tammoippen/plotille) - Braille charts
- [yfinance](https://github.com/ranaroussi/yfinance) - Stock data
- [python-binance](https://github.com/sammchardy/python-binance) - Crypto WebSocket

## License

MIT

---

**Happy Trading! 📈**
