# --- strategies/strategies_factory.py ---
import logging
from typing import List, Dict, Any, Union

# Setup logging
logger = logging.getLogger(__name__)

def create_strategy(strategy_type: str, **kwargs) -> List[Dict[str, Any]]:
    """
    Factory function to create strategy legs based on the strategy type.
    
    Parameters:
        strategy_type (str): The type of strategy to create
        **kwargs: Strategy-specific parameters
    
    Returns:
        List[Dict[str, Any]]: A list of strategy legs
    
    Raises:
        ValueError: If the strategy type is unknown or required parameters are missing
    """
    # Create the appropriate strategy based on the type
    strategy_creators = {
        # Basic strategies
        "long_call": create_long_call,
        "long_put": create_long_put,
        "covered_call": create_covered_call,
        "cash_secured_put": create_cash_secured_put,
        "naked_call": create_naked_call,
        "naked_put": create_naked_put,
        
        # Spread strategies
        "bull_call_spread": create_bull_call_spread,
        "bear_put_spread": create_bear_put_spread,
        "bull_put_spread": create_bull_put_spread,
        "bear_call_spread": create_bear_call_spread,
        "calendar_spread": create_calendar_spread,
        "poor_mans_covered_call": create_poor_mans_covered_call,
        "ratio_backspread": create_ratio_backspread,
        
        # Advanced strategies
        "iron_condor": create_iron_condor,
        "butterfly": create_butterfly,
        "straddle": create_straddle,
        "strangle": create_strangle,
        "collar": create_collar,
        "diagonal_spread": create_diagonal_spread,
        "double_diagonal_spread": create_double_diagonal_spread,
        
        # Custom strategies
        "custom": create_custom_strategy
    }
    
    # Check if the requested strategy type exists
    if strategy_type not in strategy_creators:
        logger.error(f"Unknown strategy type: {strategy_type}")
        raise ValueError(f"Unknown strategy type: {strategy_type}")
    
    # Create the strategy
    try:
        strategy_legs = strategy_creators[strategy_type](**kwargs)
        logger.info(f"Created {strategy_type} strategy with {len(strategy_legs)} legs")
        return strategy_legs
    except Exception as e:
        logger.error(f"Error creating {strategy_type} strategy: {str(e)}", exc_info=True)
        raise ValueError(f"Error creating {strategy_type} strategy: {str(e)}")

# Basic Strategies
def create_long_call(strike: float, expiration: str, current_premium: float = None, 
                    entry_premium: float = None, premium: float = None, quantity: int = 1, iv: float = 0.3) -> List[Dict[str, Any]]:
    """Create a long call strategy."""
    # Handle different premium parameters
    if entry_premium is None:
        if premium is not None:
            entry_premium = premium
        elif current_premium is not None:
            entry_premium = current_premium
        else:
            entry_premium = 0.0
    
    if current_premium is None:
        current_premium = entry_premium
    
    return [{
        'type': 'call',
        'position': 'long',
        'strike': strike,
        'expiry': expiration,
        'price': entry_premium,
        'current_price': current_premium,
        'quantity': quantity,
        'iv': iv
    }]

def create_long_put(strike: float, expiration: str, current_premium: float = None, 
                   entry_premium: float = None, premium: float = None, quantity: int = 1, iv: float = 0.3) -> List[Dict[str, Any]]:
    """Create a long put strategy."""
    # Handle different premium parameters
    if entry_premium is None:
        if premium is not None:
            entry_premium = premium
        elif current_premium is not None:
            entry_premium = current_premium
        else:
            entry_premium = 0.0
    
    if current_premium is None:
        current_premium = entry_premium
    
    return [{
        'type': 'put',
        'position': 'long',
        'strike': strike,
        'expiry': expiration,
        'price': entry_premium,
        'current_price': current_premium,
        'quantity': quantity,
        'iv': iv
    }]

def create_covered_call(current_stock_price: float = None, stock_price: float = None, 
                       call_strike: float = None, expiration: str = None, 
                       call_premium: float = None, current_call_premium: float = None,
                       quantity: int = 1, iv: float = 0.3) -> List[Dict[str, Any]]:
    """Create a covered call strategy (long stock + short call)."""
    # Handle stock price parameters
    if stock_price is None and current_stock_price is not None:
        stock_price = current_stock_price
    
    if current_stock_price is None and stock_price is not None:
        current_stock_price = stock_price
    
    # Handle call premium parameters
    if call_premium is None and current_call_premium is not None:
        call_premium = current_call_premium
    
    if current_call_premium is None and call_premium is not None:
        current_call_premium = call_premium
    
    strategy_legs = []
    
    # Stock leg
    strategy_legs.append({
        'type': 'stock',
        'position': 'long',
        'price': stock_price,
        'current_price': current_stock_price,
        'quantity': 100 * quantity  # 100 shares per contract
    })
    
    # Call leg
    strategy_legs.append({
        'type': 'call',
        'position': 'short',
        'strike': call_strike,
        'expiry': expiration,
        'price': call_premium,
        'current_price': current_call_premium,
        'quantity': quantity,
        'iv': iv
    })
    
    return strategy_legs

