# ui/components/strategy_selector.py
import streamlit as st
import logging
from utils.error_handlers import handle_ui_error

logger = logging.getLogger(__name__)

@handle_ui_error
def select_strategy():
    """
    Select strategy category and type.
    
    Returns:
        tuple: (strategy_category, strategy_type)
    """
    with st.sidebar:
        st.header("Strategy Selection")
        
        # Strategy category selection
        strategy_category = st.selectbox("Category", [
            "Basic Strategies",
            "Spread Strategies", 
            "Advanced Strategies",
            "Custom Strategies"
        ])
        
        # Strategy type based on category
        if strategy_category == "Basic Strategies":
            strategy_type = st.selectbox("Strategy", [
                "Long Call",
                "Long Put",
                "Covered Call",
                "Cash Secured Put",
                "Naked Call",
                "Naked Put"
            ])
        elif strategy_category == "Spread Strategies":
            strategy_type = st.selectbox("Strategy", [
                "Bull Call Spread",
                "Bear Put Spread",
                "Bull Put Credit Spread",
                "Bear Call Credit Spread",
                "Calendar Spread",
                "Poor Man's Covered Call",
                "Ratio Back Spread"
            ])
        elif strategy_category == "Advanced Strategies":
            strategy_type = st.selectbox("Strategy", [
                "Iron Condor",
                "Butterfly",
                "Straddle", 
                "Strangle",
                "Collar",
                "Diagonal Spread"
            ])
        else:  # Custom Strategies
            strategy_type = st.selectbox("Strategy", [
                "Custom - 2 Legs",
                "Custom - 3 Legs",
                "Custom - 4 Legs"
            ])
        
        # Strategy information
        with st.expander("Strategy Information"):
            show_strategy_info(strategy_category, strategy_type)
        
        return strategy_category, strategy_type

