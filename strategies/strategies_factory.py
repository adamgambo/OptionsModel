# --- strategies/strategy_factory.py ---
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
def create_long_call(strike: float, expiration: str, premium: float, quantity: int = 1, iv: float = 0.3) -> List[Dict[str, Any]]:
    """Create a long call strategy."""
    return [{
        'type': 'call',
        'position': 'long',
        'strike': strike,
        'expiry': expiration,
        'price': premium,
        'quantity': quantity,
        'iv': iv
    }] * quantity

def create_long_put(strike: float, expiration: str, premium: float, quantity: int = 1, iv: float = 0.3) -> List[Dict[str, Any]]:
    """Create a long put strategy."""
    return [{
        'type': 'put',
        'position': 'long',
        'strike': strike,
        'expiry': expiration,
        'price': premium,
        'quantity': quantity,
        'iv': iv
    }] * quantity

def create_covered_call(stock_price: float, call_strike: float, expiration: str, call_premium: float, 
                       quantity: int = 1, iv: float = 0.3) -> List[Dict[str, Any]]:
    """Create a covered call strategy (long stock + short call)."""
    strategy_legs = []
    
    for _ in range(quantity):
        # Stock leg
        strategy_legs.append({
            'type': 'stock',
            'position': 'long',
            'price': stock_price,
            'quantity': 100  # 100 shares per contract
        })
        
        # Call leg
        strategy_legs.append({
            'type': 'call',
            'position': 'short',
            'strike': call_strike,
            'expiry': expiration,
            'price': call_premium,
            'quantity': 1,
            'iv': iv
        })
    
    return strategy_legs

def create_cash_secured_put(strike: float, expiration: str, premium: float, quantity: int = 1, iv: float = 0.3) -> List[Dict[str, Any]]:
    """Create a cash secured put strategy (short put with cash to secure)."""
    return [{
        'type': 'put',
        'position': 'short',
        'strike': strike,
        'expiry': expiration,
        'price': premium,
        'quantity': quantity,
        'iv': iv,
        'cash_secured': True  # Flag as cash secured for analysis
    }] * quantity

def create_naked_call(strike: float, expiration: str, premium: float, quantity: int = 1, iv: float = 0.3) -> List[Dict[str, Any]]:
    """Create a naked call strategy (short call without stock)."""
    return [{
        'type': 'call',
        'position': 'short',
        'strike': strike,
        'expiry': expiration,
        'price': premium,
        'quantity': quantity,
        'iv': iv
    }] * quantity

def create_naked_put(strike: float, expiration: str, premium: float, quantity: int = 1, iv: float = 0.3) -> List[Dict[str, Any]]:
    """Create a naked put strategy (short put without cash secured)."""
    return [{
        'type': 'put',
        'position': 'short',
        'strike': strike,
        'expiry': expiration,
        'price': premium,
        'quantity': quantity,
        'iv': iv,
        'cash_secured': False  # Flag as not cash secured for analysis
    }] * quantity

# Spread Strategies
def create_bull_call_spread(long_strike: float, short_strike: float, expiration: str, 
                          long_premium: float, short_premium: float, quantity: int = 1,
                          long_iv: float = 0.3, short_iv: float = 0.3) -> List[Dict[str, Any]]:
    """Create a bull call spread strategy (long call + short call at higher strike)."""
    if long_strike >= short_strike:
        raise ValueError("Long call strike must be less than short call strike for a bull call spread")
    
    strategy_legs = []
    
    for _ in range(quantity):
        # Long call (lower strike)
        strategy_legs.append({
            'type': 'call',
            'position': 'long',
            'strike': long_strike,
            'expiry': expiration,
            'price': long_premium,
            'quantity': 1,
            'iv': long_iv
        })
        
        # Short call (higher strike)
        strategy_legs.append({
            'type': 'call',
            'position': 'short',
            'strike': short_strike,
            'expiry': expiration,
            'price': short_premium,
            'quantity': 1,
            'iv': short_iv
        })
    
    return strategy_legs

def create_bear_put_spread(long_strike: float, short_strike: float, expiration: str, 
                         long_premium: float, short_premium: float, quantity: int = 1,
                         long_iv: float = 0.3, short_iv: float = 0.3) -> List[Dict[str, Any]]:
    """Create a bear put spread strategy (long put at higher strike + short put at lower strike)."""
    if long_strike <= short_strike:
        raise ValueError("Long put strike must be greater than short put strike for a bear put spread")
    
    strategy_legs = []
    
    for _ in range(quantity):
        # Long put (higher strike)
        strategy_legs.append({
            'type': 'put',
            'position': 'long',
            'strike': long_strike,
            'expiry': expiration,
            'price': long_premium,
            'quantity': 1,
            'iv': long_iv
        })
        
        # Short put (lower strike)
        strategy_legs.append({
            'type': 'put',
            'position': 'short',
            'strike': short_strike,
            'expiry': expiration,
            'price': short_premium,
            'quantity': 1,
            'iv': short_iv
        })
    
    return strategy_legs

