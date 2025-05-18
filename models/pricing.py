# models/pricing.py
import numpy as np
import pandas as pd
import logging
from scipy.stats import norm
from scipy import optimize
from utils.error_handlers import handle_calculation_error

# Setup logging
logger = logging.getLogger(__name__)

@handle_calculation_error
def black_scholes(option_type, S, K, t, r, sigma):
    """
    Calculate option price using the Black-Scholes formula with improved handling of edge cases.
    
    Parameters:
        option_type (str): 'call' or 'put'
        S (float): Current stock price
        K (float): Strike price
        t (float): Time to expiration in years
        r (float): Risk-free interest rate (decimal)
        sigma (float): Implied volatility (decimal)
    
    Returns:
        float: Option price
    """
    # Handle edge cases
    if t <= 0:
        # At or past expiration
        if option_type.lower() == "call":
            return max(0, S - K)
        else:
            return max(0, K - S)
    
    if sigma <= 0:
        sigma = 0.0001  # Prevent division by zero
    
    # Ensure inputs are floats
    S = float(S)
    K = float(K)
    t = float(t)
    r = float(r)
    sigma = float(sigma)
    
    try:
        # Calculate d1 and d2
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * t) / (sigma * np.sqrt(t))
        d2 = d1 - sigma * np.sqrt(t)
        
        # Calculate option price
        if option_type.lower() == "call":
            price = S * norm.cdf(d1) - K * np.exp(-r * t) * norm.cdf(d2)
        elif option_type.lower() == "put":
            price = K * np.exp(-r * t) * norm.cdf(-d2) - S * norm.cdf(-d1)
        else:
            raise ValueError(f"Invalid option type: {option_type}. Use 'call' or 'put'.")
        
        return max(0, price)  # Ensure non-negative price
    
    except Exception as e:
        logger.error(f"Black-Scholes calculation error: {str(e)}", exc_info=True)
        # Return intrinsic value as fallback
        if option_type.lower() == "call":
            return max(0, S - K)
        else:
            return max(0, K - S)

@handle_calculation_error
def calculate_greeks(option_type, S, K, t, r, sigma):
    """
    Calculate option Greeks with improved accuracy and error handling.
    
    Parameters:
        option_type (str): 'call' or 'put'
        S (float): Current stock price
        K (float): Strike price
        t (float): Time to expiration in years
        r (float): Risk-free interest rate (decimal)
        sigma (float): Implied volatility (decimal)
    
    Returns:
        dict: Dictionary containing delta, gamma, theta, vega, and rho
    """
    # Handle edge cases
    if t <= 0:
        # At or past expiration
        if option_type.lower() == "call":
            delta = 1.0 if S > K else 0.0
        else:
            delta = -1.0 if S < K else 0.0
        return {
            "delta": delta,
            "gamma": 0.0,
            "vega": 0.0,
            "theta": 0.0,
            "rho": 0.0
        }
    
    if sigma <= 0:
        sigma = 0.0001  # Prevent division by zero
    
    try:
        # Calculate d1 and d2
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * t) / (sigma * np.sqrt(t))
        d2 = d1 - sigma * np.sqrt(t)
        
        # Calculate probability density at d1
        pdf_d1 = norm.pdf(d1)
        
        # Calculate cumulative probabilities
        cdf_d1 = norm.cdf(d1)
        cdf_neg_d1 = norm.cdf(-d1)
        cdf_d2 = norm.cdf(d2)
        cdf_neg_d2 = norm.cdf(-d2)
        
        # Gamma (same for calls and puts)
        gamma = pdf_d1 / (S * sigma * np.sqrt(t))
        
        # Vega (same for calls and puts)
        vega = S * pdf_d1 * np.sqrt(t) / 100  # Divided by 100 for scaling
        
        if option_type.lower() == "call":
            # Delta for call
            delta = cdf_d1
            
            # Theta for call (daily)
            theta = (-(S * pdf_d1 * sigma) / (2 * np.sqrt(t)) - 
                    r * K * np.exp(-r * t) * cdf_d2) / 365
            
            # Rho for call (per 1% change)
            rho = K * t * np.exp(-r * t) * cdf_d2 / 100
        
        elif option_type.lower() == "put":
            # Delta for put
            delta = cdf_d1 - 1
            
            # Theta for put (daily)
            theta = (-(S * pdf_d1 * sigma) / (2 * np.sqrt(t)) + 
                    r * K * np.exp(-r * t) * cdf_neg_d2) / 365
            
            # Rho for put (per 1% change)
            rho = -K * t * np.exp(-r * t) * cdf_neg_d2 / 100
        
        else:
            raise ValueError(f"Invalid option type: {option_type}. Use 'call' or 'put'.")
        
        return {
            "delta": delta,
            "gamma": gamma,
            "vega": vega,
            "theta": theta,
            "rho": rho
        }
    
    except Exception as e:
        logger.error(f"Greeks calculation error: {str(e)}", exc_info=True)
        # Return default values on error
        return {
            "delta": 0.5 if option_type.lower() == "call" else -0.5,
            "gamma": 0.01,
            "vega": 0.01,
            "theta": -0.01,
            "rho": 0.01
        }