def create_cash_secured_put(strike: float, expiration: str, current_premium: float = None, 
                          entry_premium: float = None, premium: float = None, 
                          quantity: int = 1, iv: float = 0.3) -> List[Dict[str, Any]]:
    """Create a cash secured put strategy (short put with cash to secure)."""
    # Handle different premium parameters
    if entry_premium is None:
        if premium is not None:
            entry_premium = premium
        elif current_premium is not None:
            entry_premium = current_premium
        else:
            entry_premium = 0.0
    
    if current_premium is None:
        current_premium = entry_premium
    
    return [{
        'type': 'put',
        'position': 'short',
        'strike': strike,
        'expiry': expiration,
        'price': entry_premium,
        'current_price': current_premium,
        'quantity': quantity,
        'iv': iv,
        'cash_secured': True  # Flag as cash secured for analysis
    }]

def create_naked_call(strike: float, expiration: str, current_premium: float = None, 
                    entry_premium: float = None, premium: float = None,
                    quantity: int = 1, iv: float = 0.3) -> List[Dict[str, Any]]:
    """Create a naked call strategy (short call without stock)."""
    # Handle different premium parameters
    if entry_premium is None:
        if premium is not None:
            entry_premium = premium
        elif current_premium is not None:
            entry_premium = current_premium
        else:
            entry_premium = 0.0
    
    if current_premium is None:
        current_premium = entry_premium
    
    return [{
        'type': 'call',
        'position': 'short',
        'strike': strike,
        'expiry': expiration,
        'price': entry_premium,
        'current_price': current_premium,
        'quantity': quantity,
        'iv': iv
    }]

def create_naked_put(strike: float, expiration: str, current_premium: float = None, 
                   entry_premium: float = None, premium: float = None,
                   quantity: int = 1, iv: float = 0.3) -> List[Dict[str, Any]]:
    """Create a naked put strategy (short put without cash secured)."""
    # Handle different premium parameters
    if entry_premium is None:
        if premium is not None:
            entry_premium = premium
        elif current_premium is not None:
            entry_premium = current_premium
        else:
            entry_premium = 0.0
    
    if current_premium is None:
        current_premium = entry_premium
    
    return [{
        'type': 'put',
        'position': 'short',
        'strike': strike,
        'expiry': expiration,
        'price': entry_premium,
        'current_price': current_premium,
        'quantity': quantity,
        'iv': iv,
        'cash_secured': False  # Flag as not cash secured for analysis
    }]

# Spread Strategies
def create_bull_call_spread(long_strike: float, short_strike: float, expiration: str, 
                          long_premium: float = None, short_premium: float = None,
                          current_long_premium: float = None, current_short_premium: float = None,
                          quantity: int = 1, long_iv: float = 0.3, short_iv: float = 0.3) -> List[Dict[str, Any]]:
    """Create a bull call spread strategy (long call + short call at higher strike)."""
    if long_strike >= short_strike:
        raise ValueError("Long call strike must be less than short call strike for a bull call spread")
    
    # Handle premium parameters
    if long_premium is None and current_long_premium is not None:
        long_premium = current_long_premium
    
    if current_long_premium is None and long_premium is not None:
        current_long_premium = long_premium
    
    if short_premium is None and current_short_premium is not None:
        short_premium = current_short_premium
    
    if current_short_premium is None and short_premium is not None:
        current_short_premium = short_premium
    
    strategy_legs = []
    
    # Long call (lower strike)
    strategy_legs.append({
        'type': 'call',
        'position': 'long',
        'strike': long_strike,
        'expiry': expiration,
        'price': long_premium,
        'current_price': current_long_premium,
        'quantity': quantity,
        'iv': long_iv
    })
    
    # Short call (higher strike)
    strategy_legs.append({
        'type': 'call',
        'position': 'short',
        'strike': short_strike,
        'expiry': expiration,
        'price': short_premium,
        'current_price': current_short_premium,
        'quantity': quantity,
        'iv': short_iv
    })
    
    return strategy_legs

