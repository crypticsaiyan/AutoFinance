"""
Unified Dashboard - All-in-One Interface
Charts Grid (Left) + Copilot Chat (Right) + Portfolio (Header) - Single Screen
"""
import sys
import os
import time
import threading
from typing import List, Dict, Optional
import yaml

from rich.console import Console, Group
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.box import ROUNDED, SIMPLE
from rich.align import Align

# Import our components
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from components.charts import ChartGrid, LiveChart
from components.chatbox import CopilotChat
from components.portfolio import PortfolioTracker
from components.search import SearchInterface, FavoritesManager
from data.fetchers import DataManager
from utils.keyboard import KeyboardHandler, InputField


class Dashboard:
    """Unified dashboard - everything visible on one screen."""
    
    def __init__(self, config_path: str = None):
        # Load config
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize components
        self.console = Console()
        self.data_manager = DataManager()
        self.favorites = FavoritesManager()
        self.search_interface = SearchInterface(self.favorites)
        
        # Get favorite symbols or use defaults
        favorite_symbols = self.favorites.get_favorites()
        if not favorite_symbols:
            favorite_symbols = self.config['dashboard']['default_symbols']
        
        # Chart grid - optimized for side-by-side layout (2x2 grid)
        self.chart_grid = ChartGrid(
            columns=2,
            chart_width=45,
            chart_height=11
        )
        
        # Add charts for favorite symbols
        for symbol in favorite_symbols[:4]:  # Max 4 charts for unified view
            self._add_chart(symbol)
        
        # Portfolio tracker
        mcp_config = self.config['mcp']
        self.portfolio = PortfolioTracker(
            mcp_base_url=mcp_config['base_url'],
            execution_port=mcp_config['servers']['execution'],
            portfolio_port=mcp_config['servers']['portfolio'],
            market_port=mcp_config['servers']['market']
        )
        
        # Copilot chat - always visible
        self.chat = CopilotChat(
            width=50,
            height=30,
            max_history=self.config['copilot']['history_size'],
            mcp_base_url=mcp_config['base_url'],
            mcp_ports=mcp_config['servers']
        )
        
        # UI state
        self.chat_input = InputField(prompt="💬 ")
        self.search_input = InputField(prompt="🔍 ")
        self.input_mode = "chat"  # 'chat' or 'search'
        self.keyboard = KeyboardHandler()
        self.running = False
        self.update_interval = self.config['app']['refresh_rate']
        
        # Status messages
        self.status_message = "Dashboard Ready"
        self.status_timestamp = time.time()
        
        # Setup keyboard bindings
        self._setup_keybindings()
    
    def _add_chart(self, symbol: str):
        """Add a chart and start data fetching."""
        # Determine source
        source = "binance" if "USDT" in symbol else "yfinance"
        
        # Add chart
        self.chart_grid.add_chart(symbol)
        
        # Start data fetching
        fetcher = self.data_manager.add_symbol(
            symbol,
            source=source,
            interval="1m",
            max_points=self.config['dashboard']['chart_history']
        )
        
        # Register callback to update chart
        def update_callback(data):
            chart_symbol = data.get('symbol', symbol)
            self.chart_grid.update_chart(chart_symbol, data)
        
        fetcher.register_callback(update_callback)
    
    def _remove_chart(self, symbol: str):
        """Remove a chart and stop data fetching."""
        source = "binance" if "USDT" in symbol else "yfinance"
        self.chart_grid.remove_chart(symbol)
        self.data_manager.remove_symbol(symbol, source)
    
    def _setup_keybindings(self):
        """Setup keyboard shortcuts."""
        # Input mode switching
        self.keyboard.bind('tab', self._toggle_input_mode)
        
        # General
        self.keyboard.bind('q', self._quit)
        self.keyboard.bind('r', self._refresh)
        
        # Input handling
        self.keyboard.bind('backspace', self._handle_backspace)
        self.keyboard.bind('enter', self._handle_enter)
        self.keyboard.bind('esc', self._handle_esc)
        
        # Allow typing (simplified - in real app would handle all printable chars)
        for char in 'abcdefghijklmnopqrstuvwxyz0123456789 .,!?@#$%^&*()-_=+[]{}:;"\'<>/\\|`~':
            # Create closure to capture char value
            def make_handler(c):
                return lambda: self._handle_char_input(c)
            self.keyboard.bind(char, make_handler(char))
    
    def _toggle_input_mode(self):
        """Toggle between chat and search input."""
        self.input_mode = "search" if self.input_mode == "chat" else "chat"
        self.status_message = f"Input: {self.input_mode.upper()}"
        self.status_timestamp = time.time()
    
    def _handle_char_input(self, char: str):
        """Handle character input for current mode."""
        if self.input_mode == "chat":
            self.chat_input.insert(char)
        else:
            self.search_input.insert(char)
    
    def _handle_backspace(self):
        """Handle backspace."""
        if self.input_mode == "chat":
            self.chat_input.backspace()
        else:
            self.search_input.backspace()
    
    def _handle_enter(self):
        """Handle enter key - send message or add symbol."""
        if self.input_mode == "chat":
            message = self.chat_input.get_text().strip()
            if message:
                self.chat.send_message(message)
                self.chat_input.clear()
                self.status_message = "Message sent"
                self.status_timestamp = time.time()
                # Refresh portfolio after chat interaction (trades etc)
                threading.Thread(target=self.portfolio.update, daemon=True).start()
        else:
            query = self.search_input.get_text().strip()
            if query:
                # Add symbol to charts
                symbol = query.upper()
                if symbol not in [chart.symbol for chart in self.chart_grid.charts.values()]:
                    if len(self.chart_grid.charts) < 4:
                        self._add_chart(symbol)
                        self.favorites.add_favorite(symbol)
                        self.status_message = f"Added {symbol}"
                    else:
                        self.status_message = "Max 4 charts displayed"
                else:
                    self.status_message = f"{symbol} already displayed"
                self.search_input.clear()
                self.status_timestamp = time.time()
    
    def _handle_esc(self):
        """Handle escape key - clear current input."""
        if self.input_mode == "chat":
            self.chat_input.clear()
        else:
            self.search_input.clear()
    
    def _quit(self):
        """Quit the dashboard."""
        self.running = False
        return False
    
    def _refresh(self):
        """Refresh all data."""
        self.portfolio.update()
        self.status_message = "Refreshed"
        self.status_timestamp = time.time()
    
    def _render_header(self) -> Layout:
        """Render the header with portfolio summary."""
        layout = Layout()
        layout.split_row(
            Layout(name="title", ratio=1),
            Layout(name="portfolio", ratio=2),
            Layout(name="status", ratio=1)
        )
        
        # Title
        title = Text("AutoFinance Dashboard", style="bold cyan")
        layout["title"].update(Panel(Align.center(title), box=SIMPLE, border_style="cyan"))
        
        # Portfolio summary (inline)
        try:
            self.portfolio.update()
            portfolio_text = Text()
            portfolio_text.append("💼 Total: ", style="white")
            portfolio_text.append(f"${self.portfolio.total_value:,.2f} ", style="bold white")
            
            pnl_style = "bold green" if self.portfolio.total_pnl >= 0 else "bold red"
            pnl_symbol = "▲" if self.portfolio.total_pnl >= 0 else "▼"
            portfolio_text.append(f"{pnl_symbol} ", style=pnl_style)
            portfolio_text.append(f"${self.portfolio.total_pnl:+,.2f} ", style=pnl_style)
            portfolio_text.append(f"({self.portfolio.total_pnl_pct:+.2f}%)", style=pnl_style)
            
            border_style = "green" if self.portfolio.total_pnl >= 0 else "red"
        except:
            portfolio_text = Text("Loading portfolio...", style="yellow")
            border_style = "cyan"
        
        layout["portfolio"].update(Panel(Align.center(portfolio_text), box=SIMPLE, border_style=border_style))
        
        # Status
        status_text = Text()
        if time.time() - self.status_timestamp < 3:
            status_text.append(self.status_message, style="yellow")
        else:
            status_text.append("● Live", style="green")
        layout["status"].update(Panel(Align.center(status_text), box=SIMPLE, border_style="cyan"))
        
        return layout
    
    def _render_footer(self) -> Panel:
        """Render the footer with input field and shortcuts."""
        text = Text()
        
        # Input field
        input_field = self.chat_input if self.input_mode == "chat" else self.search_input
        mode_label = "Chat" if self.input_mode == "chat" else "Search"
        mode_color = "magenta" if self.input_mode == "chat" else "yellow"
        
        text.append(f"[{mode_label}] ", style=f"bold {mode_color}")
        text.append(input_field.get_display()[:80], style="white")  # Limit display length
        text.append(" │ ", style="dim")
        
        # Shortcuts
        text.append("[TAB] Switch", style="cyan")
        text.append(" │ ", style="dim")
        text.append("[ENTER] Send/Add", style="green")
        text.append(" │ ", style="dim")
        text.append("[R] Refresh", style="blue")
        text.append(" │ ", style="dim")
        text.append("[Q] Quit", style="red")
        
        return Panel(
            text,
            box=SIMPLE,
            border_style="cyan"
        )
    
    def _render_main_body(self) -> Layout:
        """Render unified dashboard: charts (left) + chat (right)."""
        layout = Layout()
        
        # Split: Charts (left 58%) + Chat (right 42%)
        layout.split_row(
            Layout(name="charts", ratio=58),
            Layout(name="chat", ratio=42)
        )
        
        # === LEFT SIDE: CHARTS GRID ===
        chart_rows = self.chart_grid.render()
        
        if chart_rows:
            # Create chart grid panel
            charts_container = []
            for row in chart_rows:
                row_table = Table.grid(padding=(0, 1))
                for _ in row:
                    row_table.add_column()
                row_table.add_row(*row)
                charts_container.append(row_table)
            
            layout["charts"].update(Panel(
                Group(*charts_container),
                title="[bold cyan]📈 Live Market Data[/bold cyan]",
                subtitle=f"[dim]{len(self.chart_grid.charts)} symbols │ Binance + yfinance[/dim]",
                box=ROUNDED,
                border_style="cyan"
            ))
        else:
            layout["charts"].update(Panel(
                Align.center(Text("\nNo charts displayed.\n\n"
                                 "Switch to Search mode: [TAB]\n"
                                 "Type a symbol (e.g., AAPL or BTCUSDT)\n"
                                 "Press [ENTER] to add\n",
                                 style="yellow", justify="center"), vertical="middle"),
                title="[bold cyan]📈 Live Market Data[/bold cyan]",
                box=ROUNDED,
                border_style="cyan"
            ))
        
        # === RIGHT SIDE: COPILOT CHAT ===
        layout["chat"].update(self.chat.render(show_last_n=20))
        
        return layout
    
    def render(self) -> Layout:
        """Render the unified dashboard - all components visible."""
        main_layout = Layout()
        
        main_layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1),
            Layout(name="footer", size=3)
        )
        
        # Header with live portfolio
        main_layout["header"].update(self._render_header())
        
        # Main body: charts + chat side-by-side
        main_layout["body"].update(self._render_main_body())
        
        # Footer with input
        main_layout["footer"].update(self._render_footer())
        
        return main_layout
    
    def run(self):
        """Run the unified dashboard."""
        self.running = True
        
        # Clear screen and hide cursor
        os.system('cls' if os.name == 'nt' else 'clear')
        sys.stdout.write("\033[?25l")
        
        # Start keyboard handler
        self.keyboard.start()
        
        try:
            with Live(
                self.render(),
                console=self.console,
                screen=True,
                refresh_per_second=4
            ) as live:
                while self.running:
                    # Process keyboard input
                    if not self.keyboard.process_input():
                        break
                    
                    # Update display
                    live.update(self.render())
                    
                    # Small sleep to prevent CPU spinning
                    time.sleep(0.05)
        
        except KeyboardInterrupt:
            pass
        
        finally:
            # Cleanup
            self.keyboard.stop()
            self.data_manager.stop_all()
            sys.stdout.write("\033[?25h")  # Show cursor
            print("\nGoodbye!")


def main():
    """Main entry point."""
    dashboard = Dashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
