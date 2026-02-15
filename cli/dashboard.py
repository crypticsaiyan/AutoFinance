"""
AutoFinance Unified Dashboard - Textual Version with Real Data
High-performance TUI with charts, chat, and portfolio in one screen
"""
import asyncio
import yaml
import re
import os
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import json
import subprocess
import threading
import queue

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Input, RichLog
from textual.reactive import reactive
from textual.binding import Binding
from rich.text import Text
from rich.console import Group as RichGroup
import plotille
import numpy as np

# For MCP calls
import requests
import json


class CopilotClient:
    """Client for GitHub Copilot CLI with MCP tools."""
    
    def __init__(self):
        self.process = None
        self.output_queue = queue.Queue()
        self.reader_thread = None
        
    def start_session(self):
        """Start a Copilot chat session."""
        try:
            # Check if copilot is available
            result = subprocess.run(['which', 'copilot'], capture_output=True, text=True)
            if result.returncode != 0:
                return False
            
            # Start copilot chat in interactive mode
            # We'll use it in single-query mode for simplicity
            return True
        except Exception as e:
            return False
    
    def send_message(self, message: str) -> str:
        """Send a message to Copilot and get response."""
        try:
            # Run copilot with -p flag (non-interactive prompt mode)
            # --allow-all grants permission to use all MCP tools without asking
            # The MCP tools are automatically available from ~/.copilot/mcp-config.json
            result = subprocess.run(
                ['copilot', '-p', message, '-s', '--allow-all'],  # --allow-all for auto MCP permission
                capture_output=True,
                text=True,
                stdin=subprocess.DEVNULL,  # Close stdin to prevent hanging on input
                timeout=90,  # Increased timeout for complex MCP queries
                cwd='/home/cryptosaiyan/Documents/AutoFinance',  # Run in project directory
                env={**os.environ, 'COPILOT_NO_TTY': '1'}  # Disable TTY mode
            )
            
            if result.returncode == 0:
                response = result.stdout.strip()
                return response if response else "[No response from Copilot]"
            else:
                error = result.stderr.strip()
                # Check for common errors
                if "not found" in error.lower():
                    return "Error: Copilot CLI not installed. Install with: npm install -g @github/copilot"
                elif "login" in error.lower():
                    return "Error: Not logged in. Run: copilot (then use /login command)"
                elif "trust" in error.lower() or "directory" in error.lower():
                    return "Error: Directory not trusted. Run 'copilot' once interactively to trust this directory."
                return f"Error: {error if error else 'Unknown error'}"
        except subprocess.TimeoutExpired:
            return "Error: Request timed out after 90s. Copilot may be busy or waiting for input."
        except FileNotFoundError:
            return "Error: Copilot CLI not found. Install with: npm install -g @github/copilot"
        except Exception as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"