def create_bear_put_spread(long_strike: float, short_strike: float, expiration: str, 
                         long_premium: float = None, short_premium: float = None,
                         current_long_premium: float = None, current_short_premium: float = None,
                         quantity: int = 1, long_iv: float = 0.3, short_iv: float = 0.3) -> List[Dict[str, Any]]:
    """Create a bear put spread strategy (long put at higher strike + short put at lower strike)."""
    if long_strike <= short_strike:
        raise ValueError("Long put strike must be greater than short put strike for a bear put spread")
    
    # Handle premium parameters
    if long_premium is None and current_long_premium is not None:
        long_premium = current_long_premium
    
    if current_long_premium is None and long_premium is not None:
        current_long_premium = long_premium
    
    if short_premium is None and current_short_premium is not None:
        short_premium = current_short_premium
    
    if current_short_premium is None and short_premium is not None:
        current_short_premium = short_premium
    
    strategy_legs = []
    
    # Long put (higher strike)
    strategy_legs.append({
        'type': 'put',
        'position': 'long',
        'strike': long_strike,
        'expiry': expiration,
        'price': long_premium,
        'current_price': current_long_premium,
        'quantity': quantity,
        'iv': long_iv
    })
    
    # Short put (lower strike)
    strategy_legs.append({
        'type': 'put',
        'position': 'short',
        'strike': short_strike,
        'expiry': expiration,
        'price': short_premium,
        'current_price': current_short_premium,
        'quantity': quantity,
        'iv': short_iv
    })
    
    return strategy_legs

def create_bull_put_spread(short_put_strike: float, long_put_strike: float, expiration: str, 
                         short_put_premium: float = None, long_put_premium: float = None,
                         current_short_put_premium: float = None, current_long_put_premium: float = None,
                         quantity: int = 1, short_put_iv: float = 0.3, long_put_iv: float = 0.3) -> List[Dict[str, Any]]:
    """
    Create a bull put spread strategy (short put at higher strike + long put at lower strike).
    This is a credit spread.
    """
    if short_put_strike <= long_put_strike:
        raise ValueError("Short put strike must be greater than long put strike for a bull put spread")
    
    # Handle premium parameters
    if short_put_premium is None and current_short_put_premium is not None:
        short_put_premium = current_short_put_premium
    
    if current_short_put_premium is None and short_put_premium is not None:
        current_short_put_premium = short_put_premium
    
    if long_put_premium is None and current_long_put_premium is not None:
        long_put_premium = current_long_put_premium
    
    if current_long_put_premium is None and long_put_premium is not None:
        current_long_put_premium = long_put_premium
    
    strategy_legs = []
    
    # Short put (higher strike)
    strategy_legs.append({
        'type': 'put',
        'position': 'short',
        'strike': short_put_strike,
        'expiry': expiration,
        'price': short_put_premium,
        'current_price': current_short_put_premium,
        'quantity': quantity,
        'iv': short_put_iv
    })
    
    # Long put (lower strike)
    strategy_legs.append({
        'type': 'put',
        'position': 'long',
        'strike': long_put_strike,
        'expiry': expiration,
        'price': long_put_premium,
        'current_price': current_long_put_premium,
        'quantity': quantity,
        'iv': long_put_iv
    })
    
    return strategy_legs

def create_bear_call_spread(short_call_strike: float, long_call_strike: float, expiration: str, 
                          short_call_premium: float = None, long_call_premium: float = None,
                          current_short_call_premium: float = None, current_long_call_premium: float = None,
                          quantity: int = 1, short_call_iv: float = 0.3, long_call_iv: float = 0.3) -> List[Dict[str, Any]]:
    """
    Create a bear call spread strategy (short call at lower strike + long call at higher strike).
    This is a credit spread.
    """
    if short_call_strike >= long_call_strike:
        raise ValueError("Short call strike must be less than long call strike for a bear call spread")
    
    # Handle premium parameters
    if short_call_premium is None and current_short_call_premium is not None:
        short_call_premium = current_short_call_premium
    
    if current_short_call_premium is None and short_call_premium is not None:
        current_short_call_premium = short_call_premium
    
    if long_call_premium is None and current_long_call_premium is not None:
        long_call_premium = current_long_call_premium
    
    if current_long_call_premium is None and long_call_premium is not None:
        current_long_call_premium = long_call_premium
    
    strategy_legs = []
    
    # Short call (lower strike)
    strategy_legs.append({
        'type': 'call',
        'position': 'short',
        'strike': short_call_strike,
        'expiry': expiration,
        'price': short_call_premium,
        'current_price': current_short_call_premium,
        'quantity': quantity,
        'iv': short_call_iv
    })
    
    # Long call (higher strike)
    strategy_legs.append({
        'type': 'call',
        'position': 'long',
        'strike': long_call_strike,
        'expiry': expiration,
        'price': long_call_premium,
        'current_price': current_long_call_premium,
        'quantity': quantity,
        'iv': long_call_iv
    })
    
    return strategy_legs