def show_strategy_info(category, strategy_type):
    """Show information about the selected strategy."""
    if category == "Basic Strategies":
        if strategy_type == "Long Call":
            st.markdown("""
            **Long Call**: Buy a call option to profit from a rise in the stock price.
            
            - **Max Loss**: Limited to premium paid
            - **Max Gain**: Unlimited (stock price - strike - premium)
            - **Breakeven**: Strike price + premium
            - **When to Use**: Bullish outlook, want leverage
            """)
        elif strategy_type == "Long Put":
            st.markdown("""
            **Long Put**: Buy a put option to profit from a fall in the stock price.
            
            - **Max Loss**: Limited to premium paid
            - **Max Gain**: Limited to (strike - premium) if stock goes to zero
            - **Breakeven**: Strike price - premium
            - **When to Use**: Bearish outlook, hedge long stock positions
            """)
        elif strategy_type == "Covered Call":
            st.markdown("""
            **Covered Call**: Own stock and sell a call against it.
            
            - **Max Loss**: Stock price can fall to zero, offset by premium
            - **Max Gain**: Limited to (strike - stock purchase price + premium)
            - **Breakeven**: Stock purchase price - premium
            - **When to Use**: Slightly bullish or neutral, generate income
            """)
        elif strategy_type == "Cash Secured Put":
            st.markdown("""
            **Cash Secured Put**: Sell a put and set aside cash to buy the stock if assigned.
            
            - **Max Loss**: Limited to (strike - premium) if stock goes to zero
            - **Max Gain**: Limited to premium received
            - **Breakeven**: Strike price - premium
            - **When to Use**: Bullish to neutral, willing to buy stock at lower price
            """)
        elif strategy_type == "Naked Call":
            st.markdown("""
            **Naked Call**: Sell a call option without owning the stock (high risk).
            
            - **Max Loss**: Unlimited
            - **Max Gain**: Limited to premium received
            - **Breakeven**: Strike price + premium
            - **When to Use**: Very bearish, high-risk strategy
            """)
        elif strategy_type == "Naked Put":
            st.markdown("""
            **Naked Put**: Sell a put option without cash secured.
            
            - **Max Loss**: Limited to (strike - premium) if stock goes to zero
            - **Max Gain**: Limited to premium received
            - **Breakeven**: Strike price - premium
            - **When to Use**: Bullish, higher leverage version of Cash Secured Put
            """)
    elif category == "Spread Strategies":
        if strategy_type == "Bull Call Spread":
            st.markdown("""
            **Bull Call Spread**: Buy a lower strike call and sell a higher strike call.
            
            - **Max Loss**: Limited to net debit paid
            - **Max Gain**: Difference between strikes minus net debit
            - **Breakeven**: Lower strike + net debit
            - **When to Use**: Moderately bullish, defined risk/reward
            """)
        elif strategy_type == "Bear Put Spread":
            st.markdown("""
            **Bear Put Spread**: Buy a higher strike put and sell a lower strike put.
            
            - **Max Loss**: Limited to net debit paid
            - **Max Gain**: Difference between strikes minus net debit
            - **Breakeven**: Higher strike - net debit
            - **When to Use**: Moderately bearish, defined risk/reward
            """)
        elif strategy_type == "Bull Put Credit Spread":
            st.markdown("""
            **Bull Put Credit Spread**: Sell a higher strike put and buy a lower strike put.
            
            - **Max Loss**: Difference between strikes minus net credit received
            - **Max Gain**: Limited to net credit received
            - **Breakeven**: Higher strike - net credit
            - **When to Use**: Bullish to neutral, profit from time decay
            """)
        elif strategy_type == "Bear Call Credit Spread":
            st.markdown("""
            **Bear Call Credit Spread**: Sell a lower strike call and buy a higher strike call.
            
            - **Max Loss**: Difference between strikes minus net credit received
            - **Max Gain**: Limited to net credit received
            - **Breakeven**: Lower strike + net credit
            - **When to Use**: Bearish to neutral, profit from time decay
            """)
        elif strategy_type == "Calendar Spread":
            st.markdown("""
            **Calendar Spread**: Sell near-term option and buy longer-term option at same strike.
            
            - **Max Loss**: Limited to net debit paid
            - **Max Gain**: Variable, depends on volatility and time decay
            - **When to Use**: Neutral outlook, expecting little movement in near term
            """)
        elif strategy_type == "Poor Man's Covered Call":
            st.markdown("""
            **Poor Man's Covered Call**: Buy deep ITM LEAP call and sell shorter-term OTM call.
            
            - **Max Loss**: Limited to cost of LEAP minus premium received
            - **Max Gain**: LEAP appreciation + premium received
            - **When to Use**: Alternative to covered call with less capital
            """)
        elif strategy_type == "Ratio Back Spread":
            st.markdown("""
            **Ratio Back Spread**: Sell one option and buy multiple options at different strike.
            
            - **Max Loss**: Variable, depends on strikes and ratio
            - **Max Gain**: Potentially unlimited in direction of long options
            - **When to Use**: Expect large move in direction of long options
            """)
    elif category == "Advanced Strategies":
        if strategy_type == "Iron Condor":
            st.markdown("""
            **Iron Condor**: Combination of bull put spread and bear call spread.
            
            - **Max Loss**: Difference between either spread's strikes minus net credit
            - **Max Gain**: Limited to net credit received
            - **Breakeven Points**: Two breakevens - put spread and call spread
            - **When to Use**: Neutral outlook, expect price to stay within range
            """)
        elif strategy_type == "Butterfly":
            st.markdown("""
            **Butterfly**: Buy one lower strike, sell two middle strikes, buy one higher strike.
            
            - **Max Loss**: Limited to net debit paid
            - **Max Gain**: Difference between adjacent strikes minus net debit
            - **Breakeven Points**: Two breakevens on either side of middle strike
            - **When to Use**: Neutral, expect price to be near middle strike at expiration
            """)
        elif strategy_type == "Straddle":
            st.markdown("""
            **Straddle**: Buy a call and put at the same strike.
            
            - **Max Loss**: Limited to total premium paid
            - **Max Gain**: Unlimited (price moves far from strike)
            - **Breakeven Points**: Strike ± total premium
            - **When to Use**: Volatile market, expecting large move either direction
            """)
        elif strategy_type == "Strangle":
            st.markdown("""
            **Strangle**: Buy OTM call and OTM put.
            
            - **Max Loss**: Limited to total premium paid
            - **Max Gain**: Unlimited (price moves far from strikes)
            - **Breakeven Points**: Call strike + total premium OR put strike - total premium
            - **When to Use**: Volatile market, cheaper than straddle but needs larger move
            """)
        elif strategy_type == "Collar":
            st.markdown("""
            **Collar**: Own stock, buy protective put, sell covered call.
            
            - **Max Loss**: Stock price down to put strike - net cost/credit
            - **Max Gain**: Call strike - stock purchase + net cost/credit
            - **When to Use**: Protect existing stock position with minimal cost
            """)
        elif strategy_type == "Diagonal Spread":
            st.markdown("""
            **Diagonal Spread**: Long option with farther expiry + short option with nearer expiry at different strike.
            
            - **Max Loss**: Limited to net debit (for debit diagonal)
            - **Max Gain**: Variable based on price action and time decay
            - **When to Use**: Neutral to directional bias with time decay benefit
            """)
    elif category == "Custom Strategies":
        if "Custom" in strategy_type:
            st.markdown("""
            **Custom Strategy**: Build your own multi-leg strategy.
            
            - Design complex strategies with multiple legs
            - Mix calls, puts, and stock positions
            - Choose different strikes, expirations, and quantities
            - Analyze custom risk/reward profiles
            """)