def create_bull_put_spread(short_put_strike: float, long_put_strike: float, expiration: str, 
                         short_put_premium: float, long_put_premium: float, quantity: int = 1,
                         short_put_iv: float = 0.3, long_put_iv: float = 0.3) -> List[Dict[str, Any]]:
    """
    Create a bull put spread strategy (short put at higher strike + long put at lower strike).
    This is a credit spread.
    """
    if short_put_strike <= long_put_strike:
        raise ValueError("Short put strike must be greater than long put strike for a bull put spread")
    
    strategy_legs = []
    
    for _ in range(quantity):
        # Short put (higher strike)
        strategy_legs.append({
            'type': 'put',
            'position': 'short',
            'strike': short_put_strike,
            'expiry': expiration,
            'price': short_put_premium,
            'quantity': 1,
            'iv': short_put_iv
        })
        
        # Long put (lower strike)
        strategy_legs.append({
            'type': 'put',
            'position': 'long',
            'strike': long_put_strike,
            'expiry': expiration,
            'price': long_put_premium,
            'quantity': 1,
            'iv': long_put_iv
        })
    
    return strategy_legs

def create_bear_call_spread(short_call_strike: float, long_call_strike: float, expiration: str, 
                          short_call_premium: float, long_call_premium: float, quantity: int = 1,
                          short_call_iv: float = 0.3, long_call_iv: float = 0.3) -> List[Dict[str, Any]]:
    """
    Create a bear call spread strategy (short call at lower strike + long call at higher strike).
    This is a credit spread.
    """
    if short_call_strike >= long_call_strike:
        raise ValueError("Short call strike must be less than long call strike for a bear call spread")
    
    strategy_legs = []
    
    for _ in range(quantity):
        # Short call (lower strike)
        strategy_legs.append({
            'type': 'call',
            'position': 'short',
            'strike': short_call_strike,
            'expiry': expiration,
            'price': short_call_premium,
            'quantity': 1,
            'iv': short_call_iv
        })
        
        # Long call (higher strike)
        strategy_legs.append({
            'type': 'call',
            'position': 'long',
            'strike': long_call_strike,
            'expiry': expiration,
            'price': long_call_premium,
            'quantity': 1,
            'iv': long_call_iv
        })
    
    return strategy_legs

def create_calendar_spread(strike: float, near_expiration: str, far_expiration: str, 
                         near_premium: float, far_premium: float, option_type: str = 'call',
                         quantity: int = 1, near_iv: float = 0.3, far_iv: float = 0.3) -> List[Dict[str, Any]]:
    """
    Create a calendar spread (short near-term option + long far-term option at same strike).
    """
    if option_type.lower() not in ['call', 'put']:
        raise ValueError(f"Invalid option type: {option_type}. Use 'call' or 'put'.")
    
    strategy_legs = []
    
    for _ in range(quantity):
        # Short near-term option
        strategy_legs.append({
            'type': option_type.lower(),
            'position': 'short',
            'strike': strike,
            'expiry': near_expiration,
            'price': near_premium,
            'quantity': 1,
            'iv': near_iv
        })
        
        # Long far-term option
        strategy_legs.append({
            'type': option_type.lower(),
            'position': 'long',
            'strike': strike,
            'expiry': far_expiration,
            'price': far_premium,
            'quantity': 1,
            'iv': far_iv
        })
    
    return strategy_legs

def create_poor_mans_covered_call(long_call_strike: float, short_call_strike: float, 
                                long_call_exp: str, short_call_exp: str,
                                long_call_premium: float, short_call_premium: float,
                                quantity: int = 1, long_call_iv: float = 0.3, 
                                short_call_iv: float = 0.3) -> List[Dict[str, Any]]:
    """
    Create a poor man's covered call (long deep ITM LEAP call + short OTM near-term call).
    """
    if long_call_strike >= short_call_strike:
        raise ValueError("Long call strike should be less than short call strike for a PMCC")
    
    strategy_legs = []
    
    for _ in range(quantity):
        # Long LEAP call (lower strike)
        strategy_legs.append({
            'type': 'call',
            'position': 'long',
            'strike': long_call_strike,
            'expiry': long_call_exp,
            'price': long_call_premium,
            'quantity': 1,
            'iv': long_call_iv
        })
        
        # Short near-term call (higher strike)
        strategy_legs.append({
            'type': 'call',
            'position': 'short',
            'strike': short_call_strike,
            'expiry': short_call_exp,
            'price': short_call_premium,
            'quantity': 1,
            'iv': short_call_iv
        })
    
    return strategy_legs