def create_calendar_spread(strike: float, near_expiration: str, far_expiration: str, 
                         near_premium: float = None, far_premium: float = None,
                         current_near_premium: float = None, current_far_premium: float = None,
                         option_type: str = 'call', quantity: int = 1, 
                         near_iv: float = 0.3, far_iv: float = 0.3) -> List[Dict[str, Any]]:
    """
    Create a calendar spread (short near-term option + long far-term option at same strike).
    """
    if option_type.lower() not in ['call', 'put']:
        raise ValueError(f"Invalid option type: {option_type}. Use 'call' or 'put'.")
    
    # Handle premium parameters
    if near_premium is None and current_near_premium is not None:
        near_premium = current_near_premium
    
    if current_near_premium is None and near_premium is not None:
        current_near_premium = near_premium
    
    if far_premium is None and current_far_premium is not None:
        far_premium = current_far_premium
    
    if current_far_premium is None and far_premium is not None:
        current_far_premium = far_premium
    
    strategy_legs = []
    
    # Short near-term option
    strategy_legs.append({
        'type': option_type.lower(),
        'position': 'short',
        'strike': strike,
        'expiry': near_expiration,
        'price': near_premium,
        'current_price': current_near_premium,
        'quantity': quantity,
        'iv': near_iv
    })
    
    # Long far-term option
    strategy_legs.append({
        'type': option_type.lower(),
        'position': 'long',
        'strike': strike,
        'expiry': far_expiration,
        'price': far_premium,
        'current_price': current_far_premium,
        'quantity': quantity,
        'iv': far_iv
    })
    
    return strategy_legs

def create_poor_mans_covered_call(long_call_strike: float, short_call_strike: float, 
                                long_call_exp: str, short_call_exp: str,
                                long_call_premium: float = None, short_call_premium: float = None,
                                current_long_call_premium: float = None, current_short_call_premium: float = None,
                                quantity: int = 1, long_call_iv: float = 0.3, 
                                short_call_iv: float = 0.3) -> List[Dict[str, Any]]:
    """
    Create a poor man's covered call (long deep ITM LEAP call + short OTM near-term call).
    """
    if long_call_strike >= short_call_strike:
        raise ValueError("Long call strike should be less than short call strike for a PMCC")
    
    # Handle premium parameters
    if long_call_premium is None and current_long_call_premium is not None:
        long_call_premium = current_long_call_premium
    
    if current_long_call_premium is None and long_call_premium is not None:
        current_long_call_premium = long_call_premium
    
    if short_call_premium is None and current_short_call_premium is not None:
        short_call_premium = current_short_call_premium
    
    if current_short_call_premium is None and short_call_premium is not None:
        current_short_call_premium = short_call_premium
    
    strategy_legs = []
    
    # Long LEAP call (lower strike)
    strategy_legs.append({
        'type': 'call',
        'position': 'long',
        'strike': long_call_strike,
        'expiry': long_call_exp,
        'price': long_call_premium,
        'current_price': current_long_call_premium,
        'quantity': quantity,
        'iv': long_call_iv
    })
    
    # Short near-term call (higher strike)
    strategy_legs.append({
        'type': 'call',
        'position': 'short',
        'strike': short_call_strike,
        'expiry': short_call_exp,
        'price': short_call_premium,
        'current_price': current_short_call_premium,
        'quantity': quantity,
        'iv': short_call_iv
    })
    
    return strategy_legs

