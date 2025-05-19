# --- strategies/__init__.py ---
"""
Options Strategy Calculator - Strategy Module

This module imports all strategy implementations to make them
available through a unified interface.
"""

# Import all strategy implementations
from .basic_strategies import *
from .spread_strategies import *
from .advanced_strategies import *
from .custom_strategy import *
from .strategies_factory import create_strategy