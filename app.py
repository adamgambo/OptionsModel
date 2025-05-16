# --- app.py ---
import streamlit as st
from data_fetch import get_stock_price, get_option_chain
from strategies.basic_strategies import long_call_strategy

st.title("Options Strategy Calculator")

ticker = st.text_input("Enter Stock Ticker", value="AAPL")
if ticker:
    price = get_stock_price(ticker)
    st.write(f"Current Price: ${price:.2f}")

# Example input for long call strategy
strike = st.number_input("Strike Price", value=price)
premium = st.number_input("Premium", value=1.0)
expiration = st.date_input("Expiration Date")

if st.button("Calculate Long Call"):
    legs = long_call_strategy(strike, expiration, premium)
    st.write("Strategy Legs:", legs)