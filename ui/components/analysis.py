# ui/components/analysis.py
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import logging
from scipy.stats import norm

from utils.calculation import (
    calculate_strategy_payoff, 
    calculate_strategy_current_value,
    find_breakeven_points,
    calculate_strategy_volatility
)
from utils.error_handlers import handle_ui_error
from utils.formatters import format_price

logger = logging.getLogger(__name__)

@handle_ui_error
def analyze_strategy(strategy_legs, current_price, expiry_date, days_to_expiry):
    """
    Analyze and visualize the strategy.
    
    Parameters:
        strategy_legs (list): List of strategy leg dictionaries
        current_price (float): Current stock price
        expiry_date (str): Expiration date string
        days_to_expiry (int): Days to expiration
    """
    if not strategy_legs:
        st.info("Configure your options strategy to see analysis here")
        return
    
    # Create tabs for different analysis views
    tabs = st.tabs([
        "📈 Payoff Diagram", 
        "📊 Risk Analysis", 
        "⏱️ Time Decay", 
        "📱 Mobile View",
        "💼 Position Analysis"
    ])
    
    with tabs[0]:  # Payoff Diagram
        display_payoff_diagram(strategy_legs, current_price, days_to_expiry)
    
    with tabs[1]:  # Risk Analysis
        display_risk_analysis(strategy_legs, current_price, days_to_expiry)
    
    with tabs[2]:  # Time Decay
        display_time_decay_analysis(strategy_legs, current_price, days_to_expiry)
    
    with tabs[3]:  # Mobile View
        display_mobile_summary(strategy_legs, current_price, days_to_expiry)
    
    with tabs[4]:  # Position Analysis
        display_position_analysis(strategy_legs, current_price)

