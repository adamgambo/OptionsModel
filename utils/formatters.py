# utils/formatters.py
"""
Utility functions for formatting data in the Options Strategy Calculator.
"""
import pandas as pd
import numpy as np
from datetime import datetime

def format_price(price, prefix="$", decimals=2):
    """
    Format price with currency symbol and fixed decimals.
    
    Parameters:
        price (float): Price to format
        prefix (str): Currency symbol
        decimals (int): Number of decimal places
        
    Returns:
        str: Formatted price
    """
    if price is None:
        return "N/A"
    if isinstance(price, str):
        return price
    return f"{prefix}{price:.{decimals}f}"

def format_percent(value, decimals=2, with_sign=True):
    """
    Format value as percentage.
    
    Parameters:
        value (float): Value to format (as decimal, e.g., 0.05 for 5%)
        decimals (int): Number of decimal places
        with_sign (bool): Whether to include + sign for positive values
        
    Returns:
        str: Formatted percentage
    """
    if value is None:
        return "N/A"
    
    value_pct = value * 100
    
    if with_sign and value_pct > 0:
        return f"+{value_pct:.{decimals}f}%"
    else:
        return f"{value_pct:.{decimals}f}%"

def format_contract_size(value, contract_size=100):
    """
    Format option contract size (typically 100 shares per contract).
    
    Parameters:
        value (float): Value per share
        contract_size (int): Number of shares per contract
        
    Returns:
        float: Value per contract
    """
    return value * contract_size

def format_date(date_obj, format_str="%Y-%m-%d"):
    """
    Format date object as string.
    
    Parameters:
        date_obj (datetime or str): Date to format
        format_str (str): Format string
        
    Returns:
        str: Formatted date
    """
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.strptime(date_obj, format_str).date()
        except ValueError:
            return date_obj
    
    if isinstance(date_obj, datetime):
        return date_obj.strftime(format_str)
    
    return "N/A"

def format_days_to_expiry(days):
    """
    Format days to expiry with descriptive text.
    
    Parameters:
        days (int): Days to expiry
        
    Returns:
        str: Formatted days to expiry
    """
    if days <= 0:
        return "Expires today"
    elif days == 1:
        return "1 day to expiry"
    elif days < 7:
        return f"{days} days to expiry (very short-term)"
    elif days < 30:
        return f"{days} days to expiry (short-term)"
    elif days < 90:
        return f"{days} days to expiry (medium-term)"
    elif days < 180:
        return f"{days} days to expiry (quarterly)"
    elif days < 365:
        return f"{days} days to expiry (long-term)"
    else:
        years = days / 365
        if years < 1.5:
            return f"{days} days to expiry (LEAP - {years:.1f} year)"
        else:
            return f"{days} days to expiry (LEAP - {years:.1f} years)"

def format_greeks(greeks_dict, decimals=4):
    """
    Format Greeks dictionary with consistent precision.
    
    Parameters:
        greeks_dict (dict): Dictionary of Greeks
        decimals (int): Number of decimal places
        
    Returns:
        dict: Dictionary with formatted Greeks
    """
    if not greeks_dict:
        return {}
    
    formatted = {}
    for key, value in greeks_dict.items():
        if key == 'delta':
            formatted[key] = f"{value:.{decimals}f}"
        elif key == 'gamma':
            formatted[key] = f"{value:.{decimals+2}f}"
        elif key == 'theta':
            formatted[key] = f"${value:.{decimals-1}f}"
        elif key == 'vega':
            formatted[key] = f"${value:.{decimals-1}f}"
        elif key == 'rho':
            formatted[key] = f"${value:.{decimals-1}f}"
        else:
            formatted[key] = f"{value:.{decimals}f}"
    
    return formatted

def format_option_type(option_type, position=None):
    """
    Format option type and position for display.
    
    Parameters:
        option_type (str): 'call' or 'put'
        position (str, optional): 'long' or 'short'
        
    Returns:
        str: Formatted option type and position
    """
    if not option_type:
        return "N/A"
    
    option_type = option_type.lower()
    
    if position:
        position = position.lower()
        if position == 'long':
            if option_type == 'call':
                return "Long Call"
            elif option_type == 'put':
                return "Long Put"
            else:
                return f"Long {option_type.capitalize()}"
        elif position == 'short':
            if option_type == 'call':
                return "Short Call"
            elif option_type == 'put':
                return "Short Put"
            else:
                return f"Short {option_type.capitalize()}"
    
    if option_type == 'call':
        return "Call"
    elif option_type == 'put':
        return "Put"
    else:
        return option_type.capitalize()

def format_moneyness(strike, current_price):
    """
    Format option moneyness (ITM, ATM, OTM) based on strike and current price.
    
    Parameters:
        strike (float): Option strike price
        current_price (float): Current stock price
        
    Returns:
        str: Moneyness description
    """
    if strike is None or current_price is None:
        return "N/A"
    
    pct_diff = (strike / current_price - 1) * 100
    
    if abs(pct_diff) < 1:
        return "ATM (At The Money)"
    elif pct_diff > 20:
        return f"Deep OTM (+{pct_diff:.1f}%)"
    elif pct_diff > 10:
        return f"OTM (+{pct_diff:.1f}%)"
    elif pct_diff > 0:
        return f"Slightly OTM (+{pct_diff:.1f}%)"
    elif pct_diff > -10:
        return f"Slightly ITM ({pct_diff:.1f}%)"
    elif pct_diff > -20:
        return f"ITM ({pct_diff:.1f}%)"
    else:
        return f"Deep ITM ({pct_diff:.1f}%)"

def format_dataframe_for_display(df):
    """
    Format a DataFrame for display in Streamlit.
    
    Parameters:
        df (pd.DataFrame): DataFrame to format
        
    Returns:
        pd.DataFrame: Formatted DataFrame
    """
    formatted_df = df.copy()
    
    # Format numeric columns
    for col in formatted_df.columns:
        if col.lower() in ['price', 'lastprice', 'bid', 'ask', 'last', 'mark']:
            formatted_df[col] = formatted_df[col].apply(lambda x: format_price(x) if pd.notnull(x) else "N/A")
        elif col.lower() in ['change', 'changepct', 'iv', 'impliedvolatility']:
            formatted_df[col] = formatted_df[col].apply(lambda x: format_percent(x) if pd.notnull(x) else "N/A")
    
    return formatted_df