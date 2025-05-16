# --- strategies/basic_strategies.py ---
from dataclasses import dataclass

@dataclass
class Leg:
    type: str  # 'call', 'put', or 'stock'
    position: str  # 'long' or 'short'
    strike: float = None
    expiry: str = None
    price: float = 0.0
    quantity: int = 1

def long_call_strategy(strike, expiration, premium):
    return [
        Leg(type='call', position='long', strike=strike, expiry=str(expiration), price=premium)
    ]


def long_put_strategy(strike, expiration, premium):
    return [
        Leg(type='put', position='long', strike=strike, expiry=str(expiration), price=premium)
    ]


def covered_call_strategy(stock_price, call_strike, expiration, call_premium):
    return [
        Leg(type='stock', position='long', price=stock_price),
        Leg(type='call', position='short', strike=call_strike, expiry=str(expiration), price=call_premium)
    ]


def cash_secured_put_strategy(put_strike, expiration, premium):
    return [
        Leg(type='put', position='short', strike=put_strike, expiry=str(expiration), price=premium)
    ]


def naked_call_strategy(call_strike, expiration, premium):
    return [
        Leg(type='call', position='short', strike=call_strike, expiry=str(expiration), price=premium)
    ]


def naked_put_strategy(put_strike, expiration, premium):
    return [
        Leg(type='put', position='short', strike=put_strike, expiry=str(expiration), price=premium)
    ]