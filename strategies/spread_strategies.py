# --- strategies/spread_strategies.py ---
"""
Spread strategy implementations.
These are multi-leg strategies involving two or more options of the same type
but with different strikes or expirations.
"""
import logging

logger = logging.getLogger(__name__)

def bull_call_spread(long_strike, short_strike, expiration, 
                    long_premium=0.0, short_premium=0.0,
                    current_long_premium=None, current_short_premium=None,
                    quantity=1, long_iv=0.3, short_iv=0.3):
    """
    Bull Call Spread: Buy a call at a lower strike, sell a call at a higher strike.
    Limited risk, limited reward, bullish outlook.
    
    Parameters:
        long_strike (float): Strike price of the long call
        short_strike (float): Strike price of the short call
        expiration (str): Expiration date in YYYY-MM-DD format
        long_premium (float): Entry premium paid for the long call
        short_premium (float): Entry premium received for the short call
        current_long_premium (float): Current market premium of the long call
        current_short_premium (float): Current market premium of the short call
        quantity (int): Number of spreads
        long_iv (float): Implied volatility of the long call
        short_iv (float): Implied volatility of the short call
        
    Returns:
        list: List of strategy leg dictionaries
    """
    if long_strike >= short_strike:
        raise ValueError("Long call strike must be less than short call strike for a bull call spread")
    
    # Use entry premiums as current premiums if not provided separately
    if current_long_premium is None:
        current_long_premium = long_premium
    if current_short_premium is None:
        current_short_premium = short_premium
    
    return [
        {
            'type': 'call',
            'position': 'long',
            'strike': long_strike,
            'expiry': str(expiration),
            'price': long_premium,
            'current_price': current_long_premium,
            'quantity': quantity,
            'iv': long_iv
        },
        {
            'type': 'call',
            'position': 'short',
            'strike': short_strike,
            'expiry': str(expiration),
            'price': short_premium,
            'current_price': current_short_premium,
            'quantity': quantity,
            'iv': short_iv
        }
    ]

def bear_put_spread(long_strike, short_strike, expiration, 
                   long_premium=0.0, short_premium=0.0,
                   current_long_premium=None, current_short_premium=None,
                   quantity=1, long_iv=0.3, short_iv=0.3):
    """
    Bear Put Spread: Buy a put at a higher strike, sell a put at a lower strike.
    Limited risk, limited reward, bearish outlook.
    
    Parameters:
        long_strike (float): Strike price of the long put (higher strike)
        short_strike (float): Strike price of the short put (lower strike)
        expiration (str): Expiration date in YYYY-MM-DD format
        long_premium (float): Entry premium paid for the long put
        short_premium (float): Entry premium received for the short put
        current_long_premium (float): Current market premium of the long put
        current_short_premium (float): Current market premium of the short put
        quantity (int): Number of spreads
        long_iv (float): Implied volatility of the long put
        short_iv (float): Implied volatility of the short put
        
    Returns:
        list: List of strategy leg dictionaries
    """
    if long_strike <= short_strike:
        raise ValueError("Long put strike must be greater than short put strike for a bear put spread")
    
    # Use entry premiums as current premiums if not provided separately
    if current_long_premium is None:
        current_long_premium = long_premium
    if current_short_premium is None:
        current_short_premium = short_premium
    
    return [
        {
            'type': 'put',
            'position': 'long',
            'strike': long_strike,
            'expiry': str(expiration),
            'price': long_premium,
            'current_price': current_long_premium,
            'quantity': quantity,
            'iv': long_iv
        },
        {
            'type': 'put',
            'position': 'short',
            'strike': short_strike,
            'expiry': str(expiration),
            'price': short_premium,
            'current_price': current_short_premium,
            'quantity': quantity,
            'iv': short_iv
        }
    ]

def bull_put_spread(short_put_strike, long_put_strike, expiration, 
                   short_put_premium=0.0, long_put_premium=0.0,
                   current_short_put_premium=None, current_long_put_premium=None,
                   quantity=1, short_put_iv=0.3, long_put_iv=0.3):
    """
    Bull Put Spread: Sell a put at a higher strike, buy a put at a lower strike.
    Credit spread with limited risk and reward, bullish outlook.
    
    Parameters:
        short_put_strike (float): Strike price of the short put (higher strike)
        long_put_strike (float): Strike price of the long put (lower strike)
        expiration (str): Expiration date in YYYY-MM-DD format
        short_put_premium (float): Entry premium received for selling the put
        long_put_premium (float): Entry premium paid for buying the put
        current_short_put_premium (float): Current market premium of the short put
        current_long_put_premium (float): Current market premium of the long put
        quantity (int): Number of spreads
        short_put_iv (float): Implied volatility of the short put
        long_put_iv (float): Implied volatility of the long put
        
    Returns:
        list: List of strategy leg dictionaries
    """
    if short_put_strike <= long_put_strike:
        raise ValueError("Short put strike must be greater than long put strike for a bull put spread")
    
    # Use entry premiums as current premiums if not provided separately
    if current_short_put_premium is None:
        current_short_put_premium = short_put_premium
    if current_long_put_premium is None:
        current_long_put_premium = long_put_premium
    
    return [
        {
            'type': 'put',
            'position': 'short',
            'strike': short_put_strike,
            'expiry': str(expiration),
            'price': short_put_premium,
            'current_price': current_short_put_premium,
            'quantity': quantity,
            'iv': short_put_iv
        },
        {
            'type': 'put',
            'position': 'long',
            'strike': long_put_strike,
            'expiry': str(expiration),
            'price': long_put_premium,
            'current_price': current_long_put_premium,
            'quantity': quantity,
            'iv': long_put_iv
        }
    ]

def bear_call_spread(short_call_strike, long_call_strike, expiration, 
                    short_call_premium=0.0, long_call_premium=0.0,
                    current_short_call_premium=None, current_long_call_premium=None,
                    quantity=1, short_call_iv=0.3, long_call_iv=0.3):
    """
    Bear Call Spread: Sell a call at a lower strike, buy a call at a higher strike.
    Credit spread with limited risk and reward, bearish outlook.
    
    Parameters:
        short_call_strike (float): Strike price of the short call (lower strike)
        long_call_strike (float): Strike price of the long call (higher strike)
        expiration (str): Expiration date in YYYY-MM-DD format
        short_call_premium (float): Entry premium received for selling the call
        long_call_premium (float): Entry premium paid for buying the call
        current_short_call_premium (float): Current market premium of the short call
        current_long_call_premium (float): Current market premium of the long call
        quantity (int): Number of spreads
        short_call_iv (float): Implied volatility of the short call
        long_call_iv (float): Implied volatility of the long call
        
    Returns:
        list: List of strategy leg dictionaries
    """
    if short_call_strike >= long_call_strike:
        raise ValueError("Short call strike must be less than long call strike for a bear call spread")
    
    # Use entry premiums as current premiums if not provided separately
    if current_short_call_premium is None:
        current_short_call_premium = short_call_premium
    if current_long_call_premium is None:
        current_long_call_premium = long_call_premium
    
    return [
        {
            'type': 'call',
            'position': 'short',
            'strike': short_call_strike,
            'expiry': str(expiration),
            'price': short_call_premium,
            'current_price': current_short_call_premium,
            'quantity': quantity,
            'iv': short_call_iv
        },
        {
            'type': 'call',
            'position': 'long',
            'strike': long_call_strike,
            'expiry': str(expiration),
            'price': long_call_premium,
            'current_price': current_long_call_premium,
            'quantity': quantity,
            'iv': long_call_iv
        }
    ]

def calendar_spread(strike, near_expiration, far_expiration, 
                   near_premium=0.0, far_premium=0.0,
                   current_near_premium=None, current_far_premium=None,
                   option_type='call', quantity=1, 
                   near_iv=0.3, far_iv=0.3):
    """
    Calendar Spread: Sell a near-term option and buy a longer-term option at the same strike.
    Profit from time decay differential, neutral outlook.
    
    Parameters:
        strike (float): Strike price for both options
        near_expiration (str): Expiration date of the short option in YYYY-MM-DD format
        far_expiration (str): Expiration date of the long option in YYYY-MM-DD format
        near_premium (float): Entry premium received for the near-term option
        far_premium (float): Entry premium paid for the far-term option
        current_near_premium (float): Current market premium of the near-term option
        current_far_premium (float): Current market premium of the far-term option
        option_type (str): 'call' or 'put'
        quantity (int): Number of spreads
        near_iv (float): Implied volatility of the near-term option
        far_iv (float): Implied volatility of the far-term option
        
    Returns:
        list: List of strategy leg dictionaries
    """
    if option_type.lower() not in ['call', 'put']:
        raise ValueError(f"Invalid option type: {option_type}. Use 'call' or 'put'.")
    
    # Use entry premiums as current premiums if not provided separately
    if current_near_premium is None:
        current_near_premium = near_premium
    if current_far_premium is None:
        current_far_premium = far_premium
    
    return [
        {
            'type': option_type.lower(),
            'position': 'short',
            'strike': strike,
            'expiry': str(near_expiration),
            'price': near_premium,
            'current_price': current_near_premium,
            'quantity': quantity,
            'iv': near_iv
        },
        {
            'type': option_type.lower(),
            'position': 'long',
            'strike': strike,
            'expiry': str(far_expiration),
            'price': far_premium,
            'current_price': current_far_premium,
            'quantity': quantity,
            'iv': far_iv
        }
    ]

def poor_mans_covered_call(long_call_strike, short_call_strike, 
                          long_call_exp, short_call_exp,
                          long_call_premium=0.0, short_call_premium=0.0,
                          current_long_call_premium=None, current_short_call_premium=None,
                          quantity=1, long_call_iv=0.3, short_call_iv=0.3):
    """
    Poor Man's Covered Call: Buy a deep ITM LEAP call, sell short-term OTM calls against it.
    Similar to covered call but requires less capital.
    
    Parameters:
        long_call_strike (float): Strike price of the long LEAP call (lower strike)
        short_call_strike (float): Strike price of the short call (higher strike)
        long_call_exp (str): Expiration date of the long LEAP call in YYYY-MM-DD format
        short_call_exp (str): Expiration date of the short call in YYYY-MM-DD format
        long_call_premium (float): Entry premium paid for the long LEAP call
        short_call_premium (float): Entry premium received for the short call
        current_long_call_premium (float): Current market premium of the long LEAP call
        current_short_call_premium (float): Current market premium of the short call
        quantity (int): Number of spreads
        long_call_iv (float): Implied volatility of the long LEAP call
        short_call_iv (float): Implied volatility of the short call
        
    Returns:
        list: List of strategy leg dictionaries
    """
    # Use entry premiums as current premiums if not provided separately
    if current_long_call_premium is None:
        current_long_call_premium = long_call_premium
    if current_short_call_premium is None:
        current_short_call_premium = short_call_premium
    
    return [
        {
            'type': 'call',
            'position': 'long',
            'strike': long_call_strike,
            'expiry': str(long_call_exp),
            'price': long_call_premium,
            'current_price': current_long_call_premium,
            'quantity': quantity,
            'iv': long_call_iv
        },
        {
            'type': 'call',
            'position': 'short',
            'strike': short_call_strike,
            'expiry': str(short_call_exp),
            'price': short_call_premium,
            'current_price': current_short_call_premium,
            'quantity': quantity,
            'iv': short_call_iv
        }
    ]

def ratio_backspread(short_strike, long_strike, expiration,
                    short_premium=0.0, long_premium=0.0,
                    current_short_premium=None, current_long_premium=None,
                    ratio=2, option_type='call', quantity=1, 
                    short_iv=0.3, long_iv=0.3):
    """
    Ratio Backspread: Short 1 option at one strike, long multiple options at another strike.
    For calls: short lower strike, long higher strikes
    For puts: short higher strike, long lower strikes
    
    Parameters:
        short_strike (float): Strike price of the short option
        long_strike (float): Strike price of the long options
        expiration (str): Expiration date in YYYY-MM-DD format
        short_premium (float): Entry premium received for selling the option
        long_premium (float): Entry premium paid for buying each long option
        current_short_premium (float): Current market premium of the short option
        current_long_premium (float): Current market premium of the long options
        ratio (int): Number of long options per short option (typically 2 or 3)
        option_type (str): 'call' or 'put'
        quantity (int): Number of spreads
        short_iv (float): Implied volatility of the short option
        long_iv (float): Implied volatility of the long options
        
    Returns:
        list: List of strategy leg dictionaries
    """
    if option_type.lower() not in ['call', 'put']:
        raise ValueError(f"Invalid option type: {option_type}. Use 'call' or 'put'.")
    
    if ratio < 2:
        raise ValueError("Ratio must be at least 2 for a ratio backspread")
    
    # Validate strike relationships based on option type
    if option_type.lower() == 'call' and short_strike >= long_strike:
        raise ValueError("For call ratio backspread, short strike must be less than long strike")
    elif option_type.lower() == 'put' and short_strike <= long_strike:
        raise ValueError("For put ratio backspread, short strike must be greater than long strike")
    
    # Use entry premiums as current premiums if not provided separately
    if current_short_premium is None:
        current_short_premium = short_premium
    if current_long_premium is None:
        current_long_premium = long_premium
    
    strategy_legs = []
    
    # Add short leg
    strategy_legs.append({
        'type': option_type.lower(),
        'position': 'short',
        'strike': short_strike,
        'expiry': str(expiration),
        'price': short_premium,
        'current_price': current_short_premium,
        'quantity': quantity,
        'iv': short_iv
    })
    
    # Add multiple long legs
    for _ in range(ratio):
        strategy_legs.append({
            'type': option_type.lower(),
            'position': 'long',
            'strike': long_strike,
            'expiry': str(expiration),
            'price': long_premium,
            'current_price': current_long_premium,
            'quantity': quantity,
            'iv': long_iv
        })
    
    return strategy_legs
