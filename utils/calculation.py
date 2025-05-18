# utils/calculation.py
import numpy as np
import pandas as pd
import logging
from models.pricing import black_scholes, calculate_greeks, calculate_implied_volatility
from utils.error_handlers import handle_calculation_error

logger = logging.getLogger(__name__)

@handle_calculation_error
def calculate_strategy_payoff(strategy_legs, price_range, current_price=None):
    """
    Calculate the payoff of a strategy over a range of prices at expiration.
    Uses entry prices for P/L calculations.
    
    Parameters:
    strategy_legs (list): List of leg dictionaries with type, position, strike, etc.
    price_range (array): Array of prices to calculate payoff for
    current_price (float): Current stock price (for reference)
    
    Returns:
    list: Payoff values for each price in price_range
    """
    # Convert price_range to numpy array if it's not already
    price_range = np.array(price_range)
    
    payoffs = np.zeros(len(price_range))
    
    for leg in strategy_legs:
        leg_type = leg.get('type')
        position = leg.get('position')
        strike = leg.get('strike')
        
        # Use entry price (price) for P/L calculations, not current_price
        premium = leg.get('price', 0)
        quantity = leg.get('quantity', 1)
        
        # Sign based on position (long or short)
        sign = 1 if position == 'long' else -1
        
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
            purchase_price = leg.get('price', current_price)
            leg_payoffs = price_range - purchase_price
            payoffs += sign * leg_payoffs * quantity
    
    return payoffs * 100  # Multiply by contract size (100 shares per contract)

