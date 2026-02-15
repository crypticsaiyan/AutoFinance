"""
AutoFinance Unified Dashboard - Textual Version
High-performance TUI with charts, chat, and portfolio in one screen
"""
import asyncio
import yaml
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Static, Input, RichLog
from textual.reactive import reactive
from textual.binding import Binding
from textual import events
import asciichartpy


class PriceChart(Static):
    """Widget to display a live price chart for a single symbol."""
    
    symbol: reactive[str] = reactive("", recompose=True)
    prices: reactive[list] = reactive([], recompose=True)
    
    def __init__(self, symbol: str = "", **kwargs):
        super().__init__(**kwargs)
        self.symbol = symbol
        self.prices = []
        self.max_points = 50
    
    def render(self) -> str:
        """Render the ASCII chart."""
        if not self.prices or len(self.prices) < 2:
            return f"[bold cyan]{self.symbol}[/]\n[dim]Waiting for data...[/]"
        
        try:
            # Get the last N points
            data = self.prices[-self.max_points:]
            
            # Generate ASCII chart
            config = {
                'height': 8,
                'format': '{:8.2f}',
            }
            
            chart = asciichartpy.plot(data, config)
            
            # Get current price and change
            current = data[-1]
            previous = data[-2] if len(data) > 1 else current
            change = current - previous
            change_pct = (change / previous * 100) if previous != 0 else 0
            
            # Color based on change
            color = "green" if change >= 0 else "red"
            sign = "+" if change >= 0 else ""
            
            # Build header
            header = f"[bold cyan]{self.symbol}[/] [bold white]{current:.2f}[/] [{color}]{sign}{change:.2f} ({sign}{change_pct:.2f}%)[/{color}]"
            
            return f"{header}\n{chart}"
            
        except Exception as e:
            return f"[bold cyan]{self.symbol}[/]\n[red]Chart error: {e}[/]"
    
    def add_price(self, price: float):
        """Add a new price point to the chart."""
        self.prices = [*self.prices, price]
        if len(self.prices) > self.max_points * 2:
            # Trim to prevent unbounded growth
            self.prices = self.prices[-self.max_points:]


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
            f"💰 Portfolio: [bold white]${self.total_value:,.2f}[/] | "
            f"P/L: [{color}]{sign}${self.pnl:,.2f} ({sign}{self.pnl_pct:.2f}%)[/{color}]"
        )


