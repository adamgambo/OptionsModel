# --- utils.py ---
"""
Utility functions for the Options Strategy Calculator.
Includes functions for calculations, visualizations, and formatting.
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import streamlit as st
import logging
from pricing import black_scholes, calculate_greeks

# Setup logging
logger = logging.getLogger(__name__)

def get_chart_theme():
    """Get the current chart theme based on session state."""
    theme = st.session_state.get('theme', 'light')
    
    if theme == 'dark':
        return {
            'template': 'plotly_dark',
            'paper_bgcolor': '#121212',
            'plot_bgcolor': '#1E1E1E',
            'font_color': '#E0E0E0',
            'grid_color': '#333333'
        }
    else:
        return {
            'template': 'plotly_white',
            'paper_bgcolor': '#FFFFFF',
            'plot_bgcolor': '#FFFFFF',
            'font_color': '#212121',
            'grid_color': '#E0E0E0'
        }

def apply_chart_theme(fig):
    """Apply the current theme to a plotly figure."""
    theme_config = get_chart_theme()
    
    fig.update_layout(
        template=theme_config['template'],
        paper_bgcolor=theme_config['paper_bgcolor'],
        plot_bgcolor=theme_config['plot_bgcolor'],
        font=dict(color=theme_config['font_color']),
        xaxis=dict(gridcolor=theme_config['grid_color']),
        yaxis=dict(gridcolor=theme_config['grid_color'])
    )
    
    return fig

def annualized_days(expiration_date, current_date=None):
    """
    Convert days to expiration to annualized fraction.
    
    Parameters:
        expiration_date (str|date): Expiration date
        current_date (date): Current date (defaults to today)
        
    Returns:
        float: Time to expiration in years
    """
    if current_date is None:
        current_date = datetime.now().date()
    if isinstance(expiration_date, str):
        expiration_date = datetime.strptime(expiration_date, "%Y-%m-%d").date()
    delta = (expiration_date - current_date).days
    return max(delta, 0) / 365  # Ensure non-negative value

def format_price(price, prefix="$", decimals=2):
    """
    Format price with currency symbol and fixed decimals.
    
    Parameters:
        price (float): Price to format
        prefix (str): Currency symbol
        decimals (int): Number of decimal places
        
    Returns:
        str: Formatted price string
    """
    if price is None:
        return "N/A"
    if isinstance(price, str):
        return price
    return f"{prefix}{price:.{decimals}f}"

def format_percent(value, decimals=2):
    """
    Format value as percentage.
    
    Parameters:
        value (float): Value to format (in decimal form)
        decimals (int): Number of decimal places
        
    Returns:
        str: Formatted percentage string
    """
    if value is None:
        return "N/A"
    return f"{value * 100:.{decimals}f}%"

def calculate_strategy_payoff(strategy_legs, price_range, current_price=None):
    """
    Calculate the payoff of a strategy over a range of prices at expiration.
    Uses entry prices for P/L calculations.
    
    Parameters:
        strategy_legs (list): List of leg dictionaries with type, position, strike, etc.
        price_range (array): Array of prices to calculate payoff for
        current_price (float): Current stock price (for reference)
        
    Returns:
        array: Payoff values for each price in price_range
    """
    # Convert price_range to numpy array if it's not already
    price_range = np.array(price_range)
    
    # Initialize payoffs array with zeros
    payoffs = np.zeros(len(price_range))
    
    # Validate strategy_legs
    if not strategy_legs or not isinstance(strategy_legs, list):
        logger.warning("Invalid strategy_legs provided to calculate_strategy_payoff")
        return payoffs
    
    # Calculate payoff for each leg
    for leg in strategy_legs:
        # Validate leg format
        if not isinstance(leg, dict):
            logger.warning(f"Invalid leg format in calculate_strategy_payoff: {leg}")
            continue
        
        # Extract leg parameters with defaults for missing values
        leg_type = leg.get('type', '')
        position = leg.get('position', '')
        strike = leg.get('strike', 0)
        premium = leg.get('price', 0)
        quantity = leg.get('quantity', 1)
        
        # Skip invalid legs
        if not leg_type or not position:
            continue
        
        # Determine position sign
        sign = 1 if position == 'long' else -1
        
        # Calculate payoff based on leg type
        if leg_type == 'call':
            # Call payoff at expiration: max(0, stock_price - strike) - premium
            leg_payoffs = np.maximum(0, price_range - strike) - premium
            payoffs += sign * leg_payoffs * quantity
            
        elif leg_type == 'put':
            # Put payoff at expiration: max(0, strike - stock_price) - premium
            leg_payoffs = np.maximum(0, strike - price_range) - premium
            payoffs += sign * leg_payoffs * quantity
            
        elif leg_type == 'stock':
            # Stock payoff: (current_price - purchase_price)
            purchase_price = leg.get('price', current_price or 0)
            leg_payoffs = price_range - purchase_price
            payoffs += sign * leg_payoffs * quantity
    
    # Multiply by contract size (100 shares per contract) for options
    return payoffs * 100

def calculate_strategy_current_value(strategy_legs, price_range, days_to_expiry, 
                                    risk_free_rate=0.03, volatility=0.3):
    """
    Calculate the current value of a strategy over a range of prices before expiration.
    Uses current_price for market value calculations and price for cost basis.
    
    Parameters:
        strategy_legs (list): List of leg dictionaries with type, position, strike, etc.
        price_range (array): Array of prices to calculate value for
        days_to_expiry (int): Days remaining until expiration
        risk_free_rate (float): Annualized risk-free interest rate
        volatility (float): Implied volatility if not specified in legs
        
    Returns:
        array: Current values for each price in price_range
    """
    # Convert price_range to numpy array if it's not already
    price_range = np.array(price_range)
    
    # Initialize values array with zeros
    values = np.zeros(len(price_range))
    
    # Convert days to years
    years_to_expiry = max(days_to_expiry, 0) / 365
    
    # Validate strategy_legs
    if not strategy_legs or not isinstance(strategy_legs, list):
        logger.warning("Invalid strategy_legs provided to calculate_strategy_current_value")
        return values
    
    # Calculate value for each leg
    for leg in strategy_legs:
        # Validate leg format
        if not isinstance(leg, dict):
            logger.warning(f"Invalid leg format in calculate_strategy_current_value: {leg}")
            continue
        
        # Extract leg parameters with defaults for missing values
        leg_type = leg.get('type', '')
        position = leg.get('position', '')
        strike = leg.get('strike', 0)
        entry_premium = leg.get('price', 0)
        current_premium = leg.get('current_price', entry_premium)
        quantity = leg.get('quantity', 1)
        leg_iv = leg.get('iv', volatility)
        
        # Skip invalid legs
        if not leg_type or not position:
            continue
        
        # Determine position sign
        sign = 1 if position == 'long' else -1
        
        # Calculate current value based on leg type
        if leg_type in ['call', 'put']:
            # For option legs, calculate theoretical value at each price point
            for i, price in enumerate(price_range):
                if years_to_expiry <= 0:
                    # At or past expiration, use intrinsic value
                    if leg_type == 'call':
                        option_value = max(0, price - strike)
                    else:  # put
                        option_value = max(0, strike - price)
                else:
                    # Before expiration, use Black-Scholes
                    option_value = black_scholes(
                        leg_type, price, strike, years_to_expiry, risk_free_rate, leg_iv
                    )
                
                # Calculate unrealized P/L: current theoretical value - entry price
                unrealized_pl = option_value - entry_premium
                values[i] += sign * unrealized_pl * quantity
                
        elif leg_type == 'stock':
            # Stock value: current_price - purchase_price
            purchase_price = leg.get('price', price_range[0])
            values += sign * (price_range - purchase_price) * quantity
    
    # Multiply by contract size (100 shares per contract) for options
    return values * 100

def create_unrealized_pl_table(strategy_legs, current_price):
    """
    Create a table showing unrealized P/L for each leg of the strategy.
    
    Parameters:
        strategy_legs (list): List of leg dictionaries
        current_price (float): Current stock price
        
    Returns:
        pd.DataFrame: DataFrame with unrealized P/L analysis
    """
    # Validate inputs
    if not strategy_legs or not isinstance(strategy_legs, list):
        logger.warning("Invalid strategy_legs provided to create_unrealized_pl_table")
        return pd.DataFrame()
    
    if current_price is None or not isinstance(current_price, (int, float)):
        logger.warning(f"Invalid current_price provided to create_unrealized_pl_table: {current_price}")
        current_price = 0
    
    # Create DataFrame
    pl_data = []
    
    total_entry_cost = 0
    total_current_value = 0
    
    # Process each leg
    for i, leg in enumerate(strategy_legs):
        # Skip invalid legs
        if not isinstance(leg, dict):
            continue
        
        # Extract leg parameters
        leg_type = leg.get('type', '')
        position = leg.get('position', '')
        quantity = leg.get('quantity', 1)
        
        # Skip invalid legs
        if not leg_type or not position:
            continue
        
        # Get prices
        entry_price = leg.get('price', 0)
        current_market_price = leg.get('current_price', entry_price)
        
        # Calculate contract multiplier
        multiplier = 100 if leg_type in ['call', 'put'] else 1
        
        # Calculate leg costs/values
        if position == 'long':
            entry_cost = entry_price * quantity * multiplier
            current_value = current_market_price * quantity * multiplier
            sign = 1
        else:  # short
            entry_cost = -entry_price * quantity * multiplier
            current_value = -current_market_price * quantity * multiplier
            sign = -1
        
        # Calculate P/L
        unrealized_pl = current_value - entry_cost
        
        # Format type and position
        if leg_type == 'call':
            desc = f"{position.capitalize()} Call"
            if 'strike' in leg:
                desc += f" @ ${leg['strike']:.2f}"
        elif leg_type == 'put':
            desc = f"{position.capitalize()} Put"
            if 'strike' in leg:
                desc += f" @ ${leg['strike']:.2f}"
        else:  # stock
            desc = f"{position.capitalize()} Stock"
        
        # Add expiration date if available
        if 'expiry' in leg and leg.get('expiry'):
            desc += f" ({leg['expiry']})"
        
        # Add to data
        pl_data.append({
            'Leg': f"Leg {i+1}",
            'Description': desc,
            'Entry Price': f"${entry_price:.2f}",
            'Current Price': f"${current_market_price:.2f}",
            'Unrealized P/L': f"${unrealized_pl:.2f}",
            'P/L %': f"{(unrealized_pl/abs(entry_cost))*100:.1f}%" if entry_cost != 0 else "N/A"
        })
        
        # Update totals
        total_entry_cost += entry_cost
        total_current_value += current_value
    
    # Add total row
    total_pl = total_current_value - total_entry_cost
    if pl_data:  # Only add total if there are valid legs
        pl_data.append({
            'Leg': "Total",
            'Description': "All Legs",
            'Entry Price': f"${abs(total_entry_cost):.2f}",
            'Current Price': f"${abs(total_current_value):.2f}",
            'Unrealized P/L': f"${total_pl:.2f}",
            'P/L %': f"{(total_pl/abs(total_entry_cost))*100:.1f}%" if total_entry_cost != 0 else "N/A"
        })
    
    return pd.DataFrame(pl_data)

def create_payoff_chart(strategy_name, strategy_legs, current_price, price_range=None, 
                       days_to_expiry=None, show_current_value=True):
    """
    Create an interactive plotly payoff chart for an options strategy.
    
    Parameters:
        strategy_name (str): Name of the strategy for the chart title
        strategy_legs (list): List of leg dictionaries
        current_price (float): Current stock price
        price_range (array): Optional price range, or will be generated based on current_price
        days_to_expiry (int): Days to expiration, for calculating current value
        show_current_value (bool): Whether to show current value line in addition to expiration
        
    Returns:
        go.Figure: Plotly figure object
    """
    # Validate inputs
    if not strategy_legs or not isinstance(strategy_legs, list):
        logger.warning("Invalid strategy_legs provided to create_payoff_chart")
        return go.Figure()
    
    if current_price is None or not isinstance(current_price, (int, float)):
        logger.warning(f"Invalid current_price provided to create_payoff_chart: {current_price}")
        current_price = 100  # Default value
    
    # Generate price range if not provided
    if price_range is None:
        price_range_pct = 0.3  # 30% up and down from current price
        min_price = current_price * (1 - price_range_pct)
        max_price = current_price * (1 + price_range_pct)
        price_range = np.linspace(min_price, max_price, 100)
    
    # Calculate payoff at expiration
    payoffs = calculate_strategy_payoff(strategy_legs, price_range, current_price)
    
    # Create figure
    fig = go.Figure()
    
    # Add P/L at expiration
    fig.add_trace(go.Scatter(
        x=price_range, 
        y=payoffs,
        mode='lines',
        name='P/L at Expiration',
        line=dict(color='#1f77b4', width=2)
    ))
    
    # Add current value line if days_to_expiry is provided and we're before expiration
    if show_current_value and days_to_expiry is not None and days_to_expiry > 0:
        # Get average implied volatility from legs
        ivs = [leg.get('iv', 0.3) for leg in strategy_legs 
              if leg.get('type') in ('call', 'put') and 'iv' in leg]
        avg_iv = sum(ivs) / len(ivs) if ivs else 0.3
        
        current_values = calculate_strategy_current_value(
            strategy_legs, price_range, days_to_expiry, volatility=avg_iv
        )
        
        fig.add_trace(go.Scatter(
            x=price_range, 
            y=current_values,
            mode='lines',
            name=f'Current Value (T-{days_to_expiry})',
            line=dict(color='#2ca02c', width=2, dash='dash')
        ))
    
    # Add zero line
    fig.add_shape(
        type="line",
        x0=min(price_range), x1=max(price_range),
        y0=0, y1=0,
        line=dict(color="gray", width=1)
    )
    
    # Add current price line
    fig.add_shape(
        type="line",
        x0=current_price, x1=current_price,
        y0=min(min(payoffs), 0) * 1.1, 
        y1=max(max(payoffs), 0) * 1.1,
        line=dict(color="#d62728", width=1, dash="dash")
    )
    
    # Find breakeven points (where the expiration P/L crosses zero)
    breakeven_points = find_breakeven_points(price_range, payoffs)
    
    # Add breakeven annotations
    for i, be in enumerate(breakeven_points):
        fig.add_shape(
            type="line",
            x0=be, x1=be,
            y0=min(min(payoffs), 0) * 1.1, 
            y1=max(max(payoffs), 0) * 1.1,
            line=dict(color="green", width=1, dash="dash")
        )
        
        fig.add_annotation(
            x=be,
            y=0,
            text=f"BE: ${be:.2f}",
            showarrow=True,
            arrowhead=1
        )
    
    # Add key metrics to figure
    max_profit = max(payoffs)
    max_loss = min(payoffs)
    
    metrics_text = (
        f"Max Profit: ${max_profit:.2f}<br>"
        f"Max Loss: ${max_loss:.2f}<br>"
    )
    
    if breakeven_points:
        metrics_text += "Breakeven: " + ", ".join([f"${be:.2f}" for be in breakeven_points])
    
    # Get theme colors for annotation background
    theme_config = get_chart_theme()
    
    fig.add_annotation(
        x=min(price_range) + (max(price_range) - min(price_range)) * 0.05,
        y=max(max(payoffs), 0) * 0.9,
        text=metrics_text,
        showarrow=False,
        align="left",
        bgcolor=theme_config['paper_bgcolor'],
        bordercolor=theme_config['font_color'],
        borderwidth=1,
        font=dict(color=theme_config['font_color'])
    )
    
    # Update layout
    fig.update_layout(
        title=f"{strategy_name} Profit/Loss Analysis",
        xaxis_title="Stock Price",
        yaxis_title="Profit/Loss ($)",
        hovermode="x unified",
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    # Apply theme
    fig = apply_chart_theme(fig)
    
    return fig

def find_breakeven_points(price_range, payoffs):
    """
    Find breakeven points in a strategy (where payoff crosses zero).
    
    Parameters:
        price_range (array): Array of prices
        payoffs (array): Array of payoff values corresponding to prices
        
    Returns:
        list: List of breakeven prices
    """
    breakeven_points = []
    
    # Validate inputs
    if len(price_range) != len(payoffs) or len(price_range) < 2:
        return breakeven_points
    
    # Find zero crossings
    for i in range(1, len(price_range)):
        if (payoffs[i-1] <= 0 and payoffs[i] > 0) or (payoffs[i-1] >= 0 and payoffs[i] < 0):
            # Linear interpolation to find more precise breakeven
            x0, y0 = price_range[i-1], payoffs[i-1]
            x1, y1 = price_range[i], payoffs[i]
            
            if y1 - y0 != 0:  # Avoid division by zero
                breakeven = x0 + (x1 - x0) * (-y0) / (y1 - y0)
                breakeven_points.append(breakeven)
    
    return breakeven_points

def create_heatmap(strategy_legs, current_price, expiry_date, risk_free_rate=0.03, volatility=0.3):
    """
    Create a heatmap showing strategy PnL over different price points and days to expiry.
    
    Parameters:
        strategy_legs (list): List of leg dictionaries
        current_price (float): Current stock price  
        expiry_date (datetime|str): Expiration date
        risk_free_rate (float): Annualized risk-free interest rate
        volatility (float): Implied volatility
        
    Returns:
        go.Figure: Plotly figure object with heatmap
    """
    # Validate inputs
    if not strategy_legs or not isinstance(strategy_legs, list):
        logger.warning("Invalid strategy_legs provided to create_heatmap")
        return go.Figure()
    
    if current_price is None or not isinstance(current_price, (int, float)):
        logger.warning(f"Invalid current_price provided to create_heatmap: {current_price}")
        current_price = 100  # Default value
    
    # Generate price range
    price_range_pct = 0.3  # 30% up and down
    min_price = current_price * (1 - price_range_pct)
    max_price = current_price * (1 + price_range_pct)
    prices = np.linspace(min_price, max_price, 30)
    
    # Handle expiry date
    current_date = datetime.now().date()
    if isinstance(expiry_date, str):
        try:
            expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d").date()
        except ValueError:
            logger.warning(f"Invalid expiry_date format: {expiry_date}")
            expiry_date = current_date + timedelta(days=30)  # Default to 30 days
    
    total_days = (expiry_date - current_date).days
    if total_days < 0:
        logger.warning("Expiry date is in the past")
        total_days = 0
    
    # Create days array from now to expiry
    if total_days <= 1:
        days = np.array([0])  # Just show expiration if almost expired
    elif total_days <= 7:
        days = np.array(list(range(0, total_days + 1)))  # Daily for short-term
    else:
        # Sample days more sparsely for longer periods
        day_points = min(15, total_days)  # Max 15 time points
        days = np.linspace(0, total_days, day_points).astype(int)
        days = np.unique(days)  # Remove duplicates
    
    # Create arrays to hold values
    z = np.zeros((len(days), len(prices)))
    
    # Calculate PnL for each price and day combination
    for i, day in enumerate(days):
        days_to_expiry = total_days - day
        
        if days_to_expiry == 0:  # At expiration
            z[i, :] = calculate_strategy_payoff(strategy_legs, prices, current_price)
        else:  # Before expiration
            # Get average implied volatility from legs
            ivs = [leg.get('iv', volatility) for leg in strategy_legs 
                  if leg.get('type') in ('call', 'put') and 'iv' in leg]
            avg_iv = sum(ivs) / len(ivs) if ivs else volatility
            
            z[i, :] = calculate_strategy_current_value(
                strategy_legs, prices, days_to_expiry, risk_free_rate, avg_iv
            )
    
    # Create the heatmap figure
    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=prices,
        y=days,
        colorscale='RdBu',
        zmid=0,  # Center colorscale at zero
        colorbar=dict(title='P/L ($)'),
    ))
    
    # Add current price line
    fig.add_shape(
        type="line",
        x0=current_price, x1=current_price,
        y0=min(days), y1=max(days),
        line=dict(color="yellow", width=2, dash="dash")
    )
    
    # Update layout
    fig.update_layout(
        title="P/L Heatmap: Price vs Days Until Expiration",
        xaxis_title="Stock Price",
        yaxis_title="Days to Expiration",
        xaxis=dict(
            tickformat="$.2f"
        )
    )
    
    # Apply theme
    fig = apply_chart_theme(fig)
    
    return fig

def create_risk_table(strategy_legs, current_price, days_to_expiry, volatility=0.3):
    """
    Create a table showing potential P/L at different price points.
    
    Parameters:
        strategy_legs (list): List of leg dictionaries
        current_price (float): Current stock price
        days_to_expiry (int): Days to expiration
        volatility (float): Implied volatility
        
    Returns:
        pd.DataFrame: DataFrame with risk analysis
    """
    # Validate inputs
    if not strategy_legs or not isinstance(strategy_legs, list):
        logger.warning("Invalid strategy_legs provided to create_risk_table")
        return pd.DataFrame()
    
    if current_price is None or not isinstance(current_price, (int, float)):
        logger.warning(f"Invalid current_price provided to create_risk_table: {current_price}")
        current_price = 100  # Default value
    
    # Generate price points: -30%, -20%, -10%, -5%, current, +5%, +10%, +20%, +30%
    change_pcts = [-0.3, -0.2, -0.1, -0.05, 0, 0.05, 0.1, 0.2, 0.3]
    prices = [current_price * (1 + pct) for pct in change_pcts]
    
    # Format price for column names
    price_labels = [f"{pct:+.0%}" for pct in change_pcts]
    
    # Create DataFrame
    df = pd.DataFrame(index=["At Expiration"])
    
    # Calculate payoff at expiration
    expiry_payoffs = calculate_strategy_payoff(strategy_legs, prices, current_price)
    df.loc["At Expiration"] = [f"${p:.2f}" for p in expiry_payoffs]
    
    # Calculate current value if days_to_expiry > 0
    if days_to_expiry > 0:
        # Get average implied volatility from legs
        ivs = [leg.get('iv', volatility) for leg in strategy_legs 
              if leg.get('type') in ('call', 'put') and 'iv' in leg]
        avg_iv = sum(ivs) / len(ivs) if ivs else volatility
        
        current_values = calculate_strategy_current_value(
            strategy_legs, prices, days_to_expiry, volatility=avg_iv
        )
        df.loc[f"Current (T-{days_to_expiry})"] = [f"${p:.2f}" for p in current_values]
    
    # Set column names
    df.columns = [f"{price_labels[i]} (${prices[i]:.2f})" for i in range(len(prices))]
    
    return df