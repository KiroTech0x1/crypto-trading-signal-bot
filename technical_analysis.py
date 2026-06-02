"""
Technical Analysis Engine
==========================
Calculates RSI, MACD, EMA and generates trading signals.
"""

import numpy as np
from config import (
    RSI_PERIOD, RSI_OVERSOLD, RSI_OVERBOUGHT,
    MACD_FAST, MACD_SLOW, MACD_SIGNAL,
    EMA_SHORT, EMA_LONG,
    MIN_SIGNAL_STRENGTH,
    TAKE_PROFIT_PERCENT, STOP_LOSS_PERCENT,
)


def calculate_ema(prices, period):
    """Calculate Exponential Moving Average."""
    prices = np.array(prices, dtype=float)
    ema = np.zeros_like(prices)
    multiplier = 2 / (period + 1)
    ema[0] = prices[0]
    for i in range(1, len(prices)):
        ema[i] = (prices[i] - ema[i-1]) * multiplier + ema[i-1]
    return ema


def calculate_rsi(prices, period=RSI_PERIOD):
    """Calculate Relative Strength Index."""
    prices = np.array(prices, dtype=float)
    deltas = np.diff(prices)

    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)

    avg_gain = np.zeros_like(prices)
    avg_loss = np.zeros_like(prices)

    # First average
    avg_gain[period] = np.mean(gains[:period])
    avg_loss[period] = np.mean(losses[:period])

    # Smoothed averages
    for i in range(period + 1, len(prices)):
        avg_gain[i] = (avg_gain[i-1] * (period - 1) + gains[i-1]) / period
        avg_loss[i] = (avg_loss[i-1] * (period - 1) + losses[i-1]) / period

    rs = np.divide(avg_gain, avg_loss, out=np.zeros_like(avg_gain), where=avg_loss != 0)
    rsi = 100 - (100 / (1 + rs))

    return rsi


def calculate_macd(prices, fast=MACD_FAST, slow=MACD_SLOW, signal=MACD_SIGNAL):
    """Calculate MACD (Moving Average Convergence Divergence)."""
    prices = np.array(prices, dtype=float)

    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)

    macd_line = ema_fast - ema_slow
    signal_line = calculate_ema(macd_line, signal)
    histogram = macd_line - signal_line

    return macd_line, signal_line, histogram


def analyze(prices, volumes=None):
    """
    Analyze price data and generate trading signal.

    Args:
        prices: List of closing prices (most recent last)
        volumes: List of volumes (optional)

    Returns:
        dict with signal info or None if no signal
    """
    if len(prices) < 50:
        return None

    current_price = prices[-1]

    # Calculate indicators
    rsi = calculate_rsi(prices)
    current_rsi = rsi[-1]

    macd_line, signal_line, histogram = calculate_macd(prices)
    current_macd = macd_line[-1]
    current_signal = signal_line[-1]
    prev_macd = macd_line[-2]
    prev_signal = signal_line[-2]

    ema_short = calculate_ema(prices, EMA_SHORT)
    ema_long = calculate_ema(prices, EMA_LONG)

    # === BUY SIGNALS ===
    buy_signals = 0
    buy_reasons = []

    # RSI oversold
    if current_rsi < RSI_OVERSOLD:
        buy_signals += 1
        buy_reasons.append(f"RSI Oversold ({current_rsi:.1f})")

    # MACD bullish crossover
    if prev_macd <= prev_signal and current_macd > current_signal:
        buy_signals += 1
        buy_reasons.append("MACD Bullish Crossover")

    # EMA bullish crossover (short crosses above long)
    if ema_short[-2] <= ema_long[-2] and ema_short[-1] > ema_long[-1]:
        buy_signals += 1
        buy_reasons.append("EMA Bullish Crossover")

    # === SELL SIGNALS ===
    sell_signals = 0
    sell_reasons = []

    # RSI overbought
    if current_rsi > RSI_OVERBOUGHT:
        sell_signals += 1
        sell_reasons.append(f"RSI Overbought ({current_rsi:.1f})")

    # MACD bearish crossover
    if prev_macd >= prev_signal and current_macd < current_signal:
        sell_signals += 1
        sell_reasons.append("MACD Bearish Crossover")

    # EMA bearish crossover (short crosses below long)
    if ema_short[-2] >= ema_long[-2] and ema_short[-1] < ema_long[-1]:
        sell_signals += 1
        sell_reasons.append("EMA Bearish Crossover")

    # === GENERATE SIGNAL ===
    if buy_signals >= MIN_SIGNAL_STRENGTH:
        take_profit = current_price * (1 + TAKE_PROFIT_PERCENT / 100)
        stop_loss = current_price * (1 - STOP_LOSS_PERCENT / 100)

        return {
            "type": "BUY",
            "price": current_price,
            "take_profit": take_profit,
            "stop_loss": stop_loss,
            "strength": buy_signals,
            "reasons": buy_reasons,
            "rsi": current_rsi,
            "macd": current_macd,
            "signal_line": current_signal,
        }

    elif sell_signals >= MIN_SIGNAL_STRENGTH:
        take_profit = current_price * (1 - TAKE_PROFIT_PERCENT / 100)
        stop_loss = current_price * (1 + STOP_LOSS_PERCENT / 100)

        return {
            "type": "SELL",
            "price": current_price,
            "take_profit": take_profit,
            "stop_loss": stop_loss,
            "strength": sell_signals,
            "reasons": sell_reasons,
            "rsi": current_rsi,
            "macd": current_macd,
            "signal_line": current_signal,
        }

    return None
