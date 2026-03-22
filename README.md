# Options Strategy Calculator

A comprehensive Python web application for analysing and visualising options trading strategies using real-time market data.

![Version](https://img.shields.io/badge/version-2.5.0-blue)
![Python](https://img.shields.io/badge/Python-3.12+-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.45+-red)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

## Features

- **28 Built-in Strategies**
  - **Basic**: Long Call, Long Put, Covered Call, Cash Secured Put, Naked Call, Naked Put
  - **Spreads**: Bull Call/Put, Bear Call/Put, Calendar, Poor Man's Covered Call, Ratio Backspread, Synthetic Long/Short, Call/Put Ratio Spread
  - **Advanced**: Iron Condor, Iron Butterfly, Butterfly, Straddle, Strangle, Strip, Strap, Collar, Diagonal, Double Diagonal, Jade Lizard
  - **Custom**: Build multi-leg strategies with up to 4 legs (calls, puts, stock)

- **Live Market Data**
  - Real-time stock prices and option chains via Yahoo Finance
  - Volume, open interest, implied volatility, bid/ask spreads
  - Company fundamentals: sector, market cap, 52-week range

- **Analysis Tabs**
  - **Payoff Diagram** — interactive P/L curve at expiration with breakeven markers
  - **Risk Analysis** — heatmap of P/L across price × time dimensions
  - **Time Decay** — how theta erodes strategy value over days to expiration
  - **Greeks** — Delta, Gamma, Theta, Vega per leg and portfolio total
  - **Position Analysis** — unrealised P/L tracking with CSV export
  - **IV Analysis** — implied volatility smile/skew chart and historical vs implied volatility comparison

- **Pricing Models**
  - Black-Scholes-Merton (continuous dividend yield)
  - Binomial tree (CRR, American options, vectorised)
  - Monte Carlo simulation with antithetic variates for variance reduction

- **UI**
  - Light and dark mode themes
  - Responsive layout with mobile-optimised views
  - Cached API responses for fast repeat analysis

## Installation

### Prerequisites

- Python 3.12+
- pip

### Setup

```bash
git clone https://github.com/adamgambo/OptionsModel.git
cd OptionsModel

python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

## Usage

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

1. Enter a stock ticker in the sidebar (e.g. `AAPL`, `SPY`, `TSLA`)
2. Select an expiration date and options strategy
3. Configure strikes and parameters
4. Explore the analysis tabs

## Project Structure

```
OptionsModel/
├── app.py                      # Main Streamlit application
├── config.py                   # App version, strategy metadata, constants
├── data_fetch.py               # Yahoo Finance data fetching + historical volatility
├── pricing.py                  # Black-Scholes, binomial tree, Monte Carlo, Greeks, IV solver
├── utils.py                    # Plotly chart builders, IV smile/skew, HV vs IV charts
├── requirements.txt            # Python dependencies
├── styles/
│   └── main.css                # Custom CSS (light + dark mode)
├── assets/                     # Static assets
└── strategies/
    ├── __init__.py
    ├── basic_strategies.py     # Single-leg strategies
    ├── spread_strategies.py    # Two-leg spread strategies
    ├── advanced_strategies.py  # Multi-leg complex strategies
    ├── custom_strategy.py      # User-defined strategy builder
    └── strategies_factory.py   # Factory pattern for strategy creation
```

## Key Components

### Pricing (`pricing.py`)
- **Black-Scholes-Merton**: European options with continuous dividend yield `q`
- **Binomial tree (CRR)**: American options with early exercise, fully vectorised inner loop
- **Monte Carlo**: Antithetic variates for variance reduction, numpy-vectorised across all paths and steps simultaneously
- **Implied Volatility**: Newton-Raphson solver with Brenner-Subrahmanyam initial guess
- **Greeks**: Delta, Gamma, Theta, Vega, Rho via closed-form BSM partial derivatives

### Data Fetching (`data_fetch.py`)
- Multi-key fallback for yfinance price fields (`currentPrice` → `regularMarketPrice` → `price` → `previousClose`)
- Historical volatility: 21-day rolling annualised HV cached for 5 minutes
- Option chain caching with `@st.cache_data(ttl=300)`

### Strategy Factory (`strategies/strategies_factory.py`)
- Single `create_strategy(strategy_type, **kwargs)` entry point
- All 28 strategies registered; raises `ValueError` for unknown types
- Each strategy returns a list of leg dictionaries with `option_type`, `action`, `strike`, `expiration`, `premium`, `quantity`

### IV Analysis (`utils.py`)
- `create_iv_smile_chart`: IV vs strike for calls and puts with current price reference
- `create_hv_vs_iv_chart`: Rolling 21-day HV vs average IV with ratio metrics

## Dependencies

| Package | Min Version | Purpose |
|---------|-------------|---------|
| streamlit | 1.45.0 | Web application framework |
| pandas | 2.2.0 | Data manipulation |
| numpy | 2.2.0 | Numerical computing |
| scipy | 1.15.0 | Scientific computing |
| yfinance | 0.2.61 | Yahoo Finance API wrapper |
| requests | 2.32.0 | HTTP client |
| plotly | 6.1.0 | Interactive visualisations |

## Disclaimer

This software is provided for **educational and informational purposes only**. Options trading involves significant risk and is not suitable for all investors. Nothing in this tool constitutes financial advice.

---

*Options Strategy Calculator v2.5.0*