@handle_calculation_error
def calculate_implied_volatility(option_type, S, K, t, r, market_price, precision=0.0001, max_iterations=100):
    """
    Calculate implied volatility using the Newton-Raphson method with better convergence.
    
    Parameters:
        option_type (str): 'call' or 'put'
        S (float): Current stock price
        K (float): Strike price
        t (float): Time to expiration in years
        r (float): Risk-free interest rate (decimal)
        market_price (float): Market price of the option
        precision (float): Error tolerance for convergence
        max_iterations (int): Maximum number of iterations
    
    Returns:
        float: Implied volatility (decimal)
    """
    # Handle edge cases
    if market_price <= 0:
        return 0.0001  # Minimum IV for zero or negative prices
    
    # Calculate intrinsic value
    if option_type.lower() == "call":
        intrinsic = max(0, S - K)
    else:
        intrinsic = max(0, K - S)
    
    # If market price is less than intrinsic value (shouldn't happen in theory), 
    # return a very low IV
    if market_price < intrinsic:
        return 0.0001
    
    try:
        # Define the objective function (difference between BS price and market price)
        def objective(sigma):
            return black_scholes(option_type, S, K, t, r, sigma) - market_price
        
        # Use scipy's root finding to find IV
        result = optimize.newton(objective, x0=0.3, tol=precision, maxiter=max_iterations)
        
        # Ensure result is within reasonable bounds
        result = max(0.0001, min(result, 5.0))  # Cap IV between 0.01% and 500%
        
        return result
    
    except Exception as e:
        # If Newton-Raphson method fails, try bisection method
        logger.warning(f"Newton method failed for IV calculation: {str(e)}. Trying bisection.")
        try:
            return _calculate_iv_bisection(option_type, S, K, t, r, market_price)
        except Exception as e2:
            logger.error(f"IV calculation error: {str(e2)}", exc_info=True)
            # Return a reasonable default
            return 0.3  # 30% as a fallback

def _calculate_iv_bisection(option_type, S, K, t, r, market_price, min_vol=0.0001, max_vol=5.0, precision=0.0001):
    """
    Calculate implied volatility using the bisection method (fallback method).
    
    Parameters:
        option_type (str): 'call' or 'put'
        S (float): Current stock price
        K (float): Strike price
        t (float): Time to expiration in years
        r (float): Risk-free interest rate (decimal)
        market_price (float): Market price of the option
        min_vol (float): Minimum volatility bound
        max_vol (float): Maximum volatility bound
        precision (float): Error tolerance
    
    Returns:
        float: Implied volatility
    """
    if min_vol >= max_vol:
        return 0.3  # Default if bounds are invalid
    
    # Check if market price is within the bounds
    min_price = black_scholes(option_type, S, K, t, r, min_vol)
    max_price = black_scholes(option_type, S, K, t, r, max_vol)
    
    # If market price is outside our bounds, return boundary value
    if market_price <= min_price:
        return min_vol
    if market_price >= max_price:
        return max_vol
    
    # Bisection search
    for _ in range(100):  # Limit iterations
        mid_vol = (min_vol + max_vol) / 2
        mid_price = black_scholes(option_type, S, K, t, r, mid_vol)
        
        if abs(mid_price - market_price) < precision:
            return mid_vol
        
        if mid_price < market_price:
            min_vol = mid_vol
        else:
            max_vol = mid_vol
    
    # Return the midpoint if we don't converge
    return (min_vol + max_vol) / 2

@handle_calculation_error
def binomial_tree_price(option_type, S, K, t, r, sigma, steps=100, american=False):
    """
    Calculate option price using the binomial tree model, which can handle American options.
    
    Parameters:
        option_type (str): 'call' or 'put'
        S (float): Current stock price
        K (float): Strike price
        t (float): Time to expiration in years
        r (float): Risk-free interest rate (decimal)
        sigma (float): Implied volatility (decimal)
        steps (int): Number of time steps in the tree
        american (bool): True for American options, False for European
    
    Returns:
        float: Option price
    """
    # Handle edge cases
    if t <= 0:
        # At or past expiration
        if option_type.lower() == "call":
            return max(0, S - K)
        else:
            return max(0, K - S)
    
    if sigma <= 0:
        sigma = 0.0001  # Prevent division by zero
    
    try:
        # Calculate parameters for the tree
        dt = t / steps
        u = np.exp(sigma * np.sqrt(dt))
        d = 1 / u
        p = (np.exp(r * dt) - d) / (u - d)
        discount = np.exp(-r * dt)
        
        # Initialize asset prices at each node of the final step
        prices = np.zeros(steps + 1)
        for i in range(steps + 1):
            prices[i] = S * (u ** (steps - i)) * (d ** i)
        
        # Initialize option values at final nodes
        if option_type.lower() == "call":
            option_values = np.maximum(0, prices - K)
        else:
            option_values = np.maximum(0, K - prices)
        
        # Work backwards through the tree
        for step in range(steps - 1, -1, -1):
            for i in range(step + 1):
                # Calculate asset price at this node
                spot = S * (u ** (step - i)) * (d ** i)
                
                # Calculate option value at this node (expectation)
                option_values[i] = discount * (p * option_values[i] + (1 - p) * option_values[i + 1])
                
                # For American options, check for early exercise
                if american:
                    if option_type.lower() == "call":
                        option_values[i] = max(option_values[i], spot - K)
                    else:
                        option_values[i] = max(option_values[i], K - spot)
        
        # Return the option value at the root node
        return option_values[0]
    
    except Exception as e:
        logger.error(f"Binomial tree calculation error: {str(e)}", exc_info=True)
        # Fall back to Black-Scholes
        return black_scholes(option_type, S, K, t, r, sigma)

