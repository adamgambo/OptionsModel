import numpy as np
import matplotlib.pyplot as plt

# === INPUTS ===
strike_price = 100     # Strike price of the call
premium_paid = 5       # Cost to buy the call option
contract_size = 100    # Standard number of shares per contract

# === CALCULATE PAYOFF ===
stock_prices = np.linspace(80, 130, 100)
payoff = np.maximum(stock_prices - strike_price, 0) - premium_paid
payoff = payoff * contract_size

# === PLOT ===
plt.plot(stock_prices, payoff)
plt.axhline(0, color='black', linestyle='--')
plt.title("Call Option Payoff")
plt.xlabel("Stock Price at Expiration")
plt.ylabel("Profit / Loss")
plt.grid(True)
plt.show()