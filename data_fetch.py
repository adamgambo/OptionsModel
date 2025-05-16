# --- data_fetch.py ---
import yfinance as yf
import streamlit as st
import pandas as pd
from datetime import datetime

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_stock_price(ticker):
    """Get the latest stock price for a given ticker."""
    if not isinstance(ticker, str) or not ticker.strip():
        raise ValueError("Ticker must be a non-empty string.")
    
    try:
        stock = yf.Ticker(ticker)
        price_data = stock.history(period="1d")
        
        if price_data.empty:
            raise ValueError(f"No price data available for {ticker}")
        
        return price_data["Close"].iloc[-1]
    except Exception as e:
        raise Exception(f"Error fetching stock price for {ticker}: {str(e)}")

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_option_chain(ticker, expiration):
    """Get the full option chain for a specific expiration date."""
    if not isinstance(ticker, str) or not ticker.strip():
        raise ValueError("Ticker must be a non-empty string.")
    if not expiration:
        raise ValueError("Expiration date must be provided.")
    
    try:
        stock = yf.Ticker(ticker)
        chain = stock.option_chain(expiration)
        
        # Convert to easier-to-use format
        calls = chain.calls
        puts = chain.puts
        
        # Add some calculated columns that might be useful
        for df in [calls, puts]:
            # Calculate implied volatility if not already present
            if 'impliedVolatility' not in df.columns:
                df['impliedVolatility'] = 0.3  # Default value
            
            # Add in-the-money flag
            current_price = get_stock_price(ticker)
            if 'inTheMoney' not in df.columns:
                if 'call' in chain.__dir__():  # If this is a calls dataframe
                    df['inTheMoney'] = df['strike'] < current_price
                else:  # If this is a puts dataframe
                    df['inTheMoney'] = df['strike'] > current_price
        
        return calls, puts
    except Exception as e:
        raise Exception(f"Error fetching option chain for {ticker} (expiration: {expiration}): {str(e)}")

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_expiration_dates(ticker):
    """Get all available expiration dates for options."""
    if not isinstance(ticker, str) or not ticker.strip():
        raise ValueError("Ticker must be a non-empty string.")
    
    try:
        stock = yf.Ticker(ticker)
        dates = stock.options
        
        if not dates:
            return []
        
        # Filter out expired dates
        today = datetime.now().date()
        valid_dates = [date for date in dates if datetime.strptime(date, "%Y-%m-%d").date() >= today]
        
        return valid_dates
    except Exception as e:
        raise Exception(f"Error fetching expiration dates for {ticker}: {str(e)}")

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_historical_data(ticker, period="1y", interval="1d"):
    """Get historical price data for backtesting."""
    if not isinstance(ticker, str) or not ticker.strip():
        raise ValueError("Ticker must be a non-empty string.")
    
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period=period, interval=interval)
        
        if data.empty:
            raise ValueError(f"No historical data available for {ticker}")
        
        return data
    except Exception as e:
        raise Exception(f"Error fetching historical data for {ticker}: {str(e)}")

# Utility function to get ATM options
def get_atm_options(ticker, expiration, width=0.1):
    """Get at-the-money options within a certain width of current price."""
    current_price = get_stock_price(ticker)
    calls, puts = get_option_chain(ticker, expiration)
    
    # Filter for options within range
    price_min = current_price * (1 - width)
    price_max = current_price * (1 + width)
    
    atm_calls = calls[(calls['strike'] >= price_min) & (calls['strike'] <= price_max)]
    atm_puts = puts[(puts['strike'] >= price_min) & (puts['strike'] <= price_max)]
    
    return atm_calls, atm_puts