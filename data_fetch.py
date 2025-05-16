# --- data_fetch.py ---
import yfinance as yf

def get_stock_price(ticker):
    stock = yf.Ticker(ticker)
    return stock.history(period="1d")["Close"].iloc[-1]

def get_option_chain(ticker, expiration):
    stock = yf.Ticker(ticker)
    chain = stock.option_chain(str(expiration))
    return chain.calls, chain.puts