"""
Hashtag Generator
==================
Generates random trending hashtags for tweets.
More hashtags = more reach on Twitter/X.
"""

import random

# Core crypto hashtags (always include 3-4 of these)
CRYPTO_CORE = [
    "#crypto", "#cryptocurrency", "#bitcoin", "#BTC", "#ethereum", "#ETH",
    "#altcoins", "#cryptotrading", "#trading", "#trader", "#forex",
    "#cryptosignals", "#signals", "#binance", "#defi", "#web3",
    "#blockchain", "#cryptonews", "#cryptomarket", "#btcusdt",
]

# Trending/viral hashtags
TRENDING = [
    "#ElonMusk", "#money", "#rich", "#millionaire", "#billionaire",
    "#passive income", "#financialfreedom", "#investing", "#investment",
    "#stockmarket", "#wallstreet", "#daytrading", "#swingtrading",
    "#makemoney", "#earnmoney", "#sidehustle", "#hustle",
    "#motivation", "#success", "#wealth", "#profit", "#gains",
]

# Coin specific hashtags
COIN_TAGS = [
    "#BTC", "#ETH", "#SOL", "#XRP", "#DOGE", "#ADA", "#AVAX",
    "#DOT", "#LINK", "#MATIC", "#BNB", "#ATOM", "#UNI", "#APT",
    "#SUI", "#ARB", "#OP", "#PEPE", "#SHIB", "#NEAR", "#FTM",
    "#INJ", "#TIA", "#SEI", "#BONK", "#WIF", "#FLOKI", "#RUNE",
]

# Engagement hashtags (get more likes/retweets)
ENGAGEMENT = [
    "#100x", "#1000x", "#gem", "#moonshot", "#bullish", "#bearish",
    "#pump", "#rally", "#breakout", "#altseason", "#bullrun",
    "#hodl", "#diamond", "#tothemoon", "#lambo", "#wagmi",
    "#nfa", "#dyor", "#fomo", "#buythedip", "#cryptolife",
]

# People/influencer tags (increases visibility)
PEOPLE = [
    "#ElonMusk", "#CZ", "#Vitalik", "#SBF", "#crypto Twitter",
    "#CryptoX", "#FinTwit", "#TradingView", "#Binance",
    "#Coinbase", "#Bybit", "#OKX", "#KuCoin",
]

# Time-based hashtags
TIME_BASED = [
    "#today", "#now", "#live", "#breaking", "#alert",
    "#update", "#new", "#hot", "#trending", "#viral",
]


def generate_hashtags(coin=None, count=15):
    """
    Generate a random set of hashtags for a tweet.
    
    Args:
        coin: Optional coin name (e.g., "BTC") to include specific tag
        count: Total number of hashtags to include
    
    Returns:
        String of hashtags
    """
    tags = set()
    
    # Always include some core crypto tags (3-4)
    tags.update(random.sample(CRYPTO_CORE, min(4, len(CRYPTO_CORE))))
    
    # Add coin-specific tag if provided
    if coin:
        tags.add(f"#{coin}")
        tags.add(f"#{coin}USDT")
    
    # Add from each category
    tags.update(random.sample(TRENDING, min(3, len(TRENDING))))
    tags.update(random.sample(ENGAGEMENT, min(3, len(ENGAGEMENT))))
    tags.update(random.sample(PEOPLE, min(2, len(PEOPLE))))
    tags.update(random.sample(TIME_BASED, min(2, len(TIME_BASED))))
    tags.update(random.sample(COIN_TAGS, min(2, len(COIN_TAGS))))
    
    # Shuffle and limit
    tags_list = list(tags)
    random.shuffle(tags_list)
    
    return " ".join(tags_list[:count])
