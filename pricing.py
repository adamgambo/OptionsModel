# --- pricing.py ---
import numpy as np
import streamlit as st
from scipy.stats import norm

@st.cache_data
def black_scholes(option_type, S, K, t, r, sigma):
    if t <= 0 or sigma <= 0:
        return 0.0  # Prevent divide-by-zero or non-sensical input

    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * t) / (sigma * np.sqrt(t))
    d2 = d1 - sigma * np.sqrt(t)
    if option_type == "call":
        return S * norm.cdf(d1) - K * np.exp(-r * t) * norm.cdf(d2)
    elif option_type == "put":
        return K * np.exp(-r * t) * norm.cdf(-d2) - S * norm.cdf(-d1)
    else:
        raise ValueError("Invalid option type")


# --- Calculate Greeks ---
def calculate_greeks(option_type, S, K, t, r, sigma):
    if t <= 0 or sigma <= 0:
        return {"delta": 0.0, "gamma": 0.0, "vega": 0.0, "theta": 0.0, "rho": 0.0}

    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * t) / (sigma * np.sqrt(t))
    d2 = d1 - sigma * np.sqrt(t)
    pdf_d1 = norm.pdf(d1)
    cdf_d1 = norm.cdf(d1)
    cdf_d2 = norm.cdf(d2)

    gamma = pdf_d1 / (S * sigma * np.sqrt(t))
    vega = S * pdf_d1 * np.sqrt(t)

    if option_type == "call":
        delta = cdf_d1
        theta = (-S * pdf_d1 * sigma / (2 * np.sqrt(t))) - (r * K * np.exp(-r * t) * cdf_d2)
        rho = K * t * np.exp(-r * t) * cdf_d2
    elif option_type == "put":
        delta = cdf_d1 - 1
        theta = (-S * pdf_d1 * sigma / (2 * np.sqrt(t))) + (r * K * np.exp(-r * t) * norm.cdf(-d2))
        rho = -K * t * np.exp(-r * t) * norm.cdf(-d2)
    else:
        raise ValueError("Invalid option type")

    return {
        "delta": delta,
        "gamma": gamma,
        "vega": vega / 100,
        "theta": theta / 365,
        "rho": rho / 100
    }