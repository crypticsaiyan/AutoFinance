"""
AutoFinance CLI - Main Entry Point
Landing Menu → Unified Dashboard (Textual)
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from landing import main as landing_main
from dashboard import main as dashboard_main


def main():
    """Main application entry point."""
    # Show landing page menu
    choice = landing_main()
    
    if choice == "dashboard" or choice == "d":
        # Start unified dashboard (Textual-based, high performance)
        dashboard_main()
    
    elif choice == "quit" or choice == "q" or choice is None:
        print("Goodbye!")
    
    else:
        # Default: go to dashboard
        print("Starting dashboard...")
        dashboard_main()


if __name__ == "__main__":
    main()