def create_ratio_backspread(short_strike: float, long_strike: float, expiration: str,
                          short_premium: float = None, long_premium: float = None,
                          current_short_premium: float = None, current_long_premium: float = None,
                          ratio: int = 2, option_type: str = 'call', quantity: int = 1, 
                          short_iv: float = 0.3, long_iv: float = 0.3) -> List[Dict[str, Any]]:
    """
    Create a ratio backspread (short 1 option + long multiple options at different strike).
    """
    if option_type.lower() not in ['call', 'put']:
        raise ValueError(f"Invalid option type: {option_type}. Use 'call' or 'put'.")
    
    if ratio < 2:
        raise ValueError("Ratio must be at least 2 for a ratio backspread")
    
    # Handle premium parameters
    if short_premium is None and current_short_premium is not None:
        short_premium = current_short_premium
    
    if current_short_premium is None and short_premium is not None:
        current_short_premium = short_premium
    
    if long_premium is None and current_long_premium is not None:
        long_premium = current_long_premium
    
    if current_long_premium is None and long_premium is not None:
        current_long_premium = long_premium
    
    strategy_legs = []
    
    # Short option
    strategy_legs.append({
        'type': option_type.lower(),
        'position': 'short',
        'strike': short_strike,
        'expiry': expiration,
        'price': short_premium,
        'current_price': current_short_premium,
        'quantity': quantity,
        'iv': short_iv
    })
    
    # Long options (multiple)
    for _ in range(ratio):
        strategy_legs.append({
            'type': option_type.lower(),
            'position': 'long',
            'strike': long_strike,
            'expiry': expiration,
            'price': long_premium,
            'current_price': current_long_premium,
            'quantity': quantity,
            'iv': long_iv
        })
    
    return strategy_legs

# Advanced Strategies
def create_iron_condor(long_put_strike: float, short_put_strike: float, 
                     short_call_strike: float, long_call_strike: float,
                     expiration: str, long_put_premium: float = None, short_put_premium: float = None,
                     short_call_premium: float = None, long_call_premium: float = None,
                     current_long_put_premium: float = None, current_short_put_premium: float = None,
                     current_short_call_premium: float = None, current_long_call_premium: float = None,
                     quantity: int = 1, long_put_iv: float = 0.3, short_put_iv: float = 0.3,
                     short_call_iv: float = 0.3, long_call_iv: float = 0.3) -> List[Dict[str, Any]]:
    """
    Create an iron condor strategy (bull put spread + bear call spread).
    """
    if not (long_put_strike < short_put_strike < short_call_strike < long_call_strike):
        raise ValueError("Strike order must be: long put < short put < short call < long call")
    
    # Handle premium parameters
    if long_put_premium is None and current_long_put_premium is not None:
        long_put_premium = current_long_put_premium
    
    if current_long_put_premium is None and long_put_premium is not None:
        current_long_put_premium = long_put_premium
    
    if short_put_premium is None and current_short_put_premium is not None:
        short_put_premium = current_short_put_premium
    
    if current_short_put_premium is None and short_put_premium is not None:
        current_short_put_premium = short_put_premium
    
    if short_call_premium is None and current_short_call_premium is not None:
        short_call_premium = current_short_call_premium
    
    if current_short_call_premium is None and short_call_premium is not None:
        current_short_call_premium = short_call_premium
    
    if long_call_premium is None and current_long_call_premium is not None:
        long_call_premium = current_long_call_premium
    
    if current_long_call_premium is None and long_call_premium is not None:
        current_long_call_premium = long_call_premium
    
    strategy_legs = []
    
    # Bull put spread
    strategy_legs.append({
        'type': 'put',
        'position': 'long',
        'strike': long_put_strike,
        'expiry': expiration,
        'price': long_put_premium,
        'current_price': current_long_put_premium,
        'quantity': quantity,
        'iv': long_put_iv
    })
    
    strategy_legs.append({
        'type': 'put',
        'position': 'short',
        'strike': short_put_strike,
        'expiry': expiration,
        'price': short_put_premium,
        'current_price': current_short_put_premium,
        'quantity': quantity,
        'iv': short_put_iv
    })
    
    # Bear call spread
    strategy_legs.append({
        'type': 'call',
        'position': 'short',
        'strike': short_call_strike,
        'expiry': expiration,
        'price': short_call_premium,
        'current_price': current_short_call_premium,
        'quantity': quantity,
        'iv': short_call_iv
    })
    
    strategy_legs.append({
        'type': 'call',
        'position': 'long',
        'strike': long_call_strike,
        'expiry': expiration,
        'price': long_call_premium,
        'current_price': current_long_call_premium,
        'quantity': quantity,
        'iv': long_call_iv
    })
    
    return strategy_legs

