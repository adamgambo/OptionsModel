# --- strategies/advanced_strategies.py ---
"""
Advanced options strategy implementations.
These are complex, multi-leg strategies like iron condors, butterflies, etc.
"""
import logging

logger = logging.getLogger(__name__)

def iron_condor(long_put_strike, short_put_strike, short_call_strike, long_call_strike,
               expiration, long_put_premium=0.0, short_put_premium=0.0,
               short_call_premium=0.0, long_call_premium=0.0,
               current_long_put_premium=None, current_short_put_premium=None,
               current_short_call_premium=None, current_long_call_premium=None,
               quantity=1, long_put_iv=0.3, short_put_iv=0.3,
               short_call_iv=0.3, long_call_iv=0.3):
    """
    Iron Condor: Combination of a bull put spread and a bear call spread.
    Profit when the underlying price stays between the short strikes.
    
    Parameters:
        long_put_strike (float): Strike of the long put (lowest strike)
        short_put_strike (float): Strike of the short put
        short_call_strike (float): Strike of the short call
        long_call_strike (float): Strike of the long call (highest strike)
        expiration (str): Expiration date in YYYY-MM-DD format
        long_put_premium (float): Entry premium paid for the long put
        short_put_premium (float): Entry premium received for the short put
        short_call_premium (float): Entry premium received for the short call
        long_call_premium (float): Entry premium paid for the long call
        current_long_put_premium (float): Current market premium of the long put
        current_short_put_premium (float): Current market premium of the short put
        current_short_call_premium (float): Current market premium of the short call
        current_long_call_premium (float): Current market premium of the long call
        quantity (int): Number of iron condors
        long_put_iv (float): Implied volatility of the long put
        short_put_iv (float): Implied volatility of the short put
        short_call_iv (float): Implied volatility of the short call
        long_call_iv (float): Implied volatility of the long call
        
    Returns:
        list: List of strategy leg dictionaries
    """
    if not (long_put_strike < short_put_strike < short_call_strike < long_call_strike):
        raise ValueError("Strike order must be: long put < short put < short call < long call")
    
    # Use entry premiums as current premiums if not provided separately
    if current_long_put_premium is None:
        current_long_put_premium = long_put_premium
    if current_short_put_premium is None:
        current_short_put_premium = short_put_premium
    if current_short_call_premium is None:
        current_short_call_premium = short_call_premium
    if current_long_call_premium is None:
        current_long_call_premium = long_call_premium
    
    # Create the iron condor legs
    return [
        # Bull put spread legs
        {
            'type': 'put',
            'position': 'long',
            'strike': long_put_strike,
            'expiry': str(expiration),
            'price': long_put_premium,
            'current_price': current_long_put_premium,
            'quantity': quantity,
            'iv': long_put_iv
        },
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
        # Bear call spread legs
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

def butterfly(low_strike, mid_strike, high_strike, expiration,
             low_premium=0.0, mid_premium=0.0, high_premium=0.0,
             current_low_premium=None, current_mid_premium=None, current_high_premium=None,
             option_type='call', quantity=1,
             low_iv=0.3, mid_iv=0.3, high_iv=0.3):
    """
    Butterfly Spread: Buy 1 lower strike option, sell 2 middle strike options, buy 1 higher strike option.
    Maximum profit when the stock price is at the middle strike at expiration.
    
    Parameters:
        low_strike (float): Lower strike price
        mid_strike (float): Middle strike price
        high_strike (float): Higher strike price
        expiration (str): Expiration date in YYYY-MM-DD format
        low_premium (float): Entry premium paid for the lower strike option
        mid_premium (float): Entry premium received for each middle strike option
        high_premium (float): Entry premium paid for the higher strike option
        current_low_premium (float): Current market premium of the lower strike option
        current_mid_premium (float): Current market premium of the middle strike option
        current_high_premium (float): Current market premium of the higher strike option
        option_type (str): 'call' or 'put'
        quantity (int): Number of butterflies
        low_iv (float): Implied volatility of the lower strike option
        mid_iv (float): Implied volatility of the middle strike option
        high_iv (float): Implied volatility of the higher strike option
        
    Returns:
        list: List of strategy leg dictionaries
    """
    if option_type.lower() not in ['call', 'put']:
        raise ValueError(f"Invalid option type: {option_type}. Use 'call' or 'put'.")
    
    if not (low_strike < mid_strike < high_strike):
        raise ValueError("Strikes must be in order: low < mid < high")
    
    # Check if strikes are evenly spaced (not required but common)
    if abs((mid_strike - low_strike) - (high_strike - mid_strike)) > 0.01:
        logger.warning("Butterfly strikes are not evenly spaced")
    
    # Use entry premiums as current premiums if not provided separately
    if current_low_premium is None:
        current_low_premium = low_premium
    if current_mid_premium is None:
        current_mid_premium = mid_premium
    if current_high_premium is None:
        current_high_premium = high_premium
    
    return [
        # Lower strike (long)
        {
            'type': option_type.lower(),
            'position': 'long',
            'strike': low_strike,
            'expiry': str(expiration),
            'price': low_premium,
            'current_price': current_low_premium,
            'quantity': quantity,
            'iv': low_iv
        },
        # Middle strike (short) - first contract
        {
            'type': option_type.lower(),
            'position': 'short',
            'strike': mid_strike,
            'expiry': str(expiration),
            'price': mid_premium,
            'current_price': current_mid_premium,
            'quantity': quantity,
            'iv': mid_iv
        },
        # Middle strike (short) - second contract
        {
            'type': option_type.lower(),
            'position': 'short',
            'strike': mid_strike,
            'expiry': str(expiration),
            'price': mid_premium,
            'current_price': current_mid_premium,
            'quantity': quantity,
            'iv': mid_iv
        },
        # Higher strike (long)
        {
            'type': option_type.lower(),
            'position': 'long',
            'strike': high_strike,
            'expiry': str(expiration),
            'price': high_premium,
            'current_price': current_high_premium,
            'quantity': quantity,
            'iv': high_iv
        }
    ]

def straddle(strike, expiration, call_premium=0.0, put_premium=0.0,
            current_call_premium=None, current_put_premium=None,
            quantity=1, call_iv=0.3, put_iv=0.3):
    """
    Straddle: Buy a call and a put at the same strike price and expiration.
    Profit when the underlying price moves significantly in either direction.
    
    Parameters:
        strike (float): Strike price for both options
        expiration (str): Expiration date in YYYY-MM-DD format
        call_premium (float): Entry premium paid for the call
        put_premium (float): Entry premium paid for the put
        current_call_premium (float): Current market premium of the call
        current_put_premium (float): Current market premium of the put
        quantity (int): Number of straddles
        call_iv (float): Implied volatility of the call option
        put_iv (float): Implied volatility of the put option
        
    Returns:
        list: List of strategy leg dictionaries
    """
    # Use entry premiums as current premiums if not provided separately
    if current_call_premium is None:
        current_call_premium = call_premium
    if current_put_premium is None:
        current_put_premium = put_premium
    
    return [
        # Long call
        {
            'type': 'call',
            'position': 'long',
            'strike': strike,
            'expiry': str(expiration),
            'price': call_premium,
            'current_price': current_call_premium,
            'quantity': quantity,
            'iv': call_iv
        },
        # Long put
        {
            'type': 'put',
            'position': 'long',
            'strike': strike,
            'expiry': str(expiration),
            'price': put_premium,
            'current_price': current_put_premium,
            'quantity': quantity,
            'iv': put_iv
        }
    ]

def strangle(put_strike, call_strike, expiration,
            put_premium=0.0, call_premium=0.0,
            current_put_premium=None, current_call_premium=None,
            quantity=1, put_iv=0.3, call_iv=0.3):
    """
    Strangle: Buy an OTM put and an OTM call.
    Profit when the underlying price moves significantly in either direction.
    
    Parameters:
        put_strike (float): Strike price of the put (lower strike)
        call_strike (float): Strike price of the call (higher strike)
        expiration (str): Expiration date in YYYY-MM-DD format
        put_premium (float): Entry premium paid for the put
        call_premium (float): Entry premium paid for the call
        current_put_premium (float): Current market premium of the put
        current_call_premium (float): Current market premium of the call
        quantity (int): Number of strangles
        put_iv (float): Implied volatility of the put option
        call_iv (float): Implied volatility of the call option
        
    Returns:
        list: List of strategy leg dictionaries
    """
    if put_strike >= call_strike:
        raise ValueError("Put strike must be less than call strike for a strangle")
    
    # Use entry premiums as current premiums if not provided separately
    if current_put_premium is None:
        current_put_premium = put_premium
    if current_call_premium is None:
        current_call_premium = call_premium
    
    return [
        # Long OTM put
        {
            'type': 'put',
            'position': 'long',
            'strike': put_strike,
            'expiry': str(expiration),
            'price': put_premium,
            'current_price': current_put_premium,
            'quantity': quantity,
            'iv': put_iv
        },
        # Long OTM call
        {
            'type': 'call',
            'position': 'long',
            'strike': call_strike,
            'expiry': str(expiration),
            'price': call_premium,
            'current_price': current_call_premium,
            'quantity': quantity,
            'iv': call_iv
        }
    ]

def collar(current_stock_price=None, stock_price=None, 
         put_strike=None, call_strike=None, 
         expiration=None, put_premium=0.0, call_premium=0.0,
         current_put_premium=None, current_call_premium=None,
         quantity=1, put_iv=0.3, call_iv=0.3):
    """
    Collar: Long stock, long protective put, short covered call.
    Provides downside protection and generates income, but caps upside potential.
    
    Parameters:
        current_stock_price (float): Current market price of the stock
        stock_price (float): Cost basis of the stock
        put_strike (float): Strike price of the protective put (lower strike)
        call_strike (float): Strike price of the covered call (higher strike)
        expiration (str): Expiration date in YYYY-MM-DD format
        put_premium (float): Entry premium paid for the put
        call_premium (float): Entry premium received for the call
        current_put_premium (float): Current market premium of the put
        current_call_premium (float): Current market premium of the call
        quantity (int): Number of collars (each represents 100 shares)
        put_iv (float): Implied volatility of the put option
        call_iv (float): Implied volatility of the call option
        
    Returns:
        list: List of strategy leg dictionaries
    """
    # Handle stock price parameters
    if stock_price is None and current_stock_price is not None:
        stock_price = current_stock_price
    if current_stock_price is None and stock_price is not None:
        current_stock_price = stock_price
    
    # Use entry premiums as current premiums if not provided separately
    if current_put_premium is None:
        current_put_premium = put_premium
    if current_call_premium is None:
        current_call_premium = call_premium
    
    return [
        # Long stock
        {
            'type': 'stock',
            'position': 'long',
            'price': stock_price,
            'current_price': current_stock_price,
            'quantity': 100 * quantity  # 100 shares per contract
        },
        # Long protective put
        {
            'type': 'put',
            'position': 'long',
            'strike': put_strike,
            'expiry': str(expiration),
            'price': put_premium,
            'current_price': current_put_premium,
            'quantity': quantity,
            'iv': put_iv
        },
        # Short covered call
        {
            'type': 'call',
            'position': 'short',
            'strike': call_strike,
            'expiry': str(expiration),
            'price': call_premium,
            'current_price': current_call_premium,
            'quantity': quantity,
            'iv': call_iv
        }
    ]

def diagonal_spread(long_strike, short_strike, long_expiration, short_expiration,
                   long_premium=0.0, short_premium=0.0,
                   current_long_premium=None, current_short_premium=None,
                   option_type='call', quantity=1,
                   long_iv=0.3, short_iv=0.3):
    """
    Diagonal Spread: Long option with farther expiration at one strike, 
    short option with nearer expiration at another strike.
    
    Parameters:
        long_strike (float): Strike price of the long option
        short_strike (float): Strike price of the short option
        long_expiration (str): Expiration date of the long option in YYYY-MM-DD format
        short_expiration (str): Expiration date of the short option in YYYY-MM-DD format
        long_premium (float): Entry premium paid for the long option
        short_premium (float): Entry premium received for the short option
        current_long_premium (float): Current market premium of the long option
        current_short_premium (float): Current market premium of the short option
        option_type (str): 'call' or 'put'
        quantity (int): Number of spreads
        long_iv (float): Implied volatility of the long option
        short_iv (float): Implied volatility of the short option
        
    Returns:
        list: List of strategy leg dictionaries
    """
    if option_type.lower() not in ['call', 'put']:
        raise ValueError(f"Invalid option type: {option_type}. Use 'call' or 'put'.")
    
    # Use entry premiums as current premiums if not provided separately
    if current_long_premium is None:
        current_long_premium = long_premium
    if current_short_premium is None:
        current_short_premium = short_premium
    
    return [
        # Long farther-term option
        {
            'type': option_type.lower(),
            'position': 'long',
            'strike': long_strike,
            'expiry': str(long_expiration),
            'price': long_premium,
            'current_price': current_long_premium,
            'quantity': quantity,
            'iv': long_iv
        },
        # Short near-term option
        {
            'type': option_type.lower(),
            'position': 'short',
            'strike': short_strike,
            'expiry': str(short_expiration),
            'price': short_premium,
            'current_price': current_short_premium,
            'quantity': quantity,
            'iv': short_iv
        }
    ]

def double_diagonal_spread(put_long_strike, put_short_strike, call_short_strike, call_long_strike,
                          long_expiration, short_expiration,
                          put_long_premium=0.0, put_short_premium=0.0,
                          call_short_premium=0.0, call_long_premium=0.0,
                          current_put_long_premium=None, current_put_short_premium=None,
                          current_call_short_premium=None, current_call_long_premium=None,
                          quantity=1, put_long_iv=0.3, put_short_iv=0.3,
                          call_short_iv=0.3, call_long_iv=0.3):
    """
    Double Diagonal Spread: Combines a put diagonal spread and a call diagonal spread.
    
    Parameters:
        put_long_strike (float): Strike price of the long put (typically lower)
        put_short_strike (float): Strike price of the short put
        call_short_strike (float): Strike price of the short call
        call_long_strike (float): Strike price of the long call (typically higher)
        long_expiration (str): Expiration date of the long options in YYYY-MM-DD format
        short_expiration (str): Expiration date of the short options in YYYY-MM-DD format
        put_long_premium (float): Entry premium paid for the long put
        put_short_premium (float): Entry premium received for the short put
        call_short_premium (float): Entry premium received for the short call
        call_long_premium (float): Entry premium paid for the long call
        current_put_long_premium (float): Current market premium of the long put
        current_put_short_premium (float): Current market premium of the short put
        current_call_short_premium (float): Current market premium of the short call
        current_call_long_premium (float): Current market premium of the long call
        quantity (int): Number of spreads
        put_long_iv (float): Implied volatility of the long put
        put_short_iv (float): Implied volatility of the short put
        call_short_iv (float): Implied volatility of the short call
        call_long_iv (float): Implied volatility of the long call
        
    Returns:
        list: List of strategy leg dictionaries
    """
    if not (put_long_strike <= put_short_strike < call_short_strike <= call_long_strike):
        raise ValueError("Strike order must be: put_long ≤ put_short < call_short ≤ call_long")
    
    # Use entry premiums as current premiums if not provided separately
    if current_put_long_premium is None:
        current_put_long_premium = put_long_premium
    if current_put_short_premium is None:
        current_put_short_premium = put_short_premium
    if current_call_short_premium is None:
        current_call_short_premium = call_short_premium
    if current_call_long_premium is None:
        current_call_long_premium = call_long_premium
    
    return [
        # Put diagonal spread
        {
            'type': 'put',
            'position': 'long',
            'strike': put_long_strike,
            'expiry': str(long_expiration),
            'price': put_long_premium,
            'current_price': current_put_long_premium,
            'quantity': quantity,
            'iv': put_long_iv
        },
        {
            'type': 'put',
            'position': 'short',
            'strike': put_short_strike,
            'expiry': str(short_expiration),
            'price': put_short_premium,
            'current_price': current_put_short_premium,
            'quantity': quantity,
            'iv': put_short_iv
        },
        # Call diagonal spread
        {
            'type': 'call',
            'position': 'short',
            'strike': call_short_strike,
            'expiry': str(short_expiration),
            'price': call_short_premium,
            'current_price': current_call_short_premium,
            'quantity': quantity,
            'iv': call_short_iv
        },
        {
            'type': 'call',
            'position': 'long',
            'strike': call_long_strike,
            'expiry': str(long_expiration),
            'price': call_long_premium,
            'current_price': current_call_long_premium,
            'quantity': quantity,
            'iv': call_long_iv
        }
    ]


def iron_butterfly(put_long_strike, atm_strike, call_long_strike,
                   expiration,
                   put_long_premium=0.0, atm_put_premium=0.0,
                   atm_call_premium=0.0, call_long_premium=0.0,
                   current_put_long_premium=None, current_atm_put_premium=None,
                   current_atm_call_premium=None, current_call_long_premium=None,
                   quantity=1,
                   put_long_iv=0.3, atm_put_iv=0.3,
                   atm_call_iv=0.3, call_long_iv=0.3):
    """
    Iron Butterfly: Sell an ATM straddle and buy OTM wings for protection.
    Maximum profit when the underlying closes exactly at the ATM strike.

    Structure:
        Long OTM put  |  Short ATM put  |  Short ATM call  |  Long OTM call

    Parameters:
        put_long_strike (float): OTM put wing strike (lowest)
        atm_strike (float): ATM short straddle strike (middle)
        call_long_strike (float): OTM call wing strike (highest)
        expiration (str): Expiration date YYYY-MM-DD
        put_long_premium (float): Premium paid for OTM put wing
        atm_put_premium (float): Premium received for short ATM put
        atm_call_premium (float): Premium received for short ATM call
        call_long_premium (float): Premium paid for OTM call wing
    """
    if not (put_long_strike < atm_strike < call_long_strike):
        raise ValueError("Strike order must be: put wing < ATM < call wing")

    if current_put_long_premium is None:
        current_put_long_premium = put_long_premium
    if current_atm_put_premium is None:
        current_atm_put_premium = atm_put_premium
    if current_atm_call_premium is None:
        current_atm_call_premium = atm_call_premium
    if current_call_long_premium is None:
        current_call_long_premium = call_long_premium

    return [
        # Long OTM put (lower wing)
        {
            'type': 'put', 'position': 'long',
            'strike': put_long_strike, 'expiry': str(expiration),
            'price': put_long_premium, 'current_price': current_put_long_premium,
            'quantity': quantity, 'iv': put_long_iv
        },
        # Short ATM put
        {
            'type': 'put', 'position': 'short',
            'strike': atm_strike, 'expiry': str(expiration),
            'price': atm_put_premium, 'current_price': current_atm_put_premium,
            'quantity': quantity, 'iv': atm_put_iv
        },
        # Short ATM call
        {
            'type': 'call', 'position': 'short',
            'strike': atm_strike, 'expiry': str(expiration),
            'price': atm_call_premium, 'current_price': current_atm_call_premium,
            'quantity': quantity, 'iv': atm_call_iv
        },
        # Long OTM call (upper wing)
        {
            'type': 'call', 'position': 'long',
            'strike': call_long_strike, 'expiry': str(expiration),
            'price': call_long_premium, 'current_price': current_call_long_premium,
            'quantity': quantity, 'iv': call_long_iv
        },
    ]


def jade_lizard(put_strike, call_short_strike, call_long_strike,
                expiration,
                put_premium=0.0, call_short_premium=0.0, call_long_premium=0.0,
                current_put_premium=None, current_call_short_premium=None,
                current_call_long_premium=None,
                quantity=1, put_iv=0.3, call_short_iv=0.3, call_long_iv=0.3):
    """
    Jade Lizard: Short OTM put + short OTM call spread.
    Structured so total credit > width of call spread → no upside risk.
    Bullish to neutral. Profits if stock stays above put strike.

    Structure:
        Short OTM put  |  Short OTM call  |  Long higher OTM call

    Parameters:
        put_strike (float): OTM short put strike (below current price)
        call_short_strike (float): OTM short call strike (above current price)
        call_long_strike (float): OTM long call strike (above call_short_strike)
        expiration (str): Expiration date YYYY-MM-DD
        put_premium (float): Premium received for the short put
        call_short_premium (float): Premium received for the short call
        call_long_premium (float): Premium paid for the long call
    """
    if not (put_strike < call_short_strike < call_long_strike):
        raise ValueError("Strike order must be: put strike < short call strike < long call strike")

    if current_put_premium is None:
        current_put_premium = put_premium
    if current_call_short_premium is None:
        current_call_short_premium = call_short_premium
    if current_call_long_premium is None:
        current_call_long_premium = call_long_premium

    return [
        # Short OTM put
        {
            'type': 'put', 'position': 'short',
            'strike': put_strike, 'expiry': str(expiration),
            'price': put_premium, 'current_price': current_put_premium,
            'quantity': quantity, 'iv': put_iv
        },
        # Short OTM call (lower leg of call spread)
        {
            'type': 'call', 'position': 'short',
            'strike': call_short_strike, 'expiry': str(expiration),
            'price': call_short_premium, 'current_price': current_call_short_premium,
            'quantity': quantity, 'iv': call_short_iv
        },
        # Long OTM call (upper leg of call spread — caps upside risk)
        {
            'type': 'call', 'position': 'long',
            'strike': call_long_strike, 'expiry': str(expiration),
            'price': call_long_premium, 'current_price': current_call_long_premium,
            'quantity': quantity, 'iv': call_long_iv
        },
    ]


def strip(strike, expiration,
          call_premium=0.0, put_premium=0.0,
          current_call_premium=None, current_put_premium=None,
          quantity=1, call_iv=0.3, put_iv=0.3):
    """
    Strip: Long 1 call + Long 2 puts at the same strike and expiration.
    Like a straddle but more bearish — doubles down on downside.
    Profits from large moves, with greater gains to the downside.

    Parameters:
        strike (float): Strike price for all legs
        expiration (str): Expiration date YYYY-MM-DD
        call_premium (float): Premium paid for the call
        put_premium (float): Premium paid per put (paid twice)
    """
    if current_call_premium is None:
        current_call_premium = call_premium
    if current_put_premium is None:
        current_put_premium = put_premium

    return [
        # Long 1 call
        {
            'type': 'call', 'position': 'long',
            'strike': strike, 'expiry': str(expiration),
            'price': call_premium, 'current_price': current_call_premium,
            'quantity': quantity, 'iv': call_iv
        },
        # Long 2 puts (represented as two legs for payoff clarity)
        {
            'type': 'put', 'position': 'long',
            'strike': strike, 'expiry': str(expiration),
            'price': put_premium, 'current_price': current_put_premium,
            'quantity': quantity * 2, 'iv': put_iv
        },
    ]


def strap(strike, expiration,
          call_premium=0.0, put_premium=0.0,
          current_call_premium=None, current_put_premium=None,
          quantity=1, call_iv=0.3, put_iv=0.3):
    """
    Strap: Long 2 calls + Long 1 put at the same strike and expiration.
    Like a straddle but more bullish — doubles down on upside.
    Profits from large moves, with greater gains to the upside.

    Parameters:
        strike (float): Strike price for all legs
        expiration (str): Expiration date YYYY-MM-DD
        call_premium (float): Premium paid per call (paid twice)
        put_premium (float): Premium paid for the put
    """
    if current_call_premium is None:
        current_call_premium = call_premium
    if current_put_premium is None:
        current_put_premium = put_premium

    return [
        # Long 2 calls
        {
            'type': 'call', 'position': 'long',
            'strike': strike, 'expiry': str(expiration),
            'price': call_premium, 'current_price': current_call_premium,
            'quantity': quantity * 2, 'iv': call_iv
        },
        # Long 1 put
        {
            'type': 'put', 'position': 'long',
            'strike': strike, 'expiry': str(expiration),
            'price': put_premium, 'current_price': current_put_premium,
            'quantity': quantity, 'iv': put_iv
        },
    ]
