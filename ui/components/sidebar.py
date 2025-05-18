# ui/components/sidebar.py
import streamlit as st
import os
import time
import logging
from datetime import datetime
from data.fetcher import get_stock_price, get_stock_info, get_expiration_dates
from utils.error_handlers import handle_ui_error, safe_execute
from utils.formatters import format_price, format_percent

logger = logging.getLogger(__name__)

def setup_sidebar():
    """Set up the sidebar with logo and title."""
    with st.sidebar:
        # Add logo and app title
        if os.path.exists("assets/logo.png"):
            st.image("assets/logo.png", width=100)
        st.title("Options Strategy Calculator")
        
        # Theme selector
        theme = st.radio("Theme", ["Light", "Dark"], 
                        index=0 if st.session_state.get('theme', "light") == "light" else 1,
                        horizontal=True)
        st.session_state['theme'] = theme.lower()
        
        st.divider()

@handle_ui_error
def handle_ticker_selection():
    """Handle ticker selection and data loading."""
    with st.sidebar:
        st.header("Stock Selection")
        
        # Ticker input with validation
        ticker = st.text_input("Stock Ticker", value="AAPL").upper().strip()
        
        # Show recently viewed tickers
        ticker = display_recent_tickers(ticker)
        
        # Load stock data when ticker is provided
        if ticker:
            return load_ticker_data(ticker)
    
    return None, None, []

def display_recent_tickers(current_ticker):
    """Display recently viewed tickers with buttons."""
    if 'recent_tickers' in st.session_state:
        recent = st.session_state['recent_tickers']
        if recent:
            st.caption("Recently viewed:")
            cols = st.columns(len(recent))
            for i, recent_ticker in enumerate(recent):
                if cols[i].button(recent_ticker, key=f"recent_{i}"):
                    return recent_ticker
    
    return current_ticker

@handle_ui_error
def load_ticker_data(ticker):
    """Load data for the selected ticker with robust error handling."""
    with st.sidebar:
        try:
            with st.spinner(f"Loading data for {ticker}..."):
                start_time = time.time()
                
                # Get stock info and price
                stock_info = safe_execute(
                    lambda: get_stock_info(ticker),
                    default_value={},
                    error_message=f"Could not fetch information for {ticker}"
                )
                
                current_price = safe_execute(
                    lambda: get_stock_price(ticker),
                    default_value=None,
                    error_message=f"Could not fetch price for {ticker}"
                )
                
                if current_price is None:
                    return None, None, []
                
                # Update session state
                st.session_state['current_price'] = current_price
                st.session_state['stock_info'] = stock_info
                
                # Store in recent tickers
                update_recent_tickers(ticker)
                
                # Display stock info
                display_stock_price(stock_info, current_price)
                
                # Get available expiration dates
                expirations = safe_execute(
                    lambda: get_expiration_dates(ticker),
                    default_value=[],
                    error_message=f"Could not fetch option expiration dates for {ticker}"
                )
                
                if not expirations:
                    st.error(f"No options data available for {ticker}")
                    return ticker, current_price, []
                
                st.success(f"Found {len(expirations)} expiration dates")
                logger.info(f"Data loading for {ticker} completed in {time.time() - start_time:.2f} seconds")
                return ticker, current_price, expirations
                
        except Exception as e:
            st.error(f"Error loading data for {ticker}: {str(e)}")
            logger.error(f"Error loading data for {ticker}: {str(e)}")
            return None, None, []
    
    return None, None, []

def update_recent_tickers(ticker):
    """Update the list of recently viewed tickers."""
    if 'recent_tickers' not in st.session_state:
        st.session_state['recent_tickers'] = []
    
    # Add to recent tickers (avoid duplicates and limit to 5)
    recent = st.session_state['recent_tickers']
    if ticker not in recent:
        recent.insert(0, ticker)
        if len(recent) > 5:
            recent.pop()

def display_stock_price(stock_info, current_price):
    """Display the current stock price and change."""
    if not stock_info or not current_price:
        return
        
    price_change = stock_info.get('regularMarketChangePercent', 0)
    price_change_color = "green" if price_change >= 0 else "red"
    
    st.markdown(f"""
    <div class='price-card'>
        <div class='current-price'>${current_price:.2f}</div>
        <div class='price-change' style='color:{price_change_color}'>
            {price_change:+.2f}%
        </div>
    </div>
    """, unsafe_allow_html=True)