# tests/test_calculations.py
import unittest
import numpy as np
from utils.calculation import (
    calculate_strategy_payoff,
    calculate_strategy_current_value,
    find_breakeven_points
)

class TestStrategyCalculations(unittest.TestCase):
    def test_long_call_payoff(self):
        """Test payoff calculation for a long call strategy."""
        # Simple long call strategy
        strategy_legs = [{
            'type': 'call',
            'position': 'long',
            'strike': 100,
            'price': 5,
            'quantity': 1
        }]
        
        # Test at various prices
        prices = np.array([90, 100, 105, 110, 120])
        payoffs = calculate_strategy_payoff(strategy_legs, prices)
        
        # Expected payoffs: max(0, price - strike) - premium
        expected = np.array([-5, -5, 0, 5, 15]) * 100
        
        # Assert payoffs match expected values
        np.testing.assert_array_almost_equal(payoffs, expected)
    
    def test_long_put_payoff(self):
        """Test payoff calculation for a long put strategy."""
        # Simple long put strategy
        strategy_legs = [{
            'type': 'put',
            'position': 'long',
            'strike': 100,
            'price': 5,
            'quantity': 1
        }]
        
        # Test at various prices
        prices = np.array([80, 90, 95, 100, 110])
        payoffs = calculate_strategy_payoff(strategy_legs, prices)
        
        # Expected payoffs: max(0, strike - price) - premium
        expected = np.array([15, 5, 0, -5, -5]) * 100
        
        # Assert payoffs match expected values
        np.testing.assert_array_almost_equal(payoffs, expected)
    
    def test_bull_call_spread_payoff(self):
        """Test payoff calculation for a bull call spread strategy."""
        # Bull call spread (long 100 call, short 110 call)
        strategy_legs = [
            {
                'type': 'call',
                'position': 'long',
                'strike': 100,
                'price': 5,
                'quantity': 1
            },
            {
                'type': 'call',
                'position': 'short',
                'strike': 110,
                'price': 2,
                'quantity': 1
            }
        ]
        
        # Test at various prices
        prices = np.array([90, 100, 105, 110, 120])
        payoffs = calculate_strategy_payoff(strategy_legs, prices)
        
        # Expected payoffs for bull call spread
        # Debit = 5 - 2 = 3, width = 10
        expected = np.array([-3, -3, 2, 7, 7]) * 100
        
        # Assert payoffs match expected values
        np.testing.assert_array_almost_equal(payoffs, expected)
    
    def test_breakeven_points(self):
        """Test finding breakeven points."""
        # Simple linear function crossing zero twice
        prices = np.array([1, 2, 3, 4, 5])
        payoffs = np.array([-2, -1, 0, 1, 2])
        
        # Find breakeven points
        breakevens = find_breakeven_points(prices, payoffs)
        
        # Should find one breakeven at x=3
        self.assertEqual(len(breakevens), 1)
        self.assertAlmostEqual(breakevens[0], 3.0)
        
        # Test with no breakeven points
        prices = np.array([1, 2, 3, 4, 5])
        payoffs = np.array([1, 2, 3, 4, 5])  # Always positive
        
        breakevens = find_breakeven_points(prices, payoffs)
        self.assertEqual(len(breakevens), 0)
        
        # Test with multiple breakeven points
        prices = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9])
        payoffs = np.array([-1, 1, 2, 1, -1, -2, -1, 1, 2])  # Crosses zero multiple times
        
        breakevens = find_breakeven_points(prices, payoffs)
        self.assertEqual(len(breakevens), 4)  # Should find 4 breakeven points

if __name__ == '__main__':
    unittest.main()