# --- app.py ---
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Import custom modules
from data_fetch import get_stock_price, get_option_chain, get_expiration_dates
from strategies.basic_strategies import long_call_strategy, long_put_strategy, covered_call_strategy, cash_secured_put_strategy, naked_call_strategy, naked_put_strategy
from strategies.spread_strategies import credit_spread, call_spread_strategy, put_spread_strategy, calendar_spread, ratio_backspread, poor_mans_covered_call
from strategies.advanced_strategies import iron_condor_strategy, butterfly_strategy, collar_strategy, diagonal_spread_strategy, double_diagonal_strategy, straddle_strategy, strangle_strategy, covered_strangle_strategy, synthetic_put_strategy, reverse_conversion_strategy
from strategies.custom_strategy import custom_strategy
from pricing import black_scholes, calculate_greeks
from utils import calculate_strategy_payoff, calculate_strategy_current_value, create_payoff_chart, create_heatmap, create_risk_table


# Page configuration
st.set_page_config(
    page_title="Options Strategy Calculator",
    page_icon="📈",
    layout="wide",
)

# Add custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem !important;
        font-weight: 600;
        color: #1E88E5;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 500;
        color: #424242;
    }
    .metric-card {
        background-color: #f9f9f9;
        border-radius: 5px;
        padding: 10px;
        margin: 5px 0;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #616161;
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
</style>
""", unsafe_allow_html=True)

# Initialize session state for storing data between reruns
if 'strategy_legs' not in st.session_state:
    st.session_state['strategy_legs'] = None
if 'current_price' not in st.session_state:
    st.session_state['current_price'] = None

# App title
st.markdown("<div class='main-header'>Options Strategy Calculator</div>", unsafe_allow_html=True)
st.markdown("Analyze and visualize options strategies with real-time market data")

# Create a two-column layout for the main content
col1, col2 = st.columns([1, 2])

# Sidebar for ticker and strategy selection
with st.sidebar:
    st.header("Configuration")
    
    # Ticker selection
    ticker = st.text_input("Stock Ticker", value="AAPL")
    
    # Load stock data when ticker is provided
    if ticker:
        try:
            with st.spinner(f"Loading data for {ticker}..."):
                current_price = get_stock_price(ticker)
                st.session_state['current_price'] = current_price
                
                st.success(f"Current Price: ${current_price:.2f}")
                
                # Get available expiration dates
                expirations = get_expiration_dates(ticker)
                
                if not expirations:
                    st.error(f"No options data available for {ticker}")
                else:
                    st.info(f"Found {len(expirations)} expiration dates")
        except Exception as e:
            st.error(f"Error: {str(e)}")
            current_price = None
            expirations = []
    else:
        current_price = None
        expirations = []
    
    # Strategy selection
    st.header("Strategy Selection")
    
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
    
    # Strategy help
    with st.expander("Strategy Information"):
        if strategy_category == "Basic Strategies":
            if strategy_type == "Long Call":
                st.write("**Long Call**: Buy a call option to profit from a rise in the stock price.")
                st.write("- Max Loss: Limited to premium paid")
                st.write("- Max Gain: Unlimited (stock price - strike - premium)")
                st.write("- Breakeven: Strike price + premium")
            elif strategy_type == "Long Put":
                st.write("**Long Put**: Buy a put option to profit from a fall in the stock price.")
                st.write("- Max Loss: Limited to premium paid")
                st.write("- Max Gain: Limited to (strike - premium) if stock goes to zero")
                st.write("- Breakeven: Strike price - premium")
            # Add descriptions for other strategies...

# Strategy configuration panel
with col1:
    st.markdown("<div class='sub-header'>Strategy Configuration</div>", unsafe_allow_html=True)
    
    if current_price and expirations:
        # Common configuration - expiration selection
        selected_expiry = st.selectbox("Expiration Date", expirations)
        
        # Calculate days to expiration
        expiry_date = datetime.strptime(selected_expiry, "%Y-%m-%d").date()
        today = datetime.now().date()
        days_to_expiry = (expiry_date - today).days
        
        st.write(f"Days to Expiration: {days_to_expiry}")
        
        # Load option chain for selected expiry
        try:
            with st.spinner("Loading option chain..."):
                calls, puts = get_option_chain(ticker, selected_expiry)
                
                # Convert to DataFrame for easier handling
                calls_df = pd.DataFrame(calls)
                puts_df = pd.DataFrame(puts)
                
                # Show option chains in expandable section
                with st.expander("View Option Chain Data"):
                    st.write("#### Call Options")
                    st.dataframe(calls_df[['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility']])
                    
                    st.write("#### Put Options")
                    st.dataframe(puts_df[['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility']])
        except Exception as e:
            st.error(f"Error loading option chain: {str(e)}")
            st.stop()
        
        # Strategy-specific inputs
        if strategy_category == "Basic Strategies":
            if strategy_type == "Long Call":
                # Find strikes near the current price
                available_strikes = sorted(calls_df['strike'].unique().tolist())
                atm_index = min(range(len(available_strikes)), 
                               key=lambda i: abs(available_strikes[i] - current_price))
                
                # Strike selection
                selected_strike_index = st.selectbox(
                    "Strike Price",
                    range(len(available_strikes)),
                    format_func=lambda i: f"${available_strikes[i]:.2f}",
                    index=atm_index
                )
                selected_strike = available_strikes[selected_strike_index]
                
                # Get option data for selected strike
                option_data = calls_df[calls_df['strike'] == selected_strike].iloc[0]
                premium = option_data['lastPrice']
                
                # Option details
                st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                st.markdown(f"<div class='metric-label'>Selected Call Option</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='metric-value'>{ticker} {selected_expiry} ${selected_strike:.2f} Call</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                    st.markdown(f"<div class='metric-label'>Premium</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='metric-value'>${premium:.2f}</div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col_b:
                    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                    st.markdown(f"<div class='metric-label'>Contract Value</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='metric-value'>${premium * 100:.2f}</div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # Option to adjust quantity
                quantity = st.number_input("Quantity (# of contracts)", min_value=1, value=1)
                
                # Create strategy legs
                strategy_legs = []
                for _ in range(quantity):
                    leg = {
                        'type': 'call',
                        'position': 'long',
                        'strike': selected_strike,
                        'expiry': selected_expiry,
                        'price': premium,
                        'iv': option_data.get('impliedVolatility', 0.3)
                    }
                    strategy_legs.append(leg)
                
                # Store in session state
                st.session_state['strategy_legs'] = strategy_legs
                
            elif strategy_type == "Long Put":
                # Similar implementation for Long Put strategy
                available_strikes = sorted(puts_df['strike'].unique().tolist())
                atm_index = min(range(len(available_strikes)), 
                               key=lambda i: abs(available_strikes[i] - current_price))
                
                selected_strike_index = st.selectbox(
                    "Strike Price",
                    range(len(available_strikes)),
                    format_func=lambda i: f"${available_strikes[i]:.2f}",
                    index=atm_index
                )
                selected_strike = available_strikes[selected_strike_index]
                
                option_data = puts_df[puts_df['strike'] == selected_strike].iloc[0]
                premium = option_data['lastPrice']
                
                st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                st.markdown(f"<div class='metric-label'>Selected Put Option</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='metric-value'>{ticker} {selected_expiry} ${selected_strike:.2f} Put</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                    st.markdown(f"<div class='metric-label'>Premium</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='metric-value'>${premium:.2f}</div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col_b:
                    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                    st.markdown(f"<div class='metric-label'>Contract Value</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='metric-value'>${premium * 100:.2f}</div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                quantity = st.number_input("Quantity (# of contracts)", min_value=1, value=1)
                
                strategy_legs = []
                for _ in range(quantity):
                    leg = {
                        'type': 'put',
                        'position': 'long',
                        'strike': selected_strike,
                        'expiry': selected_expiry,
                        'price': premium,
                        'iv': option_data.get('impliedVolatility', 0.3)
                    }
                    strategy_legs.append(leg)
                
                st.session_state['strategy_legs'] = strategy_legs
                
            elif strategy_type == "Covered Call":
                # Implementation for Covered Call strategy
                available_strikes = sorted(calls_df['strike'].unique().tolist())
                
                # Default to slightly OTM call
                default_index = min(range(len(available_strikes)), 
                                   key=lambda i: abs(available_strikes[i] - current_price * 1.05))
                
                selected_strike_index = st.selectbox(
                    "Call Strike Price",
                    range(len(available_strikes)),
                    format_func=lambda i: f"${available_strikes[i]:.2f}",
                    index=default_index
                )
                selected_strike = available_strikes[selected_strike_index]
                
                option_data = calls_df[calls_df['strike'] == selected_strike].iloc[0]
                premium = option_data['lastPrice']
                
                st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                st.markdown(f"<div class='metric-label'>Stock Price</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='metric-value'>${current_price:.2f}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                st.markdown(f"<div class='metric-label'>Call Premium</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='metric-value'>${premium:.2f}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
                quantity = st.number_input("Quantity (# of covered call units)", min_value=1, value=1)
                
                strategy_legs = []
                for _ in range(quantity):
                    # Add stock leg
                    stock_leg = {
                        'type': 'stock',
                        'position': 'long',
                        'price': current_price,
                        'quantity': 100  # 100 shares per contract
                    }
                    
                    # Add call leg
                    call_leg = {
                        'type': 'call',
                        'position': 'short',
                        'strike': selected_strike,
                        'expiry': selected_expiry,
                        'price': premium,
                        'iv': option_data.get('impliedVolatility', 0.3)
                    }
                    
                    strategy_legs.extend([stock_leg, call_leg])
                
                st.session_state['strategy_legs'] = strategy_legs

        elif strategy_category == "Spread Strategies":
            if strategy_type == "Bull Call Spread":
                # Implementation for Bull Call Spread
                available_strikes = sorted(calls_df['strike'].unique().tolist())
                atm_index = min(range(len(available_strikes)), 
                               key=lambda i: abs(available_strikes[i] - current_price))
                
                # Long call (lower strike)
                long_strike_index = st.selectbox(
                    "Long Call Strike (Lower)",
                    range(len(available_strikes)),
                    format_func=lambda i: f"${available_strikes[i]:.2f}",
                    index=max(0, atm_index-1)
                )
                long_strike = available_strikes[long_strike_index]
                
                # Short call (higher strike)
                short_options = range(long_strike_index+1, len(available_strikes))
                if short_options:
                    short_strike_index = st.selectbox(
                        "Short Call Strike (Higher)",
                        short_options,
                        format_func=lambda i: f"${available_strikes[i]:.2f}",
                        index=min(2, len(short_options)-1)
                    )
                    short_strike = available_strikes[short_strike_index]
                else:
                    st.error("No higher strikes available for the short call leg")
                    short_strike = None
                
                if short_strike:
                    # Get option data
                    long_option = calls_df[calls_df['strike'] == long_strike].iloc[0]
                    short_option = calls_df[calls_df['strike'] == short_strike].iloc[0]
                    
                    long_premium = long_option['lastPrice']
                    short_premium = short_option['lastPrice']
                    net_debit = long_premium - short_premium
                    
                    # Display strategy details
                    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                    st.markdown(f"<div class='metric-label'>Bull Call Spread</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='metric-value'>Long {ticker} {selected_expiry} ${long_strike:.2f} Call</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='metric-value'>Short {ticker} {selected_expiry} ${short_strike:.2f} Call</div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                        st.markdown(f"<div class='metric-label'>Long Premium</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='metric-value'>${long_premium:.2f}</div>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with col_b:
                        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                        st.markdown(f"<div class='metric-label'>Short Premium</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='metric-value'>${short_premium:.2f}</div>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with col_c:
                        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                        st.markdown(f"<div class='metric-label'>Net Debit</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='metric-value'>${net_debit:.2f}</div>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    quantity = st.number_input("Quantity (# of spreads)", min_value=1, value=1)
                    
                    # Create strategy legs
                    strategy_legs = []
                    for _ in range(quantity):
                        long_leg = {
                            'type': 'call',
                            'position': 'long',
                            'strike': long_strike,
                            'expiry': selected_expiry,
                            'price': long_premium,
                            'iv': long_option.get('impliedVolatility', 0.3)
                        }
                        
                        short_leg = {
                            'type': 'call',
                            'position': 'short',
                            'strike': short_strike,
                            'expiry': selected_expiry,
                            'price': short_premium,
                            'iv': short_option.get('impliedVolatility', 0.3)
                        }
                        
                        strategy_legs.extend([long_leg, short_leg])
                    
                    st.session_state['strategy_legs'] = strategy_legs
                
            elif strategy_type == "Iron Condor":
                # Implementation for Iron Condor
                # This combines a bull put spread and a bear call spread
                
                # Step 1: Bull Put Spread (lower strikes)
                available_put_strikes = sorted(puts_df['strike'].unique().tolist())
                atm_index_put = min(range(len(available_put_strikes)), 
                                   key=lambda i: abs(available_put_strikes[i] - current_price))
                
                # Default to OTM puts (below current price)
                default_short_put_index = max(0, atm_index_put - 3)  # ~15% OTM
                
                short_put_index = st.selectbox(
                    "Short Put Strike (Bull Put Spread)",
                    range(len(available_put_strikes)),
                    format_func=lambda i: f"${available_put_strikes[i]:.2f}",
                    index=default_short_put_index
                )
                short_put_strike = available_put_strikes[short_put_index]
                
                # Long put must be below short put
                long_put_options = range(0, short_put_index)
                if long_put_options:
                    default_long_put_index = max(0, short_put_index - 2)  # ~10% below short put
                    
                    long_put_index = st.selectbox(
                        "Long Put Strike (Bull Put Spread)",
                        long_put_options,
                        format_func=lambda i: f"${available_put_strikes[i]:.2f}",
                        index=min(default_long_put_index, len(long_put_options)-1)
                    )
                    long_put_strike = available_put_strikes[long_put_index]
                else:
                    st.error("No lower strikes available for the long put leg")
                    long_put_strike = None
                
                # Step 2: Bear Call Spread (higher strikes)
                available_call_strikes = sorted(calls_df['strike'].unique().tolist())
                atm_index_call = min(range(len(available_call_strikes)), 
                                    key=lambda i: abs(available_call_strikes[i] - current_price))
                
                # Default to OTM calls (above current price)
                default_short_call_index = min(len(available_call_strikes)-1, atm_index_call + 3)  # ~15% OTM
                
                short_call_index = st.selectbox(
                    "Short Call Strike (Bear Call Spread)",
                    range(len(available_call_strikes)),
                    format_func=lambda i: f"${available_call_strikes[i]:.2f}",
                    index=default_short_call_index
                )
                short_call_strike = available_call_strikes[short_call_index]
                
                # Long call must be above short call
                long_call_options = range(short_call_index + 1, len(available_call_strikes))
                if long_call_options:
                    default_long_call_index = min(len(available_call_strikes)-1, short_call_index + 2)
                    
                    long_call_index = st.selectbox(
                        "Long Call Strike (Bear Call Spread)",
                        long_call_options,
                        format_func=lambda i: f"${available_call_strikes[i]:.2f}",
                        index=min(default_long_call_index - short_call_index - 1, len(long_call_options)-1)
                    )
                    long_call_strike = available_call_strikes[long_call_index]
                else:
                    st.error("No higher strikes available for the long call leg")
                    long_call_strike = None
                
                if long_put_strike and long_call_strike:
                    # Get option data
                    short_put_data = puts_df[puts_df['strike'] == short_put_strike].iloc[0]
                    long_put_data = puts_df[puts_df['strike'] == long_put_strike].iloc[0]
                    short_call_data = calls_df[calls_df['strike'] == short_call_strike].iloc[0]
                    long_call_data = calls_df[calls_df['strike'] == long_call_strike].iloc[0]
                    
                    # Calculate premiums
                    short_put_premium = short_put_data['lastPrice']
                    long_put_premium = long_put_data['lastPrice']
                    short_call_premium = short_call_data['lastPrice']
                    long_call_premium = long_call_data['lastPrice']
                    
                    # Net credit
                    net_credit = (short_put_premium - long_put_premium) + (short_call_premium - long_call_premium)
                    
                    # Display strategy details
                    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                    st.markdown(f"<div class='metric-label'>Iron Condor</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='metric-value'>Long {ticker} {selected_expiry} ${long_put_strike:.2f} Put</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='metric-value'>Short {ticker} {selected_expiry} ${short_put_strike:.2f} Put</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='metric-value'>Short {ticker} {selected_expiry} ${short_call_strike:.2f} Call</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='metric-value'>Long {ticker} {selected_expiry} ${long_call_strike:.2f} Call</div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                        st.markdown(f"<div class='metric-label'>Net Credit</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='metric-value profit'>${net_credit:.2f}</div>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with col_b:
                        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                        st.markdown(f"<div class='metric-label'>Width</div>", unsafe_allow_html=True)
                        put_width = short_put_strike - long_put_strike
                        call_width = long_call_strike - short_call_strike
                        st.markdown(f"<div class='metric-value'>Puts: ${put_width:.2f} / Calls: ${call_width:.2f}</div>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    quantity = st.number_input("Quantity (# of iron condors)", min_value=1, value=1)
                    
                    # Create strategy legs
                    strategy_legs = []
                    for _ in range(quantity):
                        legs = [
                            {
                                'type': 'put',
                                'position': 'long',
                                'strike': long_put_strike,
                                'expiry': selected_expiry,
                                'price': long_put_premium,
                                'iv': long_put_data.get('impliedVolatility', 0.3)
                            },
                            {
                                'type': 'put',
                                'position': 'short',
                                'strike': short_put_strike,
                                'expiry': selected_expiry,
                                'price': short_put_premium,
                                'iv': short_put_data.get('impliedVolatility', 0.3)
                            },
                            {
                                'type': 'call',
                                'position': 'short',
                                'strike': short_call_strike,
                                'expiry': selected_expiry,
                                'price': short_call_premium,
                                'iv': short_call_data.get('impliedVolatility', 0.3)
                            },
                            {
                                'type': 'call',
                                'position': 'long',
                                'strike': long_call_strike,
                                'expiry': selected_expiry,
                                'price': long_call_premium,
                                'iv': long_call_data.get('impliedVolatility', 0.3)
                            }
                        ]
                        strategy_legs.extend(legs)
                    
                    st.session_state['strategy_legs'] = strategy_legs

        elif strategy_category == "Custom Strategies":
            # Implementation for custom strategy builder
            st.write("Build your own custom strategy by adding legs")
            
            num_legs = int(strategy_type.split(" - ")[1][0])  # Extract number of legs from strategy type
            
            strategy_legs = []
            
            for i in range(num_legs):
                st.write(f"### Leg {i+1}")
                col1, col2 = st.columns(2)
                
                with col1:
                    leg_type = st.selectbox(f"Type #{i+1}", ["Call", "Put", "Stock"], key=f"type_{i}")
                    position = st.selectbox(f"Position #{i+1}", ["Long", "Short"], key=f"pos_{i}")
                
                with col2:
                    quantity = st.number_input(f"Quantity #{i+1}", min_value=1, value=1, key=f"qty_{i}")
                    
                    if leg_type != "Stock":
                        available_strikes = sorted(calls_df['strike'].unique().tolist()) if leg_type == "Call" else sorted(puts_df['strike'].unique().tolist())
                        
                        strike_index = st.selectbox(
                            f"Strike #{i+1}",
                            range(len(available_strikes)),
                            format_func=lambda i: f"${available_strikes[i]:.2f}",
                            key=f"strike_{i}"
                        )
                        strike = available_strikes[strike_index]
                        
                        # Get option data
                        option_chain = calls_df if leg_type == "Call" else puts_df
                        option_data = option_chain[option_chain['strike'] == strike].iloc[0]
                        premium = option_data['lastPrice']
                        
                        leg = {
                            'type': leg_type.lower(),
                            'position': position.lower(),
                            'strike': strike,
                            'expiry': selected_expiry,
                            'price': premium,
                            'quantity': quantity,
                            'iv': option_data.get('impliedVolatility', 0.3)
                        }
                    else:  # Stock leg
                        leg = {
                            'type': 'stock',
                            'position': position.lower(),
                            'price': current_price,
                            'quantity': quantity * 100  # 100 shares per standard contract
                        }
                    
                    strategy_legs.append(leg)
            
            # Show summary of the custom strategy
            if strategy_legs:
                st.write("### Strategy Summary")
                
                # Calculate net debit/credit
                net_cost = 0
                for leg in strategy_legs:
                    leg_cost = leg.get('price', 0) * leg.get('quantity', 1)
                    if leg.get('position') == 'long':
                        net_cost += leg_cost
                    else:  # short
                        net_cost -= leg_cost
                
                # Adjust for stock legs which are priced per share
                for leg in strategy_legs:
                    if leg.get('type') == 'stock':
                        net_cost *= 100  # Adjust to match option contract sizing
                
                cost_type = "Debit" if net_cost > 0 else "Credit"
                
                st.markdown(f"#### Net {cost_type}: ${abs(net_cost):.2f}")
                
                for i, leg in enumerate(strategy_legs):
                    leg_type = leg.get('type').capitalize()
                    position = leg.get('position').capitalize()
                    quantity = leg.get('quantity', 1)
                    
                    if leg_type in ('Call', 'Put'):
                        strike = leg.get('strike')
                        st.write(f"{position} {quantity} x {ticker} {leg_type} @ ${strike:.2f}")
                    else:  # Stock
                        st.write(f"{position} {quantity} shares of {ticker} @ ${leg.get('price'):.2f}")
                
                st.session_state['strategy_legs'] = strategy_legs
    else:
        st.info("Enter a valid ticker and select expiration date to configure strategy")

# Strategy analysis and visualization
with col2:
    st.markdown("<div class='sub-header'>Strategy Analysis</div>", unsafe_allow_html=True)
    
    # Check if we have strategy legs and current price
    if 'strategy_legs' in st.session_state and st.session_state['strategy_legs'] and 'current_price' in st.session_state and st.session_state['current_price']:
        strategy_legs = st.session_state['strategy_legs']
        current_price = st.session_state['current_price']
        
        # Get strategy name from sidebar
        if 'strategy_type' in locals():
            strategy_name = strategy_type
        else:
            strategy_name = "Options Strategy"
        
        # Create tabs for different analysis views
        tab1, tab2, tab3 = st.tabs(["Payoff Diagram", "Risk Analysis", "Time Decay"])
        
        with tab1:
            # Create payoff diagram using utility function
            try:
                # Generate price range for analysis
                price_range_pct = 0.25  # 25% up and down
                min_price = current_price * (1 - price_range_pct)
                max_price = current_price * (1 + price_range_pct)
                price_range = np.linspace(min_price, max_price, 100)
                
                # Calculate P/L at expiration
                expiry_payoffs = calculate_strategy_payoff(strategy_legs, price_range, current_price)
                
                # Calculate P/L before expiration if applicable
                if 'days_to_expiry' in locals() and days_to_expiry > 0:
                    # Get average implied volatility from strategy legs
                    ivs = [leg.get('iv', 0.3) for leg in strategy_legs if leg.get('type') in ('call', 'put')]
                    avg_iv = sum(ivs) / len(ivs) if ivs else 0.3
                    
                    # Calculate current values
                    current_values = calculate_strategy_current_value(
                        strategy_legs, price_range, days_to_expiry, volatility=avg_iv
                    )
                    
                    # Create plot with both lines
                    fig = go.Figure()
                    
                    # Add P/L at expiration
                    fig.add_trace(go.Scatter(
                        x=price_range, 
                        y=expiry_payoffs,
                        mode='lines',
                        name='P/L at Expiration',
                        line=dict(color='blue', width=2)
                    ))
                    
                    # Add current P/L
                    fig.add_trace(go.Scatter(
                        x=price_range, 
                        y=current_values,
                        mode='lines',
                        name=f'Current Value (T-{days_to_expiry})',
                        line=dict(color='green', width=2)
                    ))
                else:
                    # Create plot with expiration P/L only
                    fig = go.Figure()
                    
                    # Add P/L at expiration
                    fig.add_trace(go.Scatter(
                        x=price_range, 
                        y=expiry_payoffs,
                        mode='lines',
                        name='P/L at Expiration',
                        line=dict(color='blue', width=2)
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
                    y0=min(min(expiry_payoffs), 0) * 1.1, 
                    y1=max(max(expiry_payoffs), 0) * 1.1,
                    line=dict(color="red", width=1, dash="dash")
                )
                
                # Find breakeven points
                breakeven_points = []
                for i in range(1, len(price_range)):
                    if (expiry_payoffs[i-1] <= 0 and expiry_payoffs[i] > 0) or (expiry_payoffs[i-1] >= 0 and expiry_payoffs[i] < 0):
                        # Linear interpolation to find more precise breakeven
                        x0, y0 = price_range[i-1], expiry_payoffs[i-1]
                        x1, y1 = price_range[i], expiry_payoffs[i]
                        if y1 - y0 != 0:  # Avoid division by zero
                            breakeven = x0 + (x1 - x0) * (-y0) / (y1 - y0)
                            breakeven_points.append(breakeven)
                
                # Add breakeven annotations
                for i, be in enumerate(breakeven_points):
                    fig.add_shape(
                        type="line",
                        x0=be, x1=be,
                        y0=min(min(expiry_payoffs), 0) * 1.1, 
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
                
                # Add metrics annotation
                fig.add_annotation(
                    x=min_price + (max_price - min_price) * 0.05,
                    y=max(max(expiry_payoffs), 0) * 0.9,
                    text=f"<b>Max Profit:</b> ${max_profit:.2f}<br><b>Max Loss:</b> ${max_loss:.2f}",
                    showarrow=False,
                    align="left",
                    bordercolor="black",
                    borderwidth=1,
                    bgcolor="white",
                    opacity=0.8
                )
                
                # Update layout
                fig.update_layout(
                    title=f"{strategy_name} P/L Diagram",
                    xaxis_title="Stock Price",
                    yaxis_title="Profit/Loss ($)",
                    hovermode="x unified",
                    legend=dict(
                        yanchor="top",
                        y=0.99,
                        xanchor="left",
                        x=0.01
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error creating payoff chart: {str(e)}")
        
        with tab2:
            # Show risk analysis table
            try:
                # Create price points at different percentage changes
                change_pcts = [-0.3, -0.2, -0.1, -0.05, 0, 0.05, 0.1, 0.2, 0.3]
                prices = [current_price * (1 + pct) for pct in change_pcts]
                
                # Calculate payoffs at expiration
                expiry_payoffs = calculate_strategy_payoff(strategy_legs, prices, current_price)
                
                # Create DataFrame
                df = pd.DataFrame(index=["At Expiration"])
                df.loc["At Expiration"] = [f"${p:.2f}" for p in expiry_payoffs]
                
                # Calculate current value if days_to_expiry > 0
                if 'days_to_expiry' in locals() and days_to_expiry > 0:
                    # Get average implied volatility
                    ivs = [leg.get('iv', 0.3) for leg in strategy_legs if leg.get('type') in ('call', 'put')]
                    avg_iv = sum(ivs) / len(ivs) if ivs else 0.3
                    
                    current_values = calculate_strategy_current_value(
                        strategy_legs, prices, days_to_expiry, volatility=avg_iv
                    )
                    df.loc[f"Current (T-{days_to_expiry})"] = [f"${p:.2f}" for p in current_values]
                
                # Set column names
                df.columns = [f"{pct:+.0%} (${p:.2f})" for pct, p in zip(change_pcts, prices)]
                
                st.table(df)
                
                # Display metrics
                max_profit = max(expiry_payoffs)
                max_loss = min(expiry_payoffs)
                profit_potential = max_profit
                risk_amount = abs(max_loss) if max_loss < 0 else 0
                
                if risk_amount > 0:
                    risk_reward = profit_potential / risk_amount
                else:
                    risk_reward = float('inf')  # No risk or undefined
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                    st.markdown(f"<div class='metric-label'>Max Profit</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='metric-value profit'>${max_profit:.2f}</div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col_b:
                    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                    st.markdown(f"<div class='metric-label'>Max Loss</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='metric-value loss'>${max_loss:.2f}</div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col_c:
                    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                    st.markdown(f"<div class='metric-label'>Risk/Reward Ratio</div>", unsafe_allow_html=True)
                    if risk_reward == float('inf'):
                        st.markdown(f"<div class='metric-value'>No Risk</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='metric-value'>1:{risk_reward:.2f}</div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error creating risk analysis: {str(e)}")
        
        with tab3:
            # Time decay analysis
            if 'days_to_expiry' in locals() and days_to_expiry > 0:
                try:
                    # Create price range
                    price_range_pct = 0.25  # 25% up and down
                    min_price = current_price * (1 - price_range_pct)
                    max_price = current_price * (1 + price_range_pct)
                    price_range = np.linspace(min_price, max_price, 100)
                    
                    # Create time decay slider
                    st.write("### Time Decay Analysis")
                    days_remaining = st.slider("Days Remaining", 0, days_to_expiry, days_to_expiry)
                    
                    # Get average implied volatility
                    ivs = [leg.get('iv', 0.3) for leg in strategy_legs if leg.get('type') in ('call', 'put')]
                    avg_iv = sum(ivs) / len(ivs) if ivs else 0.3
                    
                    # Calculate P/L at expiration
                    expiry_payoffs = calculate_strategy_payoff(strategy_legs, price_range, current_price)
                    
                    # Calculate P/L at selected time
                    if days_remaining > 0:
                        current_values = calculate_strategy_current_value(
                            strategy_legs, price_range, days_remaining, volatility=avg_iv
                        )
                    else:
                        current_values = expiry_payoffs
                    
                    # Create figure
                    fig = go.Figure()
                    
                    # Add lines
                    fig.add_trace(go.Scatter(
                        x=price_range,
                        y=expiry_payoffs,
                        mode='lines',
                        name='At Expiration',
                        line=dict(color='blue', width=2)
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=price_range,
                        y=current_values,
                        mode='lines',
                        name=f'At T-{days_remaining}',
                        line=dict(color='green', width=2)
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
                        y0=min(min(expiry_payoffs), min(current_values)) * 1.1, 
                        y1=max(max(expiry_payoffs), max(current_values)) * 1.1,
                        line=dict(color="red", width=1, dash="dash")
                    )
                    
                    # Update layout
                    fig.update_layout(
                        title=f"Time Decay Analysis (T-{days_remaining} vs Expiration)",
                        xaxis_title="Stock Price",
                        yaxis_title="Profit/Loss ($)",
                        hovermode="x unified"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Add time decay heatmap
                    st.write("### P/L Heatmap (Price vs Days Remaining)")
                    
                    # Generate days range
                    if days_to_expiry <= 7:
                        day_points = days_to_expiry + 1
                    else:
                        day_points = min(15, days_to_expiry)
                    
                    days = np.linspace(0, days_to_expiry, day_points).astype(int)
                    days = np.unique(days)  # Remove duplicates
                    
                    # Generate price range for heatmap (fewer points for efficiency)
                    prices = np.linspace(min_price, max_price, 30)
                    
                    # Create arrays to hold values
                    z = np.zeros((len(days), len(prices)))
                    
                    # Calculate PnL for each price and day combination
                    for i, day in enumerate(days):
                        days_remain = days_to_expiry - day
                        
                        if days_remain == 0:  # At expiration
                            z[i, :] = calculate_strategy_payoff(strategy_legs, prices, current_price)
                        else:  # Before expiration
                            z[i, :] = calculate_strategy_current_value(
                                strategy_legs, prices, days_remain, volatility=avg_iv
                            )
                    
                    # Create the heatmap figure
                    heatmap_fig = go.Figure(data=go.Heatmap(
                        z=z,
                        x=prices,
                        y=days,
                        colorscale='RdBu',
                        zmid=0,  # Center colorscale at zero
                        colorbar=dict(title='P/L ($)'),
                    ))
                    
                    # Add current price line
                    heatmap_fig.add_shape(
                        type="line",
                        x0=current_price, x1=current_price,
                        y0=min(days), y1=max(days),
                        line=dict(color="black", width=1, dash="dash")
                    )
                    
                    # Update layout
                    heatmap_fig.update_layout(
                        title="P/L Heatmap: Price vs Days to Expiration",
                        xaxis_title="Stock Price",
                        yaxis_title="Days to Expiration",
                        xaxis=dict(
                            tickformat="$.2f"
                        )
                    )
                    
                    st.plotly_chart(heatmap_fig, use_container_width=True)
                    
                except Exception as e:
                    st.error(f"Error creating time decay analysis: {str(e)}")
            else:
                st.info("Time decay analysis is only available for options before expiration")
    else:
        st.info("Configure your options strategy to see analysis here")

# Add footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align:center">
        <p><small>
        This options calculator uses real-time market data from Yahoo Finance via yfinance. 
        The analysis is provided for educational purposes only and does not constitute investment advice.
        </small></p>
    </div>
    """, 
    unsafe_allow_html=True
)