@handle_calculation_error
def monte_carlo_price(option_type, S, K, t, r, sigma, paths=10000, steps=100):
    """
    Calculate option price using Monte Carlo simulation.
    
    Parameters:
        option_type (str): 'call' or 'put'
        S (float): Current stock price
        K (float): Strike price
        t (float): Time to expiration in years
        r (float): Risk-free interest rate (decimal)
        sigma (float): Implied volatility (decimal)
        paths (int): Number of price paths to simulate
        steps (int): Number of time steps per path
    
    Returns:
        float: Option price
    """
    # Handle edge cases
    if t <= 0:
        # At or past expiration
        if option_type.lower() == "call":
            return max(0, S - K)
        else:
            return max(0, K - S)
    
    if sigma <= 0:
        sigma = 0.0001  # Prevent division by zero
    
    try:
        # Time step
        dt = t / steps
        
        # Initialize array for final stock prices
        final_prices = np.zeros(paths)
        
        # Generate random paths
        for i in range(paths):
            # Generate random normal variables
            Z = np.random.standard_normal(steps)
            
            # Initialize path
            stock_price = S
            
            # Simulate path
            for j in range(steps):
                # Calculate price movement
                stock_price *= np.exp((r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z[j])
            
            # Store final price
            final_prices[i] = stock_price
        
        # Calculate payoffs
        if option_type.lower() == "call":
            payoffs = np.maximum(0, final_prices - K)
        else:
            payoffs = np.maximum(0, K - final_prices)
        
        # Discount payoffs
        option_price = np.exp(-r * t) * np.mean(payoffs)
        
        return option_price
    
    except Exception as e:
        logger.error(f"Monte Carlo calculation error: {str(e)}", exc_info=True)
        # Fall back to Black-Scholes
        return black_scholes(option_type, S, K, t, r, sigma)

def price_option(pricing_method, option_type, S, K, t, r, sigma, american=False):
    """
    Price an option using the specified method.
    
    Parameters:
        pricing_method (str): 'black_scholes', 'binomial', or 'monte_carlo'
        option_type (str): 'call' or 'put'
        S (float): Current stock price
        K (float): Strike price
        t (float): Time to expiration in years
        r (float): Risk-free interest rate (decimal)
        sigma (float): Implied volatility (decimal)
        american (bool): True for American options (only for binomial)
    
    Returns:
        float: Option price
    """
    if pricing_method == 'black_scholes':
        return black_scholes(option_type, S, K, t, r, sigma)
    elif pricing_method == 'binomial':
        return binomial_tree_price(option_type, S, K, t, r, sigma, american=american)
    elif pricing_method == 'monte_carlo':
        return monte_carlo_price(option_type, S, K, t, r, sigma)
    else:
        raise ValueError(f"Unknown pricing method: {pricing_method}")

def calculate_option_value(option_data, current_price, days_to_expiry, risk_free_rate=0.03):
    """
    Calculate the theoretical value of an option using appropriate pricing model.
    
    Parameters:
        option_data (dict): Option data including type, strike, etc.
        current_price (float): Current stock price
        days_to_expiry (int): Days to expiration
        risk_free_rate (float): Risk-free interest rate
    
    Returns:
        float: Option theoretical value
    """
    if not option_data:
        return 0
    
    # Extract option parameters
    option_type = option_data.get('type', 'call')
    strike = option_data.get('strike', current_price)
    iv = option_data.get('iv', 0.3)
    
    # Convert days to years
    years = max(0, days_to_expiry / 365)
    
    try:
        # For very short-dated options or options near the money, use binomial model
        if days_to_expiry < 7 or abs(strike / current_price - 1) < 0.03:
            american = option_data.get('style', 'american').lower() == 'american'
            return binomial_tree_price(option_type, current_price, strike, years, risk_free_rate, iv, american=american)
        else:
            return black_scholes(option_type, current_price, strike, years, risk_free_rate, iv)
    except Exception as e:
        logger.error(f"Option valuation error: {str(e)}", exc_info=True)
        return 0