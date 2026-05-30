# Randall's Crypto-Crisis Monitoring Dashboard

A Streamlit-based dashboard for monitoring crypto-crisis indicators and traditional financial markets. This project fetches and visualizes key economic indicators including Federal Reserve data, stablecoin market caps, and various ETFs to help analyze market conditions during periods of crypto-market stress.

## Overview

This dashboard was created to monitor crypto-crisis situations by tracking:
- Federal Reserve Economic Data (FRED) series: SOFR, Federal Funds Rate (DFF), 10-Year Treasury Yield (DGS10)
- Stablecoin market capitalization data from Llama.fi
- Various ETFs representing different market segments:
  - SPY (S&P 500 ETF)
  - VIX (Volatility Index)
  - GLD (Gold ETF)
  - VTIP (Inflation-Protected Treasuries ETF)
  - TLT (Long-Term Treasury ETF)
  - CRCL (Circle Stablecoin ETF)
  - DRAM (Memory/AI Data Center Proxy ETF)
  - JNK (High-Yield Bond ETF)
  - EMB (Emerging Market Bond ETF)

## Features

- **Automatic Data Fetching**: Retrieves latest data from FRED API and stablecoin market cap APIs
- **Interactive Visualizations**: Uses Altair and Streamlit for interactive charts
- **Regime Analysis**: Includes logic for identifying oil supply vs. demand shocks
- **Spread Calculations**: Computes SOFR-FFR spread and other key indicators
- **Missing Data Handling**: Forward-fills missing values for continuity
- **Business Day Alignment**: Resamples data to business days for consistency

## Files in Repository

- `complex_dash.py` - Main Streamlit dashboard application
- `email.txt` - Background information and explanation of the project's purpose
- `Activating the virtual environment.txt` - Instructions for setting up the Python environment
- `.gitnexus/` - GitNexus knowledge graph index (auto-generated)
- `.git/` - Git repository metadata

## Installation & Setup

### Prerequisites
- Python 3.7+
- Git
- Internet connection (for API data fetching)

### Setup Instructions

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd Randall
   ```

2. **Set up virtual environment** (refer to `Activating the virtual environment.txt` for detailed instructions):
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt  # If requirements.txt exists
   # Or install manually:
   pip install streamlit yfinance pandas requests altair
   ```

3. **Run the dashboard**:
   ```bash
   streamlit run complex_dash_refactored.py
   ```

## Usage

Once running, the dashboard will display:

1. **10-Year Treasury Yield (DGS10)** - Shows the yield on 10-year US Treasury bonds
2. **SOFR vs FFR (Zoomed Spread View)** - Compares Secured Overnight Financing Rate with Federal Funds Rate
3. **SOFR Spread (SOFR - FFR)** - Visualizes the spread between SOFR and Federal Funds Rate
4. **Stablecoin Market Cap (USD)** - Tracks the total market capitalization of stablecoins
5. **Stablecoin Market Cap (% Change)** - Shows percentage changes in stablecoin market cap
6. **Individual ETF Charts** - Displays price movements for:
   - VIX Index (Volatility)
   - SPY ETF (S&P 500)
   - GLD ETF (Gold)
   - VTIP ETF (Inflation-Protected Treasuries)
   - TLT ETF (Long-Term Treasuries)
   - CRCL ETF (Circle Stablecoin)
   - DRAM ETF (Memory/AI Data Center)
   - JNK ETF (High-Yield Bonds)
   - EMB ETF (Emerging Market Bonds)

## Data Sources

- **FRED API**: Federal Reserve Economic Data for SOFR, DFF, and DGS10 series
- **Llama.fi**: Stablecoin market capitalization data
- **Yahoo Finance**: ETF price data via yfinance library

## Configuration

The dashboard automatically calculates date ranges for the last 60 business days. Key configuration variables in `complex_dash.py`:

- `FRED_API_KEY` - Get your free API key from [https://fred.stlouisfed.org/](https://fred.stlouisfed.org/)
- `START_DATE` / `END_DATE` - Date range for data fetching (automatically calculated)
- `SERIES` dictionary - Maps display names to FRED series IDs

## Interpretation Guidance

As explained in `email.txt`, this dashboard can be used to identify different market regimes:

### Oil Supply Shock Regime
- Oil prices ↑ strongly
- S&P 500 ↓ or flat
- VIX ↑ noticeably (> +10%)
- 10-Year Treasury Yield ↑ or mixed (inflation worry)

### Oil Demand Shock Regime
- Oil prices ↑ strongly
- S&P 500 ↑ (> 0.3-0.5%)
- VIX flat or ↓
- 10-Year Treasury Yield ↑ modestly (growth) or breakevens ↑ more than real yields

## GitNexus Integration

This repository has been indexed with GitNexus for code intelligence and knowledge graph exploration. To explore the codebase structure:

```bash
# Start GitNexus backend
npx gitnexus serve

# In another terminal, start the proxy
node ~/.local/share/gitnexus/proxy.mjs ~/.local/share/gitnexus/gitnexus-web/dist 8888

# Access the web UI at http://localhost:8888
```

Or use the GitNexus CLI for quick queries:
```bash
npx gitnexus query "stablecoin OR SOFR OR ETF"
npx gitnexus context complex_dash.py
```

## Notes

- The `.gitnexus/` directory is automatically generated and should not be committed to version control
- The `.claude/` directory contains Claude Code integration files that are not needed for standard usage
- API keys should be kept secure and not shared publicly
- For Windows users, refer to `Activating the virtual environment.txt` for PowerShell-specific instructions

## Contributing

Feel free to fork this repository and submit pull requests for:
- Additional indicators or data sources
- Improved visualizations
- Bug fixes
- Documentation improvements

## License

MIT License - feel free to use and modify as needed.

---

*Created by Randall. Enhanced with GitNexus code analysis for optimal documentation.*