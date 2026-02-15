"""
Portfolio Tracker - Real-time Portfolio Value Display
"""
import requests
from typing import Dict, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.box import ROUNDED


class PortfolioTracker:
    """Track and display portfolio value in real-time."""
    
    def __init__(
        self,
        mcp_base_url: str = "http://localhost",
        execution_port: int = 9003,
        portfolio_port: int = 9008,
        market_port: int = 9001
    ):
        self.mcp_base_url = mcp_base_url
        self.execution_port = execution_port
        self.portfolio_port = portfolio_port
        self.market_port = market_port
        
        self.holdings: Dict[str, any] = {}
        self.total_value: float = 0.0
        self.cash: float = 0.0
        self.total_cost: float = 0.0
        self.total_pnl: float = 0.0
        self.total_pnl_pct: float = 0.0
        
        # Cache for prices
        self.price_cache: Dict[str, float] = {}
    
    def _call_mcp(self, port: int, method: str, params: Dict = None) -> Dict:
        """Call an MCP server."""
        url = f"{self.mcp_base_url}:{port}/mcp"
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }
        
        try:
            response = requests.post(url, json=payload, timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_portfolio(self) -> Dict:
        """Get current portfolio from execution server."""
        response = self._call_mcp(self.execution_port, "tools/call", {
            "name": "get_portfolio",
            "arguments": {}
        })
        
        if "result" in response:
            return response["result"].get("content", [{}])[0].get("text", "{}")
        return "{}"
    
    def get_price(self, symbol: str) -> Optional[float]:
        """Get current price for a symbol."""
        # Check cache first
        if symbol in self.price_cache:
            return self.price_cache[symbol]
        
        response = self._call_mcp(self.market_port, "tools/call", {
            "name": "get_price",
            "arguments": {"symbol": symbol}
        })
        
        if "result" in response:
            content = response["result"].get("content", [{}])[0].get("text", "")
            try:
                import json
                data = json.loads(content)
                price = data.get("price", 0)
                self.price_cache[symbol] = price
                return price
            except:
                pass
        
        return None
    
    def update(self):
        """Update portfolio data."""
        try:
            import json
            portfolio_json = self.get_portfolio()
            portfolio_data = json.loads(portfolio_json) if isinstance(portfolio_json, str) else portfolio_data
            
            self.holdings = portfolio_data.get("positions", {})
            self.cash = portfolio_data.get("cash", 100000.0)
            
            # Calculate total value
            total_position_value = 0.0
            self.total_cost = 0.0
            
            for symbol, position in self.holdings.items():
                quantity = position.get("quantity", 0)
                avg_price = position.get("avg_price", 0)
                current_price = self.get_price(symbol)
                
                if current_price:
                    position_value = quantity * current_price
                    total_position_value += position_value
                    
                    # Store current values in position
                    position["current_price"] = current_price
                    position["market_value"] = position_value
                    position["cost_basis"] = quantity * avg_price
                    position["pnl"] = position_value - (quantity * avg_price)
                    position["pnl_pct"] = ((current_price - avg_price) / avg_price * 100) if avg_price > 0 else 0
                    
                    self.total_cost += quantity * avg_price
            
            self.total_value = self.cash + total_position_value
            self.total_pnl = self.total_value - (100000.0)  # Assuming starting capital
            self.total_pnl_pct = (self.total_pnl / 100000.0) * 100 if self.total_value > 0 else 0
            
        except Exception as e:
            print(f"Error updating portfolio: {e}")
    
    def render_summary(self) -> Panel:
        """Render portfolio summary panel."""
        # Create content
        content = Text()
        
        # Total Value
        content.append("Total Value: ", style="white")
        content.append(f"${self.total_value:,.2f}\n", style="bold white")
        
        # Cash
        content.append("Cash: ", style="white")
        content.append(f"${self.cash:,.2f}\n", style="cyan")
        
        # Positions Value
        position_value = self.total_value - self.cash
        content.append("Positions: ", style="white")
        content.append(f"${position_value:,.2f}\n\n", style="cyan")
        
        # P&L
        pnl_style = "bold green" if self.total_pnl >= 0 else "bold red"
        pnl_symbol = "▲" if self.total_pnl >= 0 else "▼"
        
        content.append("P&L: ", style="white")
        content.append(f"{pnl_symbol} ", style=pnl_style)
        content.append(f"${self.total_pnl:+,.2f} ", style=pnl_style)
        content.append(f"({self.total_pnl_pct:+.2f}%)", style=pnl_style)
        
        panel = Panel(
            content,
            title="[bold cyan]💼 Portfolio[/bold cyan]",
            box=ROUNDED,
            border_style="cyan"
        )
        
        return panel
    
    def render_positions(self) -> Panel:
        """Render detailed positions table."""
        if not self.holdings:
            return Panel(
                Text("No positions", style="dim"),
                title="[bold cyan]📊 Positions[/bold cyan]",
                box=ROUNDED,
                border_style="cyan"
            )
        
        # Create table
        table = Table(box=None, show_header=True, header_style="bold cyan")
        table.add_column("Symbol", style="cyan", no_wrap=True)
        table.add_column("Qty", justify="right")
        table.add_column("Avg Price", justify="right")
        table.add_column("Current", justify="right")
        table.add_column("Value", justify="right")
        table.add_column("P&L", justify="right")
        table.add_column("%", justify="right")
        
        for symbol, position in self.holdings.items():
            quantity = position.get("quantity", 0)
            avg_price = position.get("avg_price", 0)
            current_price = position.get("current_price", 0)
            market_value = position.get("market_value", 0)
            pnl = position.get("pnl", 0)
            pnl_pct = position.get("pnl_pct", 0)
            
            pnl_style = "green" if pnl >= 0 else "red"
            pnl_symbol = "▲" if pnl >= 0 else "▼"
            
            table.add_row(
                symbol,
                f"{quantity:.0f}",
                f"${avg_price:.2f}",
                f"${current_price:.2f}",
                f"${market_value:,.2f}",
                f"[{pnl_style}]{pnl_symbol} ${pnl:+,.2f}[/{pnl_style}]",
                f"[{pnl_style}]{pnl_pct:+.2f}%[/{pnl_style}]"
            )
        
        panel = Panel(
            table,
            title="[bold cyan]📊 Positions[/bold cyan]",
            box=ROUNDED,
            border_style="cyan"
        )
        
        return panel
    
    def render(self, show_positions: bool = True) -> List[Panel]:
        """Render portfolio panels."""
        panels = [self.render_summary()]
        
        if show_positions:
            panels.append(self.render_positions())
        
        return panels


# Example usage
if __name__ == "__main__":
    console = Console()
    
    tracker = PortfolioTracker()
    tracker.update()
    
    for panel in tracker.render():
        console.print(panel)
        console.print()
