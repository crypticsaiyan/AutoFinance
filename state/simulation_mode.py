"""
Simulation mode configuration for deterministic testing and demos.
"""

from typing import Dict, Any, List

SIMULATION_MODE: bool = False

def _generate_simulated_candles(base_price: float, num_candles: int) -> List[Dict[str, Any]]:
    """Generate simulated candle data for testing."""
    import random
    candles = []
    current_price = base_price
    
    for i in range(num_candles):
        volatility = random.uniform(-0.02, 0.02)
        open_price = current_price
        close_price = current_price * (1 + volatility)
        high_price = max(open_price, close_price) * (1 + abs(volatility) * 0.5)
        low_price = min(open_price, close_price) * (1 - abs(volatility) * 0.5)
        volume = random.uniform(1000, 2000)
        
        candles.append({
            "timestamp": f"2026-02-14T{10 + (i // 60):02d}:{i % 60:02d}:00Z",
            "open": round(open_price, 2),
            "high": round(high_price, 2),
            "low": round(low_price, 2),
            "close": round(close_price, 2),
            "volume": round(volume, 2)
        })
        
        current_price = close_price
    
    return candles


SIMULATED_VALUES: Dict[str, Dict[str, Any]] = {
    "BTCUSDT": {
        "price": 48000.0,
        "volatility": 0.05,
        "sentiment": -0.6,
        "candles": _generate_simulated_candles(47000.0, 100),
        "headlines": [
            "Bitcoin crashes amid regulatory concerns",
            "Major selloff in crypto markets continues",
            "Investors flee Bitcoin as losses mount"
        ]
    },
    "AAPL": {
        "price": 185.50,
        "volatility": 0.025,
        "sentiment": 0.4,
        "candles": _generate_simulated_candles(180.0, 100),
        "headlines": [
            "Apple reports record quarterly profits",
            "Strong iPhone sales drive growth",
            "Apple stock surges on positive earnings"
        ]
    },
    "ETHUSDT": {
        "price": 3200.0,
        "volatility": 0.045,
        "sentiment": 0.1,
        "candles": _generate_simulated_candles(3100.0, 100),
        "headlines": [
            "Ethereum upgrade scheduled for next month",
            "Mixed sentiment around ETH price action"
        ]
    }
}


def get_simulated_value(symbol: str, key: str) -> Any:
    """
    Retrieve simulated value for a given symbol and key.
    
    Args:
        symbol: Asset symbol (e.g., 'BTCUSDT', 'AAPL')
        key: Data key (e.g., 'price', 'volatility', 'sentiment')
    
    Returns:
        Simulated value or None if not found
    """
    return SIMULATED_VALUES.get(symbol, {}).get(key)
