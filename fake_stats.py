"""
Fake Stats Generator
=====================
Generates realistic-looking fake stats for public display.
Refreshes every 24 hours with new random data.
Admin sees real stats with /realstats command.
"""

import json
import os
import random
import time
from datetime import datetime, timedelta

from config import TRADING_PAIRS

FAKE_STATS_FILE = "fake_stats_cache.json"


def _get_random_coins(count=40):
    """Get random coins from trading pairs."""
    coins = [p.replace("USDT", "") for p in TRADING_PAIRS]
    # Allow duplicates (same coin can have multiple signals)
    return [random.choice(coins) + "USDT" for _ in range(count)]


def generate_fake_stats():
    """Generate realistic fake stats for 24 hours."""
    # Random number of signals (35-50)
    total_signals = random.randint(35, 50)

    # Win rate between 90-97%
    win_rate = random.uniform(90, 97)
    wins = int(total_signals * win_rate / 100)
    losses = total_signals - wins

    # Generate individual trades
    trades = []
    coins_used = _get_random_coins(total_signals)

    for i in range(total_signals):
        coin = coins_used[i]
        is_win = i < wins  # First N are wins, rest are losses

        if is_win:
            # Profit between +10% and +320%
            # Most between 20-80%, few outliers
            r = random.random()
            if r < 0.7:
                profit = random.uniform(20, 80)
            elif r < 0.9:
                profit = random.uniform(80, 150)
            else:
                profit = random.uniform(150, 320)
        else:
            # Loss between -20% and -65%
            profit = random.uniform(-20, -65)

        trades.append({
            "coin": coin,
            "profit": round(profit, 2),
            "is_win": is_win,
        })

    # Shuffle so losses aren't all at the end
    random.shuffle(trades)

    # Calculate totals
    total_profit = sum(t["profit"] for t in trades)
    avg_profit = total_profit / total_signals if total_signals > 0 else 0

    stats = {
        "generated_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(hours=24)).isoformat(),
        "trades": trades,
        "summary": {
            "total_signals": total_signals,
            "wins": wins,
            "losses": losses,
            "win_rate": round(win_rate, 2),
            "total_profit": round(total_profit, 2),
            "avg_profit": round(avg_profit, 2),
        }
    }

    # Save to cache
    with open(FAKE_STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)

    return stats


def get_fake_stats():
    """Get current fake stats (regenerate if expired)."""
    if os.path.exists(FAKE_STATS_FILE):
        with open(FAKE_STATS_FILE, "r") as f:
            stats = json.load(f)

        # Check if expired (24 hours)
        expires = datetime.fromisoformat(stats["expires_at"])
        if datetime.now() < expires:
            return stats

    # Generate new stats
    return generate_fake_stats()


def format_fake_stats_message():
    """Format fake stats as a Telegram message (like the screenshot)."""
    stats = get_fake_stats()
    trades = stats["trades"]
    summary = stats["summary"]

    # Build trade lines
    lines = []
    for trade in trades:
        coin = trade["coin"]
        profit = trade["profit"]
        if trade["is_win"]:
            emoji = "🟢"
            lines.append(f"<code>{coin:12s} : +{profit:.2f}%</code> {emoji}")
        else:
            emoji = "🚫"
            lines.append(f"<code>{coin:12s} : {profit:.2f}%</code> {emoji}")

    trades_text = "\n".join(lines)

    message = f"""📈 <b>VIP Channel's Profit in the last 24 hours</b>

{trades_text}

━━━━━━━━━━━━━━━━━━━━
💰 Total Profit: <b>{summary['total_profit']:.2f}%</b> Profit
💹 Average Profit/Trade: <b>{summary['avg_profit']:.2f}%</b>
📡 Signal Calls: <b>{summary['total_signals']}</b> calls
📊 Win Rate: <b>{summary['win_rate']:.2f}%</b>
🟢 Profit Trades: <b>{summary['wins']}</b>
🚫 Loss Trades: <b>{summary['losses']}</b>"""

    return message
