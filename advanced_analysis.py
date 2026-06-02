"""
Advanced Technical Analysis Engine
====================================
Multi-timeframe analysis + Volume filter + Trend filter.
More accurate signals, fewer false positives.
"""

import numpy as np
from technical_analysis import calculate_ema, calculate_rsi, calculate_macd
from binance_api import get_klines
from config import (
    RSI_PERIOD, RSI_OVERSOLD, RSI_OVERBOUGHT,
    MACD_FAST, MACD_SLOW, MACD_SIGNAL,
    EMA_SHORT, EMA_LONG,
    TAKE_PROFIT_PERCENT, STOP_LOSS_PERCENT,
)


# === VOLUME FILTER ===

def check_volume_filter(volumes, min_multiplier=1.5):
    """
    Check if current volume is above average.
    Filters out low-volume (unreliable) signals.
    """
    if len(volumes) < 20:
        return True

    avg_volume = np.mean(volumes[-20:])
    current_volume = volumes[-1]

    return current_volume >= avg_volume * min_multiplier


# === BOLLINGER BANDS ===

def calculate_bollinger_bands(prices, period=20, std_dev=2):
    """
    Calculate Bollinger Bands.
    Returns: (upper_band, middle_band, lower_band, bandwidth)
    """
    prices = np.array(prices, dtype=float)

    if len(prices) < period:
        return None, None, None, None

    # Middle band = SMA
    middle = np.convolve(prices, np.ones(period)/period, mode='valid')

    # Standard deviation
    stds = np.array([np.std(prices[i:i+period]) for i in range(len(prices)-period+1)])

    upper = middle + (std_dev * stds)
    lower = middle - (std_dev * stds)

    # Bandwidth (how tight the bands are)
    bandwidth = ((upper[-1] - lower[-1]) / middle[-1]) * 100

    return upper, middle, lower, bandwidth


def get_bollinger_signal(prices):
    """
    Get Bollinger Bands signal.
    Returns: score (-1 to +1), reason string
    """
    upper, middle, lower, bandwidth = calculate_bollinger_bands(prices)

    if upper is None:
        return 0, None

    current_price = prices[-1]
    upper_val = upper[-1]
    lower_val = lower[-1]
    middle_val = middle[-1]

    # Price position relative to bands (0 = lower band, 1 = upper band)
    band_position = (current_price - lower_val) / (upper_val - lower_val) if (upper_val - lower_val) > 0 else 0.5

    buy_score = 0
    sell_score = 0
    reason = None

    # Price at or below lower band = BUY signal
    if band_position <= 0.05:
        buy_score = 1.5
        reason = "BB: Price at Lower Band (oversold)"
    elif band_position <= 0.2:
        buy_score = 0.75
        reason = "BB: Price near Lower Band"

    # Price at or above upper band = SELL signal
    elif band_position >= 0.95:
        sell_score = 1.5
        reason = "BB: Price at Upper Band (overbought)"
    elif band_position >= 0.8:
        sell_score = 0.75
        reason = "BB: Price near Upper Band"

    # Squeeze detection (bands very tight = big move coming)
    if bandwidth < 3:  # Very tight bands
        # Don't add score but note it
        if reason:
            reason += " [SQUEEZE]"

    return buy_score - sell_score, reason


# === FUNDING RATE ===

def get_funding_rate(symbol):
    """
    Get current funding rate from Binance Futures.
    Positive = longs pay shorts (too many longs)
    Negative = shorts pay longs (too many shorts)
    """
    import requests

    url = "https://fapi.binance.com/fapi/v1/fundingRate"
    params = {"symbol": symbol, "limit": 1}

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                return float(data[0]["fundingRate"])
    except:
        pass

    return None


def get_funding_signal(symbol):
    """
    Get trading signal from funding rate.
    Contrarian: go against the crowd.
    """
    rate = get_funding_rate(symbol)

    if rate is None:
        return 0, None

    buy_score = 0
    sell_score = 0
    reason = None

    # Very positive funding = too many longs = SHORT signal (contrarian)
    if rate >= 0.001:  # 0.1%+
        sell_score = 1.5
        reason = f"Funding: +{rate*100:.3f}% (crowd is LONG, contrarian SHORT)"
    elif rate >= 0.0005:  # 0.05%+
        sell_score = 0.5
        reason = f"Funding: +{rate*100:.3f}% (slightly long-heavy)"

    # Very negative funding = too many shorts = LONG signal (contrarian)
    elif rate <= -0.001:  # -0.1%
        buy_score = 1.5
        reason = f"Funding: {rate*100:.3f}% (crowd is SHORT, contrarian LONG)"
    elif rate <= -0.0005:  # -0.05%
        buy_score = 0.5
        reason = f"Funding: {rate*100:.3f}% (slightly short-heavy)"

    return buy_score - sell_score, reason


