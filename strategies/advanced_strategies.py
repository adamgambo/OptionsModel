# --- strategies/advanced_strategies.py ---
def iron_condor_strategy(p1, p2, c1, c2, expiration, premiums):
    """
    Iron Condor:
    Short Put at P1 (strike)
    Long Put at P2 (lower strike)
    Short Call at C1 (strike)
    Long Call at C2 (higher strike)
    All same expiration.

    premiums: dict with keys 'short_put', 'long_put', 'short_call', 'long_call'
    """
    return [
        {"type": "put", "position": "short", "strike": p1, "expiry": expiration, "price": premiums["short_put"]},
        {"type": "put", "position": "long", "strike": p2, "expiry": expiration, "price": premiums["long_put"]},
        {"type": "call", "position": "short", "strike": c1, "expiry": expiration, "price": premiums["short_call"]},
        {"type": "call", "position": "long", "strike": c2, "expiry": expiration, "price": premiums["long_call"]},
    ]


def butterfly_strategy(k1, k2, k3, expiration, premiums):
    """
    Butterfly Spread (Call):
    Long Call at K1 (lower strike)
    Short 2 Calls at K2 (middle strike)
    Long Call at K3 (higher strike)
    All same expiration.

    premiums: dict with keys 'long_low', 'short_mid', 'long_high'
    """
    return [
        {"type": "call", "position": "long", "strike": k1, "expiry": expiration, "price": premiums["long_low"]},
        {"type": "call", "position": "short", "strike": k2, "expiry": expiration, "price": premiums["short_mid"]},
        {"type": "call", "position": "short", "strike": k2, "expiry": expiration, "price": premiums["short_mid"]},
        {"type": "call", "position": "long", "strike": k3, "expiry": expiration, "price": premiums["long_high"]},
    ]


def collar_strategy(stock_price, put_strike, call_strike, expiration, premiums):
    """
    Collar:
    Long Stock
    Long Put (protection)
    Short Call (income)

    premiums: dict with keys 'long_put', 'short_call'
    """
    return [
        {"type": "stock", "position": "long", "price": stock_price},
        {"type": "put", "position": "long", "strike": put_strike, "expiry": expiration, "price": premiums["long_put"]},
        {"type": "call", "position": "short", "strike": call_strike, "expiry": expiration, "price": premiums["short_call"]},
    ]


def diagonal_spread_strategy(long_strike, short_strike, long_exp, short_exp, premiums):
    """
    Diagonal Spread:
    Long option with farther expiration and one strike
    Short option with nearer expiration and another strike

    premiums: dict with keys 'long', 'short'
    """
    return [
        {"type": "call", "position": "long", "strike": long_strike, "expiry": long_exp, "price": premiums["long"]},
        {"type": "call", "position": "short", "strike": short_strike, "expiry": short_exp, "price": premiums["short"]},
    ]


def double_diagonal_strategy(p1, p2, c1, c2, near_exp, far_exp, premiums):
    """
    Double Diagonal Spread:
    Short Put and Call (near expiration)
    Long Put and Call (far expiration) at different strikes

    premiums: dict with keys 'short_put', 'long_put', 'short_call', 'long_call'
    """
    return [
        {"type": "put", "position": "short", "strike": p1, "expiry": near_exp, "price": premiums["short_put"]},
        {"type": "put", "position": "long", "strike": p2, "expiry": far_exp, "price": premiums["long_put"]},
        {"type": "call", "position": "short", "strike": c1, "expiry": near_exp, "price": premiums["short_call"]},
        {"type": "call", "position": "long", "strike": c2, "expiry": far_exp, "price": premiums["long_call"]},
    ]


def straddle_strategy(strike, expiration, premiums):
    """
    Straddle:
    Long Call and Long Put at same strike and expiration

    premiums: dict with keys 'call', 'put'
    """
    return [
        {"type": "call", "position": "long", "strike": strike, "expiry": expiration, "price": premiums["call"]},
        {"type": "put", "position": "long", "strike": strike, "expiry": expiration, "price": premiums["put"]},
    ]


def strangle_strategy(put_strike, call_strike, expiration, premiums):
    """
    Strangle:
    Long Put at lower strike
    Long Call at higher strike

    premiums: dict with keys 'put', 'call'
    """
    return [
        {"type": "put", "position": "long", "strike": put_strike, "expiry": expiration, "price": premiums["put"]},
        {"type": "call", "position": "long", "strike": call_strike, "expiry": expiration, "price": premiums["call"]},
    ]


def covered_strangle_strategy(stock_price, put_strike, call_strike, expiration, premiums):
    """
    Covered Strangle:
    Long Stock
    Short Put and Short Call at different strikes

    premiums: dict with keys 'put', 'call'
    """
    return [
        {"type": "stock", "position": "long", "price": stock_price},
        {"type": "put", "position": "short", "strike": put_strike, "expiry": expiration, "price": premiums["put"]},
        {"type": "call", "position": "short", "strike": call_strike, "expiry": expiration, "price": premiums["call"]},
    ]


def synthetic_put_strategy(call_strike, expiration, call_premium, stock_price):
    """
    Synthetic Put:
    Short Stock + Long Call at same strike and expiration
    """
    return [
        {"type": "stock", "position": "short", "price": stock_price},
        {"type": "call", "position": "long", "strike": call_strike, "expiry": expiration, "price": call_premium},
    ]


def reverse_conversion_strategy(strike, expiration, premiums, stock_price):
    """
    Reverse Conversion:
    Short Stock + Long Call + Short Put at same strike and expiration

    premiums: dict with keys 'call', 'put'
    """
    return [
        {"type": "stock", "position": "short", "price": stock_price},
        {"type": "call", "position": "long", "strike": strike, "expiry": expiration, "price": premiums["call"]},
        {"type": "put", "position": "short", "strike": strike, "expiry": expiration, "price": premiums["put"]},
    ]