def create_butterfly(low_strike: float, mid_strike: float, high_strike: float, 
                   expiration: str, low_premium: float = None, mid_premium: float = None, 
                   high_premium: float = None, current_low_premium: float = None,
                   current_mid_premium: float = None, current_high_premium: float = None,
                   option_type: str = 'call', quantity: int = 1,
                   low_iv: float = 0.3, mid_iv: float = 0.3, high_iv: float = 0.3) -> List[Dict[str, Any]]:
    """
    Create a butterfly spread (long 1 lower strike + short 2 middle strike + long 1 higher strike).
    """
    if option_type.lower() not in ['call', 'put']:
        raise ValueError(f"Invalid option type: {option_type}. Use 'call' or 'put'.")
    
    if not (low_strike < mid_strike < high_strike):
        raise ValueError("Strikes must be in order: low < mid < high")
    
    # Check if strikes are evenly spaced (not required but common)
    if abs((mid_strike - low_strike) - (high_strike - mid_strike)) > 0.01:
        logger.warning("Butterfly strikes are not evenly spaced")
    
    # Handle premium parameters
    if low_premium is None and current_low_premium is not None:
        low_premium = current_low_premium
    
    if current_low_premium is None and low_premium is not None:
        current_low_premium = low_premium
    
    if mid_premium is None and current_mid_premium is not None:
        mid_premium = current_mid_premium
    
    if current_mid_premium is None and mid_premium is not None:
        current_mid_premium = mid_premium
    
    if high_premium is None and current_high_premium is not None:
        high_premium = current_high_premium
    
    if current_high_premium is None and high_premium is not None:
        current_high_premium = high_premium
    
    strategy_legs = []
    
    # Long lower strike
    strategy_legs.append({
        'type': option_type.lower(),
        'position': 'long',
        'strike': low_strike,
        'expiry': expiration,
        'price': low_premium,
        'current_price': current_low_premium,
        'quantity': quantity,
        'iv': low_iv
    })
    
    # Short middle strike (2x)
    for _ in range(2):
        strategy_legs.append({
            'type': option_type.lower(),
            'position': 'short',
            'strike': mid_strike,
            'expiry': expiration,
            'price': mid_premium,
            'current_price': current_mid_premium,
            'quantity': quantity,
            'iv': mid_iv
        })
    
    # Long higher strike
    strategy_legs.append({
        'type': option_type.lower(),
        'position': 'long',
        'strike': high_strike,
        'expiry': expiration,
        'price': high_premium,
        'current_price': current_high_premium,
        'quantity': quantity,
        'iv': high_iv
    })
    
    return strategy_legs

def create_straddle(strike: float, expiration: str, call_premium: float = None, put_premium: float = None,
                  current_call_premium: float = None, current_put_premium: float = None,
                  quantity: int = 1, call_iv: float = 0.3, put_iv: float = 0.3) -> List[Dict[str, Any]]:
    """
    Create a straddle strategy (long call + long put at same strike).
    """
    # Handle premium parameters
    if call_premium is None and current_call_premium is not None:
        call_premium = current_call_premium
    
    if current_call_premium is None and call_premium is not None:
        current_call_premium = call_premium
    
    if put_premium is None and current_put_premium is not None:
        put_premium = current_put_premium
    
    if current_put_premium is None and put_premium is not None:
        current_put_premium = put_premium
    
    strategy_legs = []
    
    # Long call
    strategy_legs.append({
        'type': 'call',
        'position': 'long',
        'strike': strike,
        'expiry': expiration,
        'price': call_premium,
        'current_price': current_call_premium,
        'quantity': quantity,
        'iv': call_iv
    })
    
    # Long put
    strategy_legs.append({
        'type': 'put',
        'position': 'long',
        'strike': strike,
        'expiry': expiration,
        'price': put_premium,
        'current_price': current_put_premium,
        'quantity': quantity,
        'iv': put_iv
    })
    
    return strategy_legs

def create_strangle(call_strike: float, put_strike: float, expiration: str,
                  call_premium: float = None, put_premium: float = None,
                  current_call_premium: float = None, current_put_premium: float = None,
                  quantity: int = 1, call_iv: float = 0.3, put_iv: float = 0.3) -> List[Dict[str, Any]]:
    """
    Create a strangle strategy (long call at higher strike + long put at lower strike).
    """
    if put_strike >= call_strike:
        raise ValueError("Put strike must be less than call strike for a strangle")
    
    # Handle premium parameters
    if call_premium is None and current_call_premium is not None:
        call_premium = current_call_premium
    
    if current_call_premium is None and call_premium is not None:
        current_call_premium = call_premium
    
    if put_premium is None and current_put_premium is not None:
        put_premium = current_put_premium
    
    if current_put_premium is None and put_premium is not None:
        current_put_premium = put_premium
    
    strategy_legs = []
    
    # Long call (higher strike)
    strategy_legs.append({
        'type': 'call',
        'position': 'long',
        'strike': call_strike,
        'expiry': expiration,
        'price': call_premium,
        'current_price': current_call_premium,
        'quantity': quantity,
        'iv': call_iv
    })
    
    # Long put (lower strike)
    strategy_legs.append({
        'type': 'put',
        'position': 'long',
        'strike': put_strike,
        'expiry': expiration,
        'price': put_premium,
        'current_price': current_put_premium,
        'quantity': quantity,
        'iv': put_iv
    })
    
    return strategy_legs

