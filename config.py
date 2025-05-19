# --- config.py ---
"""
Configuration settings for the Options Strategy Calculator application.
Centralizes constants, themes, and other configuration parameters.
"""
import os
from pathlib import Path
from datetime import datetime

# Application information
APP_NAME = "Options Strategy Calculator"
APP_VERSION = "2.1.0"
APP_DESCRIPTION = "A comprehensive Python-based web application for analyzing and visualizing options trading strategies using real-time market data."
APP_AUTHOR = "Options Analyzer Team"

# File paths
BASE_DIR = Path(__file__).parent.absolute()
LOGS_DIR = BASE_DIR / "logs"
ASSETS_DIR = BASE_DIR / "assets"
STYLES_DIR = BASE_DIR / "styles"
DATA_DIR = BASE_DIR / "data"

# Ensure directories exist
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(STYLES_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = LOGS_DIR / f"app_{datetime.now().strftime('%Y%m%d')}.log"

# API and data fetching settings
API_TIMEOUT = 30  # seconds
CACHE_TTL = 300  # seconds (5 minutes)
MAX_RETRIES = 3
RETRY_BACKOFF = 2  # seconds

# User interface settings
DEFAULT_THEME = "light"
THEMES = {
    "light": {
        "primary_color": "#1E88E5",
        "secondary_color": "#424242",
        "background_color": "#FFFFFF",
        "text_color": "#212121",
        "profit_color": "#4CAF50",
        "loss_color": "#F44336",
        "neutral_color": "#757575",
    },
    "dark": {
        "primary_color": "#90CAF9",
        "secondary_color": "#E0E0E0",
        "background_color": "#121212",
        "text_color": "#EEEEEE",
        "profit_color": "#81C784",
        "loss_color": "#E57373",
        "neutral_color": "#B0BEC5",
    }
}

# Chart settings
CHART_HEIGHT = 500
CHART_TEMPLATE = "plotly_white"  # For light mode
CHART_TEMPLATE_DARK = "plotly_dark"  # For dark mode
CHART_COLORS = {
    "expiration": "#1F77B4",  # Blue
    "current": "#2CA02C",     # Green
    "breakeven": "#7F7F7F",   # Gray
    "current_price": "#D62728",  # Red
    "zero_line": "#000000",   # Black
    "profit_region": "rgba(0, 255, 0, 0.1)",  # Light green
    "loss_region": "rgba(255, 0, 0, 0.1)",    # Light red
}

# Pricing model settings
DEFAULT_RISK_FREE_RATE = 0.03  # 3%
DEFAULT_VOLATILITY = 0.30      # 30%
DEFAULT_DIVIDEND_YIELD = 0.0   # 0%
PRICING_METHODS = ["black_scholes", "binomial", "monte_carlo"]
DEFAULT_PRICING_METHOD = "black_scholes"
BINOMIAL_STEPS = 100
MONTE_CARLO_PATHS = 10000

# Strategy default settings
DEFAULT_QUANTITY = 1
DEFAULT_PRICE_RANGE_PCT = 0.25  # 25% up and down from current price
MIN_PRICE_POINTS = 50
MAX_PRICE_POINTS = 200
DEFAULT_PRICE_POINTS = 100

# Strategy categories and types mapping (for UI display)
STRATEGY_CATEGORIES = {
    "Basic Strategies": [
        "Long Call",
        "Long Put",
        "Covered Call",
        "Cash Secured Put",
        "Naked Call",
        "Naked Put"
    ],
    "Spread Strategies": [
        "Bull Call Spread",
        "Bear Put Spread",
        "Bull Put Credit Spread",
        "Bear Call Credit Spread",
        "Calendar Spread",
        "Poor Man's Covered Call",
        "Ratio Back Spread"
    ],
    "Advanced Strategies": [
        "Iron Condor",
        "Butterfly",
        "Straddle", 
        "Strangle",
        "Collar",
        "Diagonal Spread",
        "Double Diagonal Spread"
    ],
    "Custom Strategies": [
        "Custom - 2 Legs",
        "Custom - 3 Legs",
        "Custom - 4 Legs"
    ]
}

# Strategy name to function name mapping
STRATEGY_NAME_TO_TYPE = {
    "Long Call": "long_call",
    "Long Put": "long_put",
    "Covered Call": "covered_call",
    "Cash Secured Put": "cash_secured_put",
    "Naked Call": "naked_call",
    "Naked Put": "naked_put",
    "Bull Call Spread": "bull_call_spread",
    "Bear Put Spread": "bear_put_spread",
    "Bull Put Credit Spread": "bull_put_spread",
    "Bear Call Credit Spread": "bear_call_spread",
    "Calendar Spread": "calendar_spread",
    "Poor Man's Covered Call": "poor_mans_covered_call",
    "Ratio Back Spread": "ratio_backspread",
    "Iron Condor": "iron_condor",
    "Butterfly": "butterfly",
    "Straddle": "straddle",
    "Strangle": "strangle",
    "Collar": "collar",
    "Diagonal Spread": "diagonal_spread",
    "Double Diagonal Spread": "double_diagonal_spread",
    "Custom - 2 Legs": "custom",
    "Custom - 3 Legs": "custom",
    "Custom - 4 Legs": "custom"
}

# Help text for strategy information - Updated to ensure all strategies have descriptions
STRATEGY_INFO = {
    "Long Call": """
        **Long Call**: Buy a call option to profit from a rise in the stock price.
        
        - **Max Loss**: Limited to premium paid
        - **Max Gain**: Unlimited (stock price - strike - premium)
        - **Breakeven**: Strike price + premium
        - **When to Use**: Bullish outlook, want leverage
        - **Example**: Buy 1 XYZ $50 Call for $2.00
    """,
    "Long Put": """
        **Long Put**: Buy a put option to profit from a fall in the stock price.
        
        - **Max Loss**: Limited to premium paid
        - **Max Gain**: Limited to (strike - premium) if stock goes to zero
        - **Breakeven**: Strike price - premium
        - **When to Use**: Bearish outlook, hedge long stock positions
        - **Example**: Buy 1 XYZ $50 Put for $2.00
    """,
    "Covered Call": """
        **Covered Call**: Own stock and sell a call against it.
        
        - **Max Loss**: Stock price can fall to zero, offset by premium
        - **Max Gain**: Limited to (strike - stock purchase price + premium)
        - **Breakeven**: Stock purchase price - premium
        - **When to Use**: Slightly bullish or neutral, generate income
        - **Example**: Own 100 shares of XYZ at $48, sell 1 XYZ $50 Call for $2.00
    """,
    "Cash Secured Put": """
        **Cash Secured Put**: Sell a put option and set aside enough cash to buy the stock if assigned.
        
        - **Max Loss**: Limited to (strike - premium) if stock goes to zero
        - **Max Gain**: Limited to premium received
        - **Breakeven**: Strike price - premium
        - **When to Use**: Bullish to neutral, willing to buy stock at lower price
        - **Example**: Sell 1 XYZ $45 Put for $2.00
    """,
    "Naked Call": """
        **Naked Call**: Sell a call option without owning the underlying stock.
        
        - **Max Loss**: Unlimited (stock can rise indefinitely)
        - **Max Gain**: Limited to premium received
        - **Breakeven**: Strike price + premium
        - **When to Use**: Very bearish to neutral, high-risk strategy
        - **Example**: Sell 1 XYZ $55 Call for $1.00
    """,
    "Naked Put": """
        **Naked Put**: Sell a put option without setting aside cash to buy the stock.
        
        - **Max Loss**: Limited to (strike - premium) if stock goes to zero
        - **Max Gain**: Limited to premium received
        - **Breakeven**: Strike price - premium
        - **When to Use**: Bullish, similar to Cash Secured Put but with margin
        - **Example**: Sell 1 XYZ $45 Put for $2.00
    """,
    "Bull Call Spread": """
        **Bull Call Spread**: Buy a call at a lower strike and sell a call at a higher strike.
        
        - **Max Loss**: Limited to the net debit paid
        - **Max Gain**: Limited to (higher strike - lower strike - net debit)
        - **Breakeven**: Lower strike + net debit
        - **When to Use**: Moderately bullish, defined risk/reward
        - **Example**: Buy XYZ $45 Call for $3.00, sell XYZ $50 Call for $1.00
    """,
    "Bear Put Spread": """
        **Bear Put Spread**: Buy a put at a higher strike and sell a put at a lower strike.
        
        - **Max Loss**: Limited to the net debit paid
        - **Max Gain**: Limited to (higher strike - lower strike - net debit)
        - **Breakeven**: Higher strike - net debit
        - **When to Use**: Moderately bearish, defined risk/reward
        - **Example**: Buy XYZ $50 Put for $3.00, sell XYZ $45 Put for $1.00
    """,
    "Bull Put Credit Spread": """
        **Bull Put Credit Spread**: Sell a put at a higher strike and buy a put at a lower strike.
        
        - **Max Loss**: Limited to (higher strike - lower strike - net credit)
        - **Max Gain**: Limited to the net credit received
        - **Breakeven**: Higher strike - net credit
        - **When to Use**: Bullish to neutral, profit from time decay
        - **Example**: Sell XYZ $45 Put for $2.00, buy XYZ $40 Put for $1.00
    """,
    "Bear Call Credit Spread": """
        **Bear Call Credit Spread**: Sell a call at a lower strike and buy a call at a higher strike.
        
        - **Max Loss**: Limited to (higher strike - lower strike - net credit)
        - **Max Gain**: Limited to the net credit received
        - **Breakeven**: Lower strike + net credit
        - **When to Use**: Bearish to neutral, profit from time decay
        - **Example**: Sell XYZ $45 Call for $2.00, buy XYZ $50 Call for $1.00
    """,
    "Calendar Spread": """
        **Calendar Spread**: Sell a near-term option and buy a farther-term option at the same strike.
        
        - **Max Loss**: Limited to the net debit paid
        - **Max Gain**: Varies based on underlying price at near-term expiration
        - **Breakeven**: Varies, typically near the strike price at near-term expiration
        - **When to Use**: Neutral, expecting little movement in the near term
        - **Example**: Sell XYZ $50 Call expiring in 1 month for $1.50, buy XYZ $50 Call expiring in 3 months for $3.00
    """,
    "Poor Man's Covered Call": """
        **Poor Man's Covered Call**: Buy a deep ITM long-term call and sell an OTM short-term call.
        
        - **Max Loss**: Limited to the net debit paid for the long call minus credit received
        - **Max Gain**: Limited to (short call strike - long call strike) + (credit received - debit paid)
        - **Breakeven**: Long call strike + net debit
        - **When to Use**: Similar to covered call but requires less capital
        - **Example**: Buy XYZ $40 Call expiring in 6 months for $12.00, sell XYZ $55 Call expiring in 1 month for $1.00
    """,
    "Ratio Back Spread": """
        **Ratio Back Spread**: Sell 1 option at a lower strike and buy multiple options at a higher strike.
        
        - **Max Loss**: Occurs between the two strikes
        - **Max Gain**: Potentially unlimited on the upside (for call ratio spreads)
        - **Breakeven**: Complex, depends on ratio and premiums
        - **When to Use**: Expecting a large move in one direction
        - **Example**: Sell 1 XYZ $50 Call for $2.00, buy 2 XYZ $55 Calls for $1.00 each
    """,
    "Iron Condor": """
        **Iron Condor**: A combination of a bull put spread and a bear call spread.
        
        - **Max Loss**: Limited to (width of either spread - net credit)
        - **Max Gain**: Limited to the net credit received
        - **Breakeven**: Lower call strike + net credit AND higher put strike - net credit
        - **When to Use**: Neutral outlook, expect price to stay within a range
        - **Example**: Sell XYZ $45 Put for $2.00, buy XYZ $40 Put for $1.00, 
                       sell XYZ $55 Call for $2.00, buy XYZ $60 Call for $1.00
    """,
    "Butterfly": """
        **Butterfly**: Buy one lower strike option, sell two middle strike options, buy one higher strike option.
        
        - **Max Loss**: Limited to the net debit paid
        - **Max Gain**: Limited to (middle strike - lower strike - net debit)
        - **Breakeven**: Lower strike + net debit AND higher strike - net debit
        - **When to Use**: Neutral, expect price to be near middle strike at expiration
        - **Example**: Buy XYZ $40 Call for $5.00, sell 2 XYZ $50 Calls for $2.00 each, 
                       buy XYZ $60 Call for $0.50
    """,
    "Straddle": """
        **Straddle**: Buy a call and a put at the same strike and expiration.
        
        - **Max Loss**: Limited to the total premium paid
        - **Max Gain**: Unlimited (stock moves far in either direction)
        - **Breakeven**: Strike + total premium AND Strike - total premium
        - **When to Use**: Expecting significant movement but unsure of direction
        - **Example**: Buy XYZ $50 Call for $2.00 and XYZ $50 Put for $2.00
    """,
    "Strangle": """
        **Strangle**: Buy an OTM call and an OTM put with the same expiration.
        
        - **Max Loss**: Limited to the total premium paid
        - **Max Gain**: Unlimited (stock moves far in either direction)
        - **Breakeven**: Call strike + total premium AND Put strike - total premium
        - **When to Use**: Expecting significant movement but unsure of direction, cheaper than a straddle
        - **Example**: Buy XYZ $55 Call for $1.00 and XYZ $45 Put for $1.00
    """,
    "Collar": """
        **Collar**: Own stock, buy a protective put, and sell a covered call.
        
        - **Max Loss**: Limited to (stock price - put strike + net premium)
        - **Max Gain**: Limited to (call strike - stock price - net premium)
        - **Breakeven**: Stock price + net premium
        - **When to Use**: Protect a long stock position with limited cost
        - **Example**: Own XYZ at $50, buy XYZ $45 Put for $1.00, sell XYZ $55 Call for $1.00
    """,
    "Diagonal Spread": """
        **Diagonal Spread**: Buy a longer-term option at one strike and sell a shorter-term option at a different strike.
        
        - **Max Loss**: Limited to the net debit paid
        - **Max Gain**: Varies based on underlying price movements
        - **Breakeven**: Complex, depends on stock price at near-term expiration
        - **When to Use**: Exploiting term structure of volatility, reducing cost of long options
        - **Example**: Buy XYZ $50 Call expiring in 3 months for $3.00, sell XYZ $55 Call expiring in 1 month for $1.00
    """,
    "Double Diagonal Spread": """
        **Double Diagonal Spread**: Combines a put diagonal spread and a call diagonal spread.
        
        - **Max Loss**: Limited to the net debit paid
        - **Max Gain**: Varies based on the underlying price at near-term expiration
        - **Breakeven**: Complex, multiple break-even points
        - **When to Use**: Neutral with expectation of increased volatility
        - **Example**: Buy XYZ $45 Put expiring in 3 months, sell XYZ $50 Put expiring in 1 month,
                      sell XYZ $55 Call expiring in 1 month, buy XYZ $60 Call expiring in 3 months
    """,
    "Custom - 2 Legs": """
        **Custom 2-Leg Strategy**: Build your own strategy with 2 legs.
        
        - Configure each leg with option type, position (long/short), strike, quantity, and more
        - Mix and match calls, puts, and stock positions
        - Analyze complex or non-standard strategies
        - Create strategies with multiple expirations
    """,
    "Custom - 3 Legs": """
        **Custom 3-Leg Strategy**: Build your own strategy with 3 legs.
        
        - Configure each leg with option type, position (long/short), strike, quantity, and more
        - Mix and match calls, puts, and stock positions
        - Analyze complex or non-standard strategies
        - Create strategies with multiple expirations
    """,
    "Custom - 4 Legs": """
        **Custom 4-Leg Strategy**: Build your own strategy with 4 legs.
        
        - Configure each leg with option type, position (long/short), strike, quantity, and more
        - Mix and match calls, puts, and stock positions
        - Analyze complex or non-standard strategies
        - Create strategies with multiple expirations
    """
}

# Example tickers for demonstration
EXAMPLE_TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "SPY", "QQQ", "IWM"]