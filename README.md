# Options Strategy Calculator

A comprehensive Python-based web application for analyzing and visualizing options trading strategies using real-time market data.

![Options Strategy Calculator](https://via.placeholder.com/800x400?text=Options+Strategy+Calculator)

## Features

- **Live Market Data**: Fetches current stock prices and options chains from Yahoo Finance
- **Multiple Strategy Types**:
  - **Basic Strategies**: Long Call, Long Put, Covered Call, Cash Secured Put, Naked Call, Naked Put
  - **Spread Strategies**: Bull Call Spread, Bear Put Spread, Credit Spreads, Calendar Spreads, and more
  - **Advanced Strategies**: Iron Condor, Butterfly, Straddle, Strangle, and more
  - **Custom Strategies**: Build multi-leg strategies with up to 4 legs
- **Advanced Analysis**:
  - Profit/Loss payoff curves at expiration
  - Time-based P/L simulation using Black-Scholes model
  - Implied volatility sensitivity analysis
  - Risk tables and heatmaps
- **Interactive Visualization**: Dynamic charts with Plotly showing P/L across price and time
- **Export Functionality**: Save strategy data to CSV for further analysis

## Installation

### Prerequisites

- Python 3.8 or later
- pip (Python package installer)

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/options-calculator.git
   cd options-calculator
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the Streamlit application:
   ```bash
   streamlit run app.py
   ```

2. Open your web browser at http://localhost:8501

3. Enter a stock ticker and select an options strategy to analyze

4. Configure the strategy parameters (strikes, expirations, etc.)

5. View the analysis and visualizations in the right panel

## Project Structure

```
options-calculator/
├── app.py                  # Main Streamlit application
├── data_fetch.py           # Functions to fetch market data from Yahoo Finance
├── pricing.py              # Black-Scholes model and pricing calculations
├── utils.py                # Utility functions for visualizations and calculations
├── strategies/
│   ├── __init__.py
│   ├── basic_strategies.py     # Basic single-leg strategies
│   ├── spread_strategies.py    # Two-leg spread strategies
│   ├── advanced_strategies.py  # Multi-leg complex strategies
│   └── custom_strategy.py      # Custom user-defined strategy builder
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Dependencies

- `streamlit`: Web application framework
- `yfinance`: Yahoo Finance API wrapper
- `pandas`, `numpy`: Data manipulation and numerical calculations
- `scipy`: Scientific computing (for Black-Scholes model)
- `plotly`: Interactive visualizations

## Examples

### Long Call Analysis
![Long Call](https://via.placeholder.com/600x300?text=Long+Call+Analysis)

### Iron Condor
![Iron Condor](https://via.placeholder.com/600x300?text=Iron+Condor+Analysis)

### Custom Strategy
![Custom Strategy](https://via.placeholder.com/600x300?text=Custom+Strategy+Analysis)

## Limitations

- The application uses free data from Yahoo Finance, which may have limitations in terms of data frequency and availability
- The Black-Scholes model has known limitations for American options and doesn't account for early exercise
- This tool is for educational purposes only and should not be used for actual trading decisions without additional verification

## Future Improvements

- Add more strategy templates and advanced analysis tools
- Implement Greeks calculations and visualization
- Add historical backtesting capabilities
- Enhance custom strategy builder with drag-and-drop interface
- Improve visualization capabilities and export options

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This software is provided for educational and informational purposes only. Options trading involves significant risk and is not suitable for all investors. The information provided by this tool does not constitute financial advice.

---

Happy trading and analysis!