def create_collar(current_stock_price: float = None, stock_price: float = None, 
                put_strike: float = None, call_strike: float = None, 
                expiration: str = None, put_premium: float = None, call_premium: float = None,
                current_put_premium: float = None, current_call_premium: float = None,
                quantity: int = 1, put_iv: float = 0.3, call_iv: float = 0.3) -> List[Dict[str, Any]]:
    """
    Create a collar strategy (long stock + long put + short call).
    """
    if put_strike >= call_strike:
        raise ValueError("Put strike must be less than call strike for a collar")
    
    # Handle stock price parameters
    if stock_price is None and current_stock_price is not None:
        stock_price = current_stock_price
    
    if current_stock_price is None and stock_price is not None:
        current_stock_price = stock_price
    
    # Handle premium parameters
    if put_premium is None and current_put_premium is not None:
        put_premium = current_put_premium
    
    if current_put_premium is None and put_premium is not None:
        current_put_premium = put_premium
    
    if call_premium is None and current_call_premium is not None:
        call_premium = current_call_premium
    
    if current_call_premium is None and call_premium is not None:
        current_call_premium = call_premium
    
    strategy_legs = []
    
    # Long stock
    strategy_legs.append({
        'type': 'stock',
        'position': 'long',
        'price': stock_price,
        'current_price': current_stock_price,
        'quantity': 100 * quantity  # 100 shares per contract
    })
    
    # Long put (protection)
    strategy_legs.append({
        'type': 'put',
        'position': 'long',
        'strike': put_strike,
        'expiry': expiration,
        'price': put_premium,
        'current_price': current_put_premium,
        'quantity': quantity,
        'iv': put_iv
    })
    
    # Short call (income)
    strategy_legs.append({
        'type': 'call',
        'position': 'short',
        'strike': call_strike,
        'expiry': expiration,
        'price': call_premium,
        'current_price': current_call_premium,
        'quantity': quantity,
        'iv': call_iv
    })
    
    return strategy_legs

def create_diagonal_spread(long_strike: float, short_strike: float, 
                         long_expiration: str, short_expiration: str,
                         long_premium: float = None, short_premium: float = None,
                         current_long_premium: float = None, current_short_premium: float = None,
                         option_type: str = 'call', quantity: int = 1,
                         long_iv: float = 0.3, short_iv: float = 0.3) -> List[Dict[str, Any]]:
    """
    Create a diagonal spread (long farther expiration + short nearer expiration at different strikes).
    """
    if option_type.lower() not in ['call', 'put']:
        raise ValueError(f"Invalid option type: {option_type}. Use 'call' or 'put'.")
    
    # Handle premium parameters
    if long_premium is None and current_long_premium is not None:
        long_premium = current_long_premium
    
    if current_long_premium is None and long_premium is not None:
        current_long_premium = long_premium
    
    if short_premium is None and current_short_premium is not None:
        short_premium = current_short_premium
    
    if current_short_premium is None and short_premium is not None:
        current_short_premium = short_premium
    
    strategy_legs = []
    
    # Long option (farther expiration)
    strategy_legs.append({
        'type': option_type.lower(),
        'position': 'long',
        'strike': long_strike,
        'expiry': long_expiration,
        'price': long_premium,
        'current_price': current_long_premium,
        'quantity': quantity,
        'iv': long_iv
    })
    
    # Short option (nearer expiration)
    strategy_legs.append({
        'type': option_type.lower(),
        'position': 'short',
        'strike': short_strike,
        'expiry': short_expiration,
        'price': short_premium,
        'current_price': current_short_premium,
        'quantity': quantity,
        'iv': short_iv
    })
    
    return strategy_legs

