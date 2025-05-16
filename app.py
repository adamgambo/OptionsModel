# --- app.py ---
import streamlit as st
from data_fetch import get_stock_price, get_option_chain
from strategies.basic_strategies import long_call_strategy
from strategies.spread_strategies import credit_spread, call_spread_strategy, put_spread_strategy, calendar_spread, ratio_backspread, poor_mans_covered_call
from strategies.advanced_strategies import iron_condor_strategy, butterfly_strategy, collar_strategy, diagonal_spread_strategy, double_diagonal_strategy, straddle_strategy, strangle_strategy, covered_strangle_strategy, synthetic_put_strategy, reverse_conversion_strategy
from strategies.custom_strategy import custom_strategy

st.title("Options Strategy Calculator")

ticker = st.text_input("Enter Stock Ticker", value="AAPL")
if ticker:
    price = get_stock_price(ticker)
    st.write(f"Current Price: ${price:.2f}")

strategy_type = st.selectbox("Select Strategy", [
    "Basic – Long Call",
    "Spreads – Credit Spread",
    "Spreads – Call Spread",
    "Spreads – Put Spread",
    "Spreads – Calendar Spread",
    "Spreads – Ratio Back Spread",
    "Spreads – Poor Man's Covered Call",
    "Advanced – Iron Condor",
    "Advanced – Butterfly",
    "Advanced – Collar",
    "Advanced – Diagonal Spread",
    "Advanced – Double Diagonal",
    "Advanced – Straddle",
    "Advanced – Strangle",
    "Advanced – Covered Strangle",
    "Advanced – Synthetic Put",
    "Advanced – Reverse Conversion",
    "Custom – 2 Legs",
    "Custom – 3 Legs",
    "Custom – 4 Legs",
    "Custom – 5 Legs",
    "Custom – 6 Legs",
    "Custom – 8 Legs"
])

# Placeholder routing logic for strategy selection
if strategy_type == "Basic – Long Call":
    strike = st.number_input("Strike Price", value=price)
    premium = st.number_input("Premium", value=1.0)
    expiration = st.date_input("Expiration Date")
    if st.button("Calculate Long Call"):
        legs = long_call_strategy(strike, expiration, premium)
        st.write("Strategy Legs:", legs)

elif strategy_type.startswith("Spreads"):
    st.info("Spread strategy input form will go here.")

elif strategy_type.startswith("Advanced"):
    st.info("Advanced strategy input form will go here.")

elif strategy_type.startswith("Custom"):
    st.info("Custom strategy leg builder will go here.")