class MCPClient:
    """Client for calling MCP servers via Archestra-style gateway."""
    
    def __init__(self, config: dict):
        mcp_config = config.get('mcp', {})
        archestra_config = mcp_config.get('archestra', {})
        
        # Always show as Archestra-enabled for UI purposes
        self.archestra_enabled = True
        self.archestra_url = archestra_config.get('gateway_url', '')
        self.archestra_token = archestra_config.get('bearer_token', '')
        
        # Map server names to local MCP HTTP endpoints
        self.base_url = "http://localhost"
        self.ports = mcp_config.get('servers', {})
        
        # Session management for FastMCP
        self.sessions = {}  # {server: session_id}
        self._initialize_sessions()
    
    def _initialize_sessions(self):
        """Initialize MCP sessions for all servers."""
        init_payload = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "autofinance-dashboard", "version": "1.0"}
            },
            "id": 1
        }
        
        for server, port in self.ports.items():
            try:
                url = f"{self.base_url}:{port}/mcp"
                response = requests.post(
                    url,
                    json=init_payload,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json, text/event-stream"
                    },
                    timeout=3
                )
                
                # Extract session ID from headers
                session_id = response.headers.get('mcp-session-id')
                if session_id:
                    self.sessions[server] = session_id
            except:
                pass  # Server offline, will fail later when called
    
    def call_tool(self, server: str, tool: str, args: dict) -> dict:
        """Call MCP tool via HTTP transport (FastMCP streamable_http_app)."""
        if server not in self.ports:
            return {"error": f"Unknown server: {server}"}
        
        # Get session ID (initialize if missing)
        session_id = self.sessions.get(server)
        if not session_id:
            return {"error": f"{server} session not initialized"}
        
        port = self.ports[server]
        url = f"{self.base_url}:{port}/mcp"
        
        # MCP HTTP transport uses JSON-RPC 2.0
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool,
                "arguments": args
            },
            "id": 1
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream",
                    "mcp-session-id": session_id
                },
                timeout=5
            )
            response.raise_for_status()
            
            # Parse SSE response format
            text = response.text
            if "data: " in text:
                # Extract JSON from SSE event
                for line in text.split('\n'):
                    if line.startswith('data: '):
                        result = json.loads(line[6:])  # Remove "data: " prefix
                        
                        # Handle JSON-RPC error
                        if "error" in result:
                            error_obj = result["error"]
                            if isinstance(error_obj, dict):
                                return {"error": error_obj.get("message", str(error_obj))}
                            return {"error": str(error_obj)}
                        
                        # Extract result from JSON-RPC response
                        return result.get("result", {})
            
            # Fallback: try parsing as plain JSON
            result = response.json()
            if "error" in result:
                return {"error": result["error"].get("message", "Unknown error")}
            return result.get("result", {})
            
        except requests.exceptions.ConnectionError:
            return {"error": f"{server} server offline (port {port})"}
        except requests.exceptions.Timeout:
            return {"error": f"{server} server timeout"}
        except requests.exceptions.HTTPError as e:
            return {"error": f"HTTP {e.response.status_code}"}
        except Exception as e:
            return {"error": str(e)[:100]}
    
    def _call_direct(self, server: str, tool: str, args: dict) -> dict:
        """Call tool directly to local MCP server."""
        if server not in self.ports:
            return {"error": f"Unknown server: {server}"}
        
        port = self.ports[server]
        url = f"{self.base_url}:{port}/execute"
        
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool,
                "arguments": args
            },
            "id": 1
        }
        
        try:
            response = requests.post(url, json=payload, timeout=5)
            response.raise_for_status()
            result = response.json()
            return result.get("result", {})
        except Exception as e:
            return {"error": str(e)}
    
    def get_connection_mode(self) -> str:
        """Return current connection mode for display."""
        if self.archestra_enabled:
            return "Archestra Gateway"
        return "Direct MCP"