def create_ratio_backspread(short_strike: float, long_strike: float, expiration: str,
                          short_premium: float, long_premium: float, ratio: int = 2,
                          option_type: str = 'call', quantity: int = 1, 
                          short_iv: float = 0.3, long_iv: float = 0.3) -> List[Dict[str, Any]]:
    """
    Create a ratio backspread (short 1 option + long multiple options at different strike).
    """
    if option_type.lower() not in ['call', 'put']:
        raise ValueError(f"Invalid option type: {option_type}. Use 'call' or 'put'.")
    
    if ratio < 2:
        raise ValueError("Ratio must be at least 2 for a ratio backspread")
    
    strategy_legs = []
    
    for _ in range(quantity):
        # Short option
        strategy_legs.append({
            'type': option_type.lower(),
            'position': 'short',
            'strike': short_strike,
            'expiry': expiration,
            'price': short_premium,
            'quantity': 1,
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
                'quantity': 1,
                'iv': long_iv
            })
    
    return strategy_legs

# Advanced Strategies
def create_iron_condor(long_put_strike: float, short_put_strike: float, 
                     short_call_strike: float, long_call_strike: float,
                     expiration: str, long_put_premium: float, short_put_premium: float,
                     short_call_premium: float, long_call_premium: float,
                     quantity: int = 1, long_put_iv: float = 0.3, short_put_iv: float = 0.3,
                     short_call_iv: float = 0.3, long_call_iv: float = 0.3) -> List[Dict[str, Any]]:
    """
    Create an iron condor strategy (bull put spread + bear call spread).
    """
    if not (long_put_strike < short_put_strike < short_call_strike < long_call_strike):
        raise ValueError("Strike order must be: long put < short put < short call < long call")
    
    strategy_legs = []
    
    for _ in range(quantity):
        # Bull put spread
        strategy_legs.append({
            'type': 'put',
            'position': 'long',
            'strike': long_put_strike,
            'expiry': expiration,
            'price': long_put_premium,
            'quantity': 1,
            'iv': long_put_iv
        })
        
        strategy_legs.append({
            'type': 'put',
            'position': 'short',
            'strike': short_put_strike,
            'expiry': expiration,
            'price': short_put_premium,
            'quantity': 1,
            'iv': short_put_iv
        })
        
        # Bear call spread
        strategy_legs.append({
            'type': 'call',
            'position': 'short',
            'strike': short_call_strike,
            'expiry': expiration,
            'price': short_call_premium,
            'quantity': 1,
            'iv': short_call_iv
        })
        
        strategy_legs.append({
            'type': 'call',
            'position': 'long',
            'strike': long_call_strike,
            'expiry': expiration,
            'price': long_call_premium,
            'quantity': 1,
            'iv': long_call_iv
        })
    
    return strategy_legs