def display_payoff_diagram(strategy_legs, current_price, days_to_expiry):
    """
    Display the payoff diagram for the strategy.
    
    Parameters:
        strategy_legs (list): List of strategy leg dictionaries
        current_price (float): Current stock price
        days_to_expiry (int): Days to expiration
    """
    try:
        st.subheader("Profit/Loss Analysis")
        
        # Generate price range with dynamic width based on volatility
        volatility = calculate_strategy_volatility(strategy_legs)
        price_range_pct = min(max(0.25, volatility * 2), 0.5)  # Adjust based on volatility
        min_price = current_price * (1 - price_range_pct)
        max_price = current_price * (1 + price_range_pct)
        price_range = np.linspace(min_price, max_price, 100)
        
        # Add custom price range input
        with st.expander("Customize Price Range"):
            custom_range = st.slider(
                "Price Range (%)", 
                min_value=10, 
                max_value=100, 
                value=int(price_range_pct * 100),
                step=5
            )
            if custom_range != int(price_range_pct * 100):
                price_range_pct = custom_range / 100
                min_price = current_price * (1 - price_range_pct)
                max_price = current_price * (1 + price_range_pct)
                price_range = np.linspace(min_price, max_price, 100)
        
        # Calculate P/L at expiration
        expiry_payoffs = calculate_strategy_payoff(strategy_legs, price_range, current_price)
        
        # Calculate P/L before expiration if applicable
        current_values = None
        if days_to_expiry > 0:
            # Calculate current values
            current_values = calculate_strategy_current_value(
                strategy_legs, price_range, days_to_expiry, volatility=volatility
            )
        
        # Create dynamic plot
        fig = go.Figure()
        
        # Add P/L at expiration
        fig.add_trace(go.Scatter(
            x=price_range, 
            y=expiry_payoffs,
            mode='lines',
            name='P/L at Expiration',
            line=dict(color='blue', width=3)
        ))
        
        # Add current P/L if available
        if current_values is not None:
            fig.add_trace(go.Scatter(
                x=price_range, 
                y=current_values,
                mode='lines',
                name=f'Current Value (T-{days_to_expiry})',
                line=dict(color='green', width=2, dash='dash')
            ))
        
        # Add zero line
        fig.add_shape(
            type="line",
            x0=min_price, x1=max_price,
            y0=0, y1=0,
            line=dict(color="black", width=1)
        )
        
        # Add current price line
        fig.add_shape(
            type="line",
            x0=current_price, x1=current_price,
            y0=min(min(expiry_payoffs), 0) * 1.1 if min(expiry_payoffs) < 0 else -10, 
            y1=max(max(expiry_payoffs), 0) * 1.1,
            line=dict(color="red", width=2, dash="dash")
        )
        
        # Find breakeven points
        breakeven_points = find_breakeven_points(price_range, expiry_payoffs)
        
        # Add breakeven annotations
        for i, be in enumerate(breakeven_points):
            fig.add_shape(
                type="line",
                x0=be, x1=be,
                y0=min(min(expiry_payoffs), 0) * 1.1 if min(expiry_payoffs) < 0 else -10, 
                y1=max(max(expiry_payoffs), 0) * 1.1,
                line=dict(color="green", width=1, dash="dash")
            )
            
            fig.add_annotation(
                x=be,
                y=0,
                text=f"BE: ${be:.2f}",
                showarrow=True,
                arrowhead=1
            )
        
        # Calculate key metrics
        max_profit = max(expiry_payoffs)
        max_loss = min(expiry_payoffs)
        profit_at_current = calculate_strategy_payoff(strategy_legs, [current_price], current_price)[0]
        
        # Add metrics annotation
        fig.add_annotation(
            x=min_price + (max_price - min_price) * 0.05,
            y=max(max(expiry_payoffs), 0) * 0.9,
            text=f"<b>Max Profit:</b> ${max_profit:.2f}<br><b>Max Loss:</b> ${max_loss:.2f}<br><b>Current P/L:</b> ${profit_at_current:.2f}",
            showarrow=False,
            align="left",
            bordercolor="black",
            borderwidth=1,
            bgcolor="white",
            opacity=0.8
        )
        
        # Update layout with enhanced styling
        fig.update_layout(
            title="Profit/Loss Analysis",
            xaxis_title="Stock Price",
            yaxis_title="Profit/Loss ($)",
            hovermode="x unified",
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            ),
            margin=dict(l=20, r=20, t=50, b=20),
            height=500
        )
        
        # Add range slider for interactive exploration
        fig.update_xaxes(
            rangeslider_visible=True,
            rangeslider_thickness=0.05
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add key metrics summary with improved visualization
        st.subheader("Key Metrics")
        
        metric_cols = st.columns(4)
        with metric_cols[0]:
            st.metric(
                "Max Profit", 
                f"${max_profit:.2f}", 
                delta=None,
                help="Maximum possible profit at expiration"
            )
        
        with metric_cols[1]:
            st.metric(
                "Max Loss", 
                f"${abs(max_loss):.2f}", 
                delta=None,
                help="Maximum possible loss at expiration"
            )
        
        with metric_cols[2]:
            if abs(max_loss) > 0:
                risk_reward = max_profit / abs(max_loss)
                st.metric(
                    "Risk/Reward", 
                    f"1:{risk_reward:.2f}", 
                    delta=None,
                    help="Ratio of potential reward to risk"
                )
            else:
                st.metric("Risk/Reward", "∞", delta=None)
        
        with metric_cols[3]:
            breakeven_str = ", ".join([f"${be:.2f}" for be in breakeven_points]) if breakeven_points else "N/A"
            st.metric(
                "Breakeven", 
                breakeven_str, 
                delta=None,
                help="Price points where P/L equals zero"
            )
        
    except Exception as e:
        st.error(f"Error creating payoff chart: {str(e)}")
        logger.error(f"Error creating payoff chart: {str(e)}", exc_info=True)

def display_risk_analysis(strategy_legs, current_price, days_to_expiry):
    """Display risk analysis for the strategy."""
    # Implementation for risk analysis tab
    pass

def display_time_decay_analysis(strategy_legs, current_price, days_to_expiry):
    """Display time decay analysis for the strategy."""
    # Implementation for time decay analysis tab
    pass

def display_mobile_summary(strategy_legs, current_price, days_to_expiry):
    """Display mobile-optimized summary of the strategy."""
    # Implementation for mobile view tab
    pass

def display_position_analysis(strategy_legs, current_price):
    """Display position analysis for the strategy."""
    # Implementation for position analysis tab
    pass