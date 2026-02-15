"""
Data Fetching Layer - Binance and yfinance Integration
"""
import asyncio
import time
from collections import deque
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
import threading

import yfinance as yf
from binance.client import Client as BinanceClient
from binance import ThreadedWebsocketManager
import pandas as pd
import numpy as np


class DataFetcher:
    """Base class for data fetchers."""
    
    def __init__(self, symbol: str, interval: str = "1m", max_points: int = 120):
        self.symbol = symbol
        self.interval = interval
        self.max_points = max_points
        self.prices = deque(maxlen=max_points)
        self.times = deque(maxlen=max_points)
        self.volumes = deque(maxlen=max_points)
        self.callbacks: List[Callable] = []
        self._running = False
    
    def register_callback(self, callback: Callable):
        """Register a callback to be called when new data arrives."""
        self.callbacks.append(callback)
    
    def _notify_callbacks(self):
        """Notify all registered callbacks."""
        for callback in self.callbacks:
            try:
                callback(self.get_latest_data())
            except Exception as e:
                print(f"Error in callback: {e}")
    
    def get_latest_data(self) -> Dict[str, Any]:
        """Get the latest data point."""
        if not self.prices:
            return {}
        
        return {
            'symbol': self.symbol,
            'price': self.prices[-1],
            'time': self.times[-1],
            'volume': self.volumes[-1] if self.volumes else 0,
            'prices': list(self.prices),
            'times': list(self.times),
            'volumes': list(self.volumes),
        }
    
    def calculate_sma(self, period: int) -> List[Optional[float]]:
        """Calculate Simple Moving Average."""
        data_list = list(self.prices)
        if len(data_list) < period:
            return [None] * len(data_list)
        
        weights = np.ones(period) / period
        sma = np.convolve(data_list, weights, mode='valid')
        return [None] * (period - 1) + sma.tolist()
    
    def get_price_change(self) -> Dict[str, float]:
        """Calculate price change statistics."""
        if len(self.prices) < 2:
            return {'change': 0, 'change_pct': 0}
        
        first_price = self.prices[0]
        last_price = self.prices[-1]
        change = last_price - first_price
        change_pct = (change / first_price) * 100 if first_price != 0 else 0
        
        return {
            'change': change,
            'change_pct': change_pct,
            'high': max(self.prices),
            'low': min(self.prices),
        }
    
    def start(self):
        """Start fetching data."""
        raise NotImplementedError
    
    def stop(self):
        """Stop fetching data."""
        self._running = False


class BinanceFetcher(DataFetcher):
    """Fetch real-time data from Binance."""
    
    def __init__(self, symbol: str = "BTCUSDT", interval: str = "1m", max_points: int = 120):
        super().__init__(symbol, interval, max_points)
        self.client = BinanceClient()
        self.twm: Optional[ThreadedWebsocketManager] = None
        self._load_historical_data()
    
    def _load_historical_data(self):
        """Load historical data for initialization."""
        try:
            interval_mapping = {
                "1m": BinanceClient.KLINE_INTERVAL_1MINUTE,
                "5m": BinanceClient.KLINE_INTERVAL_5MINUTE,
                "15m": BinanceClient.KLINE_INTERVAL_15MINUTE,
                "1h": BinanceClient.KLINE_INTERVAL_1HOUR,
            }
            
            interval_key = interval_mapping.get(self.interval, BinanceClient.KLINE_INTERVAL_1MINUTE)
            klines = self.client.get_historical_klines(
                self.symbol,
                interval_key,
                f"{self.max_points} minutes ago UTC"
            )
            
            for k in klines:
                self.times.append(k[0])
                self.prices.append(float(k[4]))  # Close price
                self.volumes.append(float(k[5]))
            
            print(f"Loaded {len(self.prices)} historical data points for {self.symbol}")
        except Exception as e:
            print(f"Error loading historical data for {self.symbol}: {e}")
    
    def _handle_socket_message(self, msg):
        """Handle incoming WebSocket messages."""
        if msg['e'] == 'error':
            print(f"WebSocket error: {msg}")
            return
        
        kline = msg['k']
        current_close = float(kline['c'])
        current_volume = float(kline['v'])
        candle_start_time = kline['t']
        
        # Update or append data
        if not self.times or candle_start_time != self.times[-1]:
            self.times.append(candle_start_time)
            self.prices.append(current_close)
            self.volumes.append(current_volume)
        else:
            self.prices[-1] = current_close
            self.volumes[-1] = current_volume
        
        self._notify_callbacks()
    
    def start(self):
        """Start WebSocket connection."""
        self._running = True
        self.twm = ThreadedWebsocketManager()
        self.twm.start()
        
        interval_mapping = {
            "1m": BinanceClient.KLINE_INTERVAL_1MINUTE,
            "5m": BinanceClient.KLINE_INTERVAL_5MINUTE,
            "15m": BinanceClient.KLINE_INTERVAL_15MINUTE,
            "1h": BinanceClient.KLINE_INTERVAL_1HOUR,
        }
        interval_key = interval_mapping.get(self.interval, BinanceClient.KLINE_INTERVAL_1MINUTE)
        
        self.twm.start_kline_socket(
            callback=self._handle_socket_message,
            symbol=self.symbol,
            interval=interval_key
        )
        
        print(f"Started Binance stream for {self.symbol}")
    
    def stop(self):
        """Stop WebSocket connection."""
        super().stop()
        if self.twm:
            self.twm.stop()
            print(f"Stopped Binance stream for {self.symbol}")


