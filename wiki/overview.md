# Randall's Crypto-Crisis Monitoring Dashboard

## Purpose
A Streamlit-based dashboard for monitoring crypto-crisis indicators and traditional financial markets. This project fetches and visualizes key economic indicators including Federal Reserve data, stablecoin market caps, and various ETFs to help analyze market conditions during periods of crypto-market stress.

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
- `complex_dash.py` - Primary Streamlit application

## Key Commands
- **Setup**: `python -m venv venv && source venv/bin/activate && pip install streamlit yfinance pandas requests altair`
- **Run**: `streamlit run complex_dash.py`
- **Development**: Edit `complex_dash.py` and rerun

## Repository Structure
```
Randall/
├── complex_dash.py          # Main Streamlit dashboard application
├── README.md                # Project overview and instructions
├── email.txt                # Background information and project purpose
├── Activating the virtual environment.txt  # Environment setup guide
├── .git/                    # Git repository metadata
└── .gitnexus/               # GitNexus knowledge graph index (auto-generated)
```
