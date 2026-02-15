"""
Search and Favorites Management System
"""
import json
import os
from typing import List, Dict, Set
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.box import ROUNDED


class FavoritesManager:
    """Manage favorite stocks/symbols."""
    
    def __init__(self, config_dir: str = None):
        if config_dir is None:
            config_dir = os.path.join(os.path.expanduser("~"), ".autofinance")
        
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        self.favorites_file = self.config_dir / "favorites.json"
        self.favorites: Set[str] = set()
        self.favorites_data: Dict[str, Dict] = {}
        
        self._load_favorites()
    
    def _load_favorites(self):
        """Load favorites from file."""
        if self.favorites_file.exists():
            try:
                with open(self.favorites_file, 'r') as f:
                    data = json.load(f)
                    self.favorites = set(data.get("symbols", []))
                    self.favorites_data = data.get("data", {})
            except Exception as e:
                print(f"Error loading favorites: {e}")
    
    def _save_favorites(self):
        """Save favorites to file."""
        try:
            with open(self.favorites_file, 'w') as f:
                json.dump({
                    "symbols": list(self.favorites),
                    "data": self.favorites_data
                }, f, indent=2)
        except Exception as e:
            print(f"Error saving favorites: {e}")
    
    def add_favorite(self, symbol: str, data: Dict = None):
        """Add a symbol to favorites."""
        symbol = symbol.upper()
        self.favorites.add(symbol)
        
        if data:
            self.favorites_data[symbol] = data
        elif symbol not in self.favorites_data:
            self.favorites_data[symbol] = {
                "added_at": self._get_timestamp(),
                "source": "yfinance"
            }
        
        self._save_favorites()
    
    def remove_favorite(self, symbol: str):
        """Remove a symbol from favorites."""
        symbol = symbol.upper()
        self.favorites.discard(symbol)
        self.favorites_data.pop(symbol, None)
        self._save_favorites()
    
    def is_favorite(self, symbol: str) -> bool:
        """Check if a symbol is in favorites."""
        return symbol.upper() in self.favorites
    
    def get_favorites(self) -> List[str]:
        """Get list of favorite symbols."""
        return sorted(list(self.favorites))
    
    def get_favorite_data(self, symbol: str) -> Dict:
        """Get data for a favorite symbol."""
        return self.favorites_data.get(symbol.upper(), {})
    
    @staticmethod
    def _get_timestamp():
        from datetime import datetime
        return datetime.now().isoformat()


class SymbolSearch:
    """Search for stock symbols."""
    
    # Popular symbols by category
    PREDEFINED_SYMBOLS = {
        "Tech Giants": ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA"],
        "Crypto": ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT"],
        "Finance": ["JPM", "BAC", "WFC", "GS", "MS", "C"],
        "Energy": ["XOM", "CVX", "COP", "SLB", "OXY"],
        "Healthcare": ["JNJ", "UNH", "PFE", "ABBV", "TMO"],
        "Consumer": ["WMT", "HD", "MCD", "NKE", "SBUX"],
        "Indices": ["SPY", "QQQ", "DIA", "IWM"],
    }
    
    def __init__(self):
        self.all_symbols = []
        for category, symbols in self.PREDEFINED_SYMBOLS.items():
            self.all_symbols.extend(symbols)
    
    def search(self, query: str, limit: int = 10) -> List[Dict[str, str]]:
        """Search for symbols matching query."""
        query = query.upper().strip()
        
        if not query:
            return []
        
        results = []
        
        # Exact match
        if query in self.all_symbols:
            results.append({
                "symbol": query,
                "name": self._get_name(query),
                "category": self._get_category(query),
                "match_type": "exact"
            })
        
        # Prefix match
        for symbol in self.all_symbols:
            if symbol.startswith(query) and symbol != query:
                results.append({
                    "symbol": symbol,
                    "name": self._get_name(symbol),
                    "category": self._get_category(symbol),
                    "match_type": "prefix"
                })
        
        # Contains match
        for symbol in self.all_symbols:
            if query in symbol and not symbol.startswith(query):
                results.append({
                    "symbol": symbol,
                    "name": self._get_name(symbol),
                    "category": self._get_category(symbol),
                    "match_type": "contains"
                })
        
        return results[:limit]
    
    def _get_category(self, symbol: str) -> str:
        """Get category for a symbol."""
        for category, symbols in self.PREDEFINED_SYMBOLS.items():
            if symbol in symbols:
                return category
        return "Other"
    
    def _get_name(self, symbol: str) -> str:
        """Get name for a symbol (placeholder)."""
        # In a real implementation, this would fetch from a database or API
        names = {
            "AAPL": "Apple Inc.",
            "MSFT": "Microsoft Corporation",
            "GOOGL": "Alphabet Inc.",
            "AMZN": "Amazon.com Inc.",
            "META": "Meta Platforms Inc.",
            "NVDA": "NVIDIA Corporation",
            "TSLA": "Tesla Inc.",
            "BTCUSDT": "Bitcoin/USDT",
            "ETHUSDT": "Ethereum/USDT",
            "SPY": "S&P 500 ETF",
            "QQQ": "NASDAQ-100 ETF",
        }
        return names.get(symbol, symbol)
    
    def get_categories(self) -> List[str]:
        """Get list of available categories."""
        return list(self.PREDEFINED_SYMBOLS.keys())
    
    def get_symbols_by_category(self, category: str) -> List[str]:
        """Get symbols for a specific category."""
        return self.PREDEFINED_SYMBOLS.get(category, [])