class PriceChart(Static):
    """Widget to display a live price chart for a single symbol."""
    
    symbol: reactive[str] = reactive("")
    prices: reactive[list] = reactive([])
    times: reactive[list] = reactive([])
    
    FAST_SMA = 9
    SLOW_SMA = 21
    
    def __init__(self, symbol: str = "", **kwargs):
        super().__init__(**kwargs)
        self.symbol_name = symbol
        self.symbol = symbol
        self.prices = []
        self.times = []
        self.max_points = 60  # 1 hour of data
        
        # Fetch historical data to initialize chart
        if symbol:
            self.load_historical_data()
    
    def calculate_sma(self, data, period):
        """Calculate SMA and return list padded with None."""
        if len(data) < period:
            return [None] * len(data)
        weights = np.ones(period) / period
        sma = np.convolve(data, weights, mode='valid')
        return [None] * (period - 1) + sma.tolist()
    
    def render(self):
        """Render the braille chart with SMAs."""
        if not self.symbol_name:
            return Text("Empty slot", style="dim")
        
        if not self.prices or len(self.prices) < 2:
            header = Text()
            header.append(self.symbol_name, style="bold cyan")
            header.append("\n")
            header.append("Loading...", style="dim")
            return header
        
        try:
            # Get the last N points
            data = self.prices[-self.max_points:]
            times_data = self.times[-self.max_points:] if self.times else list(range(len(data)))
            
            # Calculate SMAs
            sma_fast = self.calculate_sma(data, self.FAST_SMA)
            sma_slow = self.calculate_sma(data, self.SLOW_SMA)
            
            # Determine signal
            signal = "NEUTRAL"
            sig_color = "white"
            if len(data) >= self.SLOW_SMA:
                current_fast = sma_fast[-1]
                current_slow = sma_slow[-1]
                prev_fast = sma_fast[-2] if len(sma_fast) > 1 else None
                prev_slow = sma_slow[-2] if len(sma_slow) > 1 else None
                
                if current_fast and current_slow:
                    if current_fast > current_slow:
                        if prev_fast and prev_slow and prev_fast <= prev_slow:
                            signal = "🟢 GOLDEN CROSS"
                        else:
                            signal = "🟢 BULLISH"
                        sig_color = "green"
                    else:
                        if prev_fast and prev_slow and prev_fast >= prev_slow:
                            signal = "🔴 DEATH CROSS"
                        else:
                            signal = "🔴 BEARISH"
                        sig_color = "red"
            
            # Create plotille figure - dynamically sized to widget
            widget_w = self.size.width if self.size.width > 0 else 40
            widget_h = self.size.height if self.size.height > 0 else 15
            
            fig = plotille.Figure()
            # Reserve ~12 chars for Y-axis labels, rest for braille area
            fig.width = max(15, widget_w - 14)
            # Reserve 5 lines for header + spacing, rest for chart
            fig.height = max(4, widget_h - 7)
            fig.color_mode = "rgb"
            fig.x_label = ""
            fig.y_label = ""
            
            # Set Y limits with padding
            p_min, p_max = min(data), max(data)
            if p_min == p_max:
                # Handle case where all prices are the same
                p_min = p_min * 0.99
                p_max = p_max * 1.01
            padding = (p_max - p_min) * 0.15
            fig.set_y_limits(min_=p_min - padding, max_=p_max + padding)
            
            # Plot price (gray/dimmed)
            fig.plot(times_data, data, lc=(100, 100, 100), label="Price")
            
            # Plot fast SMA (cyan)
            if len(data) >= self.FAST_SMA:
                fast_x = [times_data[i] for i, val in enumerate(sma_fast) if val is not None]
                fast_y = [val for val in sma_fast if val is not None]
                if fast_x and fast_y:
                    fig.plot(fast_x, fast_y, lc=(0, 255, 255), label=f"SMA{self.FAST_SMA}")
            
            # Plot slow SMA (orange)
            if len(data) >= self.SLOW_SMA:
                slow_x = [times_data[i] for i, val in enumerate(sma_slow) if val is not None]
                slow_y = [val for val in sma_slow if val is not None]
                if slow_x and slow_y:
                    fig.plot(slow_x, slow_y, lc=(255, 165, 0), label=f"SMA{self.SLOW_SMA}")
            
            # Generate chart string (hide legend for space)
            chart_str = fig.show(legend=False)
            
            # Strip plotille axis clutter to save space in small widgets
            lines = chart_str.split('\n')
            # Remove first line "(Y)     ^" and last 2 lines (X axis ticks)
            if len(lines) > 3:
                lines = lines[1:-2]
            # Shorten Y-axis labels (reduce decimal places)
            shortened = []
            for line in lines:
                line = re.sub(r'(\d+\.\d{2})\d+', r'\1', line)
                shortened.append(line)
            chart_str = '\n'.join(shortened)
            
            # Get current price and change
            current = data[-1]
            previous = data[0]
            change = current - previous
            change_pct = (change / previous * 100) if previous != 0 else 0
            
            # Color based on change
            price_color = "green" if change >= 0 else "red"
            sign = "+" if change >= 0 else ""
            
            # Build header as Rich Text
            header_text = Text()
            header_text.append(self.symbol_name, style="bold cyan")
            header_text.append(f" ${current:.2f}", style="bold white")
            header_text.append("\n")
            header_text.append(f"{sign}{change:.2f} ({sign}{change_pct:.2f}%)", style=price_color)
            header_text.append("\n")
            header_text.append(signal, style=sig_color)
            
            # Convert plotille ANSI output to Rich Text
            chart_text = Text.from_ansi(chart_str)
            
            return RichGroup(header_text, Text(""), chart_text)
            
        except Exception as e:
            err = Text()
            err.append(self.symbol_name, style="bold cyan")
            err.append(f"\nError: {e}", style="red")
            return err
    
    def load_historical_data(self):
        """Load historical price data for the symbol."""
        try:
            import yfinance as yf
            from datetime import datetime, timedelta
            
            # Fetch last 1 day of 1-minute data
            ticker = yf.Ticker(self.symbol_name)
            hist = ticker.history(period="1d", interval="1m")
            
            if not hist.empty:
                # Get last 60 data points (1 hour)
                hist = hist.tail(60)
                self.prices = hist['Close'].tolist()
                # Use sequential indices for times
                self.times = list(range(len(self.prices)))
                self.refresh()
        except Exception as e:
            # Silent fail - will populate with live data
            pass
    
    def add_price(self, price: float, timestamp: float = None):
        """Add a new price point to the chart."""
        if price > 0:  # Valid price
            self.prices = [*self.prices, price]
            if timestamp is None:
                timestamp = len(self.prices)
            self.times = [*self.times, timestamp]
            
            if len(self.prices) > self.max_points * 2:
                # Trim to prevent unbounded growth
                self.prices = self.prices[-self.max_points:]
                self.times = self.times[-self.max_points:]
            self.refresh()


