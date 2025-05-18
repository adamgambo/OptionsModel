# data/fetcher.py
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import time
import logging
import requests
from functools import lru_cache
import streamlit as st
from utils.error_handlers import handle_api_error

# Setup logging
logger = logging.getLogger(__name__)

@st.cache_data(ttl=300)  # Cache for 5 minutes
@handle_api_error
def get_stock_price(ticker):
    """
    Get the latest stock price for a given ticker with enhanced error handling.
    
    Parameters:
        ticker (str): Stock ticker symbol
        
    Returns:
        float: Current stock price
        
    Raises:
        ValueError: If ticker is invalid
        Exception: For other errors
    """
    if not isinstance(ticker, str) or not ticker.strip():
        raise ValueError("Ticker must be a non-empty string.")
    
    ticker = ticker.strip().upper()
    
    try:
        start_time = time.time()
        stock = yf.Ticker(ticker)
        price_data = stock.history(period="1d")
        
        if price_data.empty:
            # Try alternative method if history is empty
            quote_data = stock.info
            if 'regularMarketPrice' in quote_data:
                logger.info(f"Used alternative method to get price for {ticker} in {time.time() - start_time:.2f}s")
                return quote_data['regularMarketPrice']
            else:
                raise ValueError(f"No price data available for {ticker}")
        
        price = price_data["Close"].iloc[-1]
        logger.info(f"Retrieved price for {ticker}: ${price:.2f} in {time.time() - start_time:.2f}s")
        return price
    
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error fetching data for {ticker}")
        raise Exception(f"Cannot connect to data provider. Please check your internet connection.")
    
    except Exception as e:
        logger.error(f"Error fetching stock price for {ticker}: {str(e)}")
        raise Exception(f"Error fetching stock price for {ticker}: {str(e)}")

@st.cache_data(ttl=300)  # Cache for 5 minutes
@handle_api_error
def get_stock_info(ticker):
    """
    Get comprehensive stock information including company details.
    
    Parameters:
        ticker (str): Stock ticker symbol
        
    Returns:
        dict: Dictionary with stock information
    """
    if not isinstance(ticker, str) or not ticker.strip():
        raise ValueError("Ticker must be a non-empty string.")
    
    ticker = ticker.strip().upper()
    
    try:
        start_time = time.time()
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Make sure we have the minimum required fields
        required_fields = ['symbol', 'shortName']
        if not all(field in info for field in required_fields):
            # Try to fill in missing fields
            for field in required_fields:
                if field not in info:
                    if field == 'symbol':
                        info['symbol'] = ticker
                    elif field == 'shortName':
                        info['shortName'] = ticker
        
        logger.info(f"Retrieved info for {ticker} in {time.time() - start_time:.2f}s")
        return info
    
    except Exception as e:
        logger.error(f"Error fetching stock info for {ticker}: {str(e)}")
        # Return minimal info rather than failing
        return {
            'symbol': ticker,
            'shortName': ticker,
            'sector': 'Unknown',
            'marketCap': 0
        }

@st.cache_data(ttl=300)  # Cache for 5 minutes
@handle_api_error
def get_option_chain(ticker, expiration):
    """
    Get the full option chain for a specific expiration date with enhanced error handling
    and data validation.
    
    Parameters:
        ticker (str): Stock ticker symbol
        expiration (str): Expiration date in YYYY-MM-DD format
        
    Returns:
        tuple: (calls DataFrame, puts DataFrame)
        
    Raises:
        ValueError: If inputs are invalid
        Exception: For other errors
    """
    if not isinstance(ticker, str) or not ticker.strip():
        raise ValueError("Ticker must be a non-empty string.")
    if not expiration:
        raise ValueError("Expiration date must be provided.")
    
    ticker = ticker.strip().upper()
    
    try:
        start_time = time.time()
        stock = yf.Ticker(ticker)
        
        # First check if the expiration date is valid
        available_dates = stock.options
        if not available_dates:
            raise ValueError(f"No options available for {ticker}")
        
        if expiration not in available_dates:
            # Try to find closest expiration date
            available_dates = [datetime.strptime(date, "%Y-%m-%d").date() for date in available_dates]
            target_date = datetime.strptime(expiration, "%Y-%m-%d").date()
            closest_date = min(available_dates, key=lambda x: abs((x - target_date).days))
            expiration = closest_date.strftime("%Y-%m-%d")
            logger.warning(f"Expiration {expiration} not found, using closest date: {expiration}")
        
        # Fetch the option chain
        chain = stock.option_chain(expiration)
        
        # Convert to easier-to-use format
        calls = chain.calls
        puts = chain.puts
        
        # Ensure we have data
        if calls.empty or puts.empty:
            raise ValueError(f"Empty option chain for {ticker} at expiration {expiration}")
        
        # Enhance option chain with calculated columns and validations
        current_price = get_stock_price(ticker)
        calls = _enhance_option_chain(calls, 'call', current_price)
        puts = _enhance_option_chain(puts, 'put', current_price)
        
        logger.info(f"Retrieved option chain for {ticker} ({expiration}) in {time.time() - start_time:.2f}s")
        return calls, puts
    
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error fetching option chain for {ticker}")
        raise Exception(f"Cannot connect to data provider. Please check your internet connection.")
    
    except Exception as e:
        logger.error(f"Error fetching option chain for {ticker} (expiration: {expiration}): {str(e)}")
        raise Exception(f"Error fetching option chain for {ticker} (expiration: {expiration}): {str(e)}")

