# app.py
import streamlit as st
import os
import logging
from datetime import datetime

# Import modularized components
from ui.components.header import show_header, load_custom_css, display_welcome
from ui.components.sidebar import setup_sidebar, handle_ticker_selection
from ui.components.strategy_selector import select_strategy
from ui.components.strategy_config import configure_strategy
from ui.components.analysis import analyze_strategy

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=f"logs/app_{datetime.now().strftime('%Y%m%d')}.log",
    filemode='a'
)
logger = logging.getLogger(__name__)

def initialize_session_state():
    """Initialize session state variables."""
    if 'strategy_legs' not in st.session_state:
        st.session_state['strategy_legs'] = None
    if 'current_price' not in st.session_state:
        st.session_state['current_price'] = None
    if 'stock_info' not in st.session_state:
        st.session_state['stock_info'] = None
    if 'theme' not in st.session_state:
        st.session_state['theme'] = "light"  # Default theme

def setup_app():
    """Set up the application with initial configuration."""
    # Set page config
    st.set_page_config(
        page_title="Options Strategy Calculator",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load custom CSS
    load_custom_css()
    
    # Create necessary directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("styles", exist_ok=True)
    os.makedirs("assets", exist_ok=True)
    
    # Initialize session state
    initialize_session_state()

def main():
    """Main application entry point."""
    try:
        # Setup application
        setup_app()
        
        # Setup sidebar
        setup_sidebar()
        
        # Show header
        show_header()
        
        # Handle ticker selection from sidebar
        ticker, current_price, expirations = handle_ticker_selection()
        
        # If ticker and price are valid, configure and analyze strategy
        if ticker and current_price and expirations:
            # Select strategy type
            strategy_category, strategy_type = select_strategy()
            
            # Create columns for main layout
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Configure strategy
                strategy_legs, selected_expiry, days_to_expiry = configure_strategy(
                    ticker, current_price, expirations, strategy_category, strategy_type
                )
                
                # Store in session state
                if strategy_legs:
                    st.session_state['strategy_legs'] = strategy_legs
            
            with col2:
                # Analyze and visualize the strategy
                analyze_strategy(
                    st.session_state.get('strategy_legs'),
                    current_price,
                    selected_expiry if 'selected_expiry' in locals() else None,
                    days_to_expiry if 'days_to_expiry' in locals() else None
                )
        else:
            # Show welcome message
            display_welcome()
    
    except Exception as e:
        st.error(f"Application Error: {str(e)}")
        logger.error(f"Application Error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()