# Options Strategy Calculator

A comprehensive Python-based web application for analysing and visualising options trading strategies using real-time market data.

![Options Strategy Calculator](https://img.shields.io/badge/Options-Strategy_Calculator-blue)
![Python Version](https://img.shields.io/badge/Python-3.8+-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-red)

## Features

- **Enhanced UI/UX**:
  - Responsive design with light/dark mode themes
  - Interactive charting and data visualisation
  - Mobile-optimised views for on-the-go analysis
  
- **Live Market Data**: 
  - Fetches current stock prices and options chains from Yahoo Finance
  - Display of key market metrics including volume, open interest, and implied volatility
  - Real-time stock information with sector and market cap data
  
- **Multiple Strategy Types**:
  - **Basic Strategies**: Long Call, Long Put, Covered Call, Cash Secured Put, Naked Call, Naked Put
  - **Spread Strategies**: Bull Call Spread, Bear Put Spread, Credit Spreads, Calendar Spreads, and more
  - **Advanced Strategies**: Iron Condor, Butterfly, Straddle, Strangle, Collar, and more
  - **Custom Strategies**: Build multi-leg strategies with up to 4 legs
  
- **Advanced Analysis**:
  - Interactive profit/loss payoff curves at expiration
  - Time-based P/L simulation using Black-Scholes model
  - Greeks calculation (Delta, Gamma, Theta, Vega)
  - Risk heatmaps showing P/L across price and time dimensions
  - Position analysis with unrealised P/L tracking
  - Probability analysis with price distribution visualisation
  
- **Educational Resources**:
  - Built-in strategy information and explanations
  - Risk/reward metrics for each strategy
  - Breakeven calculations and visualisation
  
- **Performance Optimisations**:
  - Caching of API responses for faster repeat analysis
  - Efficient data processing for real-time calculations
  - Responsive design for all device sizes

## Installation

### Prerequisites

- Python 3.8 or later
- pip (Python package installer)

### Setup

1. Clone this repository:

    ```
    git clone https://github.com/yourusername/options-calculator.git
    cd options-calculator
    ```

2. Create a virtual environment (recommended):

    ```
    python -m venv .venv
    
    # On Windows
    .venv\Scripts\activate
    
    # On macOS/Linux
    source .venv/bin/activate
    ```

3. Install required packages:

    ```
    pip install -r requirements.txt
    ```

## Usage

1. Start the Streamlit application:

    ```
    streamlit run app.py
    ```

2. Open your web browser at http://localhost:8501

3. Enter a stock ticker in the sidebar and select an options strategy to analyse

4. Configure the strategy parameters (strikes, expirations, etc.)

5. View the analysis and visualisations in the main panel

## Project Structure

```
options-calculator/
├── app.py                      # Main Streamlit application
├── config.py                   # Configuration settings and constants
├── data_fetch.py               # Functions to fetch market data from Yahoo Finance
├── pricing.py                  # Black-Scholes model and pricing calculations
├── utils.py                    # Utility functions for visualisations and calculations
├── requirements.txt            # Python dependencies
├── styles/
│   └── main.css                # Custom CSS styling
├── assets/                     # Static assets like logos
├── strategies/
│   ├── __init__.py
│   ├── basic_strategies.py     # Basic single-leg strategies
│   ├── spread_strategies.py    # Two-leg spread strategies
│   ├── advanced_strategies.py  # Multi-leg complex strategies
│   ├── custom_strategy.py      # Custom user-defined strategy builder
│   └── strategies_factory.py   # Factory pattern for strategy creation
└── README.md                   # This file
```

## Key Components

### Data Fetching
The application uses Yahoo Finance API via the `yfinance` library to fetch real-time stock data, options chains, and company information. All data operations include robust error handling and caching to ensure reliability and performance.

### Strategy Implementation
Strategies are implemented using a factory pattern, making it easy to add new strategy types. Each strategy is defined by its "legs" (individual options or stock positions) and is analysed using mathematical models.

### Pricing Models
The application implements several options pricing models:
- Black-Scholes model for European options
- Binomial tree model for American options
- Monte Carlo simulation for complex scenarios

### Visualisation
The app provides multiple visualisation types:
- Interactive payoff diagrams with Plotly
- Risk heatmaps showing P/L across price and time
- Greeks analysis for understanding option sensitivity
- Probability distribution charts

## Dependencies

- `streamlit`: Web application framework
- `yfinance`: Yahoo Finance API wrapper
- `pandas`, `numpy`: Data manipulation and numerical calculations
- `scipy`: Scientific computing (for Black-Scholes model)
- `plotly`: Interactive visualisations

## Example Strategy Visualisations

### Long Call Analysis
The application provides interactive payoff curves showing profit/loss at different stock prices. For a Long Call strategy, you'll see how your position's value changes as the underlying stock price moves, with clearly marked breakeven points and current price reference lines.

### Iron Condor
For complex strategies like an Iron Condor, the visualisation shows the characteristic "profit range" in the middle with defined maximum profit and loss boundaries. The heatmap view illustrates how the strategy's P/L profile changes as time passes, helping visualise time decay effects.

### Position Analysis
The Position Analysis tab shows unrealised P/L for each leg of your strategy, allowing you to track performance. It also provides "what-if" analysis comparing your current position with entering the same position at current market prices.

## Advanced Features

### Greeks Calculation
For option strategies, the application calculates and displays the Greeks:
- **Delta**: Sensitivity to underlying price changes
- **Gamma**: Rate of change of Delta
- **Theta**: Time decay
- **Vega**: Sensitivity to volatility changes

### Probability Analysis
The application provides probability metrics based on log-normal price distribution, including:
- Probability of profit at expiration
- Probability of reaching various price points
- Visualisation of the price probability distribution

### Custom Strategy Builder
Build complex multi-leg strategies with up to 4 legs, mixing calls, puts, and stock positions with different strikes, expirations, and positions (long/short).

## Limitations

- The application uses free data from Yahoo Finance, which may have limitations in terms of data frequency and availability
- The Black-Scholes model has known limitations for American options and doesn't account for early exercise
- The application does not account for dividends in pricing models (planned for future versions)
- This tool is for educational purposes only and should not be used for actual trading decisions without additional verification

## Future Improvements

- Add historical backtesting capabilities
- Implement more advanced pricing models including dividend considerations
- Add portfolio analysis for multiple strategies
- Enhance mobile experience with dedicated layouts
- Add export functionality for strategies and analysis
- Implement user accounts to save favourite strategies
- Add more educational content and strategy examples

## Disclaimer

This software is provided for educational and informational purposes only. Options trading involves significant risk and is not suitable for all investors. The information provided by this tool does not constitute financial advice.

---

Happy trading and analysis!