class ChatPanel(Vertical):
    """Chat panel with message history and input."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mcp_executor = None  # Will be initialized by app
    
    def compose(self) -> ComposeResult:
        """Create chat UI."""
        yield Static("[bold cyan]🤖 Copilot Chat[/]", id="chat-title")
        yield RichLog(id="chat-log", highlight=True, markup=True, wrap=True)
        yield Input(placeholder="Type message or /command...", id="chat-input")
    
    def on_mount(self) -> None:
        """Initialize chat log."""
        chat_log = self.query_one("#chat-log", RichLog)
        chat_log.write("[dim]Welcome to AutoFinance Copilot![/]")
        chat_log.write("[dim]Commands: /tools, /call <server> <tool> <json>[/]")
        chat_log.write("")
    
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
        chat_log.write(f"[bold green]You:[/] {message}")
        
        # Handle commands
        if message.startswith("/"):
            await self.handle_command(message)
        else:
            # For now, just echo
            chat_log.write(f"[bold cyan]Copilot:[/] Received: {message}")
    
    async def handle_command(self, command: str):
        """Handle chat commands."""
        chat_log = self.query_one("#chat-log", RichLog)
        
        if command == "/tools":
            chat_log.write("[bold cyan]Available MCP Servers:[/]")
            chat_log.write("• market (port 9001) - get_price, get_ohlcv")
            chat_log.write("• execution (port 9003) - execute_trade")
            chat_log.write("• portfolio (port 9008) - get_positions")
            chat_log.write("• risk (port 9002) - calculate_var")
            chat_log.write("• technical (port 9005) - get_indicators")
            
        elif command.startswith("/call"):
            parts = command.split(maxsplit=3)
            if len(parts) < 3:
                chat_log.write("[red]Usage: /call <server> <tool> <json>[/]")
                return
            
            server = parts[1]
            tool = parts[2]
            args = parts[3] if len(parts) > 3 else "{}"
            
            chat_log.write(f"[dim]Calling {server}/{tool}...[/]")
            
            # TODO: Implement actual MCP call
            import json
            try:
                args_dict = json.loads(args)
                chat_log.write(f"[yellow]Mock result for {server}/{tool}: Success[/]")
            except json.JSONDecodeError:
                chat_log.write("[red]Invalid JSON arguments[/]")
        
        elif command == "/clear":
            chat_log.clear()
            chat_log.write("[dim]Chat cleared[/]")
        
        else:
            chat_log.write(f"[red]Unknown command: {command}[/]")


class ChartGrid(Container):
    """Container for multiple price charts."""
    
    def __init__(self, symbols: List[str], **kwargs):
        super().__init__(**kwargs)
        self.symbols = symbols
        self.charts: Dict[str, PriceChart] = {}
    
    def compose(self) -> ComposeResult:
        """Create chart grid (2x2)."""
        # First row
        with Horizontal(classes="chart-row"):
            chart1 = PriceChart(self.symbols[0] if len(self.symbols) > 0 else "")
            chart2 = PriceChart(self.symbols[1] if len(self.symbols) > 1 else "")
            self.charts[self.symbols[0]] = chart1 if len(self.symbols) > 0 else None
            self.charts[self.symbols[1]] = chart2 if len(self.symbols) > 1 else None
            yield chart1
            yield chart2
        
        # Second row
        with Horizontal(classes="chart-row"):
            chart3 = PriceChart(self.symbols[2] if len(self.symbols) > 2 else "")
            chart4 = PriceChart(self.symbols[3] if len(self.symbols) > 3 else "")
            self.charts[self.symbols[2]] = chart3 if len(self.symbols) > 2 else None
            self.charts[self.symbols[3]] = chart4 if len(self.symbols) > 3 else None
            yield chart3
            yield chart4
    
    def update_price(self, symbol: str, price: float):
        """Update price for a symbol."""
        if symbol in self.charts and self.charts[symbol]:
            self.charts[symbol].add_price(price)


class DashboardApp(App):
    """Main dashboard application."""
    
    CSS = """
    Screen {
        layout: vertical;
    }
    
    #portfolio {
        height: 3;
        content-align: center middle;
        background: $boost;
        padding: 1;
    }
    
    #main-container {
        height: 1fr;
        layout: horizontal;
    }
    
    #charts-panel {
        width: 60%;
        border: solid $primary;
        padding: 1;
    }
    
    #chat-panel {
        width: 40%;
        border: solid $secondary;
        padding: 1;
        layout: vertical;
    }
    
    .chart-row {
        height: 1fr;
        layout: horizontal;
    }
    
    PriceChart {
        width: 1fr;
        border: solid $accent;
        margin: 1;
        padding: 1;
    }
    
    #chat-title {
        height: 1;
        padding: 0 1;
    }
    
    #chat-log {
        height: 1fr;
        border: solid $accent;
        margin: 1 0;
        padding: 1;
    }
    
    #chat-input {
        height: 3;
        border: solid $primary;
        margin: 0 1;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("ctrl+l", "clear_chat", "Clear Chat"),
    ]
    
    def __init__(self):
        super().__init__()
        self.config = self.load_config()
        self.portfolio = None
        self.chart_grid_widget = None
        self.data_update_task = None
    
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
        self.title = "AutoFinance - Unified Dashboard"
        self.sub_title = "Charts | Chat | Portfolio"
        
        # Start mock data updates
        self.data_update_task = self.set_interval(2.0, self.update_data)
        
        # Initialize portfolio
        self.update_portfolio()
    
    def update_data(self):
        """Update chart data (mock for now)."""
        import random
        
        # Mock price updates
        for symbol in self.config['dashboard']['default_symbols']:
            # Generate mock price
            base_price = {"AAPL": 150, "MSFT": 300, "GOOGL": 140, "TSLA": 180}.get(symbol, 100)
            price = base_price + random.uniform(-5, 5)
            
            # Update chart
            if self.chart_grid_widget:
                self.chart_grid_widget.update_price(symbol, price)
    
    def update_portfolio(self):
        """Update portfolio display (mock for now)."""
        if self.portfolio:
            self.portfolio.total_value = 125450.75
            self.portfolio.pnl = 2340.50
            self.portfolio.pnl_pct = 1.90
    
    def action_refresh(self) -> None:
        """Refresh all data."""
        self.update_data()
        self.update_portfolio()
    
    def action_clear_chat(self) -> None:
        """Clear chat history."""
        chat_log = self.query_one("#chat-log", RichLog)
        chat_log.clear()


def main():
    """Run the dashboard app."""
    app = DashboardApp()
    app.run()


if __name__ == "__main__":
    main()
