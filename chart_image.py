"""
Chart Image Generator
======================
Gets TradingView chart screenshots for signals.
Uses TradingView's mini chart widget image API.
"""

import requests
import os
import time
from config import TEMP_DIR


def get_chart_image(symbol, interval="15", theme="dark"):
    """
    Get a chart image from TradingView.
    
    Args:
        symbol: Trading pair (e.g., "BTCUSDT")
        interval: Timeframe - "15" (15m), "60" (1h), "240" (4h), "D" (daily)
        theme: "dark" or "light"
    
    Returns:
        Path to saved image file, or None if failed
    """
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    # TradingView chart image URL
    # Format: BINANCE:BTCUSDT
    tv_symbol = f"BINANCE:{symbol}"
    
    # Using TradingView's mini chart image API
    url = (
        f"https://s3.tradingview.com/snapshots/chart/"
        f"?symbol={tv_symbol}&interval={interval}"
        f"&theme={theme}&style=1&timezone=Etc/UTC"
    )
    
    # Alternative: Use a screenshot service or generate locally
    # For now, use TradingView's widget screenshot endpoint
    chart_url = (
        f"https://www.tradingview.com/widgetembed/"
        f"?frameElementId=tradingview_chart"
        f"&symbol={tv_symbol}"
        f"&interval={interval}"
        f"&theme={theme}"
        f"&style=1"
        f"&timezone=Etc%2FUTC"
    )
    
    # Best approach: Use TradingView's chart image via their public API
    # This generates a static chart image
    image_url = (
        f"https://chart-api.tradingview.com/chart/"
        f"?symbol={tv_symbol}&interval={interval}"
    )
    
    # Most reliable: Use mini-chart-image from TradingView
    # Format that actually works:
    mini_chart_url = f"https://s.tradingview.com/embed-widget/mini-symbol-overview/?symbol={tv_symbol}"
    
    # Actually the most reliable free method:
    # Use Binance's own kline image or generate with matplotlib
    return generate_chart_locally(symbol, interval)


def generate_chart_locally(symbol, interval="15"):
    """
    Generate a candlestick chart image locally using matplotlib.
    This is the most reliable method - no external dependencies.
    """
    try:
        import numpy as np
        from PIL import Image, ImageDraw, ImageFont
        from binance_api import get_klines
        
        os.makedirs(TEMP_DIR, exist_ok=True)
        
        # Get candle data
        interval_map = {"15": "15m", "60": "1h", "240": "4h"}
        tf = interval_map.get(interval, "15m")
        
        data = get_klines(symbol, tf, limit=50)
        if not data:
            return None
        
        opens = data["opens"]
        highs = data["highs"]
        lows = data["lows"]
        closes = data["prices"]
        volumes = data["volumes"]
        
        # Image dimensions
        width = 800
        height = 450
        padding = 60
        
        # Create image
        img = Image.new("RGB", (width, height), color=(22, 27, 34))
        draw = ImageDraw.Draw(img)
        
        # Calculate price range
        all_prices = highs + lows
        price_min = min(lows)
        price_max = max(highs)
        price_range = price_max - price_min
        if price_range == 0:
            price_range = 1
        
        chart_width = width - padding * 2
        chart_height = height - padding * 2 - 40  # Leave room for volume
        
        candle_width = chart_width // len(opens) - 2
        if candle_width < 3:
            candle_width = 3
        
        def price_to_y(price):
            return int(padding + chart_height - ((price - price_min) / price_range * chart_height))
        
        # Draw grid lines
        for i in range(5):
            y = padding + int(chart_height * i / 4)
            draw.line([(padding, y), (width - padding, y)], fill=(40, 50, 60), width=1)
            price_label = price_max - (price_range * i / 4)
            draw.text((width - padding + 5, y - 8), f"{price_label:.4f}", fill=(140, 150, 160))
        
        # Draw candles
        for i in range(len(opens)):
            x = padding + i * (chart_width // len(opens))
            
            o = opens[i]
            h = highs[i]
            l = lows[i]
            c = closes[i]
            
            # Color
            if c >= o:
                color = (0, 188, 136)  # Green
                body_top = price_to_y(c)
                body_bottom = price_to_y(o)
            else:
                color = (234, 57, 67)  # Red
                body_top = price_to_y(o)
                body_bottom = price_to_y(c)
            
            # Wick
            wick_x = x + candle_width // 2
            draw.line([(wick_x, price_to_y(h)), (wick_x, price_to_y(l))], fill=color, width=1)
            
            # Body
            if body_bottom - body_top < 1:
                body_bottom = body_top + 1
            draw.rectangle([(x, body_top), (x + candle_width, body_bottom)], fill=color)
        
        # Draw volume bars at bottom
        vol_height = 35
        vol_top = height - padding - vol_height
        max_vol = max(volumes) if volumes else 1
        
        for i in range(len(volumes)):
            x = padding + i * (chart_width // len(volumes))
            v_height = int((volumes[i] / max_vol) * vol_height)
            color = (0, 120, 90) if closes[i] >= opens[i] else (150, 40, 40)
            draw.rectangle(
                [(x, vol_top + vol_height - v_height), (x + candle_width, vol_top + vol_height)],
                fill=color
            )
        
        # Header text
        coin_name = symbol.replace("USDT", "")
        current_price = closes[-1]
        change = ((closes[-1] - opens[0]) / opens[0]) * 100
        change_color = (0, 188, 136) if change >= 0 else (234, 57, 67)
        
        header_text = f"{coin_name} / TetherUS · {tf} · Binance"
        draw.text((padding, 10), header_text, fill=(200, 210, 220))
        
        price_text = f"{current_price:.5f}"
        draw.text((padding, 28), price_text, fill=change_color)
        
        change_text = f"  ({change:+.2f}%)"
        draw.text((padding + len(price_text) * 8, 28), change_text, fill=change_color)
        
        # Volume label
        draw.text((padding, vol_top - 15), f"Vol: {volumes[-1]:,.0f}", fill=(100, 110, 120))
        
        # Save
        image_path = os.path.join(TEMP_DIR, f"chart_{symbol}_{int(time.time())}.png")
        img.save(image_path, "PNG")
        
        return image_path
        
    except Exception as e:
        print(f"[CHART] Error generating chart for {symbol}: {e}")
        return None


def send_chart_with_signal(bot_token, chat_id, symbol, caption, reply_markup=None):
    """
    Send a chart image with signal caption to Telegram.
    
    Args:
        bot_token: Telegram bot token
        chat_id: Channel/chat ID
        symbol: Trading pair
        caption: Message text (HTML)
        reply_markup: Optional inline keyboard
    
    Returns:
        True if sent successfully
    """
    image_path = get_chart_image(symbol)
    
    if image_path and os.path.exists(image_path):
        url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
        
        payload = {
            "chat_id": chat_id,
            "caption": caption,
            "parse_mode": "HTML",
        }
        
        if reply_markup:
            import json
            payload["reply_markup"] = json.dumps(reply_markup)
        
        try:
            with open(image_path, "rb") as photo:
                response = requests.post(url, data=payload, files={"photo": photo}, timeout=30)
            
            # Cleanup
            os.remove(image_path)
            
            if response.status_code == 200:
                return True
            else:
                print(f"[CHART] Send failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"[CHART] Error sending chart: {e}")
            if os.path.exists(image_path):
                os.remove(image_path)
            return False
    else:
        return False
