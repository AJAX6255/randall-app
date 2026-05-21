# complex_dash

## Responsibility
Main Streamlit application that orchestrates data fetching, processing, and visualization for the crypto-crisis monitoring dashboard.

## Main Functions
- `get_fred_series(series_id)`: Fetches data from FRED API for a given series ID
- `get_stablecoin_marketcap()`: Fetches stablecoin market capitalization data from Llama.fi
- Data processing pipeline: Merges FRED, stablecoin, and ETF data into a master DataFrame
- Visualization functions: Creates Altair charts for each metric
- Streamlit application: Sets up the web interface and renders charts

## Key Data Structures
- `master_df`: Pandas DataFrame containing all merged data indexed by business dates
- `SERIES`: Dictionary mapping display names to FRED series IDs
- Date range constants: `START_DATE`, `END_DATE`, `TODAY`

## Important Variables
- `FRED_API_KEY`: Hardcoded API key for FRED (consider moving to environment variable)
- `master_df`: Central DataFrame used for all visualizations
- Individual ETF DataFrames: `spy`, `vix`, `gld`, `vtip`, `tlt`, `crcl`, `dram`, `jnk`, `emb`

## Dependencies
- Internal: None (all functions are in this file)
- External: 
  - `yfinance`: For ETF data
  - `pandas`: For data manipulation
  - `requests`: For API calls to FRED and Llama.fi
  - `streamlit`: For web framework
  - `altair`: For interactive visualizations
