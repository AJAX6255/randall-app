# Randall's Crypto-Crisis Monitoring Dashboard (Refactored)

## Purpose
A refactored Streamlit-based dashboard for monitoring crypto-crisis indicators and traditional financial markets. This version organizes the code into reusable functions for better maintainability and readability.

## Technology Stack
- **Frontend**: Streamlit (Python web framework)
- **Data Processing**: Pandas
- **Data Sources**: 
  - FRED API (Federal Reserve Economic Data)
  - Llama.fi (Stablecoin market data)
  - Yahoo Finance (ETF data via yfinance)
- **Visualization**: Altair (interactive charts)
- **Environment**: Python 3.7+

## Main Entrypoint
- `complex_dash_refactored.py` - Refactored Streamlit application with modular functions

## Key Improvements
- Modular design with separate functions for data fetching, processing, and visualization
- Reusable chart creation functions
- Better organization of constants and configuration
- Improved readability and maintainability

## Key Commands
- **Setup**: `python -m venv venv && source venv/bin/activate && pip install streamlit yfinance pandas requests altair`
- **Run**: `streamlit run complex_dash_refactored.py`
- **Development**: Edit `complex_dash_refactored.py` and rerun

## Repository Structure
```
Randall/
├── complex_dash_refactored.py    # Refactored Streamlit dashboard application
├── complex_dash.py               # Original version (for reference)
├── README.md                     # Project overview and instructions
├── email.txt                     # Background information and project purpose
├── Activating the virtual environment.txt  # Environment setup guide
├── .git/                         # Git repository metadata
└── .gitnexus/                    # GitNexus knowledge graph index (auto-generated)
```
