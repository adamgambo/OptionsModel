# --- strategies/spread_strategies.py ---
# (Template only)
from collections import namedtuple

Leg = namedtuple('Leg', ['type', 'position', 'strike', 'expiration', 'price'])

def call_spread_strategy(strike_long, strike_short, expiration, premium_long, premium_short):
    """
    Debit Call Spread (Bull Call Spread):
    Buy call at lower strike, sell call at higher strike.
    """
    return [
        Leg(type='call', position='long', strike=strike_long, expiration=expiration, price=premium_long),
        Leg(type='call', position='short', strike=strike_short, expiration=expiration, price=premium_short)
    ]

def put_spread_strategy(strike_long, strike_short, expiration, premium_long, premium_short):
    """
    Debit Put Spread (Bear Put Spread):
    Buy put at higher strike, sell put at lower strike.
    """
    return [
        Leg(type='put', position='long', strike=strike_long, expiration=expiration, price=premium_long),
        Leg(type='put', position='short', strike=strike_short, expiration=expiration, price=premium_short)
    ]

def poor_mans_covered_call(long_call_strike, long_call_exp, long_call_price,
                           short_call_strike, short_call_exp, short_call_price):
    """
    Poor Man's Covered Call:
    Long deep ITM call (LEAPS), short near-term OTM call.
    """
    return [
        Leg(type='call', position='long', strike=long_call_strike, expiration=long_call_exp, price=long_call_price),
        Leg(type='call', position='short', strike=short_call_strike, expiration=short_call_exp, price=short_call_price)
    ]

def calendar_spread(strike, short_exp, short_price, long_exp, long_price):
    """
    Calendar Spread:
    Short near-term option, long farther-term option at same strike.
    """
    return [
        Leg(type='call', position='short', strike=strike, expiration=short_exp, price=short_price),
        Leg(type='call', position='long', strike=strike, expiration=long_exp, price=long_price)
    ]

def ratio_backspread(short_strike, short_exp, short_price,
                    long_strike, long_exp, long_price, ratio=2):
    """
    Ratio Backspread:
    Short 1 call, Long 2 (or more) calls at different strike.
    """
    return [
        Leg(type='call', position='short', strike=short_strike, expiration=short_exp, price=short_price),
        *[Leg(type='call', position='long', strike=long_strike, expiration=long_exp, price=long_price) for _ in range(ratio)]
    ]

def credit_spread(short_strike, short_premium, long_strike, long_premium, expiration, option_type='put'):
    """
    Credit Spread:
    Can be a call or put credit spread depending on option_type.
    Sell higher premium option, buy lower premium one to cap risk.
    """
    return [
        Leg(type=option_type, position='short', strike=short_strike, expiration=expiration, price=short_premium),
        Leg(type=option_type, position='long', strike=long_strike, expiration=expiration, price=long_premium)
    ]

def get_spread_strategy(name, **kwargs):
    if name == 'Call Spread':
        return call_spread_strategy(**kwargs)
    elif name == 'Put Spread':
        return put_spread_strategy(**kwargs)
    elif name == "Poor Man's Covered Call":
        return poor_mans_covered_call(**kwargs)
    elif name == "Calendar Spread":
        return calendar_spread(**kwargs)
    elif name == "Ratio Back Spread":
        return ratio_backspread(**kwargs)
    elif name == "Credit Spread":
        return credit_spread(**kwargs)
    else:
        raise ValueError(f"Unknown spread strategy: {name}")