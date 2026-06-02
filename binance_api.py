"""
Binance API Client
===================
Fetches price data from Binance PUBLIC API.
NO API KEY NEEDED - completely free and open.
"""

import time
import requests
from config import TIMEFRAME


BASE_URL = "https://api.binance.com"

# Timeframe to milliseconds mapping
TIMEFRAME_MS = {
    "1m": 60000,
    "5m": 300000,
    "15m": 900000,
    "30m": 1800000,
    "1h": 3600000,
    "4h": 14400000,
    "1d": 86400000,
}


def get_klines(symbol, interval=TIMEFRAME, limit=100):
    """
    Get candlestick/kline data from Binance.

    Returns:
        dict with 'prices' (close prices), 'volumes', 'highs', 'lows', 'opens'
    """
    url = f"{BASE_URL}/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        prices = [float(candle[4]) for candle in data]      # Close price
        volumes = [float(candle[5]) for candle in data]     # Volume
        highs = [float(candle[2]) for candle in data]       # High
        lows = [float(candle[3]) for candle in data]        # Low
        opens = [float(candle[1]) for candle in data]       # Open
        timestamps = [int(candle[0]) for candle in data]    # Open time

        return {
            "prices": prices,
            "volumes": volumes,
            "highs": highs,
            "lows": lows,
            "opens": opens,
            "timestamps": timestamps,
            "symbol": symbol,
        }

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to fetch data for {symbol}: {e}")
        return None


def get_current_price(symbol):
    """Get current price for a symbol."""
    url = f"{BASE_URL}/api/v3/ticker/price"
    params = {"symbol": symbol}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return float(data["price"])
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to get price for {symbol}: {e}")
        return None


def get_24h_change(symbol):
    """Get 24h price change percentage."""
    url = f"{BASE_URL}/api/v3/ticker/24hr"
    params = {"symbol": symbol}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {
            "change_percent": float(data["priceChangePercent"]),
            "volume": float(data["volume"]),
            "high": float(data["highPrice"]),
            "low": float(data["lowPrice"]),
        }
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to get 24h data for {symbol}: {e}")
        return None


def test_connection():
    """Test if Binance API is reachable."""
    url = f"{BASE_URL}/api/v3/ping"
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except:
        return False