# === TREND FILTER ===

def get_trend_direction(prices, period=50):
    """
    Determine overall trend direction using EMA 50.
    Only allows signals in the direction of the trend.

    Returns:
        "UP" - uptrend (price above EMA50)
        "DOWN" - downtrend (price below EMA50)
        "NEUTRAL" - no clear trend
    """
    if len(prices) < period:
        return "NEUTRAL"

    ema50 = calculate_ema(prices, period)
    current_price = prices[-1]
    current_ema = ema50[-1]

    # Check if price is consistently above/below EMA
    prices_above = sum(1 for i in range(-10, 0) if prices[i] > ema50[i])

    if current_price > current_ema and prices_above >= 7:
        return "UP"
    elif current_price < current_ema and prices_above <= 3:
        return "DOWN"
    else:
        return "NEUTRAL"


# === MULTI-TIMEFRAME ANALYSIS ===

def analyze_timeframe(prices, volumes=None):
    """
    Analyze a single timeframe and return signal strength.
    Now includes Bollinger Bands.
    """
    if len(prices) < 50:
        return {"buy_score": 0, "sell_score": 0}

    current_price = prices[-1]

    # RSI
    rsi = calculate_rsi(prices)
    current_rsi = rsi[-1]

    # MACD
    macd_line, signal_line, histogram = calculate_macd(prices)
    current_macd = macd_line[-1]
    current_signal = signal_line[-1]
    prev_macd = macd_line[-2]
    prev_signal = signal_line[-2]

    # EMA
    ema_short = calculate_ema(prices, EMA_SHORT)
    ema_long = calculate_ema(prices, EMA_LONG)

    buy_score = 0
    sell_score = 0

    # RSI
    if current_rsi < RSI_OVERSOLD:
        buy_score += 1
    elif current_rsi < 40:
        buy_score += 0.5

    if current_rsi > RSI_OVERBOUGHT:
        sell_score += 1
    elif current_rsi > 60:
        sell_score += 0.5

    # MACD crossover
    if prev_macd <= prev_signal and current_macd > current_signal:
        buy_score += 1
    if prev_macd >= prev_signal and current_macd < current_signal:
        sell_score += 1

    # MACD histogram momentum
    if len(histogram) >= 3:
        if histogram[-1] > histogram[-2] > histogram[-3]:
            buy_score += 0.5
        if histogram[-1] < histogram[-2] < histogram[-3]:
            sell_score += 0.5

    # EMA crossover
    if ema_short[-2] <= ema_long[-2] and ema_short[-1] > ema_long[-1]:
        buy_score += 1
    if ema_short[-2] >= ema_long[-2] and ema_short[-1] < ema_long[-1]:
        sell_score += 1

    # Price above/below EMA
    if current_price > ema_short[-1] > ema_long[-1]:
        buy_score += 0.5
    if current_price < ema_short[-1] < ema_long[-1]:
        sell_score += 0.5

    # Bollinger Bands
    bb_signal, bb_reason = get_bollinger_signal(prices)
    if bb_signal > 0:
        buy_score += bb_signal
    elif bb_signal < 0:
        sell_score += abs(bb_signal)

    return {
        "buy_score": buy_score,
        "sell_score": sell_score,
        "rsi": current_rsi,
        "macd": current_macd,
        "signal_line": current_signal,
        "price": current_price,
        "bb_reason": bb_reason,
    }


