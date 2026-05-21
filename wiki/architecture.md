# Architecture

## Overview
The Randall's Crypto-Crisis Monitoring Dashboard follows a simple data pipeline architecture:
1. **Data Ingestion**: Fetch data from multiple sources (FRED, Llama.fi, Yahoo Finance)
2. **Data Processing**: Clean, align, and merge data into a unified DataFrame
3. **Visualization**: Render interactive charts using Altair and Streamlit
4. **User Interaction**: Streamlit web interface for exploring data

## Components

### 1. Data Ingestion Layer
- **FRED API Client**: Functions `get_fred_series()` fetches Federal Reserve data
- **Stablecoin API Client**: Function `get_stablecoin_marketcap()` fetches from Llama.fi
- **Yahoo Finance Client**: Uses yfinance library to fetch ETF data

### 2. Data Processing Layer
- **Master DataFrame Construction**: Creates a business day date range and merges all data sources
- **Missing Data Handling**: Forward-fills missing values for continuity
- **Feature Engineering**: Calculates SOFR spread (SOFR - FFR) and stablecoin percentage change

### 3. Visualization Layer
- **Altair Charts**: Interactive line charts for each data series
- **Streamlit Layout**: Organized with headers, checkboxes, and interactive elements
- **Custom Styling**: Dark axis labels and specific scaling for better readability

### 4. Application Layer
- **Streamlit App**: Main entrypoint in `complex_dash.py` orchestrates the above layers
- **Configuration**: Centralized constants for API keys, date ranges, and series mappings

## Data Flow
```
[FRED API] -->                --> [Data Processing] --> [Master DataFrame] --> [Visualization] --> [Streamlit UI]
[Llama.fi] -->/
[Yahoo Finance] -->/
```

## External Dependencies
- **FRED API** (requires free API key)
- **Llama.fi** (public stablecoin data API)
- **Yahoo Finance** (via yfinance, no API key required)
- **Python Packages**: streamlit, pandas, requests, yfinance, altair