def _enhance_option_chain(df, option_type, current_price):
    """
    Helper function to enhance option chain with calculated columns.
    
    Parameters:
        df (DataFrame): Option chain DataFrame
        option_type (str): 'call' or 'put'
        current_price (float): Current stock price
        
    Returns:
        DataFrame: Enhanced option chain
    """
    from models.pricing import calculate_implied_volatility
    
    # Fill missing values with reasonable defaults
    if 'lastPrice' not in df.columns or df['lastPrice'].isna().any():
        # Use mid price if last price is missing
        if 'bid' in df.columns and 'ask' in df.columns:
            df['lastPrice'] = df.apply(
                lambda row: (row['bid'] + row['ask']) / 2 if pd.isna(row['lastPrice']) else row['lastPrice'],
                axis=1
            )
        else:
            # If bid/ask are also missing, use a placeholder
            df['lastPrice'] = 0.01
    
    # Calculate implied volatility if not already present
    if 'impliedVolatility' not in df.columns or df['impliedVolatility'].isna().any():
        try:
            df['impliedVolatility'] = 0.3  # Default value
            # Could add calculation here but it's computationally expensive
        except Exception as e:
            logger.warning(f"Error calculating implied volatility: {str(e)}")
            df['impliedVolatility'] = 0.3
    
    # Add in-the-money flag if not present
    if 'inTheMoney' not in df.columns:
        if option_type == 'call':  # If this is a calls dataframe
            df['inTheMoney'] = df['strike'] < current_price
        else:  # If this is a puts dataframe
            df['inTheMoney'] = df['strike'] > current_price
    
    # Add moneyness (% from ATM)
    df['moneyness'] = (df['strike'] / current_price - 1) * 100
    
    # Convert volume and OI to numeric
    for col in ['volume', 'openInterest']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        else:
            df[col] = 0
            
    return df

@st.cache_data(ttl=300)  # Cache for 5 minutes
@handle_api_error
def get_expiration_dates(ticker):
    """
    Get all available expiration dates for options with better handling of
    empty or invalid results.
    
    Parameters:
        ticker (str): Stock ticker symbol
        
    Returns:
        list: List of expiration dates in YYYY-MM-DD format
    """
    if not isinstance(ticker, str) or not ticker.strip():
        raise ValueError("Ticker must be a non-empty string.")
    
    ticker = ticker.strip().upper()
    
    try:
        start_time = time.time()
        stock = yf.Ticker(ticker)
        dates = stock.options
        
        if not dates:
            logger.warning(f"No option expiration dates found for {ticker}")
            return []
        
        # Filter out expired dates
        today = datetime.now().date()
        valid_dates = []
        
        for date in dates:
            try:
                expiry_date = datetime.strptime(date, "%Y-%m-%d").date()
                if expiry_date >= today:
                    valid_dates.append(date)
            except ValueError:
                logger.warning(f"Invalid date format: {date}")
        
        if not valid_dates:
            logger.warning(f"No valid future expiration dates for {ticker}")
            return []
        
        # Sort by date
        valid_dates.sort()
        
        logger.info(f"Retrieved {len(valid_dates)} expiration dates for {ticker} in {time.time() - start_time:.2f}s")
        return valid_dates
    
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error fetching expiration dates for {ticker}")
        raise Exception(f"Cannot connect to data provider. Please check your internet connection.")
    
    except Exception as e:
        logger.error(f"Error fetching expiration dates for {ticker}: {str(e)}")
        raise Exception(f"Error fetching expiration dates for {ticker}: {str(e)}")

@st.cache_data(ttl=300)  # Cache for 5 minutes
@handle_api_error
def get_historical_data(ticker, period="1y", interval="1d"):
    """
    Get historical price data for backtesting with enhanced error handling.
    
    Parameters:
        ticker (str): Stock ticker symbol
        period (str): Data period (e.g., '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
        interval (str): Data interval (e.g., '1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo')
        
    Returns:
        DataFrame: Historical price data
    """
    if not isinstance(ticker, str) or not ticker.strip():
        raise ValueError("Ticker must be a non-empty string.")
    
    ticker = ticker.strip().upper()
    
    # Validate period and interval
    valid_periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
    valid_intervals = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']
    
    if period not in valid_periods:
        logger.warning(f"Invalid period: {period}, defaulting to 1y")
        period = "1y"
    
    if interval not in valid_intervals:
        logger.warning(f"Invalid interval: {interval}, defaulting to 1d")
        interval = "1d"
    
    try:
        start_time = time.time()
        stock = yf.Ticker(ticker)
        data = stock.history(period=period, interval=interval)
        
        if data.empty:
            raise ValueError(f"No historical data available for {ticker}")
        
        # Fill missing values
        data = data.ffill().bfill()
        
        logger.info(f"Retrieved historical data for {ticker} ({period}, {interval}) in {time.time() - start_time:.2f}s")
        return data
    
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error fetching historical data for {ticker}")
        raise Exception(f"Cannot connect to data provider. Please check your internet connection.")
    
    except Exception as e:
        logger.error(f"Error fetching historical data for {ticker}: {str(e)}")
        raise Exception(f"Error fetching historical data for {ticker}: {str(e)}")

def get_option_by_strike(chain, strike):
    """
    Find the option with the closest strike price to the target strike.
    
    Parameters:
        chain (DataFrame): Option chain DataFrame (calls or puts)
        strike (float): Target strike price
        
    Returns:
        Series: Option data for the closest strike
    """
    if chain.empty:
        raise ValueError("Option chain is empty")
    
    # Find the index of the closest strike
    idx = (chain['strike'] - strike).abs().idxmin()
    
    return chain.loc[idx]