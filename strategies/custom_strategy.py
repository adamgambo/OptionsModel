# --- strategies/custom_strategy.py ---
"""
Enhanced custom strategy module for the Options Strategy Calculator.
Provides validation, UI, and analysis for custom option strategies.
"""
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import json
import io
import csv
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Any

# Setup logging
logger = logging.getLogger(__name__)

# Keep the original custom_strategy function for compatibility with the factory pattern
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

# Calculate custom strategy metrics function (keep for compatibility)
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

# Add all the new enhanced functions below
def configure_custom_strategy(ticker, current_price, expiration_dates, calls_df, puts_df):
    """
    Enhanced custom strategy builder with templates, validation, and visualization.
    
    Parameters:
        ticker (str): Stock ticker symbol
        current_price (float): Current stock price
        expiration_dates (list): Available expiration dates
        calls_df (DataFrame): Call options chain data
        puts_df (DataFrame): Put options chain data
        
    Returns:
        list: List of strategy leg dictionaries
    """
    st.subheader("Enhanced Custom Strategy Builder")
    
    # Initialize strategy legs in session state if not already there
    if 'custom_strategy_legs' not in st.session_state:
        st.session_state.custom_strategy_legs = []
    
    # Select expiration date for options
    selected_expiry = st.selectbox(
        "Primary Expiration Date", 
        expiration_dates,
        help="This will be the default expiration date for new option legs"
    )
    
    # Calculate days to expiration for the selected date
    expiry_date = datetime.strptime(selected_expiry, "%Y-%m-%d").date()
    today = datetime.now().date()
    days_to_expiry = (expiry_date - today).days
    
    # Strategy templates section
    with st.expander("Strategy Templates", expanded=True):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            template_options = [
                "Start from Scratch",
                "Iron Condor",
                "Iron Butterfly", 
                "Jade Lizard",
                "Reverse Conversion",
                "Diagonal Call Spread",
                "Double Calendar",
                "Ratio Back Spread"
            ]
            
            template = st.selectbox(
                "Select a Template", 
                template_options,
                help="Load a pre-configured strategy template as a starting point"
            )
        
        with col2:
            st.write("")
            st.write("")
            if st.button("Load Template") and template != "Start from Scratch":
                # Generate strategy legs based on the selected template
                st.session_state.custom_strategy_legs = generate_strategy_template(
                    template, current_price, selected_expiry, days_to_expiry
                )
                st.success(f"Loaded {template} template")
                st.experimental_rerun()

    # Strategy analysis preview
    if st.session_state.custom_strategy_legs:
        # Show current strategy configuration
        st.write("### Current Strategy Configuration")
        
        # Create two columns for the preview and metrics
        preview_col, metrics_col = st.columns([3, 2])
        
        with preview_col:
            # Generate a visualization of the strategy payoff
            fig = create_strategy_preview(st.session_state.custom_strategy_legs, current_price)
            st.plotly_chart(fig, use_container_width=True)
        
        with metrics_col:
            # Show key strategy metrics
            strategy_metrics = calculate_strategy_metrics(
                st.session_state.custom_strategy_legs, current_price
            )
            
            # Format and display metrics
            st.metric("Max Profit", 
                     f"${strategy_metrics['max_profit']:.2f}" if strategy_metrics['max_profit'] is not None else "Unlimited")
            
            st.metric("Max Loss", 
                     f"${strategy_metrics['max_loss']:.2f}" if strategy_metrics['max_loss'] is not None else "Unlimited")
            
            if strategy_metrics['breakevens']:
                be_text = ", ".join([f"${be:.2f}" for be in strategy_metrics['breakevens']])
                st.metric("Breakeven Points", be_text)
            else:
                st.metric("Breakeven Points", "None identified")
            
            # Calculate net cost/credit
            net_amount = strategy_metrics['net_amount']
            st.metric("Net Cost/Credit", 
                     f"${abs(net_amount):.2f} {'Credit' if net_amount > 0 else 'Debit'}")
    
    # Save/Load functionality
    with st.expander("Save/Load Strategies"):
        save_tab, load_tab = st.tabs(["Save Current", "Load Saved"])
        
        with save_tab:
            strategy_name = st.text_input("Strategy Name", "My Custom Strategy")
            
            if st.button("Save Strategy"):
                if st.session_state.custom_strategy_legs:
                    # Initialize saved strategies if not already in session
                    if 'saved_strategies' not in st.session_state:
                        st.session_state.saved_strategies = {}
                    
                    # Save the current strategy
                    st.session_state.saved_strategies[strategy_name] = st.session_state.custom_strategy_legs.copy()
                    st.success(f"Strategy '{strategy_name}' saved successfully!")
                else:
                    st.error("Cannot save empty strategy. Add at least one leg first.")
        
        with load_tab:
            if 'saved_strategies' in st.session_state and st.session_state.saved_strategies:
                saved_strategy = st.selectbox(
                    "Select Saved Strategy", 
                    list(st.session_state.saved_strategies.keys())
                )
                
                if st.button("Load Strategy"):
                    st.session_state.custom_strategy_legs = st.session_state.saved_strategies[saved_strategy].copy()
                    st.success(f"Strategy '{saved_strategy}' loaded successfully!")
                    st.experimental_rerun()
            else:
                st.info("No saved strategies found.")
    
    # Export functionality
    with st.expander("Export Strategy"):
        export_format = st.selectbox("Export Format", ["JSON", "CSV"])
        
        if st.button("Export Current Strategy"):
            if st.session_state.custom_strategy_legs:
                if export_format == "JSON":
                    data = json.dumps(st.session_state.custom_strategy_legs, indent=2)
                    mime = "application/json"
                else:  # CSV
                    output = io.StringIO()
                    writer = csv.writer(output)
                    
                    # Write header
                    writer.writerow(["Leg", "Type", "Position", "Strike", "Expiry", "Quantity", "Price"])
                    
                    # Write data
                    for i, leg in enumerate(st.session_state.custom_strategy_legs):
                        writer.writerow([
                            i+1,
                            leg.get('type', ''),
                            leg.get('position', ''),
                            leg.get('strike', ''),
                            leg.get('expiry', ''),
                            leg.get('quantity', ''),
                            leg.get('price', '')
                        ])
                    
                    data = output.getvalue()
                    mime = "text/csv"
                
                # Create download button
                st.download_button(
                    label=f"Download as {export_format}",
                    data=data,
                    file_name=f"custom_strategy.{export_format.lower()}",
                    mime=mime
                )
            else:
                st.error("No strategy to export. Add at least one leg first.")
    
    # Display current strategy legs
    leg_container = st.container()
    with leg_container:
        for i, leg in enumerate(st.session_state.custom_strategy_legs):
            # Create a container for each leg with a unique key
            with st.container():
                # Define CSS class for the leg card based on leg properties
                leg_type = leg.get('type', 'unknown')
                position = leg.get('position', 'unknown')
                leg_class = f"{leg_type}-leg {position}-position"
                
                # Create a visually distinct card for the leg
                st.markdown(f"""
                <div class="leg-card {leg_class}">
                    <h4>Leg {i+1}: {position.capitalize()} {leg_type.capitalize()}</h4>
                </div>
                """, unsafe_allow_html=True)
                
                # Create three columns for leg configuration
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    # First column - Type and Position
                    new_type = st.selectbox(
                        "Instrument Type", 
                        ["call", "put", "stock"], 
                        index=["call", "put", "stock"].index(leg_type) if leg_type in ["call", "put", "stock"] else 0,
                        key=f"type_{i}"
                    )
                    
                    new_position = st.selectbox(
                        "Position", 
                        ["long", "short"], 
                        index=["long", "short"].index(position) if position in ["long", "short"] else 0,
                        key=f"pos_{i}"
                    )
                
                with col2:
                    # Second column - Strike, Quantity, Expiry
                    new_quantity = st.number_input(
                        "Quantity", 
                        min_value=1, 
                        value=leg.get('quantity', 1),
                        key=f"qty_{i}"
                    )
                    
                    if new_type != "stock":
                        # For options, we need strike and expiry
                        if leg_type == new_type:  # Only get available strikes if type hasn't changed
                            chain_df = calls_df if new_type == "call" else puts_df
                            available_strikes = sorted(chain_df['strike'].unique().tolist())
                            
                            # Find closest strike to current leg or ATM
                            if 'strike' in leg:
                                default_index = min(range(len(available_strikes)), 
                                                  key=lambda i: abs(available_strikes[i] - leg['strike']))
                            else:
                                default_index = min(range(len(available_strikes)), 
                                                  key=lambda i: abs(available_strikes[i] - current_price))
                            
                            # Strike selection with formatting
                            selected_strike_index = st.select_slider(
                                "Strike",
                                options=range(len(available_strikes)),
                                value=default_index,
                                format_func=lambda i: f"${available_strikes[i]:.2f} {'(ITM)' if (new_type == 'call' and available_strikes[i] < current_price) or (new_type == 'put' and available_strikes[i] > current_price) else '(OTM)' if (new_type == 'call' and available_strikes[i] > current_price) or (new_type == 'put' and available_strikes[i] < current_price) else '(ATM)'}",
                                key=f"strike_{i}"
                            )
                            new_strike = available_strikes[selected_strike_index]
                        else:
                            # If type changed, just use a number input
                            new_strike = st.number_input(
                                "Strike Price", 
                                value=leg.get('strike', current_price),
                                step=0.5,
                                key=f"strike_{i}"
                            )
                        
                        # Expiry selection
                        new_expiry = st.selectbox(
                            "Expiration", 
                            expiration_dates,
                            index=expiration_dates.index(leg.get('expiry', selected_expiry)) if leg.get('expiry', selected_expiry) in expiration_dates else 0,
                            key=f"expiry_{i}"
                        )
                
                with col3:
                    # Third column - Action buttons
                    st.write("")
                    st.write("")
                    # Button to remove this leg
                    if st.button("🗑️ Remove", key=f"remove_{i}"):
                        st.session_state.custom_strategy_legs.pop(i)
                        st.experimental_rerun()
                
                # Advanced options in an expander
                with st.expander("Advanced Options"):
                    # Allow setting custom price
                    custom_price = st.checkbox(
                        "Custom Entry Price", 
                        value='price' in leg,
                        key=f"use_custom_{i}"
                    )
                    
                    if custom_price:
                        new_price = st.number_input(
                            "Entry Price", 
                            min_value=0.01, 
                            value=leg.get('price', 1.0),
                            step=0.05,
                            format="%.2f",
                            key=f"price_{i}"
                        )
                    else:
                        new_price = None
                    
                    # Allow setting custom IV
                    if new_type != "stock":
                        custom_iv = st.checkbox(
                            "Custom Implied Volatility", 
                            value='iv' in leg,
                            key=f"use_iv_{i}"
                        )
                        
                        if custom_iv:
                            new_iv = st.slider(
                                "Implied Volatility", 
                                min_value=0.05, 
                                max_value=1.50, 
                                value=leg.get('iv', 0.30),
                                step=0.05,
                                format="%.2f",
                                key=f"iv_{i}"
                            )
                        else:
                            new_iv = None
                
                # Update leg with new values
                updated_leg = {
                    'type': new_type,
                    'position': new_position,
                    'quantity': new_quantity
                }
                
                if new_type != "stock":
                    updated_leg['strike'] = new_strike
                    updated_leg['expiry'] = new_expiry
                
                if custom_price:
                    updated_leg['price'] = new_price
                
                if new_type != "stock" and custom_iv:
                    updated_leg['iv'] = new_iv
                
                # Update the leg in the strategy
                st.session_state.custom_strategy_legs[i] = updated_leg
                
                # Add a divider between legs
                st.markdown("---")
    
    # Strategy validation
    if st.session_state.custom_strategy_legs:
        validation_result, issues = validate_custom_strategy(
            st.session_state.custom_strategy_legs, current_price
        )
        
        if issues:
            with st.expander("Strategy Validation", expanded=True):
                for issue in issues:
                    if issue.startswith("⚠️"):
                        st.warning(issue)
                    else:
                        st.info(issue)
        
        # Strategy insights
        insights, recommendations = analyze_strategy_characteristics(
            st.session_state.custom_strategy_legs
        )
        
        with st.expander("Strategy Insights", expanded=True):
            for insight in insights:
                st.markdown(insight)
            
            if recommendations:
                st.subheader("Recommendations:")
                for rec in recommendations:
                    st.markdown(f"- {rec}")
    
    # Add new leg button
    max_legs = 8  # Maximum number of legs
    if len(st.session_state.custom_strategy_legs) < max_legs:
        if st.button("➕ Add New Leg", use_container_width=True):
            # Create a new leg with default values
            new_leg = {
                'type': 'call',
                'position': 'long',
                'strike': current_price,
                'expiry': selected_expiry,
                'quantity': 1
            }
            
            st.session_state.custom_strategy_legs.append(new_leg)
            st.experimental_rerun()
    else:
        st.warning(f"Maximum of {max_legs} legs reached")
    
    # Add CSS for better leg styling
    st.markdown("""
    <style>
    .leg-card {
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .call-leg {
        border-left: 5px solid #4CAF50;
    }
    .put-leg {
        border-left: 5px solid #F44336;
    }
    .stock-leg {
        border-left: 5px solid #2196F3;
    }
    .long-position {
        background-color: rgba(76, 175, 80, 0.1);
    }
    .short-position {
        background-color: rgba(244, 67, 54, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    return st.session_state.custom_strategy_legs

def generate_strategy_template(template_name, current_price, expiration, days_to_expiry):
    """
    Generate a pre-configured strategy template.
    
    Parameters:
        template_name (str): Name of the template
        current_price (float): Current stock price
        expiration (str): Expiration date
        days_to_expiry (int): Days to expiration
        
    Returns:
        list: List of strategy leg dictionaries
    """
    legs = []
    
    # Round current price to nearest 5 for cleaner strikes
    rounded_price = round(current_price / 5) * 5
    
    if template_name == "Iron Condor":
        # Classical iron condor with 10% OTM short strikes and 5% protection
        width = max(5, round(current_price * 0.05 / 5) * 5)  # 5% width, minimum $5
        
        legs = [
            # Long put (lowest strike)
            {
                'type': 'put',
                'position': 'long',
                'strike': rounded_price - (width * 2),
                'expiry': expiration,
                'quantity': 1
            },
            # Short put
            {
                'type': 'put',
                'position': 'short',
                'strike': rounded_price - width,
                'expiry': expiration,
                'quantity': 1
            },
            # Short call
            {
                'type': 'call',
                'position': 'short',
                'strike': rounded_price + width,
                'expiry': expiration,
                'quantity': 1
            },
            # Long call (highest strike)
            {
                'type': 'call',
                'position': 'long',
                'strike': rounded_price + (width * 2),
                'expiry': expiration,
                'quantity': 1
            }
        ]
    
    elif template_name == "Iron Butterfly":
        # Iron butterfly with ATM short options and 10% OTM long options
        width = max(5, round(current_price * 0.1 / 5) * 5)  # 10% width, minimum $5
        
        legs = [
            # Long put (lowest strike)
            {
                'type': 'put',
                'position': 'long',
                'strike': rounded_price - width,
                'expiry': expiration,
                'quantity': 1
            },
            # Short put (ATM)
            {
                'type': 'put',
                'position': 'short',
                'strike': rounded_price,
                'expiry': expiration,
                'quantity': 1
            },
            # Short call (ATM)
            {
                'type': 'call',
                'position': 'short',
                'strike': rounded_price,
                'expiry': expiration,
                'quantity': 1
            },
            # Long call (highest strike)
            {
                'type': 'call',
                'position': 'long',
                'strike': rounded_price + width,
                'expiry': expiration,
                'quantity': 1
            }
        ]
    
    elif template_name == "Jade Lizard":
        # Jade Lizard: Short put + short call spread
        width = max(5, round(current_price * 0.05 / 5) * 5)  # 5% width, minimum $5
        
        legs = [
            # Short put
            {
                'type': 'put',
                'position': 'short',
                'strike': rounded_price - width,
                'expiry': expiration,
                'quantity': 1
            },
            # Short call
            {
                'type': 'call',
                'position': 'short',
                'strike': rounded_price + width,
                'expiry': expiration,
                'quantity': 1
            },
            # Long call (for protection)
            {
                'type': 'call',
                'position': 'long',
                'strike': rounded_price + (width * 2),
                'expiry': expiration,
                'quantity': 1
            }
        ]
    
    elif template_name == "Reverse Conversion":
        # Reverse conversion: Short stock + long call + short put, all at the money
        legs = [
            # Short stock
            {
                'type': 'stock',
                'position': 'short',
                'quantity': 100  # 100 shares
            },
            # Long call
            {
                'type': 'call',
                'position': 'long',
                'strike': rounded_price,
                'expiry': expiration,
                'quantity': 1
            },
            # Short put
            {
                'type': 'put',
                'position': 'short',
                'strike': rounded_price,
                'expiry': expiration,
                'quantity': 1
            }
        ]
    
    elif template_name == "Diagonal Call Spread":
        # Diagonal call spread: Long ITM LEAP call + short OTM near-term call
        # Find an earlier expiration date for the short leg
        far_expiry = expiration
        
        legs = [
            # Long ITM call (LEAP)
            {
                'type': 'call',
                'position': 'long',
                'strike': rounded_price * 0.9,
                'expiry': far_expiry,
                'quantity': 1
            },
            # Short OTM call (near-term)
            {
                'type': 'call',
                'position': 'short',
                'strike': rounded_price * 1.1,
                'expiry': far_expiry,  # In a real scenario, this would be a nearer expiration
                'quantity': 1
            }
        ]
    
    elif template_name == "Double Calendar":
        # Double calendar: Calendar spread with both calls and puts
        far_expiry = expiration
        
        legs = [
            # Long put (far expiry)
            {
                'type': 'put',
                'position': 'long',
                'strike': rounded_price,
                'expiry': far_expiry,
                'quantity': 1
            },
            # Short put (near expiry) - using same expiry for demo
            {
                'type': 'put',
                'position': 'short',
                'strike': rounded_price,
                'expiry': far_expiry,  # In a real scenario, this would be a nearer expiration
                'quantity': 1
            },
            # Long call (far expiry)
            {
                'type': 'call',
                'position': 'long',
                'strike': rounded_price,
                'expiry': far_expiry,
                'quantity': 1
            },
            # Short call (near expiry) - using same expiry for demo
            {
                'type': 'call',
                'position': 'short',
                'strike': rounded_price,
                'expiry': far_expiry,  # In a real scenario, this would be a nearer expiration
                'quantity': 1
            }
        ]
    
    elif template_name == "Ratio Back Spread":
        # Call ratio back spread: Short 1 ATM call, long 2 OTM calls
        width = max(5, round(current_price * 0.05 / 5) * 5)  # 5% width, minimum $5
        
        legs = [
            # Short ATM call
            {
                'type': 'call',
                'position': 'short',
                'strike': rounded_price,
                'expiry': expiration,
                'quantity': 1
            },
            # Long OTM call #1
            {
                'type': 'call',
                'position': 'long',
                'strike': rounded_price + width,
                'expiry': expiration,
                'quantity': 1
            },
            # Long OTM call #2
            {
                'type': 'call',
                'position': 'long',
                'strike': rounded_price + width,
                'expiry': expiration,
                'quantity': 1
            }
        ]
    
    return legs

def validate_custom_strategy(strategy_legs, current_price):
    """
    Validate a custom strategy configuration and provide feedback.
    
    Parameters:
        strategy_legs (list): List of leg dictionaries
        current_price (float): Current stock price
        
    Returns:
        tuple: (is_valid, list of issues)
    """
    if not strategy_legs:
        return False, ["Strategy must have at least one leg"]
    
    # Check for common issues
    issues = []
    
    # Count leg types
    call_legs = [leg for leg in strategy_legs if leg.get('type') == 'call']
    put_legs = [leg for leg in strategy_legs if leg.get('type') == 'put']
    stock_legs = [leg for leg in strategy_legs if leg.get('type') == 'stock']
    
    # Check for complexity
    if len(strategy_legs) > 4:
        issues.append("Note: Complex strategy with 5+ legs may have higher commission costs")
    
    # Check for potential problems
    if len(call_legs) > 0 and len(put_legs) > 0:
        # Mixed option types - valid but flag as complex
        issues.append("Note: Mixed option types (calls and puts) - more complex risk profile")
    
    # Check for naked short options (no protection)
    short_calls = [leg for leg in call_legs if leg.get('position') == 'short']
    long_calls = [leg for leg in call_legs if leg.get('position') == 'long']
    short_puts = [leg for leg in put_legs if leg.get('position') == 'short']
    long_puts = [leg for leg in put_legs if leg.get('position') == 'long']
    
    # Check for naked calls (unlimited risk)
    if short_calls and not long_calls and not any(l.get('type') == 'stock' and l.get('position') == 'long' for l in strategy_legs):
        issues.append("⚠️ Warning: Strategy includes naked call(s), which have unlimited risk")
    
    # Check for undefined risk spreads
    if len(short_calls) > len(long_calls):
        issues.append("⚠️ Warning: More short calls than long calls creates undefined risk")
    
    if len(short_puts) > len(long_puts):
        issues.append("⚠️ Warning: More short puts than long puts creates undefined risk")
    
    # Check if all legs use the same expiration
    expirations = set()
    for leg in strategy_legs:
        if leg.get('type') in ['call', 'put'] and 'expiry' in leg:
            expirations.add(leg['expiry'])
    
    if len(expirations) > 1:
        issues.append("Note: Strategy uses multiple expiration dates (diagonal/calendar spread)")
    
    # Try to calculate estimated max loss
    try:
        # Generate wide price range to capture extremes
        price_range = np.linspace(current_price * 0.1, current_price * 3, 200)
        payoffs = calculate_strategy_payoff(strategy_legs, price_range, current_price)
        max_loss = min(payoffs)
        
        if max_loss < -1000:
            issues.append(f"⚠️ Warning: Estimated maximum loss is ${abs(max_loss):.2f}, which exceeds $1,000")
    except Exception as e:
        pass
    
    # Return validation result
    is_valid = not any(issue.startswith("⚠️") for issue in issues)
    
    return is_valid, issues

def analyze_strategy_characteristics(strategy_legs):
    """
    Analyze a custom strategy and provide insights.
    
    Parameters:
        strategy_legs (list): List of leg dictionaries
        
    Returns:
        tuple: (insights, recommendations)
    """
    # Identify strategy characteristics
    characteristics = {
        "bullish": 0,
        "bearish": 0,
        "neutral": 0,
        "volatility": 0,  # Positive for long volatility, negative for short
        "theta": 0,      # Positive for positive theta, negative for negative theta
        "complexity": len(strategy_legs)  # Base complexity on number of legs
    }
    
    # Analyze each leg's contribution
    for leg in strategy_legs:
        leg_type = leg.get('type', '')
        position = leg.get('position', '')
        quantity = leg.get('quantity', 1)
        
        if leg_type == 'call':
            if position == 'long':
                characteristics["bullish"] += 1 * quantity
                characteristics["volatility"] += 1 * quantity
                characteristics["theta"] -= 1 * quantity
            else:  # short
                characteristics["bearish"] += 1 * quantity
                characteristics["volatility"] -= 1 * quantity
                characteristics["theta"] += 1 * quantity
                
        elif leg_type == 'put':
            if position == 'long':
                characteristics["bearish"] += 1 * quantity
                characteristics["volatility"] += 1 * quantity
                characteristics["theta"] -= 1 * quantity
            else:  # short
                characteristics["bullish"] += 1 * quantity
                characteristics["volatility"] -= 1 * quantity
                characteristics["theta"] += 1 * quantity
                
        elif leg_type == 'stock':
            if position == 'long':
                characteristics["bullish"] += 2 * (quantity / 100)  # Normalize for 100 shares
            else:  # short
                characteristics["bearish"] += 2 * (quantity / 100)
    
    # Identify overall strategy type
    if characteristics["bullish"] > characteristics["bearish"] + 1:
        strategy_type = "Bullish"
    elif characteristics["bearish"] > characteristics["bullish"] + 1:
        strategy_type = "Bearish"
    else:
        strategy_type = "Neutral"
    
    # Adjust for volatility expectation
    if characteristics["volatility"] >= 2:
        strategy_type += " / Long Volatility"
    elif characteristics["volatility"] <= -2:
        strategy_type += " / Short Volatility"
    
    # Generate insights
    insights = [f"**Strategy Outlook:** {strategy_type}"]
    
    if characteristics["theta"] > 0:
        insights.append("✓ **Positive theta:** Strategy benefits from time decay")
    elif characteristics["theta"] < 0:
        insights.append("⚠️ **Negative theta:** Strategy loses value over time")
    
    if characteristics["complexity"] >= 6:
        insights.append("⚠️ **Complex strategy:** Consider simpler alternatives for similar exposure")
    
    # Check for specific strategy patterns
    leg_count = len(strategy_legs)
    call_count = len([leg for leg in strategy_legs if leg.get('type') == 'call'])
    put_count = len([leg for leg in strategy_legs if leg.get('type') == 'put'])
    
    if leg_count == 4 and call_count == 2 and put_count == 2:
        insights.append("📊 **Recognized pattern:** Strategy resembles an Iron Condor or Iron Butterfly")
    
    # Provide recommendations
    recommendations = []
    
    if characteristics["bullish"] > 0 and characteristics["bearish"] > 0 and abs(characteristics["bullish"] - characteristics["bearish"]) < 2:
        recommendations.append("Consider making your strategy more directional for a clearer exposure")
    
    if len(strategy_legs) > 4:
        recommendations.append("Consider simplifying the strategy to reduce commission costs")
    
    if characteristics["theta"] < 0 and characteristics["volatility"] > 0:
        recommendations.append("Be mindful of time decay - consider setting a clear exit plan")
    
    return insights, recommendations

def create_strategy_preview(strategy_legs, current_price):
    """
    Create a preview visualization of the strategy payoff.
    
    Parameters:
        strategy_legs (list): List of leg dictionaries
        current_price (float): Current stock price
        
    Returns:
        go.Figure: Plotly figure with strategy visualization
    """
    # Generate price range centered around current price
    price_range_pct = 0.3  # 30% up and down
    min_price = current_price * (1 - price_range_pct)
    max_price = current_price * (1 + price_range_pct)
    price_range = np.linspace(min_price, max_price, 100)
    
    # Calculate payoff at expiration
    payoffs = calculate_strategy_payoff(strategy_legs, price_range, current_price)
    
    # Create figure
    fig = go.Figure()
    
    # Add payoff curve
    fig.add_trace(go.Scatter(
        x=price_range, 
        y=payoffs,
        mode='lines',
        name='P/L at Expiration',
        line=dict(color='blue', width=2)
    ))
    
    # Add zero line
    fig.add_shape(
        type="line",
        x0=min(price_range), x1=max(price_range),
        y0=0, y1=0,
        line=dict(color="black", width=1)
    )
    
    # Add current price line
    fig.add_shape(
        type="line",
        x0=current_price, x1=current_price,
        y0=min(min(payoffs), 0) * 1.1 if min(payoffs) < 0 else min(0, min(payoffs)), 
        y1=max(max(payoffs), 0) * 1.1 if max(payoffs) > 0 else max(0, max(payoffs)),
        line=dict(color="red", width=1, dash="dash")
    )
    
    # Find breakeven points
    breakeven_points = find_breakeven_points(price_range, payoffs)
    
    # Add breakeven lines
    for be in breakeven_points:
        fig.add_shape(
            type="line",
            x0=be, x1=be,
            y0=min(min(payoffs), 0) * 1.1 if min(payoffs) < 0 else min(0, min(payoffs)), 
            y1=max(max(payoffs), 0) * 1.1 if max(payoffs) > 0 else max(0, max(payoffs)),
            line=dict(color="green", width=1, dash="dash")
        )
    
    # Update layout
    fig.update_layout(
        title="Strategy Payoff at Expiration",
        xaxis_title="Stock Price",
        yaxis_title="Profit/Loss ($)",
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        hovermode="x unified"
    )
    
    return fig

def calculate_strategy_metrics(strategy_legs, current_price):
    """
    Calculate key metrics for a strategy.
    
    Parameters:
        strategy_legs (list): List of leg dictionaries
        current_price (float): Current stock price
        
    Returns:
        dict: Dictionary with strategy metrics
    """
    # Initialize metrics
    metrics = {
        'max_profit': None,
        'max_loss': None,
        'breakevens': [],
        'net_amount': 0
    }
    
    if not strategy_legs:
        return metrics
    
    # Generate a wide price range to capture extreme values
    price_range = np.linspace(current_price * 0.1, current_price * 3, 300)
    
    # Calculate payoff at expiration
    payoffs = calculate_strategy_payoff(strategy_legs, price_range, current_price)
    
    # Find max profit and loss
    max_profit = max(payoffs)
    min_profit = min(payoffs)
    
    # Check if profit is potentially unlimited
    if max_profit > 5000 and payoffs[-1] > 0.95 * max_profit:
        metrics['max_profit'] = None  # Unlimited upside
    else:
        metrics['max_profit'] = max_profit
    
    # Check if loss is potentially unlimited
    if min_profit < -5000 and (payoffs[0] < 0.95 * min_profit or payoffs[-1] < 0.95 * min_profit):
        metrics['max_loss'] = None  # Unlimited downside
    else:
        metrics['max_loss'] = abs(min_profit)
    
    # Find breakeven points
    metrics['breakevens'] = find_breakeven_points(price_range, payoffs)
    
    # Calculate net debit/credit
    for leg in strategy_legs:
        leg_type = leg.get('type', '')
        position = leg.get('position', '')
        price = leg.get('price', 0)
        quantity = leg.get('quantity', 1)
        
        # Determine contract multiplier
        multiplier = 100 if leg_type in ['call', 'put'] else 1
        
        # Calculate effect on net amount
        if position == 'long':
            metrics['net_amount'] -= price * quantity * multiplier
        else:  # short
            metrics['net_amount'] += price * quantity * multiplier
    
    return metrics

def calculate_strategy_payoff(strategy_legs, price_range, current_price=None):
    """
    Calculate the payoff of a strategy over a range of prices at expiration.
    
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