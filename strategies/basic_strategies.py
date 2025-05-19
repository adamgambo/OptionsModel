# --- strategies/basic_strategies.py ---
"""
Basic options strategy implementations.
These are single or dual-leg strategies like long calls/puts, covered calls, etc.
"""
import logging

logger = logging.getLogger(__name__)

def long_call_strategy(strike, expiration, premium=0.0, current_premium=None, quantity=1, iv=0.3):
    """
    Long Call Strategy: Purchase a call option, profit from price increase.
    
    Parameters:
        strike (float): Strike price of the call option
        expiration (str): Expiration date in YYYY-MM-DD format
        premium (float): Entry premium paid for the option
        current_premium (float): Current market premium of the option
        quantity (int): Number of contracts
        iv (float): Implied volatility
        
    Returns:
        list: List of strategy leg dictionaries
    """
    # Use current_premium as premium if not provided separately
    if current_premium is None:
        current_premium = premium
        
    return [{
        'type': 'call',
        'position': 'long',
        'strike': strike,
        'expiry': str(expiration),
        'price': premium,
        'current_price': current_premium,
        'quantity': quantity,
        'iv': iv
    }]


def long_put_strategy(strike, expiration, premium=0.0, current_premium=None, quantity=1, iv=0.3):
    """
    Long Put Strategy: Purchase a put option, profit from price decrease.
    
    Parameters:
        strike (float): Strike price of the put option
        expiration (str): Expiration date in YYYY-MM-DD format
        premium (float): Entry premium paid for the option
        current_premium (float): Current market premium of the option
        quantity (int): Number of contracts
        iv (float): Implied volatility
        
    Returns:
        list: List of strategy leg dictionaries
    """
    # Use current_premium as premium if not provided separately
    if current_premium is None:
        current_premium = premium
        
    return [{
        'type': 'put',
        'position': 'long',
        'strike': strike,
        'expiry': str(expiration),
        'price': premium,
        'current_price': current_premium,
        'quantity': quantity,
        'iv': iv
    }]


def covered_call_strategy(stock_price, current_stock_price=None, call_strike=None, 
                         expiration=None, call_premium=0.0, current_call_premium=None, 
                         quantity=1, iv=0.3):
    """
    Covered Call Strategy: Own stock and sell a call against it. Generate income but cap upside.
    
    Parameters:
        stock_price (float): Purchase price of the stock
        current_stock_price (float): Current market price of the stock
        call_strike (float): Strike price of the call option
        expiration (str): Expiration date in YYYY-MM-DD format
        call_premium (float): Entry premium received for selling the call
        current_call_premium (float): Current market premium of the call
        quantity (int): Number of contracts (each represents 100 shares)
        iv (float): Implied volatility of the call option
        
    Returns:
        list: List of strategy leg dictionaries
    """
    # Use stock_price as current_stock_price if not provided separately
    if current_stock_price is None:
        current_stock_price = stock_price
        
    # Use call_premium as current_call_premium if not provided separately
    if current_call_premium is None:
        current_call_premium = call_premium
        
    return [
        {
            'type': 'stock',
            'position': 'long',
            'price': stock_price,
            'current_price': current_stock_price,
            'quantity': 100 * quantity  # 100 shares per contract
        },
        {
            'type': 'call',
            'position': 'short',
            'strike': call_strike,
            'expiry': str(expiration),
            'price': call_premium,
            'current_price': current_call_premium,
            'quantity': quantity,
            'iv': iv
        }
    ]


def cash_secured_put_strategy(strike, expiration, premium=0.0, current_premium=None, quantity=1, iv=0.3):
    """
    Cash Secured Put Strategy: Sell a put option and set aside cash to purchase shares if assigned.
    Generate income and potentially buy stock at a lower price.
    
    Parameters:
        strike (float): Strike price of the put option
        expiration (str): Expiration date in YYYY-MM-DD format
        premium (float): Entry premium received for selling the put
        current_premium (float): Current market premium of the put
        quantity (int): Number of contracts
        iv (float): Implied volatility
        
    Returns:
        list: List of strategy leg dictionaries
    """
    # Use premium as current_premium if not provided separately
    if current_premium is None:
        current_premium = premium
        
    return [{
        'type': 'put',
        'position': 'short',
        'strike': strike,
        'expiry': str(expiration),
        'price': premium,
        'current_price': current_premium,
        'quantity': quantity,
        'iv': iv,
        'cash_secured': True  # Flag as cash secured for analysis
    }]


def naked_call_strategy(strike, expiration, premium=0.0, current_premium=None, quantity=1, iv=0.3):
    """
    Naked Call Strategy: Sell a call option without owning the underlying stock.
    High risk strategy with unlimited potential loss.
    
    Parameters:
        strike (float): Strike price of the call option
        expiration (str): Expiration date in YYYY-MM-DD format
        premium (float): Entry premium received for selling the call
        current_premium (float): Current market premium of the call
        quantity (int): Number of contracts
        iv (float): Implied volatility
        
    Returns:
        list: List of strategy leg dictionaries
    """
    # Use premium as current_premium if not provided separately
    if current_premium is None:
        current_premium = premium
        
    return [{
        'type': 'call',
        'position': 'short',
        'strike': strike,
        'expiry': str(expiration),
        'price': premium,
        'current_price': current_premium,
        'quantity': quantity,
        'iv': iv
    }]


def naked_put_strategy(strike, expiration, premium=0.0, current_premium=None, quantity=1, iv=0.3):
    """
    Naked Put Strategy: Sell a put option without setting aside cash to buy the stock.
    
    Parameters:
        strike (float): Strike price of the put option
        expiration (str): Expiration date in YYYY-MM-DD format
        premium (float): Entry premium received for selling the put
        current_premium (float): Current market premium of the put
        quantity (int): Number of contracts
        iv (float): Implied volatility
        
    Returns:
        list: List of strategy leg dictionaries
    """
    # Use premium as current_premium if not provided separately
    if current_premium is None:
        current_premium = premium
        
    return [{
        'type': 'put',
        'position': 'short',
        'strike': strike,
        'expiry': str(expiration),
        'price': premium,
        'current_price': current_premium,
        'quantity': quantity,
        'iv': iv,
        'cash_secured': False  # Flag as not cash secured for analysis
    }]
