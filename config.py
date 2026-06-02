"""
Crypto Signal Bot - Configuration
==================================
Fill in your API keys and channel IDs below.
"""

# === TELEGRAM SETTINGS ===
# Get from @BotFather on Telegram
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# Channel IDs (get by forwarding a message from channel to @userinfobot)
# Format: -100xxxxxxxxxx
PREMIUM_CHANNEL_ID = "-100XXXXXXXXXX"  # Premium channel
FREE_CHANNEL_ID = "@YourFreeChannel"     # Free channel

# Tweet channel (ready-to-post tweets for Twitter/X)
TWEET_CHANNEL_ID = "-100XXXXXXXXXX"    # Tweet channel

# Delay for free channel (in seconds)
FREE_CHANNEL_DELAY = 3600  # 1 hour = 3600 seconds

# === BINANCE SETTINGS ===
# NO API KEY NEEDED! We use public endpoints (free, no account required)
# Only reading price data, not trading
BINANCE_API_KEY = ""  # Not needed
BINANCE_API_SECRET = ""  # Not needed

# === TRADING PAIRS TO MONITOR ===
# Top 100 coins on Binance (USDT pairs)
TRADING_PAIRS = [
    # Top 10
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
    "DOGEUSDT", "ADAUSDT", "AVAXUSDT", "DOTUSDT", "TRXUSDT",
    # 11-20
    "LINKUSDT", "MATICUSDT", "ATOMUSDT", "LTCUSDT", "UNIUSDT",
    "APTUSDT", "NEARUSDT", "ICPUSDT", "FILUSDT", "ETCUSDT",
    # 21-30
    "XLMUSDT", "VETUSDT", "HBARUSDT", "ALGOUSDT", "FTMUSDT",
    "SANDUSDT", "MANAUSDT", "AXSUSDT", "THETAUSDT", "EGLDUSDT",
    # 31-40
    "EOSUSDT", "AAVEUSDT", "GRTUSDT", "MKRUSDT", "SNXUSDT",
    "COMPUSDT", "CRVUSDT", "LDOUSDT", "RNDRUSDT", "INJUSDT",
    # 41-50
    "SUIUSDT", "SEIUSDT", "TIAUSDT", "OPUSDT", "ARBUSDT",
    "PEPEUSDT", "SHIBUSDT", "WIFUSDT", "BONKUSDT", "FLOKIUSDT",
    # 51-60
    "RUNEUSDT", "FETUSDT", "OCEANUSDT", "IMXUSDT",
    "GALAUSDT", "APEUSDT", "CHZUSDT", "ENJUSDT", "LRCUSDT",
    # 61-70
    "DYDXUSDT", "GMXUSDT", "PENDLEUSDT", "JUPUSDT",
    "STXUSDT", "BLURUSDT", "CFXUSDT",
    # 71-80
    "ZILUSDT", "KAVAUSDT", "MINAUSDT", "ROSEUSDT", "FLOWUSDT",
    "QNTUSDT", "XTZUSDT", "NEOUSDT", "IOSTUSDT", "ZECUSDT",
    # 81-90
    "DASHUSDT", "BATUSDT", "ONEUSDT", "HOTUSDT", "CELRUSDT",
    "IOTAUSDT", "ONTUSDT", "WAVESUSDT", "SKLUSDT", "ANKRUSDT",
    # 91-100
    "1INCHUSDT", "SUSHIUSDT", "YFIUSDT", "BALUSDT", "BANDUSDT",
    "KSMUSDT", "COTIUSDT", "RVNUSDT", "CHRUSDT", "CELOUSDT",
]

# === SIGNAL SETTINGS ===
# Timeframe for analysis
TIMEFRAME = "1h"  # 1h, 4h, 1d

# RSI Settings
RSI_PERIOD = 14
RSI_OVERSOLD = 30      # Below this = BUY signal
RSI_OVERBOUGHT = 70    # Above this = SELL signal

# MACD Settings
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# EMA Settings
EMA_SHORT = 9
EMA_LONG = 21

# Minimum signal strength (how many indicators must agree)
# 1 = any single indicator triggers signal
# 2 = at least 2 indicators must agree
# 3 = all 3 must agree (most conservative)
MIN_SIGNAL_STRENGTH = 2

# Take Profit & Stop Loss (percentage)
TAKE_PROFIT_PERCENT = 3.0   # 3% profit target
STOP_LOSS_PERCENT = 1.5     # 1.5% stop loss

# === SCAN INTERVAL ===
SCAN_INTERVAL_SECONDS = 600  # Check every 10 minutes (100 coins takes ~5 min to scan)

# === PATHS ===
TEMP_DIR = "temp"

# === MESSAGE SETTINGS ===
BOT_NAME = "SignalX"

# === ADMIN SETTINGS ===
# Your Telegram user ID (get from @userinfobot)
ADMIN_USER_ID = 123456789  # Change this to your Telegram user ID