class YFinanceFetcher(DataFetcher):
    """Fetch data from Yahoo Finance (polling-based)."""
    
    def __init__(self, symbol: str = "AAPL", interval: str = "1m", max_points: int = 120):
        super().__init__(symbol, interval, max_points)
        self.ticker = yf.Ticker(symbol)
        self._thread: Optional[threading.Thread] = None
        self._load_historical_data()
    
    def _load_historical_data(self):
        """Load historical data for initialization."""
        try:
            period_mapping = {
                "1m": "1d",
                "2m": "1d",
                "5m": "5d",
                "15m": "5d",
                "30m": "5d",
                "1h": "1mo",
            }
            
            period = period_mapping.get(self.interval, "1d")
            df = self.ticker.history(period=period, interval=self.interval)
            
            if not df.empty:
                # Get the last max_points
                df = df.tail(self.max_points)
                
                for idx, row in df.iterrows():
                    self.times.append(int(idx.timestamp() * 1000))
                    self.prices.append(float(row['Close']))
                    self.volumes.append(float(row['Volume']))
                
                print(f"Loaded {len(self.prices)} historical data points for {self.symbol}")
            else:
                print(f"No historical data available for {self.symbol}")
        except Exception as e:
            print(f"Error loading historical data for {self.symbol}: {e}")
    
    def _fetch_loop(self):
        """Continuously fetch data in background thread."""
        interval_seconds = {
            "1m": 60,
            "2m": 120,
            "5m": 300,
            "15m": 900,
            "30m": 1800,
            "1h": 3600,
        }
        
        sleep_time = interval_seconds.get(self.interval, 60)
        
        while self._running:
            try:
                # Fetch latest data
                df = self.ticker.history(period="1d", interval=self.interval)
                
                if not df.empty:
                    last_row = df.iloc[-1]
                    last_time = int(df.index[-1].timestamp() * 1000)
                    
                    # Update or append
                    if not self.times or last_time != self.times[-1]:
                        self.times.append(last_time)
                        self.prices.append(float(last_row['Close']))
                        self.volumes.append(float(last_row['Volume']))
                        self._notify_callbacks()
                
            except Exception as e:
                print(f"Error fetching data for {self.symbol}: {e}")
            
            time.sleep(sleep_time)
    
    def start(self):
        """Start background fetching thread."""
        self._running = True
        self._thread = threading.Thread(target=self._fetch_loop, daemon=True)
        self._thread.start()
        print(f"Started yfinance polling for {self.symbol}")
    
    def stop(self):
        """Stop background fetching thread."""
        super().stop()
        if self._thread:
            self._thread.join(timeout=2)
            print(f"Stopped yfinance polling for {self.symbol}")


class DataManager:
    """Manage multiple data fetchers."""
    
    def __init__(self):
        self.fetchers: Dict[str, DataFetcher] = {}
    
    def add_symbol(self, symbol: str, source: str = "yfinance", interval: str = "1m", max_points: int = 120) -> DataFetcher:
        """Add a symbol to track."""
        key = f"{symbol}_{source}"
        
        if key in self.fetchers:
            return self.fetchers[key]
        
        if source == "binance":
            fetcher = BinanceFetcher(symbol, interval, max_points)
        else:
            fetcher = YFinanceFetcher(symbol, interval, max_points)
        
        self.fetchers[key] = fetcher
        fetcher.start()
        
        return fetcher
    
    def remove_symbol(self, symbol: str, source: str = "yfinance"):
        """Remove a symbol from tracking."""
        key = f"{symbol}_{source}"
        
        if key in self.fetchers:
            self.fetchers[key].stop()
            del self.fetchers[key]
    
    def get_fetcher(self, symbol: str, source: str = "yfinance") -> Optional[DataFetcher]:
        """Get a fetcher by symbol and source."""
        key = f"{symbol}_{source}"
        return self.fetchers.get(key)
    
    def get_all_data(self) -> Dict[str, Dict[str, Any]]:
        """Get latest data from all fetchers."""
        return {key: fetcher.get_latest_data() for key, fetcher in self.fetchers.items()}
    
    def stop_all(self):
        """Stop all fetchers."""
        for fetcher in self.fetchers.values():
            fetcher.stop()
        self.fetchers.clear()


# Example usage
if __name__ == "__main__":
    manager = DataManager()
    
    # Add symbols
    btc_fetcher = manager.add_symbol("BTCUSDT", "binance", "1m")
    aapl_fetcher = manager.add_symbol("AAPL", "yfinance", "1m")
    
    # Register callbacks
    def on_data_update(data):
        print(f"{data['symbol']}: ${data['price']:.2f}")
    
    btc_fetcher.register_callback(on_data_update)
    aapl_fetcher.register_callback(on_data_update)
    
    # Run for a while
    try:
        time.sleep(300)  # 5 minutes
    except KeyboardInterrupt:
        pass
    finally:
        manager.stop_all()
