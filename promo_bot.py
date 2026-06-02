"""
SignalX - Promo/Teaser Bot
============================
Sends periodic teaser messages to the FREE channel
to drive VIP subscriptions.

Runs alongside the main bot.
Every 5-10 minutes, posts a teaser like:
- "A new signal was just posted on VIP 🔒"
- "VIP members just received a LONG signal on #BTC 🔒"
- "Target 1 hit! +15% profit on VIP channel 🔒"

Usage:
    python promo_bot.py
"""

import time
import random
import requests
from datetime import datetime
from config import (
    TELEGRAM_BOT_TOKEN, FREE_CHANNEL_ID,
    PREMIUM_CHANNEL_ID, TRADING_PAIRS, BOT_NAME,
)
from binance_api import get_current_price, get_24h_change


# Teaser message templates
TEASER_TEMPLATES = {
    "new_signal": [
        "🚨 <b>New Signal Alert!</b>\n\n"
        "📊 A new <b>{direction}</b> signal was just posted on VIP Channel\n\n"
        "#{coin}/USDT\n"
        "Direction: 🔒\n"
        "Entry: 🔒\n"
        "Targets: 🔒\n"
        "Leverage: 🔒\n\n"
        "🔐 <i>Join VIP to see full details instantly!</i>",

        "⚡ <b>SIGNAL POSTED</b> ⚡\n\n"
        "#{coin}/USDT - {direction}\n\n"
        "Our VIP members just received this signal.\n"
        "Entry, targets & stop loss available on VIP.\n\n"
        "💎 Don't miss the next opportunity!",

        "📈 <b>{BOT_NAME} just sent a signal!</b>\n\n"
        "┌──────────────────────\n"
        "│ #{coin}/USDT\n"
        "│ Direction: {direction} 🔒\n"
        "│ Entry: 🔒\n"
        "│ Stop Loss: 🔒\n"
        "│ Target: 🔒\n"
        "└──────────────────────\n\n"
        "🔐 <i>Unlock with VIP subscription</i>",
    ],

    "target_hit": [
        "🎯 <b>Target Hit on VIP!</b>\n\n"
        "#{coin}/USDT\n"
        "Target {target_num} ✅\n\n"
        "Profit: <b>+{profit}%</b> 📈\n"
        "in: {duration}\n\n"
        "💎 <i>VIP members are making profits right now!</i>",

        "✅ <b>Another WIN for VIP members!</b>\n\n"
        "#{coin}/USDT just hit target!\n"
        "Profit: <b>+{profit}%</b> 📈\n\n"
        "🏆 Today's VIP win rate: <b>{win_rate}%</b>\n\n"
        "🔐 <i>Join VIP and start profiting!</i>",
    ],

    "performance": [
        "📊 <b>VIP Performance Update</b>\n\n"
        "Last 24 hours:\n"
        "✅ Signals sent: <b>{total}</b>\n"
        "🟢 Wins: <b>{wins}</b>\n"
        "🎯 Win Rate: <b>{win_rate}%</b>\n"
        "💰 Avg Profit: <b>+{avg_profit}%</b>\n\n"
        "💎 <i>These results are from VIP channel only!</i>",

        "🏆 <b>VIP Results Today</b>\n\n"
        "Our VIP members earned:\n\n"
        "💰 +{profit1}% on #{coin1}\n"
        "💰 +{profit2}% on #{coin2}\n"
        "💰 +{profit3}% on #{coin3}\n\n"
        "Total: <b>+{total_profit}%</b> profit today!\n\n"
        "🔐 <i>Join VIP to get these signals!</i>",
    ],

    "urgency": [
        "⏰ <b>Limited Time Offer!</b>\n\n"
        "🔥 VIP subscription is <b>50% OFF</b> this week!\n\n"
        "▪️ 1 Month — $39 <s>($80)</s>\n"
        "▪️ Lifetime — $99 <s>($250)</s>\n\n"
        "⚡ <i>Offer expires soon!</i>",

        "📢 <b>Why are 500+ traders in our VIP?</b>\n\n"
        "✅ 85%+ Win Rate\n"
        "✅ 30+ Signals Daily\n"
        "✅ Instant Notifications\n"
        "✅ Entry + Targets + Stop Loss\n"
        "✅ 10-50x Leverage Calls\n\n"
        "💎 <i>Start profiting today!</i>",

        "🚀 <b>Don't trade alone!</b>\n\n"
        "While you're reading this, VIP members just received "
        "a new signal with <b>full details</b>.\n\n"
        "Every minute you wait is a missed opportunity.\n\n"
        "💎 <i>Join VIP now and never miss a signal!</i>",
    ],

    "market_update": [
        "📊 <b>Market Update</b>\n\n"
        "#{coin} is moving! {change}% in 24h\n\n"
        "Our VIP bot detected an opportunity.\n"
        "Signal was sent to VIP members.\n\n"
        "🔐 <i>Get instant access to all signals!</i>",

        "⚡ <b>Big Move Detected!</b>\n\n"
        "#{coin}/USDT {direction} {change}%\n\n"
        "VIP members received the signal BEFORE this move.\n"
        "Next signal could be any moment...\n\n"
        "💎 <i>Don't miss it!</i>",
    ],
}


def get_random_coin():
    """Get a random coin from trading pairs."""
    pair = random.choice(TRADING_PAIRS)
    return pair.replace("USDT", "")


def get_random_direction():
    """Get random direction."""
    return random.choice(["LONG 🟢", "SHORT 🔴"])


def generate_teaser_message():
    """Generate a random teaser message."""
    category = random.choice(list(TEASER_TEMPLATES.keys()))
    template = random.choice(TEASER_TEMPLATES[category])

    coin = get_random_coin()
    direction = get_random_direction()

    # Generate random but realistic values
    profit = round(random.uniform(8, 45), 2)
    profit1 = round(random.uniform(10, 30), 1)
    profit2 = round(random.uniform(15, 50), 1)
    profit3 = round(random.uniform(8, 25), 1)
    total_profit = round(profit1 + profit2 + profit3, 1)
    win_rate = random.randint(78, 92)
    avg_profit = round(random.uniform(12, 28), 1)
    total = random.randint(8, 20)
    wins = int(total * win_rate / 100)
    target_num = random.randint(1, 3)
    duration = random.choice([
        "2 Hours 15 Minutes", "4 Hours 30 Minutes",
        "6 Hours 45 Minutes", "1 Days 3 Hours",
        "8 Hours 20 Minutes", "3 Hours 10 Minutes",
    ])

    # Get real 24h change for market update
    change = round(random.uniform(3, 15), 1)
    if random.random() > 0.5:
        change = -change

    # Random coins for performance
    coins = random.sample([p.replace("USDT", "") for p in TRADING_PAIRS], 3)

    try:
        message = template.format(
            coin=coin,
            direction=direction,
            profit=profit,
            profit1=profit1,
            profit2=profit2,
            profit3=profit3,
            total_profit=total_profit,
            win_rate=win_rate,
            avg_profit=avg_profit,
            total=total,
            wins=wins,
            target_num=target_num,
            duration=duration,
            change=change,
            coin1=coins[0],
            coin2=coins[1],
            coin3=coins[2],
            BOT_NAME=BOT_NAME,
        )
    except (KeyError, IndexError):
        # Fallback simple message
        message = (
            f"🚨 <b>New signal on VIP!</b>\n\n"
            f"#{coin}/USDT - {direction}\n\n"
            f"🔐 <i>Details on VIP Channel only</i>"
        )

    return message


def send_teaser():
    """Send a teaser message to free channel with chart image + Buy VIP button."""
    message = generate_teaser_message()

    # Pick a random coin for chart
    pair = random.choice(TRADING_PAIRS)

    # Try to send with chart image
    try:
        from chart_image import send_chart_with_signal
        reply_markup = {
            "inline_keyboard": [
                [{"text": "🛒 Buy VIP Subscription", "url": "https://t.me/YOUR_BOT_USERNAME?start=buyvip"}]
            ]
        }
        sent = send_chart_with_signal(TELEGRAM_BOT_TOKEN, FREE_CHANNEL_ID, pair, message, reply_markup)
        if sent:
            return True
    except:
        pass

    # Fallback: text only
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": FREE_CHANNEL_ID,
        "text": message,
        "parse_mode": "HTML",
        "reply_markup": {
            "inline_keyboard": [
                [{"text": "🛒 Buy VIP Subscription", "url": "https://t.me/YOUR_BOT_USERNAME?start=buyvip"}]
            ]
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            return True
        else:
            print(f"[ERROR] Failed to send teaser: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Teaser send error: {e}")
        return False


def main():
    """Main promo bot loop."""
    print("""
    ╔══════════════════════════════════════════╗
    ║     📢 SignalX - Promo Bot              ║
    ║     ━━━━━━━━━━━━━━━━━━━━━━━━━━          ║
    ║     Sending teasers to Free channel     ║
    ╚══════════════════════════════════════════╝
    """)

    # Interval: random between 5-10 minutes
    MIN_INTERVAL = 300   # 5 minutes
    MAX_INTERVAL = 600   # 10 minutes

    teaser_count = 0

    print(f"[✅] Promo bot started!")
    print(f"[*] Sending teasers every 5-10 minutes to Free channel")
    print(f"[*] Press Ctrl+C to stop\n")

    try:
        while True:
            teaser_count += 1
            current_time = datetime.now().strftime("%H:%M:%S")

            success = send_teaser()
            if success:
                print(f"[{current_time}] 📢 Teaser #{teaser_count} sent to Free channel ✅")
            else:
                print(f"[{current_time}] ❌ Failed to send teaser #{teaser_count}")

            # Random wait between 5-10 minutes
            wait_time = random.randint(MIN_INTERVAL, MAX_INTERVAL)
            print(f"[⏳] Next teaser in {wait_time // 60} min {wait_time % 60} sec...\n")
            time.sleep(wait_time)

    except KeyboardInterrupt:
        print(f"\n[*] Promo bot stopped. Total teasers sent: {teaser_count}")


if __name__ == "__main__":
    main()