@handle_calculation_error
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
    volatility (float): Implied volatility
    
    Returns:
    list: Current values for each price in price_range
    """
    # Convert price_range to numpy array
    price_range = np.array(price_range)
    values = np.zeros(len(price_range))
    years_to_expiry = days_to_expiry / 365
    
    for leg in strategy_legs:
        leg_type = leg.get('type')
        position = leg.get('position')
        strike = leg.get('strike')
        
        # Use price for cost basis and current_price for current value
        entry_premium = leg.get('price', 0)
        current_premium = leg.get('current_price', entry_premium)  # Default to entry if current not available
        quantity = leg.get('quantity', 1)
        iv = leg.get('iv', volatility)  # Use leg-specific IV if available
        
        # Sign based on position (long or short)
        sign = 1 if position == 'long' else -1
        
        if leg_type in ['call', 'put']:
            # Calculate current option value using Black-Scholes for each price
            leg_values = np.zeros(len(price_range))
            for i, price in enumerate(price_range):
                try:
                    option_value = black_scholes(
                        leg_type, price, strike, years_to_expiry, risk_free_rate, iv
                    )
                    
                    # Calculate unrealized P/L: current theoretical value - entry price
                    unrealized_pl = option_value - entry_premium
                    leg_values[i] = unrealized_pl
                except Exception as e:
                    logger.warning(f"Error calculating value at price {price}: {str(e)}")
                    # Use simple intrinsic value as fallback
                    if leg_type == 'call':
                        intrinsic = max(0, price - strike)
                    else:  # put
                        intrinsic = max(0, strike - price)
                    leg_values[i] = intrinsic - entry_premium
            
            values += sign * leg_values * quantity
                
        elif leg_type == 'stock':
            # Stock value: current_price - purchase_price
            purchase_price = leg.get('price', price_range[0])
            values += sign * (price_range - purchase_price) * quantity
    
    return values * 100  # Multiply by contract size

def find_breakeven_points(price_range, payoffs):
    """
    Find breakeven points in a strategy (where payoff crosses zero).
    
    Parameters:
    price_range (array): Array of stock prices
    payoffs (array): Array of corresponding payoffs
    
    Returns:
    list: List of breakeven prices
    """
    breakeven_points = []
    for i in range(1, len(price_range)):
        if (payoffs[i-1] <= 0 and payoffs[i] > 0) or (payoffs[i-1] >= 0 and payoffs[i] < 0):
            # Linear interpolation to find precise breakeven
            x0, y0 = price_range[i-1], payoffs[i-1]
            x1, y1 = price_range[i], payoffs[i]
            
            if y1 - y0 != 0:  # Avoid division by zero
                breakeven = x0 + (x1 - x0) * (-y0) / (y1 - y0)
                breakeven_points.append(breakeven)
    
    return sorted(breakeven_points)

def calculate_strategy_metrics(strategy_legs, current_price, price_range=None):
    """
    Calculate key metrics for a strategy including max profit, max loss, breakeven points.
    
    Parameters:
    strategy_legs (list): List of leg dictionaries
    current_price (float): Current stock price
    price_range (array, optional): Custom price range for analysis
    
    Returns:
    dict: Dictionary of strategy metrics
    """
    if price_range is None:
        # Generate a wide price range for accurate max profit/loss
        price_range_pct = 0.5  # 50% up and down from current price
        min_price = current_price * (1 - price_range_pct)
        max_price = current_price * (1 + price_range_pct)
        price_range = np.linspace(min_price, max_price, 1000)
    
    # Calculate payoffs at expiration
    payoffs = calculate_strategy_payoff(strategy_legs, price_range, current_price)
    
    # Calculate key metrics
    max_profit = float(max(payoffs))
    max_loss = float(min(payoffs))
    current_index = np.abs(price_range - current_price).argmin()
    profit_at_current = float(payoffs[current_index])
    
    # Find breakeven points
    breakeven_points = find_breakeven_points(price_range, payoffs)
    
    # Calculate risk-reward ratio if meaningful
    if max_loss < 0 and max_profit > 0:
        risk_reward_ratio = abs(max_profit / max_loss)
    else:
        risk_reward_ratio = float('inf') if max_profit > 0 else 0
    
    return {
        'max_profit': max_profit,
        'max_loss': max_loss,
        'profit_at_current': profit_at_current,
        'breakeven_points': breakeven_points,
        'risk_reward_ratio': risk_reward_ratio
    }

def calculate_strategy_greeks(strategy_legs, current_price, days_to_expiry, risk_free_rate=0.03):
    """
    Calculate aggregate Greeks for a strategy.
    
    Parameters:
    strategy_legs (list): List of leg dictionaries
    current_price (float): Current stock price
    days_to_expiry (int): Days to expiration
    risk_free_rate (float): Risk-free interest rate
    
    Returns:
    dict: Dictionary of aggregate Greeks
    """
    years_to_expiry = max(0, days_to_expiry / 365)
    
    # Initialize aggregate Greeks
    total_greeks = {
        'delta': 0,
        'gamma': 0,
        'theta': 0,
        'vega': 0,
        'rho': 0
    }
    
    # Calculate Greeks for each leg
    for leg in strategy_legs:
        if leg.get('type') in ['call', 'put']:
            # Get leg parameters
            option_type = leg.get('type')
            strike = leg.get('strike')
            position = leg.get('position')
            iv = leg.get('iv', 0.3)
            quantity = leg.get('quantity', 1)
            
            # Calculate Greeks
            leg_greeks = calculate_greeks(
                option_type, current_price, strike, years_to_expiry, risk_free_rate, iv
            )
            
            # Adjust by position and quantity
            sign = 1 if position == 'long' else -1
            for greek, value in leg_greeks.items():
                total_greeks[greek] += sign * value * quantity
        
        # Note: Stock legs only affect delta
        elif leg.get('type') == 'stock':
            position = leg.get('position')
            quantity = leg.get('quantity', 1)
            sign = 1 if position == 'long' else -1
            
            # Stock has delta of 1
            total_greeks['delta'] += sign * quantity
    
    return total_greeks

def calculate_probability_metrics(strategy_legs, current_price, days_to_expiry, volatility=None):
    """
    Calculate probability-based metrics for a strategy.
    
    Parameters:
    strategy_legs (list): List of leg dictionaries
    current_price (float): Current stock price
    days_to_expiry (int): Days to expiration
    volatility (float, optional): Volatility to use, or calculated from legs if None
    
    Returns:
    dict: Dictionary of probability metrics
    """
    if volatility is None:
        # Calculate average volatility from legs
        ivs = [leg.get('iv', 0.3) for leg in strategy_legs 
              if leg.get('type') in ('call', 'put') and 'iv' in leg]
        volatility = sum(ivs) / len(ivs) if ivs else 0.3
    
    years_to_expiry = max(0.01, days_to_expiry / 365)
    
    # Get strategy metrics including breakeven points
    metrics = calculate_strategy_metrics(strategy_legs, current_price)
    breakeven_points = metrics['breakeven_points']
    
    # No breakeven points, can't calculate probability
    if not breakeven_points:
        return {'probability_of_profit': None}
    
    # Calculate probability based on log-normal distribution
    results = {}
    
    # Calculate profit probability based on breakeven points
    # For strategies with single breakeven, determine if profit is above or below
    if len(breakeven_points) == 1:
        be = breakeven_points[0]
        
        # Generate a small price range around current to determine profit direction
        small_range = np.linspace(current_price * 0.95, current_price * 1.05, 21)
        small_payoffs = calculate_strategy_payoff(strategy_legs, small_range, current_price)
        mid_idx = len(small_range) // 2  # Index closest to current price
        
        # Check if profit is above or below breakeven
        if be > current_price and small_payoffs[mid_idx] >= 0:
            # Profit below breakeven
            z_score = np.log(be / current_price) / (volatility * np.sqrt(years_to_expiry))
            prob_of_profit = norm.cdf(z_score)
        else:
            # Profit above breakeven
            z_score = np.log(be / current_price) / (volatility * np.sqrt(years_to_expiry))
            prob_of_profit = 1 - norm.cdf(z_score)
    
    # For strategies with two breakevens, determine if profit is between or outside
    elif len(breakeven_points) == 2:
        be1, be2 = breakeven_points
        
        # Generate a small price range to determine profit region
        test_prices = [current_price, (be1 + be2) / 2]
        test_payoffs = calculate_strategy_payoff(strategy_legs, test_prices, current_price)
        
        # Check if profit is between or outside breakevens
        if test_payoffs[1] >= 0:
            # Profit between breakevens
            z1 = np.log(be1 / current_price) / (volatility * np.sqrt(years_to_expiry))
            z2 = np.log(be2 / current_price) / (volatility * np.sqrt(years_to_expiry))
            prob_of_profit = norm.cdf(z2) - norm.cdf(z1)
        else:
            # Profit outside breakevens
            z1 = np.log(be1 / current_price) / (volatility * np.sqrt(years_to_expiry))
            z2 = np.log(be2 / current_price) / (volatility * np.sqrt(years_to_expiry))
            prob_of_profit = norm.cdf(z1) + (1 - norm.cdf(z2))
    
    # For more complex strategies, estimate with Monte Carlo
    else:
        # Simplified Monte Carlo approach
        num_simulations = 10000
        np.random.seed(42)  # For reproducibility
        
        # Generate random final prices
        random_returns = np.random.normal(
            0, volatility * np.sqrt(years_to_expiry), num_simulations
        )
        final_prices = current_price * np.exp(random_returns)
        
        # Calculate payoffs at these prices
        final_payoffs = calculate_strategy_payoff(strategy_legs, final_prices, current_price)
        
        # Calculate probability of profit
        prob_of_profit = np.sum(final_payoffs > 0) / num_simulations
    
    results['probability_of_profit'] = prob_of_profit
    
    # Calculate expected value
    wide_range = np.linspace(current_price * 0.5, current_price * 2, 100)
    wide_payoffs = calculate_strategy_payoff(strategy_legs, wide_range, current_price)
    
    # Approximate expected value using discrete distribution
    prob_density = np.zeros(len(wide_range))
    for i, price in enumerate(wide_range):
        z = np.log(price / current_price) / (volatility * np.sqrt(years_to_expiry))
        if i == 0:
            prob_density[i] = norm.cdf(z)
        elif i == len(wide_range) - 1:
            prob_density[i] = 1 - norm.cdf(z)
        else:
            z_prev = np.log(wide_range[i-1] / current_price) / (volatility * np.sqrt(years_to_expiry))
            prob_density[i] = norm.cdf(z) - norm.cdf(z_prev)
    
    expected_value = np.sum(wide_payoffs * prob_density)
    results['expected_value'] = expected_value
    
    return results