class SearchInterface:
    """Interactive search interface."""
    
    def __init__(self, favorites_manager: FavoritesManager = None):
        self.search = SymbolSearch()
        self.favorites = favorites_manager or FavoritesManager()
        self.console = Console()
    
    def render_search_results(self, query: str, results: List[Dict]) -> Panel:
        """Render search results as a panel."""
        if not results:
            content = Text(f"No results found for: {query}", style="yellow")
        else:
            table = Table(box=None, show_header=True, header_style="bold cyan")
            table.add_column("Symbol", style="cyan", no_wrap=True)
            table.add_column("Name", style="white")
            table.add_column("Category", style="magenta")
            table.add_column("Favorite", style="yellow")
            
            for result in results:
                symbol = result["symbol"]
                is_fav = "★" if self.favorites.is_favorite(symbol) else "☆"
                
                table.add_row(
                    symbol,
                    result["name"],
                    result["category"],
                    is_fav
                )
            
            content = table
        
        panel = Panel(
            content,
            title=f"[bold cyan]🔍 Search: {query}[/bold cyan]",
            box=ROUNDED,
            border_style="cyan"
        )
        
        return panel
    
    def render_favorites(self) -> Panel:
        """Render favorites list."""
        favorites_list = self.favorites.get_favorites()
        
        if not favorites_list:
            content = Text("No favorites yet. Search and add symbols!", style="dim")
        else:
            table = Table(box=None, show_header=True, header_style="bold yellow")
            table.add_column("#", style="dim", width=3)
            table.add_column("Symbol", style="yellow", no_wrap=True)
            table.add_column("Source", style="cyan")
            table.add_column("Added", style="dim")
            
            for i, symbol in enumerate(favorites_list, 1):
                data = self.favorites.get_favorite_data(symbol)
                source = data.get("source", "yfinance")
                added_at = data.get("added_at", "")
                
                # Format timestamp
                if added_at:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(added_at)
                        added_str = dt.strftime("%m/%d %H:%M")
                    except:
                        added_str = ""
                else:
                    added_str = ""
                
                table.add_row(
                    str(i),
                    symbol,
                    source,
                    added_str
                )
            
            content = table
        
        panel = Panel(
            content,
            title="[bold yellow]★ Favorites[/bold yellow]",
            subtitle=f"[dim]{len(favorites_list)} symbols[/dim]",
            box=ROUNDED,
            border_style="yellow"
        )
        
        return panel
    
    def render_categories(self) -> Panel:
        """Render category browser."""
        categories = self.search.get_categories()
        
        table = Table(box=None, show_header=True, header_style="bold magenta")
        table.add_column("Category", style="magenta")
        table.add_column("Symbols", style="cyan")
        
        for category in categories:
            symbols = self.search.get_symbols_by_category(category)
            symbols_str = ", ".join(symbols[:5])
            if len(symbols) > 5:
                symbols_str += f" +{len(symbols) - 5} more"
            
            table.add_row(category, symbols_str)
        
        panel = Panel(
            table,
            title="[bold magenta]📁 Categories[/bold magenta]",
            box=ROUNDED,
            border_style="magenta"
        )
        
        return panel


# Example usage
if __name__ == "__main__":
    console = Console()
    
    # Create search interface
    interface = SearchInterface()
    
    # Test search
    query = "BTC"
    results = interface.search.search(query)
    console.print(interface.render_search_results(query, results))
    console.print()
    
    # Add some favorites
    interface.favorites.add_favorite("AAPL", {"source": "yfinance"})
    interface.favorites.add_favorite("BTCUSDT", {"source": "binance"})
    
    # Render favorites
    console.print(interface.render_favorites())
    console.print()
    
    # Render categories
    console.print(interface.render_categories())
