"""
Telegram Bot - Signal Sender
==============================
Sends signals to both free and premium channels.
"""

import asyncio
import time
import requests
from datetime import datetime
from config import (
    TELEGRAM_BOT_TOKEN,
    PREMIUM_CHANNEL_ID,
    FREE_CHANNEL_ID,
    FREE_CHANNEL_DELAY,
    BOT_NAME,
)


# Queue for delayed free channel messages
delayed_messages = []


def send_message(chat_id, text, parse_mode="HTML"):
    """Send a message to a Telegram chat/channel."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            return True
        else:
            print(f"[ERROR] Telegram send failed: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Telegram error: {e}")
        return False


def format_signal_message(signal_data, pair):
    """Format a trading signal for PREMIUM channel (full details, like competitors)."""
    signal_type = signal_data["type"]
    price = signal_data["price"]
    take_profit = signal_data["take_profit"]
    stop_loss = signal_data["stop_loss"]
    strength = signal_data["strength"]

    # Dynamic leverage based on signal strength
    if strength >= 3:
        leverage = "20x"
    elif strength >= 2:
        leverage = "10x"
    else:
        leverage = "5x"

    # Direction & targets
    if signal_type == "BUY":
        direction = "Long ğŸŸ¢"
        tp1 = price * 1.015
        tp2 = price * 1.03
        tp3 = price * 1.05
    else:
        direction = "Short ğŸ”´"
        tp1 = price * 0.985
        tp2 = price * 0.97
        tp3 = price * 0.95

    coin_name = pair.replace("USDT", "")
    timestamp = datetime.now().strftime("%H:%M:%S UTC")

    message = f"""ğŸ“Š <b>{BOT_NAME}</b>
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
â”‚ <b>{BOT_NAME}</b>
â”‚ #{coin_name}/USDT - {direction} Entry: ...
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

#{coin_name}/USDT
Direction: <b>{direction}</b>
Entry: <b>${price:,.5f}</b>
Stop Loss: <b>${stop_loss:,.5f}</b>

Targets:
ğŸ¯ 1: <b>${tp1:,.5f}</b>
ğŸ¯ 2: <b>${tp2:,.5f}</b>
ğŸ¯ 3: <b>${tp3:,.5f}</b>

Leverage: <b>{leverage}</b>
Signal Strength: {'ğŸŸ¢' * strength}{'âšª' * (3 - strength)}

â° {timestamp}"""

    return message


def format_signal_message_free(signal_data, pair):
    """Format signal for FREE channel (details hidden like competitors)."""
    signal_type = signal_data["type"]

    coin_name = pair.replace("USDT", "")
    timestamp = datetime.now().strftime("%H:%M UTC")

    message = f"""ğŸ“Š <b>{BOT_NAME}</b>
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
â”‚ <b>{BOT_NAME}</b>
â”‚ #{coin_name}/USDT - Direction: ğŸ”’ Entry: ...
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

#{coin_name}/USDT
Direction: ğŸ”’
Entry: ğŸ”’
Stop Loss: ğŸ”’

Target: ğŸ”’
Leverage: xğŸ”’

<i>Details Available on VIP Channel</i>"""

    return message


def format_target_hit_message(pair, target_num, profit_percent, duration_str):
    """Format target hit update message."""
    coin_name = pair.replace("USDT", "")

    if target_num == 3:
        # All targets achieved
        message = f"""ğŸ“Š <b>{BOT_NAME}</b>
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
â”‚ <b>{BOT_NAME}</b>
â”‚ #{coin_name}/USDT - Entry: ...
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

#{coin_name}/USDT All targets achieved ğŸ˜

Profit: <b>{profit_percent:.4f}%</b> ğŸ“ˆ
in: {duration_str} â°"""
    else:
        message = f"""ğŸ“Š <b>{BOT_NAME}</b>
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
â”‚ <b>{BOT_NAME}</b>
â”‚ #{coin_name}/USDT Direction: ğŸ”’ Entry: ...
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

#{coin_name}/USDT

Target Tuch {target_num} âœ…

