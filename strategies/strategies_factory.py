# --- strategies/strategies_factory.py ---
"""
Factory module for creating options strategies.
Provides a unified interface to create any supported strategy.
"""
import logging
from typing import List, Dict, Any, Union

# Import all strategy implementations
from .basic_strategies import (
    long_call_strategy, long_put_strategy, covered_call_strategy,
    cash_secured_put_strategy, naked_call_strategy, naked_put_strategy
)
from .spread_strategies import (
    bull_call_spread, bear_put_spread, bull_put_spread, bear_call_spread,
    calendar_spread, poor_mans_covered_call, ratio_backspread
)
from .advanced_strategies import (
    iron_condor, butterfly, straddle, strangle, collar,
    diagonal_spread, double_diagonal_spread
)
from .custom_strategy import custom_strategy

# Setup logging
logger = logging.getLogger(__name__)

def create_strategy(strategy_type: str, **kwargs) -> List[Dict[str, Any]]:
    """
    Factory function to create strategy legs based on the strategy type.
    
    Parameters:
        strategy_type (str): The type of strategy to create
        **kwargs: Strategy-specific parameters
    
    Returns:
        List[Dict[str, Any]]: A list of strategy legs
    
    Raises:
        ValueError: If the strategy type is unknown or required parameters are missing
    """
    # Create the appropriate strategy based on the type
    strategy_creators = {
        # Basic strategies
        "long_call": long_call_strategy,
        "long_put": long_put_strategy,
        "covered_call": covered_call_strategy,
        "cash_secured_put": cash_secured_put_strategy,
        "naked_call": naked_call_strategy,
        "naked_put": naked_put_strategy,
        
        # Spread strategies
        "bull_call_spread": bull_call_spread,
        "bear_put_spread": bear_put_spread,
        "bull_put_spread": bull_put_spread,
        "bear_call_spread": bear_call_spread,
        "calendar_spread": calendar_spread,
        "poor_mans_covered_call": poor_mans_covered_call,
        "ratio_backspread": ratio_backspread,
        
        # Advanced strategies
        "iron_condor": iron_condor,
        "butterfly": butterfly,
        "straddle": straddle,
        "strangle": strangle,
        "collar": collar,
        "diagonal_spread": diagonal_spread,
        "double_diagonal_spread": double_diagonal_spread,
        
        # Custom strategies
        "custom": custom_strategy
    }
    
    # Check if the requested strategy type exists
    if strategy_type not in strategy_creators:
        logger.error(f"Unknown strategy type: {strategy_type}")
        raise ValueError(f"Unknown strategy type: {strategy_type}")
    
    # Create the strategy
    try:
        strategy_legs = strategy_creators[strategy_type](**kwargs)
        logger.info(f"Created {strategy_type} strategy with {len(strategy_legs)} legs")
        return strategy_legs
    except Exception as e:
        logger.error(f"Error creating {strategy_type} strategy: {str(e)}", exc_info=True)
        raise ValueError(f"Error creating {strategy_type} strategy: {str(e)}")

# Helper functions for strategy creation

