# ui/components/strategy_config.py
import streamlit as st
import pandas as pd
from datetime import datetime
import logging
import time
from data.fetcher import get_option_chain
from strategies.strategies_factory import create_strategy
from models.pricing import calculate_implied_volatility, calculate_greeks
from utils.error_handlers import handle_ui_error, safe_execute
from utils.formatters import format_price, format_percent

logger = logging.getLogger(__name__)

@handle_ui_error
def configure_strategy(ticker, current_price, expirations, strategy_category, strategy_type):
    """
    Configure options strategy parameters based on selected strategy.
    
    Parameters:
        ticker (str): Stock ticker symbol
        current_price (float): Current stock price
        expirations (list): List of available expiration dates
        strategy_category (str): Strategy category
        strategy_type (str): Strategy type
        
    Returns:
        tuple: (strategy_legs, selected_expiry, days_to_expiry)
    """
    if not ticker or not current_price or not expirations:
        return None, None, None
        
    with st.sidebar:
        # Expiration selection
        st.header("Strategy Configuration")
        selected_expiry, days_to_expiry = select_expiration(expirations)
        
        # Load option chain with improved error handling
        try:
            calls_df, puts_df = load_option_chain(ticker, selected_expiry, current_price)
            
            # Strategy-specific configuration
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

def select_expiration(expirations):
    """
    Select expiration date and calculate days to expiry.
    
    Parameters:
        expirations (list): List of available expiration dates
        
    Returns:
        tuple: (selected_expiry, days_to_expiry)
    """
    selected_expiry = st.selectbox("Expiration Date", expirations)
    
    # Calculate days to expiration
    expiry_date = datetime.strptime(selected_expiry, "%Y-%m-%d").date()
    today = datetime.now().date()
    days_to_expiry = (expiry_date - today).days
    
    # Display time to expiration with visual indicators
    display_expiration_info(days_to_expiry)
    
    return selected_expiry, days_to_expiry

def display_expiration_info(days_to_expiry):
    """
    Display expiration information with visual indicators.
    
    Parameters:
        days_to_expiry (int): Days until expiration
    """
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

@handle_ui_error
def load_option_chain(ticker, expiration, current_price):
    """
    Load and enhance option chain data.
    
    Parameters:
        ticker (str): Stock ticker symbol
        expiration (str): Expiration date string
        current_price (float): Current stock price
        
    Returns:
        tuple: (calls_df, puts_df) DataFrames with option chain data
    """
    with st.spinner("Loading option chain..."):
        # Fetch option data
        calls, puts = get_option_chain(ticker, expiration)
        
        # Convert to DataFrame for easier handling
        calls_df = pd.DataFrame(calls)
        puts_df = pd.DataFrame(puts)
        
        # Enhance option chains with calculated columns if needed
        if 'impliedVolatility' not in calls_df.columns or calls_df['impliedVolatility'].isna().any():
            calls_df = enhance_option_chain(calls_df, 'call', current_price, days_to_expiry)
        
        if 'impliedVolatility' not in puts_df.columns or puts_df['impliedVolatility'].isna().any():
            puts_df = enhance_option_chain(puts_df, 'put', current_price, days_to_expiry)
        
        # Display option chains
        with st.expander("View Option Chain Data"):
            display_option_chain(calls_df, puts_df)
        
        return calls_df, puts_df

def enhance_option_chain(df, option_type, current_price, days_to_expiry):
    """
    Enhance option chain with calculated columns.
    
    Parameters:
        df (DataFrame): Option chain DataFrame
        option_type (str): 'call' or 'put'
        current_price (float): Current stock price
        days_to_expiry (int): Days to expiration
        
    Returns:
        DataFrame: Enhanced option chain
    """
    # Calculate implied volatility if missing
    if 'impliedVolatility' not in df.columns or df['impliedVolatility'].isna().any():
        df['impliedVolatility'] = df.apply(
            lambda row: safe_execute(
                lambda: calculate_implied_volatility(
                    option_type, current_price, row['strike'], days_to_expiry/365, 
                    0.03, row['lastPrice']
                ),
                default_value=0.3
            ), 
            axis=1
        )
    
    # Add in-the-money flag if not present
    if 'inTheMoney' not in df.columns:
        if option_type == 'call':
            df['inTheMoney'] = df['strike'] < current_price
        else:
            df['inTheMoney'] = df['strike'] > current_price
    
    # Add moneyness (% from ATM)
    df['moneyness'] = (df['strike'] / current_price - 1) * 100
    
    return df

