"""
SignalX - GUI Launcher
========================
Starts all bots with a visual control panel.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class SignalXGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SignalX - All-in-One Control Panel")
        self.root.geometry("800x550")
        self.root.configure(bg="#0d1117")
        self.root.resizable(True, True)

        self.running = False
        self._build_ui()

    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#161b22", height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="🤖 SignalX", font=("Arial", 20, "bold"),
                bg="#161b22", fg="white").pack(side="left", padx=20, pady=15)

        self.status_label = tk.Label(header, text="● STOPPED", font=("Arial", 13, "bold"),
                                    bg="#161b22", fg="#f85149")
        self.status_label.pack(side="right", padx=20, pady=15)

        # Buttons
        btn_frame = tk.Frame(self.root, bg="#0d1117")
        btn_frame.pack(fill="x", padx=20, pady=15)

        self.start_btn = tk.Button(btn_frame, text="▶  START ALL", font=("Arial", 14, "bold"),
                                  bg="#238636", fg="white", width=18, height=2,
                                  command=self._start_all, cursor="hand2", relief="flat")
        self.start_btn.pack(side="left", padx=5)

        self.stop_btn = tk.Button(btn_frame, text="⏹  STOP ALL", font=("Arial", 14, "bold"),
                                 bg="#da3633", fg="white", width=18, height=2,
                                 command=self._stop_all, state="disabled", cursor="hand2", relief="flat")
        self.stop_btn.pack(side="left", padx=5)

        # Info panel
        info_frame = tk.Frame(self.root, bg="#161b22", padx=15, pady=10)
        info_frame.pack(fill="x", padx=20, pady=5)

        info_items = [
            ("📊 Signal Bot", "Multi-TF Analysis (15m+1H+4H)"),
            ("👤 User Bot", "/start, Payments, Admin"),
            ("📢 Promo Bot", "Teasers every 5-10 min"),
        ]

        for i, (label, desc) in enumerate(info_items):
            tk.Label(info_frame, text=label, font=("Arial", 11, "bold"),
                    bg="#161b22", fg="#58a6ff").grid(row=i, column=0, sticky="w", pady=2)
            tk.Label(info_frame, text=desc, font=("Arial", 10),
                    bg="#161b22", fg="#8b949e").grid(row=i, column=1, sticky="w", padx=15, pady=2)

        # Log
        tk.Label(self.root, text="📋 Live Log:", font=("Arial", 11, "bold"),
                bg="#0d1117", fg="#c9d1d9").pack(anchor="w", padx=20, pady=(10, 0))

        self.log_text = scrolledtext.ScrolledText(self.root, font=("Consolas", 10),
                                                  bg="#161b22", fg="#58a6ff",
                                                  insertbackground="white", height=15)
        self.log_text.pack(fill="both", expand=True, padx=20, pady=(5, 20))
        self._log("SignalX Control Panel ready.")
        self._log("Click START ALL to begin.")

    def _log(self, msg):
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] {msg}\n")
        self.log_text.see("end")

    def _start_all(self):
        self.running = True
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.status_label.configure(text="● RUNNING", fg="#3fb950")
        self._log("Starting all bot components...")

        # Start main bot in thread
        self.bot_thread = threading.Thread(target=self._run_bots, daemon=True)
        self.bot_thread.start()

    def _stop_all(self):
        self.running = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.status_label.configure(text="● STOPPED", fg="#f85149")
        self._log("All bots stopped.")

    def _run_bots(self):
        try:
            from config import TRADING_PAIRS, SCAN_INTERVAL_SECONDS, PREMIUM_CHANNEL_ID
            from binance_api import test_connection
            from telegram_bot import test_bot, send_startup_message, send_message
            from telegram_bot import (
                send_signal_to_premium, queue_signal_for_free,
                process_delayed_messages, format_target_hit_message,
            )
            from advanced_analysis import multi_timeframe_analyze
            from signal_tracker import add_signal, check_pending_signals
            from promo_bot import send_teaser
            import random

            # Test connections
            self._log("Testing Binance API...")
            if not test_connection():
                self._log("❌ Binance connection failed!")
                self.root.after(0, self._stop_all)
                return
            self._log("✅ Binance OK")

            self._log("Testing Telegram...")
            if not test_bot():
                self._log("❌ Telegram bot failed!")
                self.root.after(0, self._stop_all)
                return
            self._log("✅ Telegram OK")

            send_startup_message()
            self._log("✅ Startup message sent")

            # Start user bot in separate thread
            user_thread = threading.Thread(target=self._run_user_bot, daemon=True)
            user_thread.start()
            self._log("✅ User bot started")

            # Main loop (signal + promo)
            scan_count = 0
            last_promo = time.time()
            recent_signals = {}

            self._log("🚀 All systems running!")

            while self.running:
                scan_count += 1
                self._log(f"🔍 Scan #{scan_count}...")

                signals_found = 0
                for pair in TRADING_PAIRS:
                    if not self.running:
                        break
                    if pair in recent_signals and time.time() - recent_signals[pair] < 7200:
                        continue

                    try:
                        signal = multi_timeframe_analyze(pair)
                        if signal:
                            signals_found += 1
                            self._log(f"🚨 SIGNAL: {pair} {signal['type']} (strength {signal['strength']}/3)")
                            send_signal_to_premium(signal, pair)
                            queue_signal_for_free(signal, pair)
                            add_signal(pair, signal["type"], signal["price"],
                                      signal["take_profit"], signal["stop_loss"], signal["reasons"])
                            recent_signals[pair] = time.time()
                    except:
                        pass
                    time.sleep(1)

                if signals_found:
                    self._log(f"📊 {signals_found} signal(s) found")

                process_delayed_messages()

                # Check targets
                stats, hits = check_pending_signals()
                for hit in hits:
                    h = int(hit["duration"] // 3600)
                    m = int((hit["duration"] % 3600) // 60)
                    dur = f"{h}h {m}m" if h > 0 else f"{m}m"
                    msg = format_target_hit_message(hit["pair"], hit["target"], hit["profit"], dur)
                    send_message(PREMIUM_CHANNEL_ID, msg)
                    self._log(f"🎯 Target {hit['target']}: {hit['pair']} +{hit['profit']:.1f}%")

                # Promo (every 5-10 min)
                if time.time() - last_promo > random.randint(300, 600):
                    send_teaser()
                    self._log("📢 Promo teaser sent")
                    last_promo = time.time()

                # Wait
                for _ in range(SCAN_INTERVAL_SECONDS):
                    if not self.running:
                        break
                    time.sleep(1)

        except Exception as e:
            self._log(f"❌ Error: {e}")
            self.root.after(0, self._stop_all)

    def _run_user_bot(self):
        """Run user bot in separate thread."""
        try:
            from telegram import Update
            from telegram.ext import Application, CommandHandler, CallbackQueryHandler
            from config import TELEGRAM_BOT_TOKEN
            from user_bot import (
                start_command, button_callback,
                admin_command, addvip_command, rmvip_command,
                users_command, viplist_command,
            )

            app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
            app.add_handler(CommandHandler("start", start_command))
            app.add_handler(CallbackQueryHandler(button_callback))
            app.add_handler(CommandHandler("admin", admin_command))
            app.add_handler(CommandHandler("addvip", addvip_command))
            app.add_handler(CommandHandler("rmvip", rmvip_command))
            app.add_handler(CommandHandler("users", users_command))
            app.add_handler(CommandHandler("viplist", viplist_command))

            app.run_polling(drop_pending_updates=True)
        except Exception as e:
            self._log(f"[USER] Error: {e}")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = SignalXGUI()
    app.run()
