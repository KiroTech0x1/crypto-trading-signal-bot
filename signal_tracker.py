"""
Signal Tracker
===============
Tracks all signals and their outcomes (win/loss).
Saves history to JSON file for performance reporting.
"""

import json
import os
import time
from datetime import datetime
from binance_api import get_current_price


HISTORY_FILE = "signal_history.json"


def load_history():
    """Load signal history from file."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return {"signals": [], "stats": {"total": 0, "wins": 0, "losses": 0, "pending": 0}}


def save_history(history):
    """Save signal history to file."""
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def add_signal(pair, signal_type, entry_price, take_profit, stop_loss, reasons):
    """Record a new signal."""
    history = load_history()

    signal = {
        "id": int(time.time()),
        "pair": pair,
        "type": signal_type,
        "entry_price": entry_price,
        "take_profit": take_profit,
        "stop_loss": stop_loss,
        "reasons": reasons,
        "timestamp": datetime.now().isoformat(),
        "timestamp_unix": time.time(),
        "status": "PENDING",  # PENDING, WIN, LOSS
        "exit_price": None,
        "profit_percent": None,
        "targets_hit": 0,
    }

    history["signals"].append(signal)
    history["stats"]["total"] += 1
    history["stats"]["pending"] += 1
    save_history(history)

    return signal["id"]


def check_pending_signals():
    """Check all pending signals if they hit TP or SL."""
    history = load_history()
    updated = False
    hit_signals = []

    for signal in history["signals"]:
        if signal["status"] != "PENDING":
            continue

        current_price = get_current_price(signal["pair"])
        if current_price is None:
            continue

        hit_tp = False
        hit_sl = False

        if signal["type"] == "BUY":
            # Check multiple targets
            tp1 = signal["entry_price"] * 1.015
            tp2 = signal["entry_price"] * 1.03
            tp3 = signal["entry_price"] * 1.05

            # Check which target was hit
            targets_hit = signal.get("targets_hit", 0)

            if targets_hit < 1 and current_price >= tp1:
                signal["targets_hit"] = 1
                # TRAILING STOP: Move stop loss to entry (breakeven)
                signal["stop_loss"] = signal["entry_price"]
                profit = ((current_price - signal["entry_price"]) / signal["entry_price"]) * 100
                duration = time.time() - signal.get("timestamp_unix", time.time())
                hit_signals.append({
                    "pair": signal["pair"],
                    "target": 1,
                    "profit": profit,
                    "duration": duration,
                })
                updated = True
                print(f"[TRAILING] {signal['pair']} SL moved to entry (breakeven)")

            if targets_hit < 2 and current_price >= tp2:
                signal["targets_hit"] = 2
                # TRAILING STOP: Move stop loss to target 1
                signal["stop_loss"] = tp1
                profit = ((current_price - signal["entry_price"]) / signal["entry_price"]) * 100
                duration = time.time() - signal.get("timestamp_unix", time.time())
                hit_signals.append({
                    "pair": signal["pair"],
                    "target": 2,
                    "profit": profit,
                    "duration": duration,
                })
                updated = True

            if current_price >= tp3:
                signal["status"] = "WIN"
                signal["targets_hit"] = 3
                signal["exit_price"] = current_price
                signal["profit_percent"] = ((current_price - signal["entry_price"]) / signal["entry_price"]) * 100
                history["stats"]["wins"] += 1
                history["stats"]["pending"] -= 1
                duration = time.time() - signal.get("timestamp_unix", time.time())
                hit_signals.append({
                    "pair": signal["pair"],
                    "target": 3,
                    "profit": signal["profit_percent"],
                    "duration": duration,
                    "signal_type": signal["type"],
                    "entry_price": signal["entry_price"],
                    "exit_price": current_price,
                    "status": "WIN",
                })
                updated = True
                print(f"[✅ WIN] {signal['pair']} hit TP3! Profit: +{signal['profit_percent']:.2f}%")

            elif current_price <= signal["stop_loss"]:
                signal["status"] = "LOSS"
                signal["exit_price"] = current_price
                signal["profit_percent"] = ((current_price - signal["entry_price"]) / signal["entry_price"]) * 100
                history["stats"]["losses"] += 1
                history["stats"]["pending"] -= 1
                duration = time.time() - signal.get("timestamp_unix", time.time())
                hit_signals.append({
                    "pair": signal["pair"],
                    "target": 0,
                    "profit": signal["profit_percent"],
                    "duration": duration,
                    "signal_type": signal["type"],
                    "entry_price": signal["entry_price"],
                    "exit_price": current_price,
                    "status": "LOSS",
                })
                updated = True
                print(f"[❌ LOSS] {signal['pair']} hit SL! Loss: {signal['profit_percent']:.2f}%")

        else:  # SELL/SHORT
            tp1 = signal["entry_price"] * 0.985
            tp2 = signal["entry_price"] * 0.97
            tp3 = signal["entry_price"] * 0.95

            targets_hit = signal.get("targets_hit", 0)

            if targets_hit < 1 and current_price <= tp1:
                signal["targets_hit"] = 1
                # TRAILING STOP: Move stop loss to entry (breakeven)
                signal["stop_loss"] = signal["entry_price"]
                profit = ((signal["entry_price"] - current_price) / signal["entry_price"]) * 100
                duration = time.time() - signal.get("timestamp_unix", time.time())
                hit_signals.append({
                    "pair": signal["pair"],
                    "target": 1,
                    "profit": profit,
                    "duration": duration,
                })
                updated = True
                print(f"[TRAILING] {signal['pair']} SL moved to entry (breakeven)")

            if targets_hit < 2 and current_price <= tp2:
                signal["targets_hit"] = 2
                # TRAILING STOP: Move stop loss to target 1
                signal["stop_loss"] = tp1
                profit = ((signal["entry_price"] - current_price) / signal["entry_price"]) * 100
                duration = time.time() - signal.get("timestamp_unix", time.time())
                hit_signals.append({
                    "pair": signal["pair"],
                    "target": 2,
                    "profit": profit,
                    "duration": duration,
                })
                updated = True

            if current_price <= tp3:
                signal["status"] = "WIN"
                signal["targets_hit"] = 3
                signal["exit_price"] = current_price
                signal["profit_percent"] = ((signal["entry_price"] - current_price) / signal["entry_price"]) * 100
                history["stats"]["wins"] += 1
                history["stats"]["pending"] -= 1
                duration = time.time() - signal.get("timestamp_unix", time.time())
                hit_signals.append({
                    "pair": signal["pair"],
                    "target": 3,
                    "profit": signal["profit_percent"],
                    "duration": duration,
                    "signal_type": signal["type"],
                    "entry_price": signal["entry_price"],
                    "exit_price": current_price,
                    "status": "WIN",
                })
                updated = True
                print(f"[✅ WIN] {signal['pair']} hit TP3! Profit: +{signal['profit_percent']:.2f}%")

            elif current_price >= signal["stop_loss"]:
                signal["status"] = "LOSS"
                signal["exit_price"] = current_price
                signal["profit_percent"] = ((signal["entry_price"] - current_price) / signal["entry_price"]) * 100
                history["stats"]["losses"] += 1
                history["stats"]["pending"] -= 1
                duration = time.time() - signal.get("timestamp_unix", time.time())
                hit_signals.append({
                    "pair": signal["pair"],
                    "target": 0,
                    "profit": signal["profit_percent"],
                    "duration": duration,
                    "signal_type": signal["type"],
                    "entry_price": signal["entry_price"],
                    "exit_price": current_price,
                    "status": "LOSS",
                })
                updated = True
                print(f"[❌ LOSS] {signal['pair']} hit SL! Loss: {signal['profit_percent']:.2f}%")

    if updated:
        save_history(history)

    return history["stats"], hit_signals


def get_daily_stats():
    """Get today's performance stats."""
    history = load_history()
    today = datetime.now().strftime("%Y-%m-%d")

    today_signals = [s for s in history["signals"] if s["timestamp"].startswith(today)]

    stats = {
        "total": len(today_signals),
        "wins": len([s for s in today_signals if s["status"] == "WIN"]),
        "losses": len([s for s in today_signals if s["status"] == "LOSS"]),
        "pending": len([s for s in today_signals if s["status"] == "PENDING"]),
        "total_profit_percent": sum(s.get("profit_percent", 0) for s in today_signals if s.get("profit_percent")),
    }

    return stats


def get_all_time_stats():
    """Get all-time performance stats."""
    history = load_history()
    stats = history["stats"]

    total_closed = stats["wins"] + stats["losses"]
    win_rate = (stats["wins"] / total_closed * 100) if total_closed > 0 else 0

    all_profits = [s.get("profit_percent", 0) for s in history["signals"] if s.get("profit_percent")]
    total_profit = sum(all_profits)
    avg_profit = (total_profit / len(all_profits)) if all_profits else 0

    return {
        "total_signals": stats["total"],
        "wins": stats["wins"],
        "losses": stats["losses"],
        "pending": stats["pending"],
        "win_rate": win_rate,
        "total_profit_percent": total_profit,
        "avg_profit_percent": avg_profit,
    }