def get_strategy_info(strategy_type: str) -> Dict[str, str]:
    """
    Get information about a specific strategy.
    
    Parameters:
        strategy_type (str): The type of strategy
    
    Returns:
        Dict[str, str]: Dictionary with strategy information
    """
    strategies_info = {
        "long_call": {
            "name": "Long Call",
            "description": "Purchase a call option to profit from a rise in the stock price.",
            "risk_profile": "Limited risk, unlimited potential reward",
            "outlook": "Bullish",
            "complexity": "Basic"
        },
        "long_put": {
            "name": "Long Put",
            "description": "Purchase a put option to profit from a fall in the stock price.",
            "risk_profile": "Limited risk, limited potential reward",
            "outlook": "Bearish",
            "complexity": "Basic"
        },
        "covered_call": {
            "name": "Covered Call",
            "description": "Own stock and sell a call against it to generate income.",
            "risk_profile": "Limited upside, downside risk partially offset by premium",
            "outlook": "Neutral to slightly bullish",
            "complexity": "Basic"
        },
        "cash_secured_put": {
            "name": "Cash Secured Put",
            "description": "Sell a put option and set aside cash to buy the stock if assigned.",
            "risk_profile": "Limited upside to premium, downside risk to strike minus premium",
            "outlook": "Neutral to slightly bullish",
            "complexity": "Basic"
        },
        "naked_call": {
            "name": "Naked Call",
            "description": "Sell a call option without owning the underlying stock.",
            "risk_profile": "Limited upside to premium, unlimited downside risk",
            "outlook": "Neutral to bearish",
            "complexity": "Advanced (high risk)"
        },
        "naked_put": {
            "name": "Naked Put",
            "description": "Sell a put option without setting aside cash to buy the stock.",
            "risk_profile": "Limited upside to premium, significant downside risk",
            "outlook": "Neutral to bullish",
            "complexity": "Advanced (high risk)"
        },
        "bull_call_spread": {
            "name": "Bull Call Spread",
            "description": "Buy a call at a lower strike and sell a call at a higher strike.",
            "risk_profile": "Limited risk, limited reward",
            "outlook": "Moderately bullish",
            "complexity": "Intermediate"
        },
        "bear_put_spread": {
            "name": "Bear Put Spread",
            "description": "Buy a put at a higher strike and sell a put at a lower strike.",
            "risk_profile": "Limited risk, limited reward",
            "outlook": "Moderately bearish",
            "complexity": "Intermediate"
        },
        "bull_put_spread": {
            "name": "Bull Put Credit Spread",
            "description": "Sell a put at a higher strike and buy a put at a lower strike.",
            "risk_profile": "Limited risk, limited reward",
            "outlook": "Moderately bullish",
            "complexity": "Intermediate"
        },
        "bear_call_spread": {
            "name": "Bear Call Credit Spread",
            "description": "Sell a call at a lower strike and buy a call at a higher strike.",
            "risk_profile": "Limited risk, limited reward",
            "outlook": "Moderately bearish",
            "complexity": "Intermediate"
        },
        "iron_condor": {
            "name": "Iron Condor",
            "description": "Combination of a bull put spread and a bear call spread.",
            "risk_profile": "Limited risk, limited reward",
            "outlook": "Neutral (range-bound)",
            "complexity": "Advanced"
        },
        "butterfly": {
            "name": "Butterfly",
            "description": "Buy one lower strike option, sell two middle strike options, buy one higher strike option.",
            "risk_profile": "Limited risk, limited reward",
            "outlook": "Neutral (price target at middle strike)",
            "complexity": "Advanced"
        },
        "straddle": {
            "name": "Straddle",
            "description": "Buy a call and a put at the same strike and expiration.",
            "risk_profile": "Limited risk, unlimited potential reward",
            "outlook": "Volatile (big move in either direction)",
            "complexity": "Intermediate"
        },
        "strangle": {
            "name": "Strangle",
            "description": "Buy an OTM call and an OTM put.",
            "risk_profile": "Limited risk, unlimited potential reward",
            "outlook": "Volatile (big move in either direction)",
            "complexity": "Intermediate"
        },
        "collar": {
            "name": "Collar",
            "description": "Own stock, buy a protective put, and sell a covered call.",
            "risk_profile": "Limited downside, limited upside",
            "outlook": "Conservative, capital preservation",
            "complexity": "Intermediate"
        },
        "calendar_spread": {
            "name": "Calendar Spread",
            "description": "Sell a near-term option and buy a longer-term option at the same strike.",
            "risk_profile": "Limited risk, limited reward",
            "outlook": "Neutral in short term",
            "complexity": "Advanced"
        },
        "poor_mans_covered_call": {
            "name": "Poor Man's Covered Call",
            "description": "Buy a deep ITM LEAP call, sell short-term OTM calls against it.",
            "risk_profile": "Reduced capital requirement vs. covered call",
            "outlook": "Neutral to slightly bullish",
            "complexity": "Advanced"
        },
        "diagonal_spread": {
            "name": "Diagonal Spread",
            "description": "Buy a longer-term option at one strike, sell a shorter-term option at a different strike.",
            "risk_profile": "Limited risk, varied reward",
            "outlook": "Depends on strikes and option types",
            "complexity": "Advanced"
        },
        "ratio_backspread": {
            "name": "Ratio Backspread",
            "description": "Sell 1 option at one strike, buy multiple options at another strike.",
            "risk_profile": "Limited or unlimited, depending on setup",
            "outlook": "Directional with volatility expectation",
            "complexity": "Advanced"
        }
    }
    
    if strategy_type not in strategies_info:
        logger.warning(f"No information available for strategy type: {strategy_type}")
        return {
            "name": strategy_type.replace('_', ' ').title(),
            "description": "No detailed description available.",
            "risk_profile": "Unknown",
            "outlook": "Unknown",
            "complexity": "Unknown"
        }
    
    return strategies_info[strategy_type]

def get_available_strategy_types() -> Dict[str, List[str]]:
    """
    Get a dictionary of all available strategy types grouped by category.
    
    Returns:
        Dict[str, List[str]]: Dictionary with strategy categories and types
    """
    return {
        "Basic Strategies": [
            "long_call",
            "long_put",
            "covered_call",
            "cash_secured_put",
            "naked_call",
            "naked_put"
        ],
        "Spread Strategies": [
            "bull_call_spread",
            "bear_put_spread",
            "bull_put_spread",
            "bear_call_spread",
            "calendar_spread",
            "poor_mans_covered_call",
            "ratio_backspread"
        ],
        "Advanced Strategies": [
            "iron_condor",
            "butterfly",
            "straddle", 
            "strangle",
            "collar",
            "diagonal_spread",
            "double_diagonal_spread"
        ],
        "Custom Strategies": [
            "custom"
        ]
    }
