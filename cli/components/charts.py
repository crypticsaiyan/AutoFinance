"""
Live Chart Component using Braille Dots (plotille)
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
import plotille
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.box import ROUNDED


class LiveChart:
    """Render live price charts with technical indicators using braille dots."""
    
    def __init__(
        self,
        symbol: str,
        width: int = 60,
        height: int = 15,
        fast_period: int = 9,
        slow_period: int = 21
    ):
        self.symbol = symbol
        self.width = width
        self.height = height
        self.fast_period = fast_period
        self.slow_period = slow_period
        
        self.prices: List[float] = []
        self.times: List[int] = []
        self.volumes: List[float] = []
    
    def update_data(self, data: Dict[str, Any]):
        """Update chart with new data."""
        self.prices = data.get('prices', [])
        self.times = data.get('times', [])
        self.volumes = data.get('volumes', [])
    
    def _calculate_sma(self, data: List[float], period: int) -> List[Optional[float]]:
        """Calculate Simple Moving Average."""
        if len(data) < period:
            return [None] * len(data)
        
        sma = []
        for i in range(len(data)):
            if i < period - 1:
                sma.append(None)
            else:
                sma.append(sum(data[i - period + 1:i + 1]) / period)
        return sma
    
    def _get_signal(self, sma_fast: List[Optional[float]], sma_slow: List[Optional[float]]) -> tuple:
        """Determine trading signal."""
        if len(sma_fast) < 2 or len(sma_slow) < 2:
            return "NEUTRAL", (255, 255, 255)
        
        current_fast = sma_fast[-1]
        current_slow = sma_slow[-1]
        prev_fast = sma_fast[-2]
        prev_slow = sma_slow[-2]
        
        if current_fast is None or current_slow is None:
            return "NEUTRAL", (255, 255, 255)
        
        if prev_fast is None or prev_slow is None:
            return "NEUTRAL", (255, 255, 255)
        
        if current_fast > current_slow:
            if prev_fast <= prev_slow:
                return "BULLISH (Golden Cross)", (0, 255, 0)
            return "HOLD BUY", (0, 255, 0)
        else:
            if prev_fast >= prev_slow:
                return "BEARISH (Death Cross)", (255, 0, 0)
            return "HOLD SELL", (255, 0, 0)
    
    def render(self) -> Panel:
        """Render the chart as a Rich Panel."""
        if len(self.prices) < self.slow_period:
            return Panel(
                Text("Loading data...", style="yellow"),
                title=f"[bold cyan]{self.symbol}[/bold cyan]",
                box=ROUNDED
            )
        
        # Prepare data
        x_axis = [datetime.fromtimestamp(t / 1000.0) for t in self.times]
        y_prices = self.prices
        
        # Calculate SMAs
        sma_fast = self._calculate_sma(y_prices, self.fast_period)
        sma_slow = self._calculate_sma(y_prices, self.slow_period)
        
        # Get signal
        signal, sig_color = self._get_signal(sma_fast, sma_slow)
        
        # Create figure
        fig = plotille.Figure()
        fig.width = self.width
        fig.height = self.height
        fig.color_mode = "rgb"
        
        # Set limits with padding
        p_min, p_max = min(y_prices), max(y_prices)
        padding = (p_max - p_min) * 0.1
        fig.set_y_limits(min_=p_min - padding, max_=p_max + padding)
        fig.set_x_limits(min_=x_axis[0], max_=x_axis[-1])
        
        # Plot price line (dimmed)
        fig.plot(x_axis, y_prices, lc=(100, 100, 100), label="Price")
        
        # Plot SMAs
        fast_plot_x = [x_axis[i] for i, val in enumerate(sma_fast) if val is not None]
        fast_plot_y = [val for val in sma_fast if val is not None]
        if fast_plot_x and fast_plot_y:
            fig.plot(fast_plot_x, fast_plot_y, lc=(0, 255, 255), label=f"SMA{self.fast_period}")
        
        slow_plot_x = [x_axis[i] for i, val in enumerate(sma_slow) if val is not None]
        slow_plot_y = [val for val in sma_slow if val is not None]
        if slow_plot_x and slow_plot_y:
            fig.plot(slow_plot_x, slow_plot_y, lc=(255, 165, 0), label=f"SMA{self.slow_period}")
        
        # Render chart
        chart_str = fig.show(legend=True)
        
        # Calculate price change
        price_change = y_prices[-1] - y_prices[0]
        price_change_pct = (price_change / y_prices[0]) * 100 if y_prices[0] != 0 else 0
        
        change_color = "green" if price_change >= 0 else "red"
        change_symbol = "▲" if price_change >= 0 else "▼"
        
        # Create info text
        info = Text()
        info.append(f"Price: ", style="white")
        info.append(f"${y_prices[-1]:.2f} ", style="bold white")
        info.append(f"{change_symbol} ", style=change_color)
        info.append(f"{price_change:+.2f} ({price_change_pct:+.2f}%)", style=change_color)
        info.append(f"\nSignal: ", style="white")
        
        # Add colored signal
        signal_style = "bold green" if "BULLISH" in signal or "BUY" in signal else "bold red" if "BEARISH" in signal or "SELL" in signal else "yellow"
        info.append(signal, style=signal_style)
        
        # Combine chart and info
        content = Text(chart_str + "\n") + info
        
        # Create panel
        panel = Panel(
            content,
            title=f"[bold cyan]{self.symbol}[/bold cyan]",
            box=ROUNDED,
            border_style="cyan"
        )
        
        return panel


class ChartGrid:
    """Manage a grid of multiple charts."""
    
    def __init__(self, columns: int = 2, chart_width: int = 60, chart_height: int = 15):
        self.columns = columns
        self.chart_width = chart_width
        self.chart_height = chart_height
        self.charts: Dict[str, LiveChart] = {}
    
    def add_chart(self, symbol: str, fast_period: int = 9, slow_period: int = 21):
        """Add a chart for a symbol."""
        if symbol not in self.charts:
            self.charts[symbol] = LiveChart(
                symbol,
                width=self.chart_width,
                height=self.chart_height,
                fast_period=fast_period,
                slow_period=slow_period
            )
    
    def remove_chart(self, symbol: str):
        """Remove a chart."""
        if symbol in self.charts:
            del self.charts[symbol]
    
    def update_chart(self, symbol: str, data: Dict[str, Any]):
        """Update a chart with new data."""
        if symbol in self.charts:
            self.charts[symbol].update_data(data)
    
    def render(self) -> List[List[Panel]]:
        """Render charts as a 2D grid."""
        chart_panels = [chart.render() for chart in self.charts.values()]
        
        # Arrange in grid
        grid = []
        for i in range(0, len(chart_panels), self.columns):
            row = chart_panels[i:i + self.columns]
            grid.append(row)
        
        return grid
    
    def get_chart(self, symbol: str) -> Optional[LiveChart]:
        """Get a specific chart."""
        return self.charts.get(symbol)


# Example usage
if __name__ == "__main__":
    import time
    from rich.console import Console
    from rich.layout import Layout
    from rich.live import Live
    
    console = Console()
    
    # Create chart grid
    grid = ChartGrid(columns=2, chart_width=60, chart_height=12)
    
    # Add charts
    grid.add_chart("AAPL")
    grid.add_chart("MSFT")
    grid.add_chart("GOOGL")
    grid.add_chart("TSLA")
    
    # Simulate data updates
    import random
    
    def generate_fake_data(symbol: str, count: int = 120):
        base_price = random.uniform(100, 500)
        prices = [base_price + random.uniform(-10, 10) for _ in range(count)]
        times = [int(time.time() * 1000) - (count - i) * 60000 for i in range(count)]
        return {
            'symbol': symbol,
            'prices': prices,
            'times': times,
            'volumes': [random.uniform(1000, 10000) for _ in range(count)]
        }
    
    # Update with fake data
    for symbol in ["AAPL", "MSFT", "GOOGL", "TSLA"]:
        grid.update_chart(symbol, generate_fake_data(symbol))
    
    # Render
    chart_rows = grid.render()
    for row in chart_rows:
        for panel in row:
            console.print(panel)
        console.print()
