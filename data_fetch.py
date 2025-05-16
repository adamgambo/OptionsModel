# --- data_fetch.py ---
import yfinance as yf
import streamlit as st

@st.cache_data
def get_stock_price(ticker):
    if not isinstance(ticker, str) or not ticker.strip():
        raise ValueError("Ticker must be a non-empty string.")
    stock = yf.Ticker(ticker)
    return stock.history(period="1d")["Close"].iloc[-1]

@st.cache_data
def get_option_chain(ticker, expiration):
    if not isinstance(ticker, str) or not ticker.strip():
        raise ValueError("Ticker must be a non-empty string.")
    if not expiration:
        raise ValueError("Expiration date must be provided.")
    stock = yf.Ticker(ticker)
    chain = stock.option_chain(str(expiration))
    return chain.calls, chain.puts

@st.cache_data
def get_expiration_dates(ticker):
    if not isinstance(ticker, str) or not ticker.strip():
        raise ValueError("Ticker must be a non-empty string.")
    stock = yf.Ticker(ticker)
    return stock.options