def multi_timeframe_analyze(symbol):
    """
    Perform multi-timeframe analysis on a symbol.
    Combines 15m, 1h, and 4h timeframes for stronger signals.

    Scoring:
        - 4H (trend): weight 3x (determines direction)
        - 1H (signal): weight 2x (main signal)
        - 15m (entry): weight 1x (timing)

    Returns:
        Signal dict or None
    """
    # Fetch data for all timeframes
    data_15m = get_klines(symbol, "15m", limit=100)
    data_1h = get_klines(symbol, "1h", limit=100)
    data_4h = get_klines(symbol, "4h", limit=100)

    if not all([data_15m, data_1h, data_4h]):
        return None

    # Analyze each timeframe
    analysis_15m = analyze_timeframe(data_15m["prices"], data_15m["volumes"])
    analysis_1h = analyze_timeframe(data_1h["prices"], data_1h["volumes"])
    analysis_4h = analyze_timeframe(data_4h["prices"], data_4h["volumes"])

    # === VOLUME FILTER ===
    if not check_volume_filter(data_1h["volumes"]):
        return None  # Skip low volume coins

    # === TREND FILTER (4H determines allowed direction) ===
    trend = get_trend_direction(data_4h["prices"])

    # === FUNDING RATE (contrarian signal) ===
    funding_score, funding_reason = get_funding_signal(symbol)

    # === WEIGHTED SCORING ===
    # 4H weight: 3, 1H weight: 2, 15m weight: 1, Funding: 1.5
    total_buy_score = (
        analysis_4h["buy_score"] * 3 +
        analysis_1h["buy_score"] * 2 +
        analysis_15m["buy_score"] * 1 +
        (funding_score * 1.5 if funding_score > 0 else 0)
    )

    total_sell_score = (
        analysis_4h["sell_score"] * 3 +
        analysis_1h["sell_score"] * 2 +
        analysis_15m["sell_score"] * 1 +
        (abs(funding_score) * 1.5 if funding_score < 0 else 0)
    )

    # Minimum score threshold (out of max ~18)
    MIN_BUY_SCORE = 5.0
    MIN_SELL_SCORE = 5.0

    current_price = analysis_1h["price"]

    # === GENERATE SIGNAL ===
    # BUY signal: trend must be UP or NEUTRAL, score must be high enough
    if total_buy_score >= MIN_BUY_SCORE and total_buy_score > total_sell_score:
        if trend == "DOWN":
            return None  # Don't buy in downtrend

        # Calculate strength (1-3)
        if total_buy_score >= 9:
            strength = 3
        elif total_buy_score >= 7:
            strength = 2
        else:
            strength = 1

        take_profit = current_price * (1 + TAKE_PROFIT_PERCENT / 100)
        stop_loss = current_price * (1 - STOP_LOSS_PERCENT / 100)

        reasons = []
        if analysis_4h["buy_score"] >= 1.5:
            reasons.append("4H Bullish")
        if analysis_1h["buy_score"] >= 1.5:
            reasons.append("1H Bullish")
        if analysis_15m["buy_score"] >= 1:
            reasons.append("15m Entry Confirmed")
        if analysis_1h["rsi"] < 40:
            reasons.append(f"RSI Oversold ({analysis_1h['rsi']:.0f})")
        if analysis_1h.get("bb_reason"):
            reasons.append(analysis_1h["bb_reason"])
        if funding_reason and funding_score > 0:
            reasons.append(funding_reason)

        return {
            "type": "BUY",
            "price": current_price,
            "take_profit": take_profit,
            "stop_loss": stop_loss,
            "strength": strength,
            "reasons": reasons if reasons else ["Multi-TF Bullish Confluence"],
            "rsi": analysis_1h["rsi"],
            "macd": analysis_1h["macd"],
            "signal_line": analysis_1h["signal_line"],
            "scores": {
                "15m": analysis_15m["buy_score"],
                "1h": analysis_1h["buy_score"],
                "4h": analysis_4h["buy_score"],
                "funding": funding_score,
                "total": total_buy_score,
            },
            "trend": trend,
        }

    # SELL signal: trend must be DOWN or NEUTRAL
    elif total_sell_score >= MIN_SELL_SCORE and total_sell_score > total_buy_score:
        if trend == "UP":
            return None  # Don't sell in uptrend

        if total_sell_score >= 9:
            strength = 3
        elif total_sell_score >= 7:
            strength = 2
        else:
            strength = 1

        take_profit = current_price * (1 - TAKE_PROFIT_PERCENT / 100)
        stop_loss = current_price * (1 + STOP_LOSS_PERCENT / 100)

        reasons = []
        if analysis_4h["sell_score"] >= 1.5:
            reasons.append("4H Bearish")
        if analysis_1h["sell_score"] >= 1.5:
            reasons.append("1H Bearish")
        if analysis_15m["sell_score"] >= 1:
            reasons.append("15m Entry Confirmed")
        if analysis_1h["rsi"] > 60:
            reasons.append(f"RSI Overbought ({analysis_1h['rsi']:.0f})")
        if analysis_1h.get("bb_reason"):
            reasons.append(analysis_1h["bb_reason"])
        if funding_reason and funding_score < 0:
            reasons.append(funding_reason)

        return {
            "type": "SELL",
            "price": current_price,
            "take_profit": take_profit,
            "stop_loss": stop_loss,
            "strength": strength,
            "reasons": reasons if reasons else ["Multi-TF Bearish Confluence"],
            "rsi": analysis_1h["rsi"],
            "macd": analysis_1h["macd"],
            "signal_line": analysis_1h["signal_line"],
            "scores": {
                "15m": analysis_15m["sell_score"],
                "1h": analysis_1h["sell_score"],
                "4h": analysis_4h["sell_score"],
                "funding": funding_score,
                "total": total_sell_score,
            },
            "trend": trend,
        }

    return None