def display_option_chain(calls_df, puts_df):
    """
    Display option chain in tabs.
    
    Parameters:
        calls_df (DataFrame): Calls option chain
        puts_df (DataFrame): Puts option chain
    """
    tab1, tab2 = st.tabs(["Calls", "Puts"])
    
    with tab1:
        if not calls_df.empty:
            display_df = calls_df[['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility']]
            display_df.columns = ['Strike', 'Last', 'Bid', 'Ask', 'Volume', 'OI', 'IV']
            display_df['IV'] = display_df['IV'].apply(lambda x: f"{x*100:.1f}%")
            st.dataframe(display_df, use_container_width=True)
        else:
            st.warning("No call options data available")
    
    with tab2:
        if not puts_df.empty:
            display_df = puts_df[['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility']]
            display_df.columns = ['Strike', 'Last', 'Bid', 'Ask', 'Volume', 'OI', 'IV']
            display_df['IV'] = display_df['IV'].apply(lambda x: f"{x*100:.1f}%")
            st.dataframe(display_df, use_container_width=True)
        else:
            st.warning("No put options data available")

def configure_specific_strategy(category, strategy_type, ticker, current_price, 
                              expiry, days_to_expiry, calls_df, puts_df):
    """
    Configure parameters for a specific strategy type.
    
    Note: This would implement all the strategy-specific configuration logic from the original app.py.
    For brevity, I'm showing the implementation for just one strategy type as an example.
    You would need to implement all the other strategy types following the same pattern.
    """
    # For demonstration, let's implement just one strategy type (Long Call)
    if category == "Basic Strategies" and strategy_type == "Long Call":
        return configure_long_call(current_price, expiry, days_to_expiry, calls_df)
    
    elif category == "Basic Strategies" and strategy_type == "Long Put":
        return configure_long_put(current_price, expiry, days_to_expiry, puts_df)
    
    elif category == "Basic Strategies" and strategy_type == "Covered Call":
        return configure_covered_call(ticker, current_price, expiry, days_to_expiry, calls_df)
    
    elif category == "Spread Strategies" and strategy_type == "Bull Call Spread":
        return configure_bull_call_spread(current_price, expiry, days_to_expiry, calls_df)
    
    elif category == "Advanced Strategies" and strategy_type == "Iron Condor":
        return configure_iron_condor(current_price, expiry, days_to_expiry, calls_df, puts_df)
    
    elif "Custom" in strategy_type:
        # Extract number of legs (2, 3, or 4)
        num_legs = int(strategy_type.split(" - ")[1][0])
        return configure_custom_strategy(num_legs, current_price, expiry, days_to_expiry, calls_df, puts_df)
    
    # Add other strategy configurations here...
    
    # For strategies not yet implemented, show a placeholder
    st.info(f"Configuration for {strategy_type} is not yet implemented in this version.")
    return None

def configure_long_call(current_price, expiry, days_to_expiry, calls_df):
    """
    Configure Long Call strategy.
    
    Parameters:
        current_price (float): Current stock price
        expiry (str): Expiration date
        days_to_expiry (int): Days to expiration
        calls_df (DataFrame): Calls option chain
        
    Returns:
        list: Strategy legs
    """
    if calls_df.empty:
        st.error("No call options data available")
        return None
    
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

# Add implementations for other strategy types...
def configure_long_put(current_price, expiry, days_to_expiry, puts_df):
    """Configure Long Put strategy."""
    # Implementation similar to long_call but for puts
    pass

def configure_covered_call(ticker, current_price, expiry, days_to_expiry, calls_df):
    """Configure Covered Call strategy."""
    # Implementation for covered call
    pass

def configure_bull_call_spread(current_price, expiry, days_to_expiry, calls_df):
    """Configure Bull Call Spread strategy."""
    # Implementation for bull call spread
    pass

def configure_iron_condor(current_price, expiry, days_to_expiry, calls_df, puts_df):
    """Configure Iron Condor strategy."""
    # Implementation for iron condor
    pass

def configure_custom_strategy(num_legs, current_price, expiry, days_to_expiry, calls_df, puts_df):
    """Configure Custom Strategy with specified number of legs."""
    # Implementation for custom strategy builder
    pass