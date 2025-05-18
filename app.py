# --- app.py ---
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
from scipy.stats import norm
import time
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import custom modules
from data_fetch import get_stock_price, get_option_chain, get_expiration_dates, get_stock_info
from strategies.strategies_factory import create_strategy
from pricing import calculate_implied_volatility, calculate_greeks
from utils import calculate_strategy_payoff, calculate_strategy_current_value, create_payoff_chart, create_heatmap, create_risk_table, format_price, create_unrealized_pl_table

# Page configuration with improved styling
st.set_page_config(
    page_title="Options Strategy Calculator",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS for enhanced styling
with open('styles/main.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize session state for storing data between reruns
if 'strategy_legs' not in st.session_state:
    st.session_state['strategy_legs'] = None
if 'current_price' not in st.session_state:
    st.session_state['current_price'] = None
if 'stock_info' not in st.session_state:
    st.session_state['stock_info'] = None
if 'theme' not in st.session_state:
    st.session_state['theme'] = "light"  # Default theme

# Theme toggle in the sidebar
with st.sidebar:
    # Add logo and app title with better styling
   if os.path.exists("assets/logo.png"):
    st.image("assets/logo.png", width=100)
    st.title("Options Strategy Calculator")
    
    # Theme selector
    theme = st.radio("Theme", ["Light", "Dark"], 
                    index=0 if st.session_state['theme'] == "light" else 1,
                    horizontal=True)
    st.session_state['theme'] = theme.lower()
    
    st.divider()

# Function to show app header
def show_header():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("<h1 class='main-header'>Options Strategy Calculator</h1>", unsafe_allow_html=True)
        st.markdown("<p class='subtitle'>Analyze and visualize options strategies with real-time market data</p>", unsafe_allow_html=True)
    with col2:
        if st.session_state.get('stock_info'):
            info = st.session_state['stock_info']
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

# Function to handle ticker selection
def handle_ticker_selection():
    with st.sidebar:
        st.header("Stock Selection")
        
        # Ticker input with validation
        ticker = st.text_input("Stock Ticker", value="AAPL").upper().strip()
        
        # Show recently viewed tickers if available
        if 'recent_tickers' in st.session_state:
            recent = st.session_state['recent_tickers']
            if recent:
                st.caption("Recently viewed:")
                cols = st.columns(len(recent))
                for i, recent_ticker in enumerate(recent):
                    if cols[i].button(recent_ticker, key=f"recent_{i}"):
                        ticker = recent_ticker
                        st.experimental_rerun()
        
        # Load stock data when ticker is provided
        if ticker:
            try:
                with st.spinner(f"Loading data for {ticker}..."):
                    start_time = time.time()
                    
                    # Get stock info and price
                    stock_info = get_stock_info(ticker)
                    current_price = get_stock_price(ticker)
                    
                    # Update session state
                    st.session_state['current_price'] = current_price
                    st.session_state['stock_info'] = stock_info
                    
                    # Store in recent tickers
                    if 'recent_tickers' not in st.session_state:
                        st.session_state['recent_tickers'] = []
                    
                    # Add to recent tickers (avoid duplicates and limit to 5)
                    recent = st.session_state['recent_tickers']
                    if ticker not in recent:
                        recent.insert(0, ticker)
                        if len(recent) > 5:
                            recent.pop()
                    
                    # Display stock info
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
                    
                    # Get available expiration dates with loading indicator
                    expirations = get_expiration_dates(ticker)
                    
                    if not expirations:
                        st.error(f"No options data available for {ticker}")
                    else:
                        st.success(f"Found {len(expirations)} expiration dates")
                        
                        # Log performance
                        logger.info(f"Data loading for {ticker} completed in {time.time() - start_time:.2f} seconds")
                        
                        return ticker, current_price, expirations
            except Exception as e:
                st.error(f"Error: {str(e)}")
                logger.error(f"Error loading data for {ticker}: {str(e)}")
                
    return None, None, []

# Function to configure strategy
def configure_strategy(ticker, current_price, expirations):
    with st.sidebar:
        st.header("Strategy Selection")
        
        # Strategy category selection
        strategy_category = st.selectbox("Category", [
            "Basic Strategies",
            "Spread Strategies", 
            "Advanced Strategies",
            "Custom Strategies"
        ])
        
        # Strategy type based on category
        if strategy_category == "Basic Strategies":
            strategy_type = st.selectbox("Strategy", [
                "Long Call",
                "Long Put",
                "Covered Call",
                "Cash Secured Put",
                "Naked Call",
                "Naked Put"
            ])
        elif strategy_category == "Spread Strategies":
            strategy_type = st.selectbox("Strategy", [
                "Bull Call Spread",
                "Bear Put Spread",
                "Bull Put Credit Spread",
                "Bear Call Credit Spread",
                "Calendar Spread",
                "Poor Man's Covered Call",
                "Ratio Back Spread"
            ])
        elif strategy_category == "Advanced Strategies":
            strategy_type = st.selectbox("Strategy", [
                "Iron Condor",
                "Butterfly",
                "Straddle", 
                "Strangle",
                "Collar",
                "Diagonal Spread"
            ])
        else:  # Custom Strategies
            strategy_type = st.selectbox("Strategy", [
                "Custom - 2 Legs",
                "Custom - 3 Legs",
                "Custom - 4 Legs"
            ])
        
        # Strategy information
        with st.expander("Strategy Information"):
            show_strategy_info(strategy_category, strategy_type)
        
        # Common configuration - expiration selection
        st.header("Strategy Configuration")
        selected_expiry = st.selectbox("Expiration Date", expirations)
        
        # Calculate days to expiration
        expiry_date = datetime.strptime(selected_expiry, "%Y-%m-%d").date()
        today = datetime.now().date()
        days_to_expiry = (expiry_date - today).days
        
        # Display time to expiration with progress bar
        if days_to_expiry <= 0:
            st.warning("Options expire today!")
        else:
            time_left_pct = min(1.0, days_to_expiry / 365)  # Cap at 1 year for visual
            st.progress(time_left_pct)
            if days_to_expiry < 7:
                st.warning(f"{days_to_expiry} days to expiration (short-term)")
            elif days_to_expiry < 30:
                st.info(f"{days_to_expiry} days to expiration")
            elif days_to_expiry < 90:
                st.success(f"{days_to_expiry} days to expiration (medium-term)")
            else:
                st.success(f"{days_to_expiry} days to expiration (long-term)")
        
        # Load option chain with better error handling
        try:
            with st.spinner("Loading option chain..."):
                calls, puts = get_option_chain(ticker, selected_expiry)
                
                # Convert to DataFrame for easier handling
                calls_df = pd.DataFrame(calls)
                puts_df = pd.DataFrame(puts)
                
                # Enhance option chain with IV calculations if missing
                if 'impliedVolatility' not in calls_df.columns:
                    calls_df['impliedVolatility'] = calls_df.apply(
                        lambda row: calculate_implied_volatility(
                            'call', current_price, row['strike'], days_to_expiry/365, 
                            0.03, row['lastPrice']
                        ), axis=1
                    )
                
                if 'impliedVolatility' not in puts_df.columns:
                    puts_df['impliedVolatility'] = puts_df.apply(
                        lambda row: calculate_implied_volatility(
                            'put', current_price, row['strike'], days_to_expiry/365, 
                            0.03, row['lastPrice']
                        ), axis=1
                    )
                
                # Show option chains in expandable section
                with st.expander("View Option Chain Data"):
                    tab1, tab2 = st.tabs(["Calls", "Puts"])
                    
                    with tab1:
                        display_df = calls_df[['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility']]
                        display_df.columns = ['Strike', 'Last', 'Bid', 'Ask', 'Volume', 'OI', 'IV']
                        display_df['IV'] = display_df['IV'].apply(lambda x: f"{x*100:.1f}%")
                        st.dataframe(display_df, use_container_width=True)
                    
                    with tab2:
                        display_df = puts_df[['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility']]
                        display_df.columns = ['Strike', 'Last', 'Bid', 'Ask', 'Volume', 'OI', 'IV']
                        display_df['IV'] = display_df['IV'].apply(lambda x: f"{x*100:.1f}%")
                        st.dataframe(display_df, use_container_width=True)
                
                # Strategy-specific configuration based on type
                strategy_legs = configure_specific_strategy(
                    strategy_category, strategy_type, ticker, current_price, 
                    selected_expiry, days_to_expiry, calls_df, puts_df
                )
                
                return strategy_legs, selected_expiry, days_to_expiry
                
        except Exception as e:
            st.error(f"Error loading option chain: {str(e)}")
            logger.error(f"Error loading option chain: {str(e)}")
            return None, None, None
    
    return None, None, None

# Function to show strategy information
def show_strategy_info(category, strategy_type):
    if category == "Basic Strategies":
        if strategy_type == "Long Call":
            st.markdown("""
            **Long Call**: Buy a call option to profit from a rise in the stock price.
            
            - **Max Loss**: Limited to premium paid
            - **Max Gain**: Unlimited (stock price - strike - premium)
            - **Breakeven**: Strike price + premium
            - **When to Use**: Bullish outlook, want leverage
            """)
        elif strategy_type == "Long Put":
            st.markdown("""
            **Long Put**: Buy a put option to profit from a fall in the stock price.
            
            - **Max Loss**: Limited to premium paid
            - **Max Gain**: Limited to (strike - premium) if stock goes to zero
            - **Breakeven**: Strike price - premium
            - **When to Use**: Bearish outlook, hedge long stock positions
            """)
        elif strategy_type == "Covered Call":
            st.markdown("""
            **Covered Call**: Own stock and sell a call against it.
            
            - **Max Loss**: Stock price can fall to zero, offset by premium
            - **Max Gain**: Limited to (strike - stock purchase price + premium)
            - **Breakeven**: Stock purchase price - premium
            - **When to Use**: Slightly bullish or neutral, generate income
            """)
        # Add other strategy descriptions...
    
    # Add descriptions for spread strategies and advanced strategies...

# Function to configure specific strategy
def configure_specific_strategy(category, strategy_type, ticker, current_price, 
                               expiry, days_to_expiry, calls_df, puts_df):
    """Configure parameters for a specific strategy type and create strategy legs."""
    
    # Implementation for specific strategy types
    if category == "Basic Strategies":
        if strategy_type == "Long Call":
            # Find strikes near current price
            available_strikes = sorted(calls_df['strike'].unique().tolist())
            atm_index = min(range(len(available_strikes)), 
                           key=lambda i: abs(available_strikes[i] - current_price))
            
            # Strike selection with improved UI
            selected_strike_index = st.select_slider(
                "Strike Selection",
                options=range(len(available_strikes)),
                value=atm_index,
                format_func=lambda i: f"${available_strikes[i]:.2f} ({'ITM' if available_strikes[i] < current_price else 'OTM' if available_strikes[i] > current_price else 'ATM'})"
            )
            selected_strike = available_strikes[selected_strike_index]
            
            # Get option data
            option_data = calls_df[calls_df['strike'] == selected_strike].iloc[0]
            market_premium = option_data['lastPrice']
            
            # Allow user to specify a different entry price
            use_custom_price = st.checkbox("I purchased this option at a different price")
            if use_custom_price:
                entry_premium = st.number_input(
                    "Your purchase price", 
                    min_value=0.01, 
                    max_value=None, 
                    value=market_premium,
                    step=0.01,
                    format="%.2f"
                )
                
                # Calculate unrealized P/L based on entry vs current
                unrealized_pl = (market_premium - entry_premium) * 100  # Per contract
                st.metric(
                    "Unrealized P/L", 
                    f"${unrealized_pl:.2f}", 
                    delta=f"{(unrealized_pl/(entry_premium*100))*100:.1f}%" if entry_premium > 0 else None
                )
            else:
                entry_premium = market_premium
            
            # Display option details with improved UI
            cols = st.columns(3)
            with cols[0]:
                st.metric("Current Market Premium", f"${market_premium:.2f}", delta=None)
            with cols[1]:
                contract_value = entry_premium * 100
                st.metric("Contract Value", f"${contract_value:.2f}", delta=None)
            with cols[2]:
                breakeven = selected_strike + entry_premium
                st.metric("Breakeven", f"${breakeven:.2f}", delta=f"{((breakeven/current_price)-1)*100:.1f}%")
            
            # Option to adjust quantity
            quantity = st.number_input("Quantity (# of contracts)", min_value=1, value=1)
            
            # Calculate IV and show Greeks
            iv = option_data.get('impliedVolatility', 0.3)
            with st.expander("View Option Greeks"):
                years_to_expiry = days_to_expiry / 365
                greeks = calculate_greeks('call', current_price, selected_strike, years_to_expiry, 0.03, iv)
                
                greek_cols = st.columns(5)
                greek_cols[0].metric("Delta", f"{greeks['delta']:.3f}")
                greek_cols[1].metric("Gamma", f"{greeks['gamma']:.4f}")
                greek_cols[2].metric("Theta", f"{greeks['theta']:.3f}")
                greek_cols[3].metric("Vega", f"{greeks['vega']:.3f}")
                greek_cols[4].metric("IV", f"{iv*100:.1f}%")
            
            # Create strategy using factory method
            return create_strategy(
                "long_call",
                strike=selected_strike,
                expiration=expiry,
                current_premium=market_premium,
                entry_premium=entry_premium,
                quantity=quantity,
                iv=iv
            )
            
        elif strategy_type == "Long Put":
            # Similar implementation for Long Put with improved UI
            available_strikes = sorted(puts_df['strike'].unique().tolist())
            atm_index = min(range(len(available_strikes)), 
                           key=lambda i: abs(available_strikes[i] - current_price))
            
            selected_strike_index = st.select_slider(
                "Strike Selection",
                options=range(len(available_strikes)),
                value=atm_index,
                format_func=lambda i: f"${available_strikes[i]:.2f} ({'ITM' if available_strikes[i] > current_price else 'OTM' if available_strikes[i] < current_price else 'ATM'})"
            )
            selected_strike = available_strikes[selected_strike_index]
            
            option_data = puts_df[puts_df['strike'] == selected_strike].iloc[0]
            market_premium = option_data['lastPrice']
            
            # Allow user to specify a different entry price
            use_custom_price = st.checkbox("I purchased this option at a different price")
            if use_custom_price:
                entry_premium = st.number_input(
                    "Your purchase price", 
                    min_value=0.01, 
                    max_value=None, 
                    value=market_premium,
                    step=0.01,
                    format="%.2f"
                )
                
                # Calculate unrealized P/L based on entry vs current
                unrealized_pl = (market_premium - entry_premium) * 100  # Per contract
                st.metric(
                    "Unrealized P/L", 
                    f"${unrealized_pl:.2f}", 
                    delta=f"{(unrealized_pl/(entry_premium*100))*100:.1f}%" if entry_premium > 0 else None
                )
            else:
                entry_premium = market_premium
            
            cols = st.columns(3)
            with cols[0]:
                st.metric("Current Market Premium", f"${market_premium:.2f}", delta=None)
            with cols[1]:
                contract_value = entry_premium * 100
                st.metric("Contract Value", f"${contract_value:.2f}", delta=None)
            with cols[2]:
                breakeven = selected_strike - entry_premium
                st.metric("Breakeven", f"${breakeven:.2f}", delta=f"{((breakeven/current_price)-1)*100:.1f}%")
            
            quantity = st.number_input("Quantity (# of contracts)", min_value=1, value=1)
            
            iv = option_data.get('impliedVolatility', 0.3)
            with st.expander("View Option Greeks"):
                years_to_expiry = days_to_expiry / 365
                greeks = calculate_greeks('put', current_price, selected_strike, years_to_expiry, 0.03, iv)
                
                greek_cols = st.columns(5)
                greek_cols[0].metric("Delta", f"{greeks['delta']:.3f}")
                greek_cols[1].metric("Gamma", f"{greeks['gamma']:.4f}")
                greek_cols[2].metric("Theta", f"{greeks['theta']:.3f}")
                greek_cols[3].metric("Vega", f"{greeks['vega']:.3f}")
                greek_cols[4].metric("IV", f"{iv*100:.1f}%")
            
            return create_strategy(
                "long_put",
                strike=selected_strike,
                expiration=expiry,
                current_premium=market_premium,
                entry_premium=entry_premium,
                quantity=quantity,
                iv=iv
            )
            
        elif strategy_type == "Covered Call":
            # Improved covered call implementation
            available_strikes = sorted(calls_df['strike'].unique().tolist())
            
            # Default to slightly OTM call
            default_index = min(range(len(available_strikes)), 
                               key=lambda i: abs(available_strikes[i] - current_price * 1.05))
            
            selected_strike_index = st.select_slider(
                "Call Strike Selection",
                options=range(len(available_strikes)),
                value=default_index,
                format_func=lambda i: f"${available_strikes[i]:.2f} ({'ITM' if available_strikes[i] < current_price else 'OTM' if available_strikes[i] > current_price else 'ATM'})"
            )
            selected_strike = available_strikes[selected_strike_index]
            
            option_data = calls_df[calls_df['strike'] == selected_strike].iloc[0]
            market_premium = option_data['lastPrice']
            
            # Allow user to specify a different entry price for the call
            use_custom_call_price = st.checkbox("I sold this call at a different price")
            if use_custom_call_price:
                entry_premium = st.number_input(
                    "Your sale price", 
                    min_value=0.01, 
                    max_value=None, 
                    value=market_premium,
                    step=0.01,
                    format="%.2f"
                )
                
                # Calculate unrealized P/L
                unrealized_pl = (entry_premium - market_premium) * 100  # Per contract
                st.metric(
                    "Unrealized Call P/L", 
                    f"${unrealized_pl:.2f}", 
                    delta=f"{(unrealized_pl/(entry_premium*100))*100:.1f}%" if entry_premium > 0 else None
                )
            else:
                entry_premium = market_premium
            
            # Stock cost basis adjustment
            st.subheader("Stock Component")
            use_custom_stock_price = st.checkbox("I purchased the stock at a different price than current")
            current_stock_price = current_price
            
            if use_custom_stock_price:
                stock_price = st.number_input(
                    "Stock Cost Basis", 
                    min_value=0.01,
                    max_value=None,
                    value=current_price,
                    step=0.01,
                    format="%.2f"
                )
                
                # Calculate unrealized stock P/L
                unrealized_stock_pl = (current_stock_price - stock_price) * 100  # 100 shares
                st.metric(
                    "Unrealized Stock P/L", 
                    f"${unrealized_stock_pl:.2f}", 
                    delta=f"{(unrealized_stock_pl/(stock_price*100))*100:.1f}%" if stock_price > 0 else None
                )
            else:
                stock_price = current_stock_price
            
            # Display strategy metrics with improved visuals
            metrics_cols = st.columns(3)
            with metrics_cols[0]:
                income = entry_premium * 100
                st.metric("Premium Income", f"${income:.2f}", delta=f"{income/(stock_price*100)*100:.2f}% yield")
            
            with metrics_cols[1]:
                max_profit = ((selected_strike - stock_price) + entry_premium) * 100
                st.metric("Max Profit", f"${max_profit:.2f}", delta=f"{max_profit/(stock_price*100)*100:.2f}% return")
            
            with metrics_cols[2]:
                breakeven = stock_price - entry_premium
                st.metric("Breakeven", f"${breakeven:.2f}", delta=f"{(breakeven-current_price):.2f} from current")
                
            quantity = st.number_input("Quantity (# of covered call units)", min_value=1, value=1)
            
            # Create strategy using factory method
            return create_strategy(
                "covered_call",
                current_stock_price=current_stock_price,
                stock_price=stock_price,
                call_strike=selected_strike,
                expiration=expiry,
                current_call_premium=market_premium,
                call_premium=entry_premium,
                quantity=quantity,
                iv=option_data.get('impliedVolatility', 0.3)
            )
        
        # Add other basic strategies...
    
    elif category == "Spread Strategies":
        if strategy_type == "Bull Call Spread":
            # Improved Bull Call Spread implementation
            available_strikes = sorted(calls_df['strike'].unique().tolist())
            atm_index = min(range(len(available_strikes)), 
                           key=lambda i: abs(available_strikes[i] - current_price))
            
            # Two-column layout for strike selection
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Long Call (Lower Strike)")
                # Long call (lower strike)
                long_strike_index = st.select_slider(
                    "Long Call Strike",
                    options=range(len(available_strikes)),
                    value=max(0, atm_index-1),
                    format_func=lambda i: f"${available_strikes[i]:.2f}"
                )
                long_strike = available_strikes[long_strike_index]
                long_option = calls_df[calls_df['strike'] == long_strike].iloc[0]
                long_market_premium = long_option['lastPrice']
                
                # Custom entry price for long leg
                use_custom_long_price = st.checkbox("I purchased this call at a different price")
                if use_custom_long_price:
                    long_entry_premium = st.number_input(
                        "Your purchase price (long call)", 
                        min_value=0.01, 
                        max_value=None, 
                        value=long_market_premium,
                        step=0.01,
                        format="%.2f",
                        key="long_entry"
                    )
                else:
                    long_entry_premium = long_market_premium
                
                st.metric("Current Market Premium", f"${long_market_premium:.2f}")
                st.caption(f"IV: {long_option.get('impliedVolatility', 0.3)*100:.1f}%")
            
            with col2:
                st.subheader("Short Call (Higher Strike)")
                # Filter available strikes to ensure short strike > long strike
                short_options = range(long_strike_index+1, len(available_strikes))
                if short_options:
                    short_strike_index = st.select_slider(
                        "Short Call Strike",
                        options=short_options,
                        value=min(long_strike_index+3, len(available_strikes)-1),
                        format_func=lambda i: f"${available_strikes[i]:.2f}"
                    )
                    short_strike = available_strikes[short_strike_index]
                    short_option = calls_df[calls_df['strike'] == short_strike].iloc[0]
                    short_market_premium = short_option['lastPrice']
                    
                    # Custom entry price for short leg
                    use_custom_short_price = st.checkbox("I sold this call at a different price")
                    if use_custom_short_price:
                        short_entry_premium = st.number_input(
                            "Your sale price (short call)", 
                            min_value=0.01, 
                            max_value=None, 
                            value=short_market_premium,
                            step=0.01,
                            format="%.2f",
                            key="short_entry"
                        )
                    else:
                        short_entry_premium = short_market_premium
                    
                    st.metric("Current Market Premium", f"${short_market_premium:.2f}")
                    st.caption(f"IV: {short_option.get('impliedVolatility', 0.3)*100:.1f}%")
                else:
                    st.error("No higher strikes available for the short call leg")
                    short_strike = None
                    short_market_premium = 0
                    short_entry_premium = 0
                    short_option = None
            
            if short_strike:
                # Calculate and display spread metrics
                entry_net_debit = long_entry_premium - short_entry_premium
                current_net_debit = long_market_premium - short_market_premium
                spread_width = short_strike - long_strike
                max_profit = (spread_width - entry_net_debit) * 100
                max_loss = entry_net_debit * 100
                
                # Calculate unrealized P/L
                unrealized_pl = (current_net_debit - entry_net_debit) * 100  # Per spread
                
                metrics_cols = st.columns(4)
                with metrics_cols[0]:
                    st.metric("Entry Net Debit", f"${entry_net_debit:.2f}")
                    st.caption(f"Current: ${current_net_debit:.2f}")
                
                with metrics_cols[1]:
                    st.metric("Spread Width", f"${spread_width:.2f}")
                
                with metrics_cols[2]:
                    st.metric("Max Profit", f"${max_profit:.2f}")
                
                with metrics_cols[3]:
                    if max_loss > 0:
                        risk_reward = max_profit / max_loss
                        st.metric("Risk/Reward", f"1:{risk_reward:.2f}")
                    else:
                        st.metric("Risk/Reward", "No Risk")
                
                # Display unrealized P/L
                st.metric(
                    "Unrealized P/L", 
                    f"${-unrealized_pl:.2f}",  # Negative because debit increased = loss
                    delta=f"{(-unrealized_pl/max_loss)*100:.1f}%" if max_loss > 0 else None
                )
                
                # Calculate breakeven
                breakeven = long_strike + entry_net_debit
                st.progress((breakeven - long_strike) / spread_width)
                st.caption(f"Breakeven: ${breakeven:.2f} ({((breakeven/current_price)-1)*100:.1f}% from current price)")
                
                quantity = st.number_input("Quantity (# of spreads)", min_value=1, value=1)
                
                return create_strategy(
                    "bull_call_spread",
                    long_strike=long_strike,
                    short_strike=short_strike,
                    expiration=expiry,
                    current_long_premium=long_market_premium,
                    current_short_premium=short_market_premium,
                    long_premium=long_entry_premium,
                    short_premium=short_entry_premium,
                    quantity=quantity,
                    long_iv=long_option.get('impliedVolatility', 0.3),
                    short_iv=short_option.get('impliedVolatility', 0.3)
                )
        
        elif strategy_type == "Iron Condor":
            # Implement Iron Condor with interactive strike selection
            st.subheader("Bull Put Spread (Lower Strikes)")
            
            # Bull Put Spread configuration (lower part)
            available_put_strikes = sorted(puts_df['strike'].unique().tolist())
            atm_index_put = min(range(len(available_put_strikes)), 
                               key=lambda i: abs(available_put_strikes[i] - current_price))
            
            # Interactive slider for put spread with visual indicator
            put_spread_range = st.slider(
                "Put Spread Strikes",
                min_value=0,
                max_value=len(available_put_strikes)-1,
                value=(max(0, atm_index_put-5), max(0, atm_index_put-2)),
                format_func=lambda i: f"${available_put_strikes[i]:.2f}"
            )
            
            long_put_index, short_put_index = put_spread_range
            long_put_strike = available_put_strikes[long_put_index]
            short_put_strike = available_put_strikes[short_put_index]
            
            # Get option data for puts
            long_put_data = puts_df[puts_df['strike'] == long_put_strike].iloc[0]
            short_put_data = puts_df[puts_df['strike'] == short_put_strike].iloc[0]
            long_put_market_premium = long_put_data['lastPrice']
            short_put_market_premium = short_put_data['lastPrice']
            
            # Allow custom entry prices for put legs
            put_col1, put_col2 = st.columns(2)
            
            with put_col1:
                st.subheader("Long Put Settings")
                use_custom_long_put = st.checkbox("Custom long put entry")
                if use_custom_long_put:
                    long_put_entry_premium = st.number_input(
                        "Your purchase price", 
                        min_value=0.01, 
                        max_value=None, 
                        value=long_put_market_premium,
                        step=0.01,
                        format="%.2f",
                        key="long_put_entry"
                    )
                else:
                    long_put_entry_premium = long_put_market_premium
                
                st.metric("Market Premium", f"${long_put_market_premium:.2f}")
            
            with put_col2:
                st.subheader("Short Put Settings")
                use_custom_short_put = st.checkbox("Custom short put entry")
                if use_custom_short_put:
                    short_put_entry_premium = st.number_input(
                        "Your sale price", 
                        min_value=0.01, 
                        max_value=None, 
                        value=short_put_market_premium,
                        step=0.01,
                        format="%.2f",
                        key="short_put_entry"
                    )
                else:
                    short_put_entry_premium = short_put_market_premium
                
                st.metric("Market Premium", f"${short_put_market_premium:.2f}")
            
            # Bear Call Spread configuration (upper part)
            st.subheader("Bear Call Spread (Higher Strikes)")
            
            available_call_strikes = sorted(calls_df['strike'].unique().tolist())
            atm_index_call = min(range(len(available_call_strikes)), 
                                key=lambda i: abs(available_call_strikes[i] - current_price))
            
            # Interactive slider for call spread with visual indicator
            call_spread_range = st.slider(
                "Call Spread Strikes",
                min_value=0,
                max_value=len(available_call_strikes)-1,
                value=(min(len(available_call_strikes)-1, atm_index_call+2), 
                       min(len(available_call_strikes)-1, atm_index_call+5)),
                format_func=lambda i: f"${available_call_strikes[i]:.2f}"
            )
            
            short_call_index, long_call_index = call_spread_range
            short_call_strike = available_call_strikes[short_call_index]
            long_call_strike = available_call_strikes[long_call_index]
            
            # Get option data for calls
            short_call_data = calls_df[calls_df['strike'] == short_call_strike].iloc[0]
            long_call_data = calls_df[calls_df['strike'] == long_call_strike].iloc[0]
            short_call_market_premium = short_call_data['lastPrice']
            long_call_market_premium = long_call_data['lastPrice']
            
            # Allow custom entry prices for call legs
            call_col1, call_col2 = st.columns(2)
            
            with call_col1:
                st.subheader("Short Call Settings")
                use_custom_short_call = st.checkbox("Custom short call entry")
                if use_custom_short_call:
                    short_call_entry_premium = st.number_input(
                        "Your sale price", 
                        min_value=0.01, 
                        max_value=None, 
                        value=short_call_market_premium,
                        step=0.01,
                        format="%.2f",
                        key="short_call_entry"
                    )
                else:
                    short_call_entry_premium = short_call_market_premium
                
                st.metric("Market Premium", f"${short_call_market_premium:.2f}")
            
            with call_col2:
                st.subheader("Long Call Settings")
                use_custom_long_call = st.checkbox("Custom long call entry")
                if use_custom_long_call:
                    long_call_entry_premium = st.number_input(
                        "Your purchase price", 
                        min_value=0.01, 
                        max_value=None, 
                        value=long_call_market_premium,
                        step=0.01,
                        format="%.2f",
                        key="long_call_entry"
                    )
                else:
                    long_call_entry_premium = long_call_market_premium
                
                st.metric("Market Premium", f"${long_call_market_premium:.2f}")
            
            # Calculate net credit and strategy metrics for entry prices
            entry_net_credit = (short_put_entry_premium - long_put_entry_premium) + (short_call_entry_premium - long_call_entry_premium)
            current_net_credit = (short_put_market_premium - long_put_market_premium) + (short_call_market_premium - long_call_market_premium)
            
            put_width = short_put_strike - long_put_strike
            call_width = long_call_strike - short_call_strike
            
            max_profit = entry_net_credit * 100
            max_loss = min(put_width, call_width) * 100 - max_profit
            
            # Calculate unrealized P/L
            unrealized_pl = (entry_net_credit - current_net_credit) * 100
            
            # Display strategy metrics with improved visuals
            metrics_cols = st.columns(4)
            with metrics_cols[0]:
                st.metric("Entry Net Credit", f"${entry_net_credit:.2f}")
                st.caption(f"Current: ${current_net_credit:.2f}")
            
            with metrics_cols[1]:
                st.metric("Max Profit", f"${max_profit:.2f}")
            
            with metrics_cols[2]:
                st.metric("Max Loss", f"${max_loss:.2f}")
            
            with metrics_cols[3]:
                if max_loss > 0:
                    risk_reward = max_profit / max_loss
                    st.metric("Risk/Reward", f"{risk_reward:.2f}:1")
                else:
                    st.metric("Risk/Reward", "∞")
            
            # Display unrealized P/L
            st.metric(
                "Unrealized P/L", 
                f"${unrealized_pl:.2f}", 
                delta=f"{(unrealized_pl/max_profit)*100:.1f}%" if max_profit > 0 else None
            )
            
            # Show profit range visually
            profit_range = f"${short_put_strike:.2f} to ${short_call_strike:.2f}"
            st.info(f"Profit Range: {profit_range}")
            
            quantity = st.number_input("Quantity (# of iron condors)", min_value=1, value=1)
            
            # Create strategy using factory method
            return create_strategy(
                "iron_condor",
                long_put_strike=long_put_strike,
                short_put_strike=short_put_strike,
                short_call_strike=short_call_strike,
                long_call_strike=long_call_strike,
                expiration=expiry,
                current_long_put_premium=long_put_market_premium,
                current_short_put_premium=short_put_market_premium,
                current_short_call_premium=short_call_market_premium,
                current_long_call_premium=long_call_market_premium,
                long_put_premium=long_put_entry_premium,
                short_put_premium=short_put_entry_premium,
                short_call_premium=short_call_entry_premium,
                long_call_premium=long_call_entry_premium,
                quantity=quantity,
                long_put_iv=long_put_data.get('impliedVolatility', 0.3),
                short_put_iv=short_put_data.get('impliedVolatility', 0.3),
                short_call_iv=short_call_data.get('impliedVolatility', 0.3),
                long_call_iv=long_call_data.get('impliedVolatility', 0.3)
            )
        
        # Add other spread strategies...
    
    # Add implementations for advanced strategies...
    
    elif category == "Custom Strategies":
        # Enhanced custom strategy builder
        st.subheader("Custom Strategy Builder")
        
        num_legs = int(strategy_type.split(" - ")[1][0])  # Extract number of legs
        
        strategy_legs = []
        total_cost = 0
        
        for i in range(num_legs):
            st.write(f"### Leg {i+1}")
            leg_expander = st.expander(f"Configure Leg {i+1}", expanded=True)
            
            with leg_expander:
                col1, col2 = st.columns(2)
                
                with col1:
                    leg_type = st.selectbox(
                        "Type", 
                        ["Call", "Put", "Stock"], 
                        key=f"type_{i}"
                    )
                    position = st.selectbox(
                        "Position", 
                        ["Long", "Short"], 
                        key=f"pos_{i}"
                    )
                
                with col2:
                    quantity = st.number_input(
                        "Quantity", 
                        min_value=1, 
                        value=1, 
                        key=f"qty_{i}"
                    )
                    
                    if leg_type != "Stock":
                        # Get appropriate chain
                        option_chain = calls_df if leg_type == "Call" else puts_df
                        available_strikes = sorted(option_chain['strike'].unique().tolist())
                        
                        # Find ATM index
                        atm_index = min(range(len(available_strikes)), 
                                       key=lambda i: abs(available_strikes[i] - current_price))
                        
                        strike_index = st.select_slider(
                            "Strike Price",
                            options=range(len(available_strikes)),
                            value=atm_index,
                            format_func=lambda i: f"${available_strikes[i]:.2f}",
                            key=f"strike_{i}"
                        )
                        strike = available_strikes[strike_index]
                        
                        # Get option data
                        option_data = option_chain[option_chain['strike'] == strike].iloc[0]
                        market_premium = option_data['lastPrice']
                        iv = option_data.get('impliedVolatility', 0.3)
                        
                        # Allow custom entry price
                        use_custom_price = st.checkbox(f"Custom entry price for leg {i+1}")
                        if use_custom_price:
                            entry_premium = st.number_input(
                                "Your entry price", 
                                min_value=0.01, 
                                max_value=None, 
                                value=market_premium,
                                step=0.01,
                                format="%.2f",
                                key=f"entry_{i}"
                            )
                        else:
                            entry_premium = market_premium
                        
                        # Display option information
                        st.metric("Market Premium", f"${market_premium:.2f}")
                        st.caption(f"IV: {iv*100:.1f}%")
                        
                        leg = {
                            'type': leg_type.lower(),
                            'position': position.lower(),
                            'strike': strike,
                            'expiry': expiry,
                            'price': entry_premium,
                            'current_price': market_premium,
                            'quantity': quantity,
                            'iv': iv
                        }
                        
                        # Calculate cost effect
                        leg_effect = entry_premium * quantity * 100
                        if position == "Long":
                            total_cost += leg_effect
                        else:
                            total_cost -= leg_effect
                    else:  # Stock leg
                        current_stock_price = current_price
                        
                        # Allow custom entry price for stock
                        use_custom_stock = st.checkbox(f"Custom entry price for stock leg {i+1}")
                        if use_custom_stock:
                            stock_price = st.number_input(
                                "Your purchase/sale price", 
                                min_value=0.01,
                                max_value=None,
                                value=current_price,
                                step=0.01,
                                format="%.2f",
                                key=f"stock_price_{i}"
                            )
                        else:
                            stock_price = current_price
                        
                        leg = {
                            'type': 'stock',
                            'position': position.lower(),
                            'price': stock_price,
                            'current_price': current_stock_price,
                            'quantity': quantity * 100  # 100 shares per contract
                        }
                        
                        # Calculate stock cost
                        stock_cost = stock_price * quantity * 100
                        if position == "Long":
                            total_cost += stock_cost
                        else:
                            total_cost -= stock_cost
                    
                    strategy_legs.append(leg)
        
        # Show strategy summary
        st.subheader("Strategy Summary")
        
        # Determine if net debit or credit
        cost_type = "Debit" if total_cost > 0 else "Credit"
        
        # Display strategy cost with improved formatting
        st.metric("Net Strategy Cost", 
                 f"${abs(total_cost):.2f} {cost_type}", 
                 delta=f"{abs(total_cost)/current_price/100:.1f}% of stock price")
        
        return strategy_legs

# Function to analyze and visualize strategy
def analyze_strategy(strategy_legs, current_price, expiry_date, days_to_expiry):
    if not strategy_legs:
        st.info("Configure your options strategy to see analysis here")
        return
    
    # Create tabs for different analysis views with improved design
    tabs = st.tabs([
        "📈 Payoff Diagram", 
        "📊 Risk Analysis", 
        "⏱️ Time Decay", 
        "📱 Mobile View",
        "💼 Position Analysis"  # New tab
    ])
    
    with tabs[0]:  # Payoff Diagram
        try:
            # Generate price range for analysis with dynamic width
            volatility = calculate_strategy_volatility(strategy_legs)
            price_range_pct = min(max(0.25, volatility * 2), 0.5)  # Adjust based on volatility
            min_price = current_price * (1 - price_range_pct)
            max_price = current_price * (1 + price_range_pct)
            price_range = np.linspace(min_price, max_price, 100)
            
            # Add custom price range input
            with st.expander("Customize Price Range"):
                custom_range = st.slider(
                    "Price Range (%)", 
                    min_value=10, 
                    max_value=100, 
                    value=int(price_range_pct * 100),
                    step=5
                )
                if custom_range != int(price_range_pct * 100):
                    price_range_pct = custom_range / 100
                    min_price = current_price * (1 - price_range_pct)
                    max_price = current_price * (1 + price_range_pct)
                    price_range = np.linspace(min_price, max_price, 100)
            
            # Calculate P/L at expiration
            expiry_payoffs = calculate_strategy_payoff(strategy_legs, price_range, current_price)
            
            # Calculate P/L before expiration if applicable
            current_values = None
            if days_to_expiry > 0:
                # Get average implied volatility from strategy legs
                volatility = calculate_strategy_volatility(strategy_legs)
                
                # Calculate current values
                current_values = calculate_strategy_current_value(
                    strategy_legs, price_range, days_to_expiry, volatility=volatility
                )
            
            # Create dynamic plot with zooming capability
            fig = go.Figure()
            
            # Add P/L at expiration
            fig.add_trace(go.Scatter(
                x=price_range, 
                y=expiry_payoffs,
                mode='lines',
                name='P/L at Expiration',
                line=dict(color='blue', width=3)
            ))
            
            # Add current P/L if available
            if current_values is not None:
                fig.add_trace(go.Scatter(
                    x=price_range, 
                    y=current_values,
                    mode='lines',
                    name=f'Current Value (T-{days_to_expiry})',
                    line=dict(color='green', width=2, dash='dash')
                ))
            
            # Add zero line
            fig.add_shape(
                type="line",
                x0=min_price, x1=max_price,
                y0=0, y1=0,
                line=dict(color="black", width=1)
            )
            
            # Add current price line
            fig.add_shape(
                type="line",
                x0=current_price, x1=current_price,
                y0=min(min(expiry_payoffs), 0) * 1.1 if min(expiry_payoffs) < 0 else -10, 
                y1=max(max(expiry_payoffs), 0) * 1.1,
                line=dict(color="red", width=2, dash="dash")
            )
            
            # Find breakeven points
            breakeven_points = find_breakeven_points(price_range, expiry_payoffs)
            
            # Add breakeven annotations
            for i, be in enumerate(breakeven_points):
                fig.add_shape(
                    type="line",
                    x0=be, x1=be,
                    y0=min(min(expiry_payoffs), 0) * 1.1 if min(expiry_payoffs) < 0 else -10, 
                    y1=max(max(expiry_payoffs), 0) * 1.1,
                    line=dict(color="green", width=1, dash="dash")
                )
                
                fig.add_annotation(
                    x=be,
                    y=0,
                    text=f"BE: ${be:.2f}",
                    showarrow=True,
                    arrowhead=1
                )
            
            # Calculate key metrics
            max_profit = max(expiry_payoffs)
            max_loss = min(expiry_payoffs)
            profit_at_current = calculate_strategy_payoff(strategy_legs, [current_price], current_price)[0]
            
            # Add metrics annotation
            fig.add_annotation(
                x=min_price + (max_price - min_price) * 0.05,
                y=max(max(expiry_payoffs), 0) * 0.9,
                text=f"<b>Max Profit:</b> ${max_profit:.2f}<br><b>Max Loss:</b> ${max_loss:.2f}<br><b>Current P/L:</b> ${profit_at_current:.2f}",
                showarrow=False,
                align="left",
                bordercolor="black",
                borderwidth=1,
                bgcolor="white",
                opacity=0.8
            )
            
            # Update layout with enhanced styling
            fig.update_layout(
                title="Profit/Loss Analysis",
                xaxis_title="Stock Price",
                yaxis_title="Profit/Loss ($)",
                hovermode="x unified",
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01
                ),
                margin=dict(l=20, r=20, t=50, b=20),
                height=500
            )
            
            # Add range slider for interactive exploration
            fig.update_xaxes(
                rangeslider_visible=True,
                rangeslider_thickness=0.05
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Add key metrics summary with improved visualization
            st.subheader("Key Metrics")
            
            metric_cols = st.columns(4)
            with metric_cols[0]:
                st.metric(
                    "Max Profit", 
                    f"${max_profit:.2f}", 
                    delta=None,
                    help="Maximum possible profit at expiration"
                )
            
            with metric_cols[1]:
                st.metric(
                    "Max Loss", 
                    f"${abs(max_loss):.2f}", 
                    delta=None,
                    help="Maximum possible loss at expiration"
                )
            
            with metric_cols[2]:
                if abs(max_loss) > 0:
                    risk_reward = max_profit / abs(max_loss)
                    st.metric(
                        "Risk/Reward", 
                        f"1:{risk_reward:.2f}", 
                        delta=None,
                        help="Ratio of potential reward to risk"
                    )
                else:
                    st.metric("Risk/Reward", "∞", delta=None)
            
            with metric_cols[3]:
                breakeven_str = ", ".join([f"${be:.2f}" for be in breakeven_points]) if breakeven_points else "N/A"
                st.metric(
                    "Breakeven", 
                    breakeven_str, 
                    delta=None,
                    help="Price points where P/L equals zero"
                )
            
        except Exception as e:
            st.error(f"Error creating payoff chart: {str(e)}")
            logger.error(f"Error creating payoff chart: {str(e)}", exc_info=True)
    
    with tabs[1]:  # Risk Analysis
        try:
            # Enhanced risk analysis with probability metrics
            st.subheader("Probability Analysis")
            
            # Get volatility
            volatility = calculate_strategy_volatility(strategy_legs)
            
            # Create price points at different percentage changes
            change_pcts = [-0.3, -0.2, -0.1, -0.05, 0, 0.05, 0.1, 0.2, 0.3]
            prices = [current_price * (1 + pct) for pct in change_pcts]
            
            # Calculate payoffs at expiration
            expiry_payoffs = calculate_strategy_payoff(strategy_legs, prices, current_price)
            
            # Create DataFrame with expiry values
            df = pd.DataFrame()
            df["Price Change"] = [f"{pct:+.0%}" for pct in change_pcts]
            df["Price"] = [f"${p:.2f}" for p in prices]
            df["P/L at Expiration"] = [f"${p:.2f}" for p in expiry_payoffs]
            
            # Calculate current value if days_to_expiry > 0
            if days_to_expiry > 0:
                current_values = calculate_strategy_current_value(
                    strategy_legs, prices, days_to_expiry, volatility=volatility
                )
                df[f"Current Value (T-{days_to_expiry})"] = [f"${p:.2f}" for p in current_values]
            
            # Calculate probability of reaching each price
            if days_to_expiry > 0:
                years = days_to_expiry / 365
                probabilities = []
                
                for price in prices:
                    # Calculate probability using log-normal distribution
                    z_score = abs(np.log(price / current_price) / (volatility * np.sqrt(years)))
                    prob = (1 - norm.cdf(z_score)) * 2  # Two-sided probability
                    probabilities.append(f"{prob*100:.1f}%")
                
                df["Probability"] = probabilities
            
            # Display enhanced table with conditional formatting
            st.dataframe(df, use_container_width=True)
            
            # Calculate probability of profit
            if days_to_expiry > 0 and breakeven_points:
                # Sort breakeven points
                breakeven_points.sort()
                
                # Calculate probability for each range
                prob_sections = []
                years = days_to_expiry / 365
                
                # Add ranges based on breakeven points
                if len(breakeven_points) == 1:
                    # Single breakeven case
                    be = breakeven_points[0]
                    if expiry_payoffs[4] > 0:  # Profit below breakeven
                        z_score = np.log(be / current_price) / (volatility * np.sqrt(years))
                        prob = norm.cdf(z_score)
                        prob_sections.append((f"Below ${be:.2f}", f"{prob*100:.1f}%"))
                    else:  # Profit above breakeven
                        z_score = np.log(be / current_price) / (volatility * np.sqrt(years))
                        prob = 1 - norm.cdf(z_score)
                        prob_sections.append((f"Above ${be:.2f}", f"{prob*100:.1f}%"))
                elif len(breakeven_points) == 2:
                    # Two breakeven case (like iron condor)
                    be1, be2 = breakeven_points
                    z1 = np.log(be1 / current_price) / (volatility * np.sqrt(years))
                    z2 = np.log(be2 / current_price) / (volatility * np.sqrt(years))
                    
                    if expiry_payoffs[4] > 0:  # Profit in the middle
                        prob = norm.cdf(z2) - norm.cdf(z1)
                        prob_sections.append((f"Between ${be1:.2f} and ${be2:.2f}", f"{prob*100:.1f}%"))
                    else:  # Profit outside
                        prob = norm.cdf(z1) + (1 - norm.cdf(z2))
                        prob_sections.append((f"Outside ${be1:.2f} and ${be2:.2f}", f"{prob*100:.1f}%"))
                
                # Display probability of profit sections
                st.subheader("Probability of Profit")
                
                for section, prob in prob_sections:
                    st.metric("Profit Region", section, delta=prob)
                
                # Visualize probability density
                st.subheader("Price Probability Distribution")
                
                # Generate price range for probability density function
                price_range = np.linspace(current_price * 0.7, current_price * 1.3, 100)
                
                # Calculate log-normal PDF values
                pdf_values = []
                for price in price_range:
                    # Log-normal PDF
                    x = np.log(price / current_price)
                    pdf = (1 / (price * volatility * np.sqrt(2 * np.pi * years))) * \
                          np.exp(-(x - (volatility**2 * years / 2))**2 / (2 * volatility**2 * years))
                    pdf_values.append(pdf)
                
                # Create probability density plot
                fig = go.Figure()
                
                # Add PDF curve
                fig.add_trace(go.Scatter(
                    x=price_range,
                    y=pdf_values,
                    mode='lines',
                    name='Probability Density',
                    line=dict(color='blue', width=2)
                ))
                
                # Add current price line
                fig.add_shape(
                    type="line",
                    x0=current_price, x1=current_price,
                    y0=0, y1=max(pdf_values) * 1.1,
                    line=dict(color="red", width=1, dash="dash")
                )
                
                # Add breakeven lines
                for be in breakeven_points:
                    fig.add_shape(
                        type="line",
                        x0=be, x1=be,
                        y0=0, y1=max(pdf_values) * 1.1,
                        line=dict(color="green", width=1, dash="dash")
                    )
                
                # Update layout
                fig.update_layout(
                    title=f"Price Probability Distribution at T-{days_to_expiry}",
                    xaxis_title="Stock Price",
                    yaxis_title="Probability Density",
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Add enhanced risk heatmap
            st.subheader("Risk Matrix")
            
            # Generate wider price range for heatmap
            price_range_wide = np.linspace(current_price * 0.7, current_price * 1.3, 50)
            
            # Create time points (more points for shorter expiries)
            if days_to_expiry <= 7:
                time_points = days_to_expiry + 1
            elif days_to_expiry <= 30:
                time_points = min(10, days_to_expiry)
            else:
                time_points = min(15, days_to_expiry)
                
            days_array = np.linspace(0, days_to_expiry, time_points).astype(int)
            days_array = np.unique(days_array)  # Remove duplicates
            
            # Create heatmap values
            z_values = np.zeros((len(days_array), len(price_range_wide)))
            
            for i, day in enumerate(days_array):
                days_remain = days_to_expiry - day
                if days_remain == 0:
                    z_values[i, :] = calculate_strategy_payoff(
                        strategy_legs, price_range_wide, current_price
                    )
                else:
                    z_values[i, :] = calculate_strategy_current_value(
                        strategy_legs, price_range_wide, days_remain, volatility=volatility
                    )
            
            # Create heatmap figure
            heatmap = go.Figure(data=go.Heatmap(
                z=z_values,
                x=price_range_wide,
                y=days_array,
                colorscale='RdBu',
                zmid=0,
                colorbar=dict(title='P/L ($)')
            ))
            
            # Add current price line
            heatmap.add_shape(
                type="line",
                x0=current_price, x1=current_price,
                y0=min(days_array), y1=max(days_array),
                line=dict(color="white", width=2, dash="dash")
            )
            
            # Update layout
            heatmap.update_layout(
                title="P/L Risk Matrix: Price vs Time",
                xaxis_title="Stock Price",
                yaxis_title="Days to Expiration",
                height=450
            )
            
            st.plotly_chart(heatmap, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error creating risk analysis: {str(e)}")
            logger.error(f"Error creating risk analysis: {str(e)}", exc_info=True)
    
    with tabs[2]:  # Time Decay Analysis
        if days_to_expiry > 0:
            try:
                st.subheader("Time Decay Analysis")
                
                # Enhanced time decay analysis with interactive elements
                # Get volatility
                volatility = calculate_strategy_volatility(strategy_legs)
                
                # Create time points selector
                time_points = st.slider(
                    "Time Points",
                    min_value=3,
                    max_value=min(10, days_to_expiry + 1),
                    value=min(5, days_to_expiry + 1),
                    help="Number of time points to analyze"
                )
                
                # Generate days array
                days = []
                if days_to_expiry <= time_points:
                    days = list(range(days_to_expiry + 1))
                else:
                    # Exponential spacing to show more detail near expiration
                    day_indices = np.round(np.logspace(
                        0, np.log10(days_to_expiry), time_points
                    )).astype(int)
                    days = sorted(list(set([0] + list(day_indices) + [days_to_expiry])))
                
                # Create price range
                price_range_pct = min(max(0.25, volatility * 2), 0.5)
                min_price = current_price * (1 - price_range_pct)
                max_price = current_price * (1 + price_range_pct)
                price_range = np.linspace(min_price, max_price, 100)
                
                # Calculate P/L for each time point
                fig = go.Figure()
                
                for day in days:
                    days_remain = days_to_expiry - day
                    if days_remain == 0:
                        # At expiration
                        values = calculate_strategy_payoff(strategy_legs, price_range, current_price)
                        name = "At Expiration"
                        width = 3
                        dash = None
                    else:
                        # Before expiration
                        values = calculate_strategy_current_value(
                            strategy_legs, price_range, days_remain, volatility=volatility
                        )
                        name = f"T-{days_remain}"
                        width = 2
                        dash = "dash" if days_remain < days_to_expiry / 2 else None
                    
                    fig.add_trace(go.Scatter(
                        x=price_range,
                        y=values,
                        mode='lines',
                        name=name,
                        line=dict(width=width, dash=dash)
                    ))
                
                # Add zero line
                fig.add_shape(
                    type="line",
                    x0=min_price, x1=max_price,
                    y0=0, y1=0,
                    line=dict(color="black", width=1)
                )
                
                # Add current price line
                fig.add_shape(
                    type="line",
                    x0=current_price, x1=current_price,
                    y0=min(fig.data[0].y) * 1.1, 
                    y1=max([max(trace.y) for trace in fig.data]) * 1.1,
                    line=dict(color="red", width=1, dash="dash")
                )
                
                # Update layout
                fig.update_layout(
                    title="Time Decay Effect on P/L",
                    xaxis_title="Stock Price",
                    yaxis_title="Profit/Loss ($)",
                    hovermode="x unified",
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Add theta decay analysis
                st.subheader("Theta Decay at Current Price")
                
                # Calculate P/L at current price for different days
                detailed_days = list(range(min(days_to_expiry + 1, 31)))
                current_price_values = []
                
                for day in detailed_days:
                    days_remain = days_to_expiry - day
                    if days_remain == 0:
                        # At expiration
                        value = calculate_strategy_payoff(
                            strategy_legs, [current_price], current_price
                        )[0]
                    else:
                        # Before expiration
                        value = calculate_strategy_current_value(
                            strategy_legs, [current_price], days_remain, volatility=volatility
                        )[0]
                    current_price_values.append(value)
                
                # Create daily decay chart
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=detailed_days,
                    y=current_price_values,
                    mode='lines+markers',
                    name='P/L',
                    line=dict(color='blue', width=2)
                ))
                
                # Add annotations for key dates
                today_value = current_price_values[0]
                expiry_value = current_price_values[-1]
                theta = (expiry_value - today_value) / days_to_expiry
                
                fig.add_annotation(
                    x=0,
                    y=today_value,
                    text=f"Today: ${today_value:.2f}",
                    showarrow=True,
                    arrowhead=1
                )
                
                fig.add_annotation(
                    x=detailed_days[-1],
                    y=expiry_value,
                    text=f"Expiry: ${expiry_value:.2f}",
                    showarrow=True,
                    arrowhead=1
                )
                
                # Calculate daily theta
                fig.add_annotation(
                    x=detailed_days[-1] / 2,
                    y=max(current_price_values),
                    text=f"Daily Theta: ${theta:.2f}",
                    showarrow=False,
                    bgcolor="rgba(255, 255, 255, 0.8)",
                    bordercolor="black",
                    borderwidth=1
                )
                
                # Update layout
                fig.update_layout(
                    title="Time Decay at Current Price",
                    xaxis_title="Days from Today",
                    yaxis_title="Profit/Loss ($)",
                    height=350
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Add Theta vs DTE analysis
                theta_values = []
                for i in range(len(detailed_days) - 1):
                    theta_values.append(current_price_values[i+1] - current_price_values[i])
                
                # Append a zero at the end to make lengths match
                theta_values.append(0)
                
                # Create theta decay chart
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    x=detailed_days,
                    y=theta_values,
                    name='Daily Theta',
                    marker_color=['red' if v < 0 else 'green' for v in theta_values]
                ))
                
                # Add zero line
                fig.add_shape(
                    type="line",
                    x0=0, x1=detailed_days[-1],
                    y0=0, y1=0,
                    line=dict(color="black", width=1)
                )
                
                # Update layout
                fig.update_layout(
                    title="Daily Theta Decay",
                    xaxis_title="Days from Today",
                    yaxis_title="Daily Change in P/L ($)",
                    height=350
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error creating time decay analysis: {str(e)}")
                logger.error(f"Error creating time decay analysis: {str(e)}", exc_info=True)
        else:
            st.info("Time decay analysis is only available for options before expiration")
    
    with tabs[3]:  # Mobile-optimized View
        st.subheader("Mobile-Optimized Summary")
        
        # Calculate key metrics
        price_range = np.linspace(current_price * 0.7, current_price * 1.3, 100)
        expiry_payoffs = calculate_strategy_payoff(strategy_legs, price_range, current_price)
        max_profit = max(expiry_payoffs)
        max_loss = min(expiry_payoffs)
        current_pl = calculate_strategy_payoff(strategy_legs, [current_price], current_price)[0]
        
        # Display compact strategy summary
        st.markdown(f"""
        <div class="mobile-card">
            <div class="mobile-header">Strategy Summary</div>
            <div class="mobile-metrics">
                <div class="metric">
                    <div class="metric-label">Current Price</div>
                    <div class="metric-value">${current_price:.2f}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Days to Expiry</div>
                    <div class="metric-value">{days_to_expiry}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Max Profit</div>
                    <div class="metric-value profit">${max_profit:.2f}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Max Loss</div>
                    <div class="metric-value loss">${max_loss:.2f}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Current P/L</div>
                    <div class="metric-value {('profit' if current_pl >= 0 else 'loss')}">${current_pl:.2f}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Create compact payoff diagram
        fig = go.Figure()
        
        # Add P/L at expiration
        fig.add_trace(go.Scatter(
            x=price_range, 
            y=expiry_payoffs,
            mode='lines',
            name='P/L at Expiration',
            line=dict(color='blue', width=3)
        ))
        
        # Add zero line
        fig.add_shape(
            type="line",
            x0=min(price_range), x1=max(price_range),
            y0=0, y1=0,
            line=dict(color="black", width=1)
        )
        
        # Add current price line
        fig.add_shape(
            type="line",
            x0=current_price, x1=current_price,
            y0=min(min(expiry_payoffs), 0) * 1.1 if min(expiry_payoffs) < 0 else -10, 
            y1=max(max(expiry_payoffs), 0) * 1.1,
            line=dict(color="red", width=2, dash="dash")
        )
        
        # Update layout optimized for mobile
        fig.update_layout(
            margin=dict(l=10, r=10, t=40, b=10),
            height=300,
            title="P/L at Expiration",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show breakeven points
        breakeven_points = find_breakeven_points(price_range, expiry_payoffs)
        if breakeven_points:
            breakeven_formatted = [f"${be:.2f} ({((be/current_price)-1)*100:.1f}%)" for be in breakeven_points]
            st.markdown(f"""
            <div class="mobile-card">
                <div class="mobile-header">Breakeven Points</div>
                <div class="mobile-content">
                    {', '.join(breakeven_formatted)}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Add simple price scenarios
        st.markdown("""
        <div class="mobile-card">
            <div class="mobile-header">Price Scenarios</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Calculate scenarios at -10%, current, +10%
        scenarios = [0.9, 1.0, 1.1]
        scenario_prices = [current_price * s for s in scenarios]
        scenario_payoffs = calculate_strategy_payoff(strategy_legs, scenario_prices, current_price)
        
        for i, scenario in enumerate(scenarios):
            direction = "Down" if scenario < 1.0 else "Up" if scenario > 1.0 else "No Change"
            pct = abs((scenario - 1.0) * 100)
            price = scenario_prices[i]
            payoff = scenario_payoffs[i]
            
            if scenario == 1.0:
                label = "Price Unchanged"
            else:
                label = f"Price {direction} {pct:.0f}%"
            
            st.markdown(f"""
            <div class="mobile-scenario">
                <div class="scenario-label">{label}</div>
                <div class="scenario-price">${price:.2f}</div>
                <div class="scenario-pl {('profit' if payoff >= 0 else 'loss')}">${payoff:.2f}</div>
            </div>
            """, unsafe_allow_html=True)

    with tabs[4]:  # Position Analysis
        st.subheader("Position Analysis")
        
        # Create position summary if we have both current prices and entry prices
        if any('current_price' in leg for leg in strategy_legs):
            # Create unrealized P/L table
            pl_table = create_unrealized_pl_table(strategy_legs, current_price)
            st.dataframe(pl_table, use_container_width=True)
            
            # Calculate total position metrics
            total_entry_cost = sum([
                leg.get('price', 0) * leg.get('quantity', 1) * 100 * (1 if leg.get('position') == 'long' else -1)
                for leg in strategy_legs
            ])
            
            total_current_value = sum([
                leg.get('current_price', leg.get('price', 0)) * leg.get('quantity', 1) * 100 * 
                (1 if leg.get('position') == 'long' else -1)
                for leg in strategy_legs
            ])
            
            unrealized_pl = total_current_value - total_entry_cost
            
            # Show position metrics
            metric_cols = st.columns(3)
            with metric_cols[0]:
                st.metric(
                    "Entry Cost", 
                    f"${abs(total_entry_cost):.2f}",
                    delta=None
                )
            
            with metric_cols[1]:
                st.metric(
                    "Current Value", 
                    f"${abs(total_current_value):.2f}",
                    delta=None
                )
            
            with metric_cols[2]:
                st.metric(
                    "Unrealized P/L", 
                    f"${unrealized_pl:.2f}",
                    delta=f"{(unrealized_pl/abs(total_entry_cost))*100:.1f}%" if total_entry_cost != 0 else None
                )
            
            # Show what if analysis
            st.subheader("What If Analysis")
            
            # What if we entered at current prices?
            what_if_legs = [
                {**leg, 'price': leg.get('current_price', leg.get('price', 0))}
                for leg in strategy_legs
            ]
            
            # Calculate payoff difference
            current_price_range = np.linspace(current_price * 0.7, current_price * 1.3, 100)
            
            # Original position payoff
            original_payoff = calculate_strategy_payoff(strategy_legs, [current_price])[0]
            
            # What if payoff (if entered at current prices)
            what_if_payoff = calculate_strategy_payoff(what_if_legs, [current_price])[0]
            
            # Display comparison
            st.write(f"If you had entered this position at current market prices:")
            
            what_if_cols = st.columns(2)
            with what_if_cols[0]:
                st.metric(
                    "Current Position P/L at Expiration", 
                    f"${original_payoff:.2f}",
                    delta=None
                )
            
            with what_if_cols[1]:
                st.metric(
                    "New Entry P/L at Expiration", 
                    f"${what_if_payoff:.2f}",
                    delta=f"{what_if_payoff - original_payoff:.2f}" 
                )
            
            # Create comparison chart
            fig = go.Figure()
            
            # Add original position payoff
            original_payoffs = calculate_strategy_payoff(strategy_legs, current_price_range)
            fig.add_trace(go.Scatter(
                x=current_price_range, 
                y=original_payoffs,
                mode='lines',
                name='Current Position',
                line=dict(color='blue', width=2)
            ))
            
            # Add what if payoff
            what_if_payoffs = calculate_strategy_payoff(what_if_legs, current_price_range)
            fig.add_trace(go.Scatter(
                x=current_price_range, 
                y=what_if_payoffs,
                mode='lines',
                name='If Entered Now',
                line=dict(color='green', width=2, dash='dash')
            ))
            
            # Add zero line
            fig.add_shape(
                type="line",
                x0=min(current_price_range), x1=max(current_price_range),
                y0=0, y1=0,
                line=dict(color="black", width=1)
            )
            
            # Add current price line
            fig.add_shape(
                type="line",
                x0=current_price, x1=current_price,
                y0=min(min(original_payoffs), min(what_if_payoffs)) * 1.1, 
                y1=max(max(original_payoffs), max(what_if_payoffs)) * 1.1,
                line=dict(color="red", width=1, dash="dash")
            )
            
            # Update layout
            fig.update_layout(
                title="Position Comparison at Expiration",
                xaxis_title="Stock Price",
                yaxis_title="Profit/Loss ($)",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No position analysis available. Use custom entry prices to analyze your actual position.")

# Helper functions
def calculate_strategy_volatility(strategy_legs):
    """Calculate average implied volatility from strategy legs."""
    ivs = [leg.get('iv', 0.3) for leg in strategy_legs 
          if leg.get('type') in ('call', 'put') and 'iv' in leg]
    
    if not ivs:
        return 0.3  # Default if no IVs found
    return sum(ivs) / len(ivs)

def find_breakeven_points(price_range, payoffs):
    """Find breakeven points in a strategy (where payoff crosses zero)."""
    breakeven_points = []
    for i in range(1, len(price_range)):
        if (payoffs[i-1] <= 0 and payoffs[i] > 0) or (payoffs[i-1] >= 0 and payoffs[i] < 0):
            # Linear interpolation to find precise breakeven
            x0, y0 = price_range[i-1], payoffs[i-1]
            x1, y1 = price_range[i], payoffs[i]
            
            if y1 - y0 != 0:  # Avoid division by zero
                breakeven = x0 + (x1 - x0) * (-y0) / (y1 - y0)
                breakeven_points.append(breakeven)
    
    return breakeven_points

# Main app flow
def main():
    # Show header
    show_header()
    
    # Handle ticker selection
    ticker, current_price, expirations = handle_ticker_selection()
    
    # If ticker and price are valid, configure and analyze strategy
    if ticker and current_price and expirations:
        # Create columns for main layout
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Configure strategy
            strategy_legs, selected_expiry, days_to_expiry = configure_strategy(
                ticker, current_price, expirations
            )
            
            # Store in session state
            if strategy_legs:
                st.session_state['strategy_legs'] = strategy_legs
        
        with col2:
            # Analyze and visualize the strategy
            analyze_strategy(
                st.session_state.get('strategy_legs'),
                current_price,
                selected_expiry if 'selected_expiry' in locals() else None,
                days_to_expiry if 'days_to_expiry' in locals() else None
            )
    else:
        # Show welcome message
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

if __name__ == "__main__":
    try:
        # Create necessary directories if they don't exist
        os.makedirs("logs", exist_ok=True)
        os.makedirs("styles", exist_ok=True)
        os.makedirs("assets", exist_ok=True)
        
        # Create CSS file if it doesn't exist
        if not os.path.exists("styles/main.css"):
            with open("styles/main.css", "w") as f:
                f.write("""
                /* Main Styles */
                .main-header {
                    font-size: 2.5rem !important;
                    font-weight: 600;
                    color: #1E88E5;
                    margin-bottom: 0;
                }
                
                .subtitle {
                    font-size: 1.2rem;
                    color: #616161;
                    margin-top: 0;
                }
                
                .stock-info-card {
                    background-color: #f8f9fa;
                    border-radius: 10px;
                    padding: 15px;
                    border-left: 5px solid #1E88E5;
                }
                
                .stock-ticker {
                    font-size: 1.5rem;
                    font-weight: 600;
                    color: #1E88E5;
                }
                
                .stock-name {
                    font-size: 1rem;
                    font-weight: 400;
                    color: #424242;
                }
                
                .stock-meta {
                    font-size: 0.8rem;
                    color: #616161;
                    margin-top: 5px;
                }
                
                .price-card {
                    display: flex;
                    align-items: center;
                    background-color: #f8f9fa;
                    border-radius: 10px;
                    padding: 10px 15px;
                    margin-top: 10px;
                }
                
                .current-price {
                    font-size: 1.5rem;
                    font-weight: 600;
                    margin-right: 10px;
                }
                
                .price-change {
                    font-size: 1rem;
                    font-weight: 500;
                }
                
                .metric-card {
                    background-color: #f9f9f9;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 5px 0;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }
                
                .metric-label {
                    font-size: 0.9rem;
                    color: #616161;
                    margin-bottom: 5px;
                }
                
                .metric-value {
                    font-size: 1.2rem;
                    font-weight: 500;
                    color: #212121;
                }
                
                .profit {
                    color: #4CAF50;
                }
                
                .loss {
                    color: #F44336;
                }
                
                /* Mobile optimized view */
                .mobile-card {
                    background-color: #f8f9fa;
                    border-radius: 10px;
                    padding: 15px;
                    margin-bottom: 15px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                        
                }.mobile-header {
                    font-size: 1.2rem;
                    font-weight: 600;
                    color: #1E88E5;
                    margin-bottom: 10px;
                }
                
                .mobile-metrics {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 10px;
                }
                
                .mobile-metrics .metric {
                    flex: 1 0 calc(50% - 10px);
                    background-color: white;
                    padding: 10px;
                    border-radius: 5px;
                }
                
                .mobile-content {
                    font-size: 1rem;
                    color: #212121;
                }
                
                .mobile-scenario {
                    display: flex;
                    justify-content: space-between;
                    padding: 10px;
                    background-color: white;
                    border-radius: 5px;
                    margin-bottom: 10px;
                }
                
                .scenario-label {
                    font-weight: 500;
                }
                
                .scenario-price {
                    font-weight: 400;
                    color: #616161;
                }
                
                .scenario-pl {
                    font-weight: 600;
                }
                """)
        
        main()
    except Exception as e:
        st.error(f"Application Error: {str(e)}")
        logger.error(f"Application Error: {str(e)}", exc_info=True)