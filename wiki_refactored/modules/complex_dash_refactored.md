# complex_dash_refactored

## Responsibility
Main Streamlit application that orchestrates data fetching, processing, and visualization for the crypto-crisis monitoring dashboard using a modular, function-based approach.

## Main Functions
- `get_fred_series(series_id)`: Fetches data from FRED API for a given series ID
- `get_stablecoin_marketcap()`: Fetches stablecoin market capitalization data from Llama.fi
- `get_etf_data(symbol, name)`: Generic function to fetch ETF data from Yahoo Finance
- `fetch_all_etf_data()`: Fetches data for all configured ETFs
- `build_master_dataframe()`: Constructs the unified DataFrame from all data sources
- `create_axis_style()`: Creates consistent axis styling for charts
- `create_line_chart()`: Generic reusable line chart creator
- `create_dual_line_chart()`: Specialized chart for comparing two data series
- `main()`: Primary Streamlit application function

## Key Data Structures
- `master_df`: Pandas DataFrame containing all merged data indexed by business dates
- `SERIES`: Dictionary mapping display names to FRED series IDs
- `ETF_SYMBOLS`: Dictionary mapping ETF symbols to display names
- Date range constants: `START_DATE`, `END_DATE`, `TODAY`

## Important Variables
- `FRED_API_KEY`: Hardcoded API key for FRED (consider moving to environment variable)
- `master_df`: Central DataFrame used for all visualizations
- Individual ETF DataFrames stored in dictionary from `fetch_all_etf_data()`

## Dependencies
- Internal: All functions are in this file, calling each other
- External: 
  - `yfinance`: For ETF data
  - `pandas`: For data manipulation
  - `requests`: For API calls to FRED and Llama.fi
  - `streamlit`: For web framework
  - `altair`: For interactive visualizations

## Design Patterns Used
1. **Separation of Concerns**: Configuration, data fetching, processing, and visualization are separated
2. **Function Abstraction**: Common operations are extracted into reusable functions
3. **Parameterization**: Functions accept parameters to increase flexibility
4. **Consistent Interface**: Visualization functions follow similar patterns for ease of use
