# ui/components/header.py
import streamlit as st
import os
import logging

logger = logging.getLogger(__name__)

def show_header():
    """Display the application header and stock info if available."""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("<h1 class='main-header'>Options Strategy Calculator</h1>", unsafe_allow_html=True)
        st.markdown("<p class='subtitle'>Analyze and visualize options strategies with real-time market data</p>", unsafe_allow_html=True)
    
    with col2:
        display_stock_info(st.session_state.get('stock_info'))

def display_stock_info(info):
    """Display stock information in the given container."""
    if not info:
        return
        
    sector = info.get('sector', 'N/A')
    market_cap = info.get('marketCap', 0)
    market_cap_str = f"${market_cap/1e9:.2f}B" if market_cap >= 1e9 else f"${market_cap/1e6:.2f}M"
    
    st.markdown(f"""
    <div class='stock-info-card'>
        <div class='stock-ticker'>{info.get('symbol', '')}</div>
        <div class='stock-name'>{info.get('shortName', '')}</div>
        <div class='stock-meta'>Sector: {sector} | Market Cap: {market_cap_str}</div>
    </div>
    """, unsafe_allow_html=True)

def load_custom_css():
    """Load custom CSS for styling."""
    try:
        with open('styles/main.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except Exception as e:
        logger.error(f"Failed to load CSS: {e}")
        # Fallback minimal styling
        st.markdown("""
        <style>
        .main-header {font-size: 2.5rem !important; font-weight: 600; color: #1E88E5;}
        .subtitle {font-size: 1.2rem; color: #616161;}
        .stock-info-card {background-color: #f8f9fa; border-radius: 10px; padding: 15px; margin-bottom: 20px; border-left: 5px solid #1E88E5;}
        .stock-ticker {font-size: 1.5rem; font-weight: 600; color: #1E88E5;}
        .stock-name {font-size: 1rem; font-weight: 400; color: #424242;}
        .stock-meta {font-size: 0.8rem; color: #616161; margin-top: 5px;}
        </style>
        """, unsafe_allow_html=True)

def display_welcome():
    """Display welcome message and examples."""
    st.markdown("""
    ### Welcome to the Options Strategy Calculator!
    
    This tool helps you analyze and visualize options trading strategies using real-time market data.
    
    To get started:
    1. Enter a stock ticker in the sidebar
    2. Select a strategy category and type
    3. Configure your strategy parameters
    4. Analyze the payoff diagram and risk metrics
    
    The calculator provides comprehensive analysis including:
    - Profit/Loss payoff diagrams
    - Breakeven analysis
    - Risk assessment and probability metrics
    - Time decay visualization
    
    **Note:** This tool is for educational purposes only and does not constitute investment advice.
    """)
    
    # Show examples
    with st.expander("Example Strategies"):
        st.markdown("""
        #### Long Call Example
        A long call gives you the right to buy stock at the strike price before expiration.
        
        - **Use case:** Bullish outlook, limited risk
        - **Max loss:** Limited to premium paid
        - **Max profit:** Unlimited as stock rises
        
        #### Iron Condor Example
        An iron condor combines a bull put spread and a bear call spread.
        
        - **Use case:** Neutral outlook, defined risk/reward
        - **Max profit:** Net credit received
        - **Max loss:** Difference between strikes minus net credit
        """)