# OptionsModel

**OptionsModel** is a Python-based web application built with Streamlit that replicates and extends the functionality of [OptionsProfitCalculator.com](https://www.optionsprofitcalculator.com). It allows users to analyze the profit/loss of a wide range of options strategies — from basic single-leg trades to complex custom multi-leg strategies (up to 8 legs).

This tool is designed for options traders, students, and professionals who want a free, interactive, and educational tool to simulate and visualize various options strategies.

---

## 🚀 Features

- 📈 **Live Options Data** – Uses free Yahoo Finance data via `yfinance` (no login or API key required).
- 💼 **Supports 25+ Strategies** – Includes Long Call, Iron Condor, Covered Call, Butterfly Spread, Straddle, Calendar Spread, and more.
- 🔧 **Custom Strategy Builder** – Model up to 8 legs manually with full flexibility.
- 📊 **Profit/Loss Visualization** – Interactive Plotly charts (payoff curves, heatmaps, ROI tables).
- ⏳ **Time-Based P/L Simulation** – Black-Scholes pricing engine to model strategy behavior before expiration.
- ⚙️ **Modular Architecture** – Easily extendable strategy logic, data source, and pricing models.

---

## 🧠 Strategy Types Supported

- **Basic**: Long Call, Long Put, Covered Call, Cash Secured Put, Naked Call, Naked Put  
- **Spreads**: Credit Spread, Call Spread, Put Spread, Calendar Spread, Poor Man’s Covered Call, Ratio Back Spread  
- **Advanced**: Iron Condor, Butterfly, Collar, Diagonal Spread, Double Diagonal, Straddle, Strangle, Covered Strangle, Synthetic Put, Reverse Conversion  
- **Custom**: 2 to 8 configurable legs

---

## 📁 Project Structure

```bash
optionsmodel/
├── app.py                  # Streamlit frontend application
├── data_fetch.py           # Retrieves live stock and options data using yfinance
├── pricing.py              # Black-Scholes model and P/L engine
├── strategies/
│   ├── __init__.py
│   ├── basic_strategies.py
│   ├── spread_strategies.py
│   ├── advanced_strategies.py
│   └── custom_strategy.py
├── utils.py                # Caching, formatting, and helper utilities
├── requirements.txt        # List of dependencies
└── README.md
