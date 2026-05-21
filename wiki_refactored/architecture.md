# Architecture (Refactored Version)

## Overview
The refactored Randall's Crypto-Crisis Monitoring Dashboard follows a modular architecture with clear separation of concerns:
1. **Configuration**: Centralized constants and settings
2. **Data Fetching**: Functions to retrieve data from various sources
3. **Data Processing**: Functions to build and manipulate the master DataFrame
4. **Visualization**: Reusable functions for creating charts
5. **Application Layer**: Streamlit app that orchestrates the workflow

## Components

### 1. Configuration Layer
- **Constants**: API keys, date ranges, series mappings, ETF symbols
- **Centralized Settings**: Easy to modify in one location

### 2. Data Fetching Layer
- **`get_fred_series(series_id)`**: Fetches FRED data for a specific series
- **`get_stablecoin_marketcap()`**: Retrieves stablecoin data from Llama.fi
- **`get_etf_data(symbol, name)`**: Generic function to fetch any ETF data
- **`fetch_all_etf_data()`**: Fetches data for all configured ETFs

### 3. Data Processing Layer
- **`build_master_dataframe()`**: Constructs the unified DataFrame from all sources
- Handles date range creation, merging, missing data handling, and feature engineering

### 4. Visualization Layer
- **`create_axis_style()`**: Creates consistent axis formatting
- **`create_line_chart()`**: Generic line chart creator
- **`create_dual_line_chart()`**: Specialized chart for comparing two series
- Eliminates code duplication in chart creation

### 5. Application Layer
- **`main()`**: Primary Streamlit application function
- Orchestrates data fetching, processing, and visualization
- Uses Streamlit components for UI layout and interactivity

## Data Flow
```
[Configuration] --> [Data Fetching] --> [Data Processing] --> [Visualization] --> [Streamlit UI]
                               ↑                     ↗
                        [ETF Fetching]--------------- 
```

## External Dependencies
- **FRED API** (requires free API key)
- **Llama.fi** (public stablecoin data API)
- **Yahoo Finance** (via yfinance, no API key required)
- **Python Packages**: streamlit, pandas, requests, yfinance, altair

## Benefits of Refactoring
1. **Reduced Code Duplication**: Reusable functions for common operations
2. **Improved Readability**: Each function has a single, clear responsibility
3. **Easier Maintenance**: Changes to data fetching or visualization affect fewer locations
4. **Better Testability**: Functions can be unit tested independently
5. **Enhanced Extensibility**: Adding new data sources or chart types is straightforward
