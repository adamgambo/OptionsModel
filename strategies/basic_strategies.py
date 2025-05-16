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