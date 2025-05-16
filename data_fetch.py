# --- data_fetch.py ---
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import time
import logging
import requests
from functools import lru_cache
import streamlit as st

# Setup logging
logger = logging.getLogger(__name__)

@st.cache_data(ttl=300)  # Cache for 5 minutes
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
        for df in [calls, puts]:
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
                df['impliedVolatility'] = 0.3  # Default value
            
            # Add in-the-money flag if not present
            current_price = get_stock_price(ticker)
            if 'inTheMoney' not in df.columns:
                if df is calls:  # If this is a calls dataframe
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
        
        logger.info(f"Retrieved option chain for {ticker} ({expiration}) in {time.time() - start_time:.2f}s")
        return calls, puts
    
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error fetching option chain for {ticker}")
        raise Exception(f"Cannot connect to data provider. Please check your internet connection.")
    
    except Exception as e:
        logger.error(f"Error fetching option chain for {ticker} (expiration: {expiration}): {str(e)}")
        raise Exception(f"Error fetching option chain for {ticker} (expiration: {expiration}): {str(e)}")

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_expiration_dates(ticker):
    """
    Get all available expiration dates for options with better handling of
    empty or invalid results.
    
    Parameters:
        ticker (str): Stock ticker symbol
        
    Returns:
        list: List of expiration dates in YYYY-MM-DD format
        
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
def get_historical_data(ticker, period="1y", interval="1d"):
    """
    Get historical price data for backtesting with enhanced error handling.
    
    Parameters:
        ticker (str): Stock ticker symbol
        period (str): Data period (e.g., '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
        interval (str): Data interval (e.g., '1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo')
        
    Returns:
        DataFrame: Historical price data
        
    Raises:
        ValueError: If parameters are invalid
        Exception: For other errors
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

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_stock_fundamentals(ticker):
    """
    Get fundamental stock data including earnings, financials, etc.
    
    Parameters:
        ticker (str): Stock ticker symbol
        
    Returns:
        dict: Dictionary with fundamental data
    """
    if not isinstance(ticker, str) or not ticker.strip():
        raise ValueError("Ticker must be a non-empty string.")
    
    ticker = ticker.strip().upper()
    
    try:
        start_time = time.time()
        stock = yf.Ticker(ticker)
        
        # Gather fundamental data
        fundamentals = {
            'financials': stock.financials.to_dict() if hasattr(stock, 'financials') and not stock.financials.empty else {},
            'quarterly_financials': stock.quarterly_financials.to_dict() if hasattr(stock, 'quarterly_financials') and not stock.quarterly_financials.empty else {},
            'balance_sheet': stock.balance_sheet.to_dict() if hasattr(stock, 'balance_sheet') and not stock.balance_sheet.empty else {},
            'quarterly_balance_sheet': stock.quarterly_balance_sheet.to_dict() if hasattr(stock, 'quarterly_balance_sheet') and not stock.quarterly_balance_sheet.empty else {},
            'cashflow': stock.cashflow.to_dict() if hasattr(stock, 'cashflow') and not stock.cashflow.empty else {},
            'quarterly_cashflow': stock.quarterly_cashflow.to_dict() if hasattr(stock, 'quarterly_cashflow') and not stock.quarterly_cashflow.empty else {},
            'earnings': stock.earnings.to_dict() if hasattr(stock, 'earnings') and not stock.earnings.empty else {},
            'quarterly_earnings': stock.quarterly_earnings.to_dict() if hasattr(stock, 'quarterly_earnings') and not stock.quarterly_earnings.empty else {},
            'sustainability': stock.sustainability.to_dict() if hasattr(stock, 'sustainability') and not stock.sustainability.empty else {},
            'recommendations': stock.recommendations.to_dict() if hasattr(stock, 'recommendations') and not stock.recommendations.empty else {},
        }
        
        logger.info(f"Retrieved fundamental data for {ticker} in {time.time() - start_time:.2f}s")
        return fundamentals
    
    except Exception as e:
        logger.error(f"Error fetching fundamental data for {ticker}: {str(e)}")
        return {}

# Enhanced utility functions
def get_atm_options(ticker, expiration, width=0.1):
    """
    Get at-the-money options within a certain width of current price.
    
    Parameters:
        ticker (str): Stock ticker symbol
        expiration (str): Expiration date in YYYY-MM-DD format
        width (float): Price range to consider ATM, as a fraction of current price
        
    Returns:
        tuple: (ATM calls DataFrame, ATM puts DataFrame)
    """
    current_price = get_stock_price(ticker)
    calls, puts = get_option_chain(ticker, expiration)
    
    # Filter for options within range
    price_min = current_price * (1 - width)
    price_max = current_price * (1 + width)
    
    atm_calls = calls[(calls['strike'] >= price_min) & (calls['strike'] <= price_max)]
    atm_puts = puts[(puts['strike'] >= price_min) & (puts['strike'] <= price_max)]
    
    return atm_calls, atm_puts

def get_option_statistics(ticker):
    """
    Get aggregate statistics for options, like average IV across different expirations.
    
    Parameters:
        ticker (str): Stock ticker symbol
        
    Returns:
        dict: Dictionary with option statistics
    """
    try:
        # Get available expirations
        expirations = get_expiration_dates(ticker)
        if not expirations:
            return {'avg_iv': 0.3, 'iv_skew': 0, 'iv_term_structure': []}
        
        # Get near-term expiration
        near_term_exp = expirations[0]
        
        # Get option chain
        calls, puts = get_option_chain(ticker, near_term_exp)
        
        # Calculate average IV
        call_ivs = calls['impliedVolatility'].dropna().tolist()
        put_ivs = puts['impliedVolatility'].dropna().tolist()
        
        all_ivs = call_ivs + put_ivs
        avg_iv = sum(all_ivs) / len(all_ivs) if all_ivs else 0.3
        
        # Calculate IV skew (difference between OTM put and call IVs)
        current_price = get_stock_price(ticker)
        
        # Find nearest OTM call and put
        otm_calls = calls[calls['strike'] > current_price]
        otm_puts = puts[puts['strike'] < current_price]
        
        if not otm_calls.empty and not otm_puts.empty:
            nearest_otm_call = otm_calls.loc[otm_calls['strike'].idxmin()]
            nearest_otm_put = otm_puts.loc[otm_puts['strike'].idxmax()]
            
            iv_skew = nearest_otm_put['impliedVolatility'] - nearest_otm_call['impliedVolatility']
        else:
            iv_skew = 0
        
        # Calculate IV term structure if multiple expirations
        iv_term_structure = []
        if len(expirations) > 1:
            for exp in expirations[:5]:  # Use first 5 expirations
                try:
                    calls, puts = get_option_chain(ticker, exp)
                    
                    # Get ATM options
                    atm_calls = calls[(calls['strike'] > current_price * 0.95) & (calls['strike'] < current_price * 1.05)]
                    atm_puts = puts[(puts['strike'] > current_price * 0.95) & (puts['strike'] < current_price * 1.05)]
                    
                    if not atm_calls.empty and not atm_puts.empty:
                        avg_atm_iv = (atm_calls['impliedVolatility'].mean() + atm_puts['impliedVolatility'].mean()) / 2
                        days_to_exp = (datetime.strptime(exp, "%Y-%m-%d").date() - datetime.now().date()).days
                        iv_term_structure.append((exp, days_to_exp, avg_atm_iv))
                except Exception:
                    pass
        
        return {
            'avg_iv': avg_iv,
            'iv_skew': iv_skew,
            'iv_term_structure': iv_term_structure
        }
    
    except Exception as e:
        logger.error(f"Error calculating option statistics for {ticker}: {str(e)}")
        return {'avg_iv': 0.3, 'iv_skew': 0, 'iv_term_structure': []}

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