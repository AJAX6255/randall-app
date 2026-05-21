# Getting Started

## Prerequisites
- Python 3.7+
- Git
- Internet connection (for API data fetching)

## Installation Steps

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd Randall
   ```

2. **Set up virtual environment**:
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   
   # Install dependencies
   pip install streamlit yfinance pandas requests altair
   ```

3. **Run the dashboard**:
   ```bash
   streamlit run complex_dash.py
   ```

## Configuration

The dashboard automatically calculates date ranges for the last 60 business days. Key configuration variables in `complex_dash.py`:

- `FRED_API_KEY` - Get your free API key from [https://fred.stlouisfed.org/](https://fred.stlouisfed.org/)
- `START_DATE` / `END_DATE` - Date range for data fetching (automatically calculated)
- `SERIES` dictionary - Maps display names to FRED series IDs

## Data Sources

- **FRED API**: Federal Reserve Economic Data for SOFR, DFF, and DGS10 series
- **Llama.fi**: Stablecoin market capitalization data
- **Yahoo Finance**: ETF price data via yfinance library