def create_butterfly(low_strike: float, mid_strike: float, high_strike: float, 
                   expiration: str, low_premium: float, mid_premium: float, high_premium: float,
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
    
    strategy_legs = []
    
    for _ in range(quantity):
        # Long lower strike
        strategy_legs.append({
            'type': option_type.lower(),
            'position': 'long',
            'strike': low_strike,
            'expiry': expiration,
            'price': low_premium,
            'quantity': 1,
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
                'quantity': 1,
                'iv': mid_iv
            })
        
        # Long higher strike
        strategy_legs.append({
            'type': option_type.lower(),
            'position': 'long',
            'strike': high_strike,
            'expiry': expiration,
            'price': high_premium,
            'quantity': 1,
            'iv': high_iv
        })
    
    return strategy_legs

def create_straddle(strike: float, expiration: str, call_premium: float, put_premium: float,
                  quantity: int = 1, call_iv: float = 0.3, put_iv: float = 0.3) -> List[Dict[str, Any]]:
    """
    Create a straddle strategy (long call + long put at same strike).
    """
    strategy_legs = []
    
    for _ in range(quantity):
        # Long call
        strategy_legs.append({
            'type': 'call',
            'position': 'long',
            'strike': strike,
            'expiry': expiration,
            'price': call_premium,
            'quantity': 1,
            'iv': call_iv
        })
        
        # Long put
        strategy_legs.append({
            'type': 'put',
            'position': 'long',
            'strike': strike,
            'expiry': expiration,
            'price': put_premium,
            'quantity': 1,
            'iv': put_iv
        })
    
    return strategy_legs

def create_strangle(call_strike: float, put_strike: float, expiration: str,
                  call_premium: float, put_premium: float, quantity: int = 1,
                  call_iv: float = 0.3, put_iv: float = 0.3) -> List[Dict[str, Any]]:
    """
    Create a strangle strategy (long call at higher strike + long put at lower strike).
    """
    if put_strike >= call_strike:
        raise ValueError("Put strike must be less than call strike for a strangle")
    
    strategy_legs = []
    
    for _ in range(quantity):
        # Long call (higher strike)
        strategy_legs.append({
            'type': 'call',
            'position': 'long',
            'strike': call_strike,
            'expiry': expiration,
            'price': call_premium,
            'quantity': 1,
            'iv': call_iv
        })
        
        # Long put (lower strike)
        strategy_legs.append({
            'type': 'put',
            'position': 'long',
            'strike': put_strike,
            'expiry': expiration,
            'price': put_premium,
            'quantity': 1,
            'iv': put_iv
        })
    
    return strategy_legs

def create_collar(stock_price: float, put_strike: float, call_strike: float, 
                expiration: str, put_premium: float, call_premium: float,
                quantity: int = 1, put_iv: float = 0.3, call_iv: float = 0.3) -> List[Dict[str, Any]]:
    """
    Create a collar strategy (long stock + long put + short call).
    """
    if put_strike >= call_strike:
        raise ValueError("Put strike must be less than call strike for a collar")
    
    strategy_legs = []
    
    for _ in range(quantity):
        # Long stock
        strategy_legs.append({
            'type': 'stock',
            'position': 'long',
            'price': stock_price,
            'quantity': 100  # 100 shares per contract
        })
        
        # Long put (protection)
        strategy_legs.append({
            'type': 'put',
            'position': 'long',
            'strike': put_strike,
            'expiry': expiration,
            'price': put_premium,
            'quantity': 1,
            'iv': put_iv
        })
        
        # Short call (income)
        strategy_legs.append({
            'type': 'call',
            'position': 'short',
            'strike': call_strike,
            'expiry': expiration,
            'price': call_premium,
            'quantity': 1,
            'iv': call_iv
        })
    
    return strategy_legs

def create_diagonal_spread(long_strike: float, short_strike: float, 
                         long_expiration: str, short_expiration: str,
                         long_premium: float, short_premium: float,
                         option_type: str = 'call', quantity: int = 1,
                         long_iv: float = 0.3, short_iv: float = 0.3) -> List[Dict[str, Any]]:
    """
    Create a diagonal spread (long farther expiration + short nearer expiration at different strikes).
    """
    if option_type.lower() not in ['call', 'put']:
        raise ValueError(f"Invalid option type: {option_type}. Use 'call' or 'put'.")
    
    strategy_legs = []
    
    for _ in range(quantity):
        # Long option (farther expiration)
        strategy_legs.append({
            'type': option_type.lower(),
            'position': 'long',
            'strike': long_strike,
            'expiry': long_expiration,
            'price': long_premium,
            'quantity': 1,
            'iv': long_iv
        })
        
        # Short option (nearer expiration)
        strategy_legs.append({
            'type': option_type.lower(),
            'position': 'short',
            'strike': short_strike,
            'expiry': short_expiration,
            'price': short_premium,
            'quantity': 1,
            'iv': short_iv
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
    validated_legs = []
    
    for leg in legs:
        # Ensure minimum required fields
        if 'type' not in leg:
            raise ValueError("Each leg must have a 'type' field")
        if 'position' not in leg:
            raise ValueError("Each leg must have a 'position' field")
        
        # Validate field values
        if leg['type'] not in ['call', 'put', 'stock']:
            raise ValueError(f"Invalid leg type: {leg['type']}. Use 'call', 'put', or 'stock'.")
        if leg['position'] not in ['long', 'short']:
            raise ValueError(f"Invalid position: {leg['position']}. Use 'long' or 'short'.")
        
        # Ensure option legs have strike and expiry
        if leg['type'] in ['call', 'put']:
            if 'strike' not in leg:
                raise ValueError(f"Option legs must have a 'strike' field")
            if 'expiry' not in leg:
                raise ValueError(f"Option legs must have an 'expiry' field")
        
        # Ensure stock legs have price
        if leg['type'] == 'stock' and 'price' not in leg:
            raise ValueError("Stock legs must have a 'price' field")
        
        # Set default values for missing fields
        if 'quantity' not in leg:
            leg['quantity'] = 1
        if 'price' not in leg:
            leg['price'] = 0.0
        if 'iv' not in leg and leg['type'] in ['call', 'put']:
            leg['iv'] = 0.3
        
        validated_legs.append(leg)
    
    return validated_legs