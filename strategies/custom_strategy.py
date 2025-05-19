# --- strategies/custom_strategy.py ---
"""
Custom strategy builder allowing users to create their own option strategies
with multiple legs of different types.
"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def custom_strategy(legs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Accepts a list of dictionaries representing user-defined legs of a custom strategy.
    Validates and normalizes the legs to ensure consistency.
    
    Parameters:
        legs (List[Dict]): List of option/stock legs with parameters
    
    Returns:
        List[Dict]: The strategy legs with validated fields
    
    Raises:
        ValueError: If the legs are invalid or missing required fields
    """
    if not isinstance(legs, list):
        raise ValueError("Legs must be provided as a list of dictionaries")
    if not legs:
        raise ValueError("At least one leg must be provided")
    
    validated_legs = []
    
    for i, leg in enumerate(legs):
        # Check if basic structure is valid
        if not isinstance(leg, dict):
            raise ValueError(f"Leg {i+1} must be a dictionary")
        
        # Ensure minimum required fields
        if 'type' not in leg:
            raise ValueError(f"Leg {i+1} is missing 'type' field")
        if 'position' not in leg:
            raise ValueError(f"Leg {i+1} is missing 'position' field")
        
        # Validate field values
        if leg['type'] not in ['call', 'put', 'stock']:
            raise ValueError(f"Invalid leg type: {leg['type']}. Use 'call', 'put', or 'stock'.")
        
        if leg['position'] not in ['long', 'short']:
            raise ValueError(f"Invalid position: {leg['position']}. Use 'long' or 'short'.")
        
        # Create a normalized leg dictionary
        normalized_leg = {
            'type': leg['type'],
            'position': leg['position'],
            'quantity': leg.get('quantity', 1)
        }
        
        # Ensure option legs have strike and expiry
        if leg['type'] in ['call', 'put']:
            if 'strike' not in leg:
                raise ValueError(f"Option leg {i+1} must have a 'strike' field")
            normalized_leg['strike'] = leg['strike']
            
            # Handle expiry field (support both expiry and expiration naming)
            if 'expiry' in leg:
                normalized_leg['expiry'] = str(leg['expiry'])
            elif 'expiration' in leg:
                normalized_leg['expiry'] = str(leg['expiration'])
            else:
                raise ValueError(f"Option leg {i+1} must have an 'expiry' or 'expiration' field")
            
            # Ensure IV is provided for option legs
            normalized_leg['iv'] = leg.get('iv', 0.3)
        
        # Handle price fields
        normalized_leg['price'] = leg.get('price', 0.0)
        normalized_leg['current_price'] = leg.get('current_price', normalized_leg['price'])
        
        # Additional fields for specific leg types
        if leg['type'] == 'put' and 'cash_secured' in leg:
            normalized_leg['cash_secured'] = leg['cash_secured']
        
        validated_legs.append(normalized_leg)
    
    return validated_legs

def calculate_custom_strategy_metrics(legs):
    """
    Calculate basic metrics for a custom strategy: net debit/credit, max profit/loss if known.
    
    Parameters:
        legs (List[Dict]): List of validated strategy leg dictionaries
    
    Returns:
        Dict: Dictionary with strategy metrics
    """
    # Calculate net premium
    net_premium = 0
    for leg in legs:
        premium_effect = leg['price'] * leg['quantity']
        # Adjust for contract multiplier (100) for options
        multiplier = 100 if leg['type'] in ['call', 'put'] else 1
        
        if leg['position'] == 'long':
            net_premium -= premium_effect * multiplier
        else:  # short
            net_premium += premium_effect * multiplier
    
    # Determine if the strategy is a debit or credit spread
    is_credit = net_premium > 0
    
    return {
        'net_premium': net_premium,
        'position_type': 'credit' if is_credit else 'debit',
        'max_profit': None,  # Would require specific analysis based on strategy
        'max_loss': None,    # Would require specific analysis based on strategy
        'breakeven': None    # Would require specific analysis based on strategy
    }