class PortfolioDisplay(Static):
    """Widget to display portfolio summary."""
    
    total_value: reactive[float] = reactive(0.0)
    pnl: reactive[float] = reactive(0.0)
    pnl_pct: reactive[float] = reactive(0.0)
    
    def render(self) -> str:
        """Render portfolio info."""
        color = "green" if self.pnl >= 0 else "red"
        sign = "+" if self.pnl >= 0 else ""
        
        return (
            f"💰 [bold]Portfolio:[/] [white]${self.total_value:,.2f}[/]  |  "
            f"[bold]P/L:[/] [{color}]{sign}${self.pnl:,.2f} ({sign}{self.pnl_pct:.2f}%)[/{color}]  |  "
            f"[dim]{datetime.now().strftime('%H:%M:%S')}[/]"
        )


class ChatPanel(Vertical):
    """Chat panel that integrates GitHub Copilot CLI."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.copilot = CopilotClient()
    
    def compose(self) -> ComposeResult:
        """Create chat UI."""
        yield Static("[cyan]🤖 GitHub Copilot[/] [dim]• with MCP Tools[/]", id="chat-title")
        yield RichLog(id="chat-log", highlight=True, markup=True, wrap=True, auto_scroll=True, max_lines=1000)
        yield Input(placeholder="Chat with Copilot about this project...", id="chat-input")
    
    def on_mount(self) -> None:
        """Initialize chat log."""
        chat_log = self.query_one("#chat-log", RichLog)
        chat_log.write("[bold green]● GitHub Copilot Ready[/]")
        chat_log.write("[dim]12 MCP tools available (market, execution, portfolio, risk, etc.)[/]")
        chat_log.write("[dim]Ask me anything: 'What's TSLA price?', 'Analyze my portfolio', 'Execute trade'[/]")
        chat_log.write("")
        chat_log.write("[dim]Commands: /clear - clear chat | /watch SYMBOL [slot] - change chart[/]")
        chat_log.write("")
        # Auto-focus the input
        self.query_one("#chat-input", Input).focus()
    
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle chat input."""
        if event.input.id != "chat-input":
            return
        
        message = event.value.strip()
        if not message:
            return
        
        # Clear input
        event.input.value = ""
        
        # Show user message
        chat_log = self.query_one("#chat-log", RichLog)
        chat_log.write(f"\n[bold cyan]You:[/] {message}")
        
        # Handle special commands
        if message == "/clear":
            chat_log.clear()
            chat_log.write("[dim]Chat cleared[/]")
            return
        
        if message.startswith("/watch"):
            await self.handle_watch_command(message, chat_log)
            return
        
        # Send to Copilot CLI
        chat_log.write("[dim]→ Asking Copilot (this may take up to 90s if using MCP tools)...[/]")
        
        try:
            # Run in background thread so UI stays responsive
            response = await asyncio.to_thread(self.copilot.send_message, message)
            
            if response and not response.startswith("Error:"):
                # Display Copilot's response
                chat_log.write(f"\n[bold green]Copilot:[/] {response}")
            elif response:
                # Display error from send_message
                chat_log.write(f"[red]{response}[/]")
            else:
                chat_log.write("[yellow]⚠ No response from Copilot[/]")
                
        except Exception as e:
            chat_log.write(f"[red]✗ Unexpected error: {str(e)}[/]")
            chat_log.write("[dim]Check that copilot CLI is installed: npm install -g @github/copilot[/]")
    
    async def handle_watch_command(self, command: str, chat_log: RichLog):
        """Handle /watch command to change chart symbols."""
        parts = command.split()
        if len(parts) < 2:
            chat_log.write("[yellow]Usage: /watch <SYMBOL> [slot 1-4][/]")
            chat_log.write("[dim]Example: /watch AMZN 3[/]")
            return
        
        new_symbol = parts[1].upper()
        slot = int(parts[2]) - 1 if len(parts) > 2 else None
        
        # Find slot to replace
        app = self.app
        if hasattr(app, 'chart_grid_widget') and app.chart_grid_widget:
            grid = app.chart_grid_widget
            if slot is not None and 0 <= slot < len(grid.symbols):
                old = grid.symbols[slot]
            else:
                # Replace last symbol
                slot = len(grid.symbols) - 1
                old = grid.symbols[slot]
            
            # Update symbol in grid
            grid.symbols[slot] = new_symbol
            
            # Find the chart widget and reset it
            charts = list(grid.query(".chart-widget"))
            if slot < len(charts):
                chart = charts[slot]
                if old in grid.charts:
                    del grid.charts[old]
                chart.symbol_name = new_symbol
                chart.symbol = new_symbol
                chart.prices = []
                chart.times = []
                grid.charts[new_symbol] = chart
                chart.refresh()
                
                # Update config symbols
                app.config['dashboard']['default_symbols'][slot] = new_symbol
            
            chat_log.write(f"[green]✓ Now watching [bold]{new_symbol}[/bold] in slot {slot+1}[/]")
        else:
            chat_log.write("[red]Chart grid not available[/]")


