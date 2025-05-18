# utils/validators.py
"""
Validator functions for input validation in Options Strategy Calculator.
"""
import re
import pandas as pd
from datetime import datetime

def validate_ticker(ticker):
    """
    Validate stock ticker format.
    
    Parameters:
        ticker (str): Stock ticker to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not ticker:
        return False, "Ticker cannot be empty"
    
    # Basic validation: alphanumeric with optional dot or dash
    if not re.match(r'^[A-Za-z0-9.\-]+$', ticker):
        return False, "Invalid ticker format"
    
    # Length check
    if len(ticker) > 6:
        return False, "Ticker too long (max 6 characters)"
    
    return True, ""

def validate_expiration_date(expiry_date):
    """
    Validate expiration date format and check if it's in the future.
    
    Parameters:
        expiry_date (str): Expiration date in YYYY-MM-DD format
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not expiry_date:
        return False, "Expiration date cannot be empty"
    
    # Check format
    try:
        expiry = datetime.strptime(expiry_date, "%Y-%m-%d").date()
    except ValueError:
        return False, "Invalid date format, use YYYY-MM-DD"
    
    # Check if in future
    today = datetime.now().date()
    if expiry < today:
        return False, "Expiration date must be in the future"
    
    return True, ""

def validate_strike_price(strike_price, stock_price=None):
    """
    Validate strike price.
    
    Parameters:
        strike_price (float or str): Strike price to validate
        stock_price (float, optional): Current stock price for reference
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # Check if empty
    if strike_price is None or (isinstance(strike_price, str) and not strike_price.strip()):
        return False, "Strike price cannot be empty"
    
    # Convert to float if string
    if isinstance(strike_price, str):
        try:
            strike_price = float(strike_price.strip())
        except ValueError:
            return False, "Strike price must be a number"
    
    # Check if positive
    if strike_price <= 0:
        return False, "Strike price must be positive"
    
    # Optional check if within reasonable range of stock price
    if stock_price is not None:
        if strike_price < stock_price * 0.1 or strike_price > stock_price * 10:
            return False, f"Strike price {strike_price} seems extreme relative to stock price {stock_price}"
    
    return True, ""

def validate_premium(premium):
    """
    Validate option premium.
    
    Parameters:
        premium (float or str): Premium to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # Check if empty
    if premium is None or (isinstance(premium, str) and not premium.strip()):
        return False, "Premium cannot be empty"
    
    # Convert to float if string
    if isinstance(premium, str):
        try:
            premium = float(premium.strip())
        except ValueError:
            return False, "Premium must be a number"
    
    # Check if non-negative
    if premium < 0:
        return False, "Premium must be non-negative"
    
    return True, ""

def validate_quantity(quantity):
    """
    Validate position quantity.
    
    Parameters:
        quantity (int or str): Quantity to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # Check if empty
    if quantity is None or (isinstance(quantity, str) and not quantity.strip()):
        return False, "Quantity cannot be empty"
    
    # Convert to int if string
    if isinstance(quantity, str):
        try:
            quantity = int(quantity.strip())
        except ValueError:
            return False, "Quantity must be an integer"
    
    # Check if positive
    if quantity <= 0:
        return False, "Quantity must be positive"
    
    return True, ""

def validate_spread_strikes(low_strike, high_strike):
    """
    Validate that spread strikes are in correct order.
    
    Parameters:
        low_strike (float): Lower strike price
        high_strike (float): Higher strike price
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # Validate individual strikes
    low_valid, low_msg = validate_strike_price(low_strike)
    if not low_valid:
        return False, f"Lower strike: {low_msg}"
    
    high_valid, high_msg = validate_strike_price(high_strike)
    if not high_valid:
        return False, f"Higher strike: {high_msg}"
    
    # Check order
    if low_strike >= high_strike:
        return False, "Lower strike must be less than higher strike"
    
    return True, ""

def validate_strategy_legs(legs):
    """
    Validate strategy legs for completeness and consistency.
    
    Parameters:
        legs (list): List of strategy leg dictionaries
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not legs:
        return False, "Strategy must have at least one leg"
    
    required_fields = {
        'call': ['strike', 'expiry', 'position'],
        'put': ['strike', 'expiry', 'position'],
        'stock': ['position']
    }
    
    for i, leg in enumerate(legs):
        leg_type = leg.get('type', '').lower()
        
        # Check leg type
        if leg_type not in required_fields:
            return False, f"Leg {i+1}: Invalid leg type '{leg_type}'"
        
        # Check required fields
        for field in required_fields[leg_type]:
            if field not in leg or leg[field] is None:
                return False, f"Leg {i+1}: Missing required field '{field}'"
        
        # Type-specific validation
        if leg_type in ['call', 'put']:
            # Validate strike
            valid_strike, strike_msg = validate_strike_price(leg['strike'])
            if not valid_strike:
                return False, f"Leg {i+1}: {strike_msg}"
            
            # Validate expiry
            valid_expiry, expiry_msg = validate_expiration_date(leg['expiry'])
            if not valid_expiry:
                return False, f"Leg {i+1}: {expiry_msg}"
        
        # Validate position
        position = leg.get('position', '').lower()
        if position not in ['long', 'short']:
            return False, f"Leg {i+1}: Invalid position '{position}'"
    
    return True, ""

def validate_dataframe(df, required_columns=None):
    """
    Validate DataFrame structure.
    
    Parameters:
        df (pd.DataFrame): DataFrame to validate
        required_columns (list, optional): List of required column names
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if df is None or df.empty:
        return False, "DataFrame is empty"
    
    if required_columns:
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return False, f"Missing required columns: {', '.join(missing_columns)}"
    
    return True, ""