Profit: <b>{profit_percent:.4f}%</b> ğŸ“ˆ
in: {duration_str} â°"""

    return message


def format_signal_result_free(pair, signal_type, entry_price, exit_price, profit_percent, duration_str, targets_hit, status):
    """Format completed signal result for FREE channel (fully visible - proof of profit)."""
    coin_name = pair.replace("USDT", "")

    if signal_type == "BUY":
        direction = "Long ğŸŸ¢"
    else:
        direction = "Short ğŸ”´"

    if status == "WIN":
        status_emoji = "âœ…"
        status_text = "All targets achieved ğŸ˜" if targets_hit >= 3 else f"Target {targets_hit} âœ…"
        profit_emoji = "ğŸ“ˆ"
    else:
        status_emoji = "âŒ"
        status_text = "Stop Loss Hit"
        profit_emoji = "ğŸ“‰"

    # Calculate targets for display
    if signal_type == "BUY":
        tp1 = entry_price * 1.015
        tp2 = entry_price * 1.03
        tp3 = entry_price * 1.05
    else:
        tp1 = entry_price * 0.985
        tp2 = entry_price * 0.97
        tp3 = entry_price * 0.95

    # Target status icons
    t1_icon = "âœ…" if targets_hit >= 1 else "â¬œ"
    t2_icon = "âœ…" if targets_hit >= 2 else "â¬œ"
    t3_icon = "âœ…" if targets_hit >= 3 else "â¬œ"

    message = f"""ğŸ“Š <b>{BOT_NAME} - Signal Result</b>
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
â”‚ <b>{BOT_NAME}</b>
â”‚ #{coin_name}/USDT - {direction}
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

{status_emoji} <b>{status_text}</b>

#{coin_name}/USDT
Direction: <b>{direction}</b>
Entry: <b>${entry_price:,.5f}</b>

Targets:
{t1_icon} 1: ${tp1:,.5f}
{t2_icon} 2: ${tp2:,.5f}
{t3_icon} 3: ${tp3:,.5f}

Profit: <b>{profit_percent:+.4f}%</b> {profit_emoji}
in: {duration_str} â°

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ğŸ’ <i>Get signals BEFORE they happen!</i>"""

    return message


def send_result_to_free(pair, signal_type, entry_price, exit_price, profit_percent, duration_str, targets_hit, status):
    """Send completed signal result to free channel with Buy VIP button."""
    message = format_signal_result_free(
        pair, signal_type, entry_price, exit_price,
        profit_percent, duration_str, targets_hit, status
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": FREE_CHANNEL_ID,
        "text": message,
        "parse_mode": "HTML",
        "reply_markup": {
            "inline_keyboard": [
                [{"text": "ğŸ›’ Buy VIP - Get Signals Early!", "url": "https://t.me/YOUR_BOT_USERNAME?start=buyvip"}]
            ]
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"[âœ…] Signal result sent to FREE channel: {pair} {status}")
            return True
    except Exception as e:
        print(f"[ERROR] Failed to send result to free: {e}")
    return False


def format_daily_profit_message(profits):
    """Format pinned message showing 24h profits."""
    lines = []
    for item in profits:
        emoji = "ğŸŸ¢" if item["profit"] > 0 else "ğŸš«"
        lines.append(f"<code>{item['pair']:12s} : {item['profit']:+.2f}%</code> {emoji}")

    profit_text = "\n".join(lines)

    message = f"""ğŸ“ˆ <b>VIP Channel's Profit in the last 24 hours</b>

<code>{'â”€' * 30}</code>
{profit_text}
<code>{'â”€' * 30}</code>

ğŸ¤– {BOT_NAME} | Updated every 24h"""

    return message


def send_signal_to_premium(signal_data, pair):
    """Send signal immediately to premium channel (full details + chart)."""
    message = format_signal_message(signal_data, pair)
    
    # Try to send with chart image
    try:
        from chart_image import send_chart_with_signal
        sent = send_chart_with_signal(
            TELEGRAM_BOT_TOKEN, PREMIUM_CHANNEL_ID, pair, message
        )
        if sent:
            print(f"[âœ…] Signal + chart sent to PREMIUM: {pair} {signal_data['type']}")
            return True
    except Exception as e:
        print(f"[âš ï¸] Chart failed, sending text only: {e}")
    
    # Fallback: send text only
    success = send_message(PREMIUM_CHANNEL_ID, message)
    if success:
        print(f"[âœ…] Signal sent to PREMIUM (no chart): {pair} {signal_data['type']}")
    return success


def queue_signal_for_free(signal_data, pair):
    """Queue signal for delayed sending to free channel (details hidden + chart)."""
    message = format_signal_message_free(signal_data, pair)
    send_time = time.time() + FREE_CHANNEL_DELAY

    delayed_messages.append({
        "message": message,
        "send_time": send_time,
        "pair": pair,
        "type": signal_data["type"],
    })
    print(f"[â³] Signal queued for FREE channel (delay: {FREE_CHANNEL_DELAY}s): {pair}")


def process_delayed_messages():
    """Check and send any delayed messages that are ready."""
    current_time = time.time()
    sent_indices = []

    for i, msg in enumerate(delayed_messages):
        if current_time >= msg["send_time"]:
            # Try to send with chart
            try:
                from chart_image import send_chart_with_signal
                reply_markup = {
                    "inline_keyboard": [
                        [{"text": "ğŸ›’ Buy VIP Subscription", "url": "https://t.me/YOUR_BOT_USERNAME?start=buyvip"}]
                    ]
                }
                sent = send_chart_with_signal(
                    TELEGRAM_BOT_TOKEN, FREE_CHANNEL_ID, msg["pair"],
                    msg["message"], reply_markup
                )
                if sent:
                    print(f"[âœ…] Signal + chart sent to FREE: {msg['pair']}")
                    sent_indices.append(i)
                    continue
            except:
                pass

            # Fallback: text only with button
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": FREE_CHANNEL_ID,
                "text": msg["message"],
                "parse_mode": "HTML",
                "reply_markup": {
                    "inline_keyboard": [
                        [{"text": "ğŸ›’ Buy VIP Subscription", "url": "https://t.me/YOUR_BOT_USERNAME?start=buyvip"}]
                    ]
                }
            }

            try:
                response = requests.post(url, json=payload, timeout=10)
                if response.status_code == 200:
                    print(f"[âœ…] Signal sent to FREE (no chart): {msg['pair']}")
                    sent_indices.append(i)
            except Exception as e:
                print(f"[ERROR] Failed to send delayed message: {e}")

    # Remove sent messages
    for i in sorted(sent_indices, reverse=True):
        delayed_messages.pop(i)


def send_daily_summary(stats):
    """Send daily performance summary to both channels and pin it."""
    total = stats.get("total", 0)
    wins = stats.get("wins", 0)
    losses = stats.get("losses", 0)
    win_rate = (wins / total * 100) if total > 0 else 0
    total_profit = stats.get("total_profit_percent", 0)

    message = f"""ğŸ“Š <b>DAILY PERFORMANCE REPORT</b> ğŸ“Š

