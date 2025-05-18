# tests/test_pricing.py
import unittest
import numpy as np
from models.pricing import black_scholes, calculate_implied_volatility, calculate_greeks

class TestBlackScholes(unittest.TestCase):
    def test_call_option_pricing(self):
        """Test Black-Scholes pricing for call options."""
        # Test parameters
        S = 100.0  # Stock price
        K = 100.0  # Strike price (at the money)
        t = 1.0    # 1 year to expiration
        r = 0.05   # 5% risk-free rate
        sigma = 0.2  # 20% volatility
        
        # Calculate price
        call_price = black_scholes('call', S, K, t, r, sigma)
        
        # Expected price (calculated separately)
        expected_price = 10.45
        
        # Assert price is within expected range
        self.assertAlmostEqual(call_price, expected_price, delta=0.1)
    
    def test_put_option_pricing(self):
        """Test Black-Scholes pricing for put options."""
        # Test parameters
        S = 100.0  # Stock price
        K = 100.0  # Strike price (at the money)
        t = 1.0    # 1 year to expiration
        r = 0.05   # 5% risk-free rate
        sigma = 0.2  # 20% volatility
        
        # Calculate price
        put_price = black_scholes('put', S, K, t, r, sigma)
        
        # Expected price (calculated separately)
        expected_price = 5.57
        
        # Assert price is within expected range
        self.assertAlmostEqual(put_price, expected_price, delta=0.1)
    
    def test_edge_cases(self):
        """Test edge cases for Black-Scholes."""
        S = 100.0
        K = 100.0
        
        # Test expiration (t=0)
        call_at_expiry = black_scholes('call', S, K, 0, 0.05, 0.2)
        self.assertEqual(call_at_expiry, 0.0)  # ATM call at expiry is worthless
        
        call_at_expiry_itm = black_scholes('call', 110, K, 0, 0.05, 0.2)
        self.assertEqual(call_at_expiry_itm, 10.0)  # ITM call at expiry has intrinsic value
        
        # Test very low volatility
        low_vol_price = black_scholes('call', S, K, 1, 0.05, 0.0001)
        self.assertTrue(low_vol_price >= 0)  # Should handle low vol without errors

class TestImpliedVolatility(unittest.TestCase):
    def test_implied_volatility_calculation(self):
        """Test implied volatility calculation."""
        # Test parameters
        S = 100.0
        K = 100.0
        t = 1.0
        r = 0.05
        
        # Generate a price using known volatility
        known_vol = 0.25
        price = black_scholes('call', S, K, t, r, known_vol)
        
        # Calculate implied volatility from this price
        calculated_vol = calculate_implied_volatility('call', S, K, t, r, price)
        
        # Assert the calculated IV is close to the known IV
        self.assertAlmostEqual(calculated_vol, known_vol, delta=0.01)

class TestGreeks(unittest.TestCase):
    def test_delta_calculation(self):
        """Test delta calculation."""
        # ATM call should have delta around 0.5
        greeks = calculate_greeks('call', 100, 100, 1, 0.05, 0.2)
        self.assertAlmostEqual(greeks['delta'], 0.5, delta=0.1)
        
        # Deep ITM call should have delta close to 1
        greeks = calculate_greeks('call', 130, 100, 1, 0.05, 0.2)
        self.assertGreater(greeks['delta'], 0.8)
        
        # Deep OTM call should have delta close to 0
        greeks = calculate_greeks('call', 70, 100, 1, 0.05, 0.2)
        self.assertLess(greeks['delta'], 0.2)
        
        # ATM put should have delta around -0.5
        greeks = calculate_greeks('put', 100, 100, 1, 0.05, 0.2)
        self.assertAlmostEqual(greeks['delta'], -0.5, delta=0.1)
    
    def test_gamma_calculation(self):
        """Test gamma calculation."""
        # Gamma should be positive for both calls and puts
        call_greeks = calculate_greeks('call', 100, 100, 1, 0.05, 0.2)
        put_greeks = calculate_greeks('put', 100, 100, 1, 0.05, 0.2)
        
        self.assertGreater(call_greeks['gamma'], 0)
        self.assertGreater(put_greeks['gamma'], 0)
        
        # Call and put gamma should be identical for same parameters
        self.assertAlmostEqual(call_greeks['gamma'], put_greeks['gamma'])
    
    def test_theta_calculation(self):
        """Test theta calculation."""
        # Theta should generally be negative (time decay)
        greeks = calculate_greeks('call', 100, 100, 1, 0.05, 0.2)
        self.assertLess(greeks['theta'], 0)

if __name__ == '__main__':
    unittest.main()