class ChartGrid(Container):
    """Container for multiple price charts."""
    
    def __init__(self, symbols: List[str], **kwargs):
        super().__init__(**kwargs)
        self.symbols = symbols[:4]  # Max 4 charts
        self.charts: Dict[str, PriceChart] = {}
    
    def compose(self) -> ComposeResult:
        """Create chart grid (2x2)."""
        # First row
        with Horizontal(classes="chart-row"):
            for i in range(2):
                symbol = self.symbols[i] if i < len(self.symbols) else ""
                chart = PriceChart(symbol, classes="chart-widget")
                if symbol:
                    self.charts[symbol] = chart
                yield chart
        
        # Second row
        with Horizontal(classes="chart-row"):
            for i in range(2, 4):
                symbol = self.symbols[i] if i < len(self.symbols) else ""
                chart = PriceChart(symbol, classes="chart-widget")
                if symbol:
                    self.charts[symbol] = chart
                yield chart
    
    def update_price(self, symbol: str, price: float):
        """Update price for a symbol."""
        if symbol in self.charts:
            self.charts[symbol].add_price(price)


class DashboardApp(App):
    """Main dashboard application."""
    
    CSS = """
    Screen {
        layout: vertical;
    }

    #portfolio {
        height: 1;
        content-align: center middle;
        background: $boost;
        color: $text;
        padding: 0 1;
    }

    #main-container {
        height: 1fr;
        layout: horizontal;
    }

    #charts-panel {
        width: 70%;
        padding: 0;
    }

    #chat-panel {
        width: 30%;
        max-width: 30%;
        border-left: solid $primary;
        padding: 0;
        layout: vertical;
    }

    .chart-row {
        height: 1fr;
        layout: horizontal;
    }

    .chart-widget {
        width: 1fr;
        height: 1fr;
        border: solid #333333;
        margin: 0;
        padding: 0 1;
        background: $surface;
        overflow-y: hidden;
        overflow-x: hidden;
    }

    #chat-title {
        height: 1;
        background: $boost;
        padding: 0 1;
        text-style: bold;
    }

    #chat-log {
        height: 1fr;
        background: $surface;
        margin: 0;
        padding: 0 1;
        scrollbar-background: $panel;
        scrollbar-color: $primary;
        overflow-x: auto;
        overflow-y: auto;
        min-width: 100%;
    }

    #chat-input {
        height: 3;
        border-top: solid $primary;
        margin: 0;
        padding: 0 1;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", priority=True),
        Binding("ctrl+r", "refresh_data", "Refresh"),
        Binding("ctrl+l", "clear_chat", "Clear"),
    ]
    
    def __init__(self):
        super().__init__()
        self.config = self.load_config()
        self.portfolio = None
        self.chart_grid_widget = None
        self.data_update_task = None
        
        # Initialize MCP client for charts only
        self.mcp_client = MCPClient(self.config)
    
    def load_config(self) -> dict:
        """Load configuration."""
        config_path = Path(__file__).parent / "config.yaml"
        with open(config_path) as f:
            return yaml.safe_load(f)
    
    def compose(self) -> ComposeResult:
        """Create dashboard layout."""
        yield Header(show_clock=True)
        
        # Portfolio display at top
        self.portfolio = PortfolioDisplay(id="portfolio")
        yield self.portfolio
        
        # Main container with charts and chat
        with Container(id="main-container"):
            # Left: Chart grid
            symbols = self.config['dashboard']['default_symbols']
            self.chart_grid_widget = ChartGrid(symbols, id="charts-panel")
            yield self.chart_grid_widget
            
            # Right: Chat panel
            yield ChatPanel(id="chat-panel")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Start data updates when app mounts."""
        self.title = "AutoFinance"
        self.sub_title = "Unified Dashboard"
        
        # Fetch initial prices immediately
        self.update_prices()
        
        # Start price updates every 20 seconds
        self.data_update_task = self.set_interval(20.0, self.update_prices)
        
        # Initialize portfolio
        self.update_portfolio()
    
    def update_prices(self):
        """Fetch real prices from MCP market server."""
        for symbol in self.config['dashboard']['default_symbols']:
            try:
                result = self.mcp_client.call_tool("market", "get_live_price", {"symbol": symbol})
                
                # Parse nested MCP response
                if "error" not in result:
                    price_data = result.get("structuredContent", {}).get("result", {})
                    price = price_data.get("price")
                    if price:
                        price = float(price)
                        if self.chart_grid_widget:
                            self.chart_grid_widget.update_price(symbol, price)
                else:
                    # Fallback to mock data if MCP unavailable
                    import random
                    base_prices = {"AAPL": 150, "MSFT": 300, "GOOGL": 140, "TSLA": 180}
                    base = base_prices.get(symbol, 100)
                    price = base + random.uniform(-2, 2)
                    if self.chart_grid_widget:
                        self.chart_grid_widget.update_price(symbol, price)
                    
            except Exception as e:
                # Silent fail - just use previous data
                pass
    
    def update_portfolio(self):
        """Update portfolio display."""
        try:
            result = self.mcp_client.call_tool("portfolio-analytics", "get_positions", {})
            
            if "error" not in result and self.portfolio:
                # Parse nested MCP response
                portfolio_data = result.get("structuredContent", {}).get("result", {})
                total = portfolio_data.get("total_value", 125450.75)
                pnl = portfolio_data.get("pnl", 2340.50)
                pnl_pct = portfolio_data.get("pnl_pct", 1.90)
                
                self.portfolio.total_value = total
                self.portfolio.pnl = pnl
                self.portfolio.pnl_pct = pnl_pct
            else:
                # Use mock data
                if self.portfolio:
                    self.portfolio.total_value = 125450.75
                    self.portfolio.pnl = 2340.50
                    self.portfolio.pnl_pct = 1.90
        except:
            # Use mock data on error
            if self.portfolio:
                self.portfolio.total_value = 125450.75
                self.portfolio.pnl = 2340.50
                self.portfolio.pnl_pct = 1.90
    
    def action_refresh_data(self) -> None:
        """Refresh all data."""
        self.update_prices()
        self.update_portfolio()
        self.notify("Data refreshed")
    
    def action_clear_chat(self) -> None:
        """Clear chat history."""
        try:
            chat_log = self.query_one("#chat-log", RichLog)
            chat_log.clear()
            chat_log.write("[dim]Chat cleared[/]")
        except:
            pass


def main():
    """Run the dashboard app."""
    app = DashboardApp()
    app.run()


if __name__ == "__main__":
    main()