ğŸ“… Date: {datetime.now().strftime("%Y-%m-%d")}

ğŸ“ˆ Total Signals: <b>{total}</b>
âœ… Wins: <b>{wins}</b>
âŒ Losses: <b>{losses}</b>
ğŸ¯ Win Rate: <b>{win_rate:.1f}%</b>
ğŸ’° Total P/L: <b>{total_profit:+.2f}%</b>

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ğŸ¤– <b>{BOT_NAME}</b>
ğŸ’ Premium: Instant signals + priority support"""

    # Send to premium and pin
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": PREMIUM_CHANNEL_ID,
        "text": message,
        "parse_mode": "HTML",
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code == 200:
            msg_id = r.json().get("result", {}).get("message_id")
            if msg_id:
                # Pin the message
                pin_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/pinChatMessage"
                requests.post(pin_url, json={
                    "chat_id": PREMIUM_CHANNEL_ID,
                    "message_id": msg_id,
                    "disable_notification": True,
                }, timeout=10)
    except:
        pass

    # Send to free channel with Buy VIP button
    free_message = message + "\n\nğŸ’ <i>These results are from VIP channel!</i>"
    url2 = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload2 = {
        "chat_id": FREE_CHANNEL_ID,
        "text": free_message,
        "parse_mode": "HTML",
        "reply_markup": {
            "inline_keyboard": [
                [{"text": "ğŸ›’ Buy VIP - Get These Signals!", "url": "https://t.me/YOUR_BOT_USERNAME?start=buyvip"}]
            ]
        }
    }
    try:
        r2 = requests.post(url2, json=payload2, timeout=10)
        if r2.status_code == 200:
            msg_id2 = r2.json().get("result", {}).get("message_id")
            if msg_id2:
                pin_url2 = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/pinChatMessage"
                requests.post(pin_url2, json={
                    "chat_id": FREE_CHANNEL_ID,
                    "message_id": msg_id2,
                    "disable_notification": True,
                }, timeout=10)
    except:
        pass

    print("[ğŸ“Š] Daily summary sent and pinned to both channels")


def send_startup_message():
    """Send bot startup notification."""
    message = f"""
ğŸ¤– <b>{BOT_NAME} is now ONLINE</b> ğŸŸ¢

Scanning markets for trading opportunities...

ğŸ“Š Indicators: RSI, MACD, EMA
â±ï¸ Timeframe: 1H
ğŸ¯ Pairs: 15 major coins

Stay tuned for signals! ğŸš€
"""
    send_message(PREMIUM_CHANNEL_ID, message.strip())
    send_message(FREE_CHANNEL_ID, message.strip())


def test_bot():
    """Test if bot token is valid."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            bot_name = data["result"]["username"]
            print(f"[âœ…] Bot connected: @{bot_name}")
            return True
        else:
            print(f"[âŒ] Bot token invalid!")
            return False
    except Exception as e:
        print(f"[âŒ] Cannot connect to Telegram: {e}")
        return False
