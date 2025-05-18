# utils/error_handlers.py
import logging
import traceback
from functools import wraps
import streamlit as st

logger = logging.getLogger(__name__)

def handle_api_error(func):
    """
    Decorator to handle API errors for data fetching functions.
    Provides standardized error handling and logging.
    
    Parameters:
        func: Function to decorate
        
    Returns:
        Wrapped function that handles errors
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_message = str(e)
            logger.error(f"API Error in {func.__name__}: {error_message}")
            logger.debug(traceback.format_exc())
            
            # Provide friendly error messages based on error type
            if "Connection" in error_message or "timeout" in error_message.lower():
                raise Exception("Cannot connect to data provider. Please check your internet connection.")
            elif "Rate limit" in error_message or "429" in error_message:
                raise Exception("Rate limit exceeded. Please try again in a few minutes.")
            elif "Not found" in error_message or "404" in error_message or "no data" in error_message.lower():
                raise Exception(f"Data not found. Please verify the ticker symbol or data availability.")
            elif "Authentication" in error_message or "401" in error_message:
                raise Exception("Authentication error. Please check your API credentials.")
            elif "Permission" in error_message or "403" in error_message:
                raise Exception("Permission denied. You may not have access to this data.")
            else:
                raise Exception(f"Error fetching data: {error_message}")
    return wrapper

def handle_calculation_error(func):
    """
    Decorator to handle calculation errors for pricing functions.
    Provides fallback values instead of crashing.
    
    Parameters:
        func: Function to decorate
        
    Returns:
        Wrapped function that handles errors
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_message = str(e)
            logger.error(f"Calculation Error in {func.__name__}: {error_message}")
            logger.debug(traceback.format_exc())
            
            # Return fallback values based on function type
            func_name = func.__name__.lower()
            
            if "black_scholes" in func_name or "price" in func_name:
                logger.info(f"Using fallback pricing for {func.__name__}")
                # For option pricing, return intrinsic value if possible
                if len(args) >= 4:
                    option_type = args[0].lower() if args else ''
                    s = args[1] if len(args) > 1 else 0
                    k = args[2] if len(args) > 2 else 0
                    
                    if option_type == 'call':
                        return max(0, s - k)
                    elif option_type == 'put':
                        return max(0, k - s)
                return 0.0  # Default price
                
            elif "greeks" in func_name:
                logger.info(f"Using fallback greeks for {func.__name__}")
                option_type = args[0].lower() if args else 'call'
                return {
                    "delta": 0.5 if option_type == "call" else -0.5,
                    "gamma": 0.01,
                    "vega": 0.01,
                    "theta": -0.01,
                    "rho": 0.01
                }
                
            elif "volatility" in func_name:
                logger.info(f"Using fallback volatility for {func.__name__}")
                return 0.3  # Default IV
                
            else:
                # Re-raise for unknown function types
                raise
    return wrapper

def handle_ui_error(func):
    """
    Decorator to handle UI-related errors.
    Catches errors and displays them in the Streamlit UI.
    
    Parameters:
        func: Function to decorate
        
    Returns:
        Wrapped function that handles UI errors
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_message = str(e)
            logger.error(f"UI Error in {func.__name__}: {error_message}")
            logger.debug(traceback.format_exc())
            
            # Display error in UI
            st.error(f"Error: {error_message}")
            
            # Return None or appropriate fallback
            return None
    return wrapper

def safe_execute(func, default_value=None, error_message=None):
    """
    Safely execute a function with proper error handling.
    
    Parameters:
        func: Function to execute
        default_value: Value to return on error
        error_message: Custom error message to display
        
    Returns:
        Result of func or default_value on error
    """
    try:
        return func()
    except Exception as e:
        if error_message:
            st.error(error_message)
        else:
            st.error(f"Error: {str(e)}")
        logger.error(f"Error in safe_execute: {str(e)}")
        logger.debug(traceback.format_exc())
        return default_value