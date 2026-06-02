"""
SignalX - All-in-One Launcher
==============================
Runs ALL bot components in a single process:
1. Signal Bot (multi-timeframe analysis + send signals)
2. User Bot (handles /start, buttons, payments)
3. Promo Bot (sends teasers to free channel)

Usage:
    python main.py

That's it. One command, everything runs.
"""

import asyncio
import threading
import time
import sys
import os
import traceback
import random
from datetime import datetime

# Ensure current directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    TRADING_PAIRS, SCAN_INTERVAL_SECONDS,
    TELEGRAM_BOT_TOKEN, PREMIUM_CHANNEL_ID, FREE_CHANNEL_ID,
    TWEET_CHANNEL_ID,
    BOT_NAME,
)
from binance_api import test_connection
from advanced_analysis import multi_timeframe_analyze
from telegram_bot import (
    send_signal_to_premium,
    process_delayed_messages,
    send_daily_summary,
    send_startup_message,
    send_message,
    format_target_hit_message,
    send_result_to_free,
    test_bot,
)
from signal_tracker import add_signal, check_pending_signals, get_daily_stats
from promo_bot import send_teaser


# ============================================================
# SIGNAL BOT (Thread 1)
# ============================================================

recent_signals = {}
SIGNAL_COOLDOWN = 7200


def _send_locked_signal_to_free(signal_data, pair):
    """Send locked signal with chart to FREE channel instantly."""
    from telegram_bot import format_signal_message_free
    from chart_image import send_chart_with_signal

    message = format_signal_message_free(signal_data, pair)
    reply_markup = {
        "inline_keyboard": [
            [{"text": "🛒 Buy VIP Subscription", "url": "https://t.me/YOUR_BOT_USERNAME?start=buyvip"}]
        ]
    }

    # Try with chart
    try:
        sent = send_chart_with_signal(TELEGRAM_BOT_TOKEN, FREE_CHANNEL_ID, pair, message, reply_markup)
        if sent:
            print(f"[FREE] 🔒 Locked signal + chart sent: {pair}")
            return
    except:
        pass

    # Fallback: text only
    import requests
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": FREE_CHANNEL_ID,
        "text": message,
        "parse_mode": "HTML",
        "reply_markup": reply_markup,
    }
    try:
        requests.post(url, json=payload, timeout=10)
        print(f"[FREE] 🔒 Locked signal sent (no chart): {pair}")
    except:
        pass


def signal_bot_worker():
    """Signal scanning loop - runs in background thread."""
    print("[SIGNAL] Signal bot thread started")

    last_daily_report = datetime.now().date()
    scan_count = 0

    while True:
        try:
            scan_count += 1
            current_time = datetime.now().strftime("%H:%M:%S")
            print(f"[SIGNAL][{current_time}] Scan #{scan_count} - {len(TRADING_PAIRS)} pairs...")

            signals_found = 0

            for pair in TRADING_PAIRS:
                # Cooldown check
                if pair in recent_signals:
                    if time.time() - recent_signals[pair] < SIGNAL_COOLDOWN:
                        continue

                try:
                    signal = multi_timeframe_analyze(pair)

                    if signal is not None:
                        signals_found += 1
                        print(f"[SIGNAL] 🚨 {pair} - {signal['type']} | "
                              f"Strength: {signal['strength']}/3 | "
                              f"Score: {signal['scores']['total']:.1f}")

                        send_signal_to_premium(signal, pair)
                        # Send locked signal to FREE channel INSTANTLY (with chart)
                        _send_locked_signal_to_free(signal, pair)
                        add_signal(pair, signal["type"], signal["price"],
                                  signal["take_profit"], signal["stop_loss"],
                                  signal["reasons"])
                        recent_signals[pair] = time.time()

                except Exception as e:
                    print(f"[SIGNAL] ⚠️ Error on {pair}: {e}")
                    continue

                time.sleep(1)

            if signals_found > 0:
                print(f"[SIGNAL] 📊 Found {signals_found} signal(s)")

            # Process delayed free channel messages
            process_delayed_messages()

            # Check target hits
            stats, hit_signals = check_pending_signals()
            for hit in hit_signals:
                hours = int(hit["duration"] // 3600)
                minutes = int((hit["duration"] % 3600) // 60)
                days = int(hours // 24)
                if days > 0:
                    duration_str = f"{days} Days {hours % 24} Hours"
                elif hours > 0:
                    duration_str = f"{hours} Hours {minutes} Minutes"
                else:
                    duration_str = f"{minutes} Minutes"

                msg = format_target_hit_message(hit["pair"], hit["target"],
                                               hit["profit"], duration_str)
                send_message(PREMIUM_CHANNEL_ID, msg)
                # Also send target hit to FREE channel with Buy VIP button
                import requests as _req
                _free_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
                _free_payload = {
                    "chat_id": FREE_CHANNEL_ID,
                    "text": msg,
                    "parse_mode": "HTML",
                    "reply_markup": {
                        "inline_keyboard": [
                            [{"text": "🛒 Buy VIP Subscription", "url": "https://t.me/YOUR_BOT_USERNAME?start=buyvip"}]
                        ]
                    }
                }
                try:
                    _req.post(_free_url, json=_free_payload, timeout=10)
                except:
                    pass
                print(f"[SIGNAL] 🎯 Target {hit['target']}: {hit['pair']} +{hit['profit']:.2f}%")

                # Send ready-to-tweet text to Tweet channel
                coin = hit["pair"].replace("USDT", "")
                from hashtags import generate_hashtags
                tags = generate_hashtags(coin)
                tweet_text = (
                    f"🎯 #{coin}/USDT — Target {hit['target']} Hit ✅\n\n"
                    f"Profit: +{hit['profit']:.2f}% 📈\n"
                    f"Time: {duration_str}\n\n"
                    f"Join free → https://t.me/YOUR_FREE_CHANNEL\n\n"
                    f"{tags}"
                )
                tweet_msg = f"🐦 <b>Ready to Tweet:</b>\n\n<code>{tweet_text}</code>\n\n👆 <i>Copy → paste to Twitter/X</i>"
                send_message(TWEET_CHANNEL_ID, tweet_msg)

                # If signal COMPLETED (all targets or stop loss) → send result to FREE channel
                if hit["target"] == 3 or hit.get("status") == "LOSS":
                    send_result_to_free(
                        pair=hit["pair"],
                        signal_type=hit.get("signal_type", "BUY"),
                        entry_price=hit.get("entry_price", 0),
                        exit_price=hit.get("exit_price", 0),
                        profit_percent=hit["profit"],
                        duration_str=duration_str,
                        targets_hit=hit["target"],
                        status="WIN" if hit["target"] == 3 else "LOSS",
                    )

            # Daily report
            today = datetime.now().date()
            if today > last_daily_report:
                daily_stats = get_daily_stats()
                if daily_stats["total"] > 0:
                    send_daily_summary(daily_stats)
                last_daily_report = today

            # Check expired VIPs (every scan)
            if scan_count % 12 == 0:  # Every ~1 hour (12 scans x 5min)
                try:
                    from user_bot import check_expired_vips
                    expired = check_expired_vips()
                    if expired:
                        print(f"[VIP] Removed {len(expired)} expired VIP(s)")
                except Exception as e:
                    print(f"[VIP] Check error: {e}")

            # Wait
            time.sleep(SCAN_INTERVAL_SECONDS)

        except Exception as e:
            print(f"[SIGNAL] ❌ Error: {e}")
            send_error_alert(f"Signal Bot: {e}")
            time.sleep(30)


# ============================================================
# PROMO BOT (Thread 2)
# ============================================================

def promo_bot_worker():
    """Promo teaser loop - runs in background thread."""
    print("[PROMO] Promo bot thread started")

    teaser_count = 0
    fake_tweet_count = 0

    # Wait 2 minutes before first
    time.sleep(120)

    while True:
        try:
            # Only send fake tweets to TWEET channel (not free channel anymore)
            fake_tweet_count += 1
            try:
                _send_fake_chart_tweet(fake_tweet_count)
            except Exception as e:
                print(f"[TWEET] ❌ Fake tweet error: {e}")

            time.sleep(120)  # Every 2 minutes

        except Exception as e:
            print(f"[PROMO] ❌ Error: {e}")
            time.sleep(60)


def _send_fake_chart_tweet(count=0):
    """Generate a fake signal result with chart and send to tweet channel."""
    from chart_image import send_chart_with_signal
    from fake_stats import get_fake_stats
    from hashtags import generate_hashtags

    stats = get_fake_stats()
    trades = stats["trades"]

    # Pick a random winning trade
    wins = [t for t in trades if t["is_win"]]
    if not wins:
        return

    trade = random.choice(wins)
    coin = trade["coin"].replace("USDT", "")
    profit = trade["profit"]
    pair = trade["coin"]

    # Random realistic duration
    durations = [
        "28 Minutes", "42 Minutes", "1h 5m", "1h 32m", "2h 15m",
        "2h 48m", "3h 20m", "4h 10m", "5h 45m", "6h 30m",
        "7h 12m", "8h 55m", "10h 20m", "12h 40m", "1 Day 3h",
    ]
    duration = random.choice(durations)

    # Random target (1, 2, or 3)
    target = random.choices([1, 2, 3], weights=[30, 35, 35])[0]

    if target == 3:
        header = f"🎯 #{coin}/USDT — All Targets Hit ✅ 😎"
    else:
        header = f"🎯 #{coin}/USDT — Target {target} Hit ✅"

    # Random direction
    direction = random.choice(["Long 🟢", "Short 🔴"])

    # Generate hashtags
    tags = generate_hashtags(coin)

    # Tweet text
    tweet_text = (
        f"{header}\n\n"
        f"Direction: {direction}\n"
        f"Profit: +{profit:.2f}% 📈\n"
        f"Time: {duration}\n\n"
        f"Join free → https://t.me/YOUR_FREE_CHANNEL\n\n"
        f"{tags}"
    )

    # Caption with FAKE label for admin
    caption = f"⚠️ <b>[FAKE]</b> Tweet #{count}:\n\n<code>{tweet_text}</code>\n\n👆 <i>Save image + copy text → Twitter/X</i>"

    # Send with chart
    sent = send_chart_with_signal(TELEGRAM_BOT_TOKEN, TWEET_CHANNEL_ID, pair, caption)
    if sent:
        print(f"[TWEET] 🐦 Fake #{count}: {coin} +{profit:.2f}% ✅")
    else:
        # Fallback text only
        send_message(TWEET_CHANNEL_ID, caption)
        print(f"[TWEET] 🐦 Fake #{count}: {coin} +{profit:.2f}% (no chart)")


# ============================================================
# USER BOT (Thread 3)
# ============================================================

def user_bot_worker():
    """User bot (handles /start, buttons, admin) - runs in background thread."""
    print("[USER] User bot thread started")

    try:
        from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
        from telegram.ext import Application, CommandHandler, CallbackQueryHandler

        from user_bot import (
            start_command, button_callback,
            admin_command, addvip_command, rmvip_command,
            users_command, viplist_command, realstats_command,
        )

        app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

        # User handlers
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CallbackQueryHandler(button_callback))

        # Admin handlers
        app.add_handler(CommandHandler("admin", admin_command))
        app.add_handler(CommandHandler("addvip", addvip_command))
        app.add_handler(CommandHandler("rmvip", rmvip_command))
        app.add_handler(CommandHandler("users", users_command))
        app.add_handler(CommandHandler("viplist", viplist_command))
        app.add_handler(CommandHandler("realstats", realstats_command))

        print("[USER] ✅ User bot listening for /start + admin commands")
        app.run_polling(drop_pending_updates=True)

    except Exception as e:
        print(f"[USER] ❌ Error: {e}")
        send_error_alert(f"User Bot: {e}")


# ============================================================
# ERROR HANDLING
# ============================================================

def send_error_alert(error_msg):
    """Send error alert to admin."""
    text = f"⚠️ <b>ERROR</b>\n\n<code>{str(error_msg)[:300]}</code>\n\n🔄 Auto-recovering..."
    try:
        send_message(PREMIUM_CHANNEL_ID, text)
    except:
        pass


# ============================================================
# MAIN
# ============================================================

def main():
    print("""
    ╔══════════════════════════════════════════════════╗
    ║                                                  ║
    ║     🤖 SignalX - All-in-One Bot v2.0             ║
    ║     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    ║
    ║                                                  ║
    ║     📊 Signal Bot  - Multi-TF Analysis           ║
    ║     👤 User Bot    - /start & Payments           ║
    ║     📢 Promo Bot   - Free Channel Teasers        ║
    ║                                                  ║
    ╚══════════════════════════════════════════════════╝
    """)

    # === TEST CONNECTIONS ===
    print("[*] Testing connections...")

    print("    Binance API...", end=" ")
    if not test_connection():
        print("❌ FAILED")
        print("    Check your internet connection!")
        sys.exit(1)
    print("✅")

    print("    Telegram Bot...", end=" ")
    if not test_bot():
        print("❌ FAILED")
        print("    Check TELEGRAM_BOT_TOKEN in config.py!")
        sys.exit(1)
    print("✅")

    # === SEND STARTUP MESSAGE ===
    send_startup_message()
    print("\n[✅] Startup message sent to channels")

    # === START ALL THREADS ===
    print("\n[*] Starting all bot components...\n")

    # Thread 1: Signal Bot
    signal_thread = threading.Thread(target=signal_bot_worker, daemon=True, name="SignalBot")
    signal_thread.start()
    print("    [1/3] 📊 Signal Bot ✅")

    # Thread 2: Promo Bot
    promo_thread = threading.Thread(target=promo_bot_worker, daemon=True, name="PromoBot")
    promo_thread.start()
    print("    [2/3] 📢 Promo Bot ✅")

    # Thread 3: User Bot (runs in main thread because telegram lib needs it)
    print("    [3/3] 👤 User Bot ✅")

    print(f"""
    ╔══════════════════════════════════════════════════╗
    ║  ✅ ALL SYSTEMS RUNNING                          ║
    ║                                                  ║
    ║  📊 Scanning {len(TRADING_PAIRS):2d} pairs every {SCAN_INTERVAL_SECONDS}s              ║
    ║  📢 Teasers every 5-10 min                       ║
    ║  👤 Listening for /start                         ║
    ║                                                  ║
    ║  Press Ctrl+C to stop all                        ║
    ╚══════════════════════════════════════════════════╝
    """)

    # Run user bot in main thread
    try:
        user_bot_worker()
    except KeyboardInterrupt:
        print("\n\n[*] Shutting down all bots...")
        print("[*] Goodbye! 👋")
        sys.exit(0)


if __name__ == "__main__":
    main()
