# --- pricing.py ---
import numpy as np
from scipy.stats import norm

def black_scholes(option_type, S, K, t, r, sigma):
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * t) / (sigma * np.sqrt(t))
    d2 = d1 - sigma * np.sqrt(t)
    if option_type == "call":
        return S * norm.cdf(d1) - K * np.exp(-r * t) * norm.cdf(d2)
    elif option_type == "put":
        return K * np.exp(-r * t) * norm.cdf(-d2) - S * norm.cdf(-d1)
    else:
        raise ValueError("Invalid option type")