def create_double_diagonal_spread(put_long_strike: float, put_short_strike: float,
                                call_short_strike: float, call_long_strike: float,
                                long_expiration: str, short_expiration: str,
                                put_long_premium: float = None, put_short_premium: float = None,
                                call_short_premium: float = None, call_long_premium: float = None,
                                current_put_long_premium: float = None, current_put_short_premium: float = None,
                                current_call_short_premium: float = None, current_call_long_premium: float = None,
                                quantity: int = 1, put_long_iv: float = 0.3, put_short_iv: float = 0.3,
                                call_short_iv: float = 0.3, call_long_iv: float = 0.3) -> List[Dict[str, Any]]:
    """
    Create a double diagonal spread (combines put diagonal and call diagonal spreads).
    """
    if not (put_long_strike <= put_short_strike < call_short_strike <= call_long_strike):
        raise ValueError("Invalid strikes order for double diagonal")
    
    # Handle premium parameters
    if put_long_premium is None and current_put_long_premium is not None:
        put_long_premium = current_put_long_premium
    
    if current_put_long_premium is None and put_long_premium is not None:
        current_put_long_premium = put_long_premium
    
    if put_short_premium is None and current_put_short_premium is not None:
        put_short_premium = current_put_short_premium
    
    if current_put_short_premium is None and put_short_premium is not None:
        current_put_short_premium = put_short_premium
    
    if call_short_premium is None and current_call_short_premium is not None:
        call_short_premium = current_call_short_premium
    
    if current_call_short_premium is None and call_short_premium is not None:
        current_call_short_premium = call_short_premium
    
    if call_long_premium is None and current_call_long_premium is not None:
        call_long_premium = current_call_long_premium
    
    if current_call_long_premium is None and call_long_premium is not None:
        current_call_long_premium = call_long_premium
    
    strategy_legs = []
    
    # Put diagonal
    strategy_legs.append({
        'type': 'put',
        'position': 'long',
        'strike': put_long_strike,
        'expiry': long_expiration,
        'price': put_long_premium,
        'current_price': current_put_long_premium,
        'quantity': quantity,
        'iv': put_long_iv
    })
    
    strategy_legs.append({
        'type': 'put',
        'position': 'short',
        'strike': put_short_strike,
        'expiry': short_expiration,
        'price': put_short_premium,
        'current_price': current_put_short_premium,
        'quantity': quantity,
        'iv': put_short_iv
    })
    
    # Call diagonal
    strategy_legs.append({
        'type': 'call',
        'position': 'short',
        'strike': call_short_strike,
        'expiry': short_expiration,
        'price': call_short_premium,
        'current_price': current_call_short_premium,
        'quantity': quantity,
        'iv': call_short_iv
    })
    
    strategy_legs.append({
        'type': 'call',
        'position': 'long',
        'strike': call_long_strike,
        'expiry': long_expiration,
        'price': call_long_premium,
        'current_price': current_call_long_premium,
        'quantity': quantity,
        'iv': call_long_iv
    })
    
    return strategy_legs

# Custom Strategy
def create_custom_strategy(legs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Create a custom strategy with user-defined legs.
    
    Parameters:
        legs (List[Dict]): List of option/stock legs with parameters
    
    Returns:
        List[Dict]: The strategy legs with validated fields
    """
    if not isinstance(legs, list):
        raise ValueError("Legs must be provided as a list of dictionaries")
    if not legs:
        raise ValueError("At least one leg must be provided")
    
    validated_legs = []
    
    for i, leg in enumerate(legs):
        # Ensure minimum required fields
        if 'type' not in leg:
            raise ValueError(f"Leg {i+1} is missing 'type' field")
        if 'position' not in leg:
            raise ValueError(f"Leg {i+1} is missing 'position' field")
        
        # Validate field values
        if leg['type'] not in ['call', 'put', 'stock']:
            raise ValueError(f"Invalid leg type: {leg['type']}. Use 'call', 'put', or 'stock'.")
        
        if leg['position'] not in ['long', 'short']:
            raise ValueError(f"Invalid position: {leg['position']}. Use 'long' or 'short'.")
        
        # Ensure option legs have strike and expiry
        if leg['type'] in ['call', 'put']:
            if 'strike' not in leg:
                raise ValueError(f"Option leg {i+1} must have a 'strike' field")
            if 'expiry' not in leg and 'expiration' not in leg:  # Support both naming conventions
                raise ValueError(f"Option leg {i+1} must have an 'expiry' or 'expiration' field")
            
            # Standardize expiry field name
            if 'expiration' in leg and 'expiry' not in leg:
                leg['expiry'] = leg['expiration']
            
            # Ensure IV is provided for option legs
            if 'iv' not in leg:
                leg['iv'] = 0.3  # Default IV
        
        # Ensure stock legs have price
        if leg['type'] == 'stock' and 'price' not in leg:
            raise ValueError(f"Stock leg {i+1} must have a 'price' field")
        
        # Set default values for missing fields
        if 'quantity' not in leg:
            leg['quantity'] = 1
        
        if 'price' not in leg:
            leg['price'] = 0.0
        
        # Handle current_price field
        if 'current_price' not in leg:
            leg['current_price'] = leg['price']
        
        validated_legs.append(leg)
    
    return validated_legs