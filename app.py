# --- app.py ---
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
from data_fetch import get_stock_price, get_option_chain, get_expiration_dates
from strategies.basic_strategies import long_call_strategy, long_put_strategy, covered_call_strategy
from strategies.spread_strategies import credit_spread, call_spread_strategy, put_spread_strategy, calendar_spread, ratio_backspread, poor_mans_covered_call
from strategies.advanced_strategies import iron_condor_strategy, butterfly_strategy, collar_strategy, diagonal_spread_strategy, double_diagonal_strategy, straddle_strategy, strangle_strategy, covered_strangle_strategy, synthetic_put_strategy, reverse_conversion_strategy
from strategies.custom_strategy import custom_strategy
from pricing import black_scholes, calculate_greeks
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="Options Strategy Calculator",
    page_icon="📈",
    layout="wide",
)

st.title("Options Strategy Calculator")

# Sidebar for ticker selection and data loading
with st.sidebar:
    st.header("Stock Selection")
    ticker = st.text_input("Enter Stock Ticker", value="AAPL")
    
    if ticker:
        try:
            with st.spinner(f"Loading data for {ticker}..."):
                price = get_stock_price(ticker)
                st.success(f"Current Price: ${price:.2f}")
                
                # Get expiration dates
                expiration_dates = get_expiration_dates(ticker)
                
                if not expiration_dates:
                    st.error(f"No options data available for {ticker}")
                else:
                    st.write(f"Found {len(expiration_dates)} expiration dates")
                    
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            price = None
            expiration_dates = []
    else:
        price = None
        expiration_dates = []

    # Strategy selection
    st.header("Strategy Type")
    strategy_category = st.selectbox("Category", [
        "Basic Strategies",
        "Spread Strategies",
        "Advanced Strategies",
        "Custom Strategies"
    ])
    
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
            "Credit Spread",
            "Call Spread",
            "Put Spread",
            "Calendar Spread",
            "Ratio Back Spread",
            "Poor Man's Covered Call"
        ])
    elif strategy_category == "Advanced Strategies":
        strategy_type = st.selectbox("Strategy", [
            "Iron Condor",
            "Butterfly",
            "Collar",
            "Diagonal Spread",
            "Double Diagonal",
            "Straddle",
            "Strangle",
            "Covered Strangle",
            "Synthetic Put",
            "Reverse Conversion"
        ])
    elif strategy_category == "Custom Strategies":
        strategy_type = st.selectbox("Strategy", [
            "Custom - 2 Legs",
            "Custom - 3 Legs",
            "Custom - 4 Legs"
        ])

# Main content
col1, col2 = st.columns([1, 2])

# Strategy configuration panel
with col1:
    st.header("Strategy Configuration")
    
    if price and expiration_dates:
        # Common parameters for most strategies
        selected_expiry = st.selectbox("Expiration Date", expiration_dates)
        
        # Fetch option chain for selected expiry
        with st.spinner("Loading option chain..."):
            calls, puts = get_option_chain(ticker, selected_expiry)
            # Convert to dataframes for easier handling
            calls_df = pd.DataFrame(calls)
            puts_df = pd.DataFrame(puts)
            
            # For debugging - show first few rows of option chains
            with st.expander("Available Options Data"):
                st.subheader("Calls")
                st.dataframe(calls_df)
                st.subheader("Puts")
                st.dataframe(puts_df)
        
        # Strategy-specific inputs
        if strategy_category == "Basic Strategies":
            if strategy_type == "Long Call":
                # Prepare strike selection from available calls
                available_strikes = sorted(calls_df['strike'].unique().tolist())
                
                # Find ATM strike (closest to current price)
                atm_index = min(range(len(available_strikes)), key=lambda i: abs(available_strikes[i] - price))
                default_strike = available_strikes[atm_index]
                
                selected_strike = st.selectbox("Strike Price", available_strikes, index=atm_index)
                
                # Get premium from option chain
                option_row = calls_df[calls_df['strike'] == selected_strike].iloc[0]
                premium = option_row['lastPrice']
                st.write(f"Option Premium: ${premium:.2f}")
                
                # Calculate some basic stats/greeks
                strategy_legs = long_call_strategy(selected_strike, selected_expiry, premium)
                
                # Calculate days to expiration
                expiry_date = datetime.strptime(selected_expiry, "%Y-%m-%d")
                days_to_expiry = (expiry_date - datetime.now()).days
                
                # Simple risk/reward metrics
                max_loss = premium * 100  # Per contract (100 shares)
                max_profit = "Unlimited"
                breakeven = selected_strike + premium
                
                st.subheader("Key Metrics")
                st.write(f"Max Loss: ${max_loss:.2f}")
                st.write(f"Max Profit: {max_profit}")
                st.write(f"Breakeven: ${breakeven:.2f}")
                
                # Calculate and display the greeks
                r = 0.03  # Assuming 3% risk-free rate
                sigma = option_row.get('impliedVolatility', 0.3)  # Get IV from data or use default
                
                greeks = calculate_greeks("call", price, selected_strike, days_to_expiry/365, r, sigma)
                
                st.subheader("Greeks")
                st.write(f"Delta: {greeks['delta']:.4f}")
                st.write(f"Gamma: {greeks['gamma']:.4f}")
                st.write(f"Theta: ${greeks['theta']:.4f}/day")
                st.write(f"Vega: ${greeks['vega']:.4f}")
            
            elif strategy_type == "Long Put":
                # Similar implementation for Long Put
                available_strikes = sorted(puts_df['strike'].unique().tolist())
                atm_index = min(range(len(available_strikes)), key=lambda i: abs(available_strikes[i] - price))
                selected_strike = st.selectbox("Strike Price", available_strikes, index=atm_index)
                
                option_row = puts_df[puts_df['strike'] == selected_strike].iloc[0]
                premium = option_row['lastPrice']
                st.write(f"Option Premium: ${premium:.2f}")
                
                # Calculate metrics
                max_loss = premium * 100
                max_profit = selected_strike * 100 if selected_strike > 0 else 0
                breakeven = selected_strike - premium
                
                st.subheader("Key Metrics")
                st.write(f"Max Loss: ${max_loss:.2f}")
                st.write(f"Max Profit: ${max_profit:.2f}")
                st.write(f"Breakeven: ${breakeven:.2f}")
            
            elif strategy_type == "Covered Call":
                # Implementation for Covered Call
                available_strikes = sorted(calls_df['strike'].unique().tolist())
                default_index = min(range(len(available_strikes)), 
                                    key=lambda i: abs(available_strikes[i] - price * 1.05))  # 5% OTM by default
                
                selected_strike = st.selectbox("Call Strike Price", available_strikes, index=default_index)
                
                option_row = calls_df[calls_df['strike'] == selected_strike].iloc[0]
                premium = option_row['lastPrice']
                st.write(f"Option Premium: ${premium:.2f}")
                
                # Calculate metrics
                max_loss = (price - premium) * 100
                max_profit = ((selected_strike - price) + premium) * 100
                breakeven = price - premium
                
                st.subheader("Key Metrics")
                st.write(f"Max Loss: ${max_loss:.2f} (if stock goes to $0)")
                st.write(f"Max Profit: ${max_profit:.2f}")
                st.write(f"Breakeven: ${breakeven:.2f}")
                
        elif strategy_category == "Spread Strategies":
            if strategy_type == "Call Spread":
                # Bull Call Spread implementation
                available_strikes = sorted(calls_df['strike'].unique().tolist())
                atm_index = min(range(len(available_strikes)), key=lambda i: abs(available_strikes[i] - price))
                
                long_strike_index = st.selectbox("Long Call Strike (Lower)", 
                                               range(len(available_strikes)),
                                               format_func=lambda i: f"${available_strikes[i]:.2f}",
                                               index=max(0, atm_index-1))
                
                short_strike_index = st.selectbox("Short Call Strike (Higher)", 
                                                range(long_strike_index+1, len(available_strikes)),
                                                format_func=lambda i: f"${available_strikes[i]:.2f}",
                                                index=min(2, len(available_strikes)-(long_strike_index+1)-1))
                
                long_strike = available_strikes[long_strike_index]
                short_strike = available_strikes[short_strike_index]
                
                # Get premiums
                long_premium = calls_df[calls_df['strike'] == long_strike].iloc[0]['lastPrice']
                short_premium = calls_df[calls_df['strike'] == short_strike].iloc[0]['lastPrice']
                
                net_debit = long_premium - short_premium
                st.write(f"Long Call Premium: ${long_premium:.2f}")
                st.write(f"Short Call Premium: ${short_premium:.2f}")
                st.write(f"Net Debit: ${net_debit:.2f}")
                
                # Calculate metrics
                max_loss = net_debit * 100
                max_profit = (short_strike - long_strike - net_debit) * 100
                breakeven = long_strike + net_debit
                
                st.subheader("Key Metrics")
                st.write(f"Max Loss: ${max_loss:.2f}")
                st.write(f"Max Profit: ${max_profit:.2f}")
                st.write(f"Breakeven: ${breakeven:.2f}")
                
        # Add similar implementation blocks for other strategy types

# Visualization and P/L analysis
with col2:
    st.header("Profit/Loss Analysis")
    
    if price and 'strategy_type' in locals():
        # Generate price range for analysis
        price_range_pct = 0.2  # 20% up and down
        min_price = price * (1 - price_range_pct)
        max_price = price * (1 + price_range_pct)
        prices = np.linspace(min_price, max_price, 100)
        
        # Calculate P/L at expiration for different strategies
        if strategy_category == "Basic Strategies":
            if strategy_type == "Long Call":
                # P/L at expiration
                payoffs = [max(0, p - selected_strike) - premium for p in prices]
                profits = [payoff * 100 for payoff in payoffs]  # Multiply by 100 for contract size
                
                # Create plot
                fig = go.Figure()
                
                # Add P/L line
                fig.add_trace(go.Scatter(
                    x=prices, 
                    y=profits,
                    mode='lines',
                    name='P/L at Expiration',
                    line=dict(color='blue', width=2)
                ))
                
                # Add breakeven line
                fig.add_shape(
                    type="line",
                    x0=breakeven, x1=breakeven,
                    y0=min(profits), y1=max(profits),
                    line=dict(color="green", width=1, dash="dash")
                )
                
                # Add current price line
                fig.add_shape(
                    type="line",
                    x0=price, x1=price,
                    y0=min(profits), y1=max(profits),
                    line=dict(color="red", width=1, dash="dash")
                )
                
                # Add strike price line
                fig.add_shape(
                    type="line",
                    x0=selected_strike, x1=selected_strike,
                    y0=min(profits), y1=max(profits),
                    line=dict(color="gray", width=1, dash="dash")
                )
                
                # Add zero line
                fig.add_shape(
                    type="line",
                    x0=min_price, x1=max_price,
                    y0=0, y1=0,
                    line=dict(color="black", width=1)
                )
                
                # Update layout
                fig.update_layout(
                    title=f"Long Call P/L at Expiration - Strike: ${selected_strike}",
                    xaxis_title="Stock Price at Expiration",
                    yaxis_title="Profit/Loss ($)",
                    hovermode="x unified",
                    legend=dict(
                        yanchor="top",
                        y=0.99,
                        xanchor="left",
                        x=0.01
                    )
                )
                
                # Add annotations
                fig.add_annotation(
                    x=breakeven,
                    y=0,
                    text="Breakeven",
                    showarrow=True,
                    arrowhead=1
                )
                
                fig.add_annotation(
                    x=price,
                    y=min(profits) * 0.8,
                    text=f"Current: ${price:.2f}",
                    showarrow=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # If we want to show P/L before expiration, we can use Black-Scholes here
                st.subheader("P/L Before Expiration")
                
                # Add time slider
                days_to_exp = (datetime.strptime(selected_expiry, "%Y-%m-%d") - datetime.now()).days
                days_remaining = st.slider("Days Remaining", 1, days_to_exp, days_to_exp)
                
                # Calculate P/L with Black-Scholes for different days to expiration
                r = 0.03  # Assuming 3% risk-free rate
                sigma = option_row.get('impliedVolatility', 0.3)
                
                # Calculate current value and P/L for each price in the range
                current_values = []
                for p in prices:
                    option_value = black_scholes("call", p, selected_strike, days_remaining/365, r, sigma)
                    current_values.append((option_value - premium) * 100)  # P/L per contract
                
                # Create second plot for current P/L
                fig2 = go.Figure()
                
                # Add current P/L line
                fig2.add_trace(go.Scatter(
                    x=prices, 
                    y=current_values,
                    mode='lines',
                    name=f'P/L at {days_remaining} days',
                    line=dict(color='purple', width=2)
                ))
                
                # Add expiration P/L for comparison
                fig2.add_trace(go.Scatter(
                    x=prices, 
                    y=profits,
                    mode='lines',
                    name='P/L at Expiration',
                    line=dict(color='blue', width=2, dash='dash')
                ))
                
                # Add zero line
                fig2.add_shape(
                    type="line",
                    x0=min_price, x1=max_price,
                    y0=0, y1=0,
                    line=dict(color="black", width=1)
                )
                
                # Add current price line
                fig2.add_shape(
                    type="line",
                    x0=price, x1=price,
                    y0=min(min(current_values), min(profits)), 
                    y1=max(max(current_values), max(profits)),
                    line=dict(color="red", width=1, dash="dash")
                )
                
                # Update layout
                fig2.update_layout(
                    title=f"Long Call P/L Before Expiration",
                    xaxis_title="Stock Price",
                    yaxis_title="Profit/Loss ($)",
                    hovermode="x unified"
                )
                
                st.plotly_chart(fig2, use_container_width=True)
                
            elif strategy_type == "Long Put":
                # Similar implementation for Long Put P/L
                payoffs = [max(0, selected_strike - p) - premium for p in prices]
                profits = [payoff * 100 for payoff in payoffs]
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=prices, y=profits, mode='lines', name='P/L at Expiration'
                ))
                
                # Add relevant lines and annotations
                # ...
                
                st.plotly_chart(fig, use_container_width=True)
                
            # Similar implementations for other strategy types
                
        elif strategy_category == "Spread Strategies":
            if strategy_type == "Call Spread":
                # Bull Call Spread P/L
                payoffs = []
                for p in prices:
                    long_payoff = max(0, p - long_strike) - long_premium
                    short_payoff = min(0, short_strike - p) + short_premium
                    payoffs.append((long_payoff + short_payoff) * 100)
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=prices, y=payoffs, mode='lines', name='P/L at Expiration'
                ))
                
                # Add relevant lines and annotations
                # ...
                
                st.plotly_chart(fig, use_container_width=True)
                
    else:
        st.info("Enter a valid ticker and select a strategy to view profit/loss analysis.")