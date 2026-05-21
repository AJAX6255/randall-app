#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
data_fetcher.py

Handles all data acquisition for the Randall market dashboard.
Responsible for:
- Environment variable loading and API key validation
- Fetching data from FRED, Stablecoins Llama, and Yahoo Finance APIs
- Health check functions for all data sources
- Constructing the master dataframe with all market data
"""

import os
import time
import datetime
import requests
import numpy as np
import pandas as pd
import yfinance as yf
from dotenv import load_dotenv

# -----------------------------------------------------------------------------
# ENVIRONMENT
# -----------------------------------------------------------------------------

load_dotenv()

FRED_API_KEY = os.getenv("FRED_API_KEY")

if not FRED_API_KEY:
    # In Streamlit context, this would show an error and stop
    # For module use, we'll raise an exception to be handled upstream
    raise ValueError("FRED_API_KEY not found in environment variables.")

# -----------------------------------------------------------------------------
# DATE RANGE
# -----------------------------------------------------------------------------

TODAY = datetime.date.today()
END_DATE = TODAY - datetime.timedelta(days=1)
START_DATE = END_DATE - datetime.timedelta(days=365)  # Need history for rolling windows

# -----------------------------------------------------------------------------
# FRED SERIES DEFINITIONS
# -----------------------------------------------------------------------------

SERIES = {
    "SOFR": "SOFR",
    "FFR": "DFF",
    "DGS10": "DGS10"
}

# -----------------------------------------------------------------------------
# HEALTH CHECK FUNCTIONS
# -----------------------------------------------------------------------------

def check_fred_api():
    """Check if FRED API is accessible and returning valid data."""
    try:
        url = "https://api.stlouisfed.org/fred/series/observations"
        params = {
            "series_id": "DFF",
            "api_key": FRED_API_KEY,
            "file_type": "json",
            "observation_start": "2024-01-01",
            "observation_end": "2024-01-02"
        }
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if "observations" in data and len(data["observations"]) > 0:
                return True, "FRED API: OK"
        
        return False, f"FRED API: Error {response.status_code}"
    
    except Exception as e:
        return False, f"FRED API: Connection failed ({str(e)[:50]}...)"

def check_stablecoins_api():
    """Check if Stablecoins Llama API is accessible."""
    try:
        url = "https://stablecoins.llama.fi/stablecoincharts/all"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                return True, "Stablecoins API: OK"
        
        return False, f"Stablecoins API: Error {response.status_code}"
    
    except Exception as e:
        return False, f"Stablecoins API: Connection failed ({str(e)[:50]}...)"

def check_yfinance_api():
    """Check if Yahoo Finance is accessible."""
    try:
        spy = yf.download("SPY", period="1d", progress=False)
        if not spy.empty:
            return True, "Yahoo Finance: OK"
        return False, "Yahoo Finance: No data returned"
    
    except Exception as e:
        return False, f"Yahoo Finance: Connection failed ({str(e)[:50]}...)"

# -----------------------------------------------------------------------------
# DATA FETCHING FUNCTIONS
# -----------------------------------------------------------------------------

def get_fred_series(series_name, series_id):
    """
    Fetch a time series from FRED.
    
    Args:
        series_name (str): Name to use for the series column
        series_id (str): FRED series ID
        
    Returns:
        pd.DataFrame: DataFrame with date and series_name columns
    """
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "observation_start": START_DATE.strftime("%Y-%m-%d"),
        "observation_end": END_DATE.strftime("%Y-%m-%d")
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    df = pd.DataFrame(data["observations"])
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df.rename(columns={"value": series_name}, inplace=True)
    
    return df[["date", series_name]]

def get_stablecoin_marketcap():
    """
    Fetch total stablecoin market cap from Stablecoins Llama.
    
    Returns:
        pd.DataFrame: DataFrame with date and Stablecoin Mkt Cap columns
    """
    try:
        url = "https://stablecoins.llama.fi/stablecoincharts/all"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        records = []
        for entry in data:
            date = datetime.datetime.fromtimestamp(int(entry["date"]))
            total_circulating = entry.get("totalCirculatingUSD", {})
            total_usd = sum(total_circulating.values())
            
            records.append({
                "date": date,
                "Stablecoin Mkt Cap": total_usd
            })
        
        df = pd.DataFrame(records)
        df = df[
            (df["date"] >= pd.Timestamp(START_DATE)) &
            (df["date"] <= pd.Timestamp(END_DATE))
        ]
        df.set_index("date", inplace=True)
        df = df.resample("B").last()  # Business day frequency
        df.ffill(inplace=True)
        df.reset_index(inplace=True)
        
        return df
    
    except Exception as e:
        # In Streamlit, we'd show a warning; for module use, return empty DataFrame
        print(f"Stablecoin API error: {str(e)}")
        return pd.DataFrame(columns=["date", "Stablecoin Mkt Cap"])

def fetch_yf_series(ticker, column_name):
    """
    Fetch price data from Yahoo Finance.
    
    Args:
        ticker (str): Yahoo Finance ticker symbol
        column_name (str): Name to use for the price column
        
    Returns:
        pd.DataFrame: DataFrame with date and column_name columns
    """
    df = yf.download(ticker, start=START_DATE, end=END_DATE, progress=False)
    df = df.reset_index()[["Date", "Close"]]
    df.columns = ["date", column_name]
    df["date"] = pd.to_datetime(df["date"])
    return df

# -----------------------------------------------------------------------------
# MASTER DATAFRAME CONSTRUCTION
# -----------------------------------------------------------------------------

def build_master_dataframe():
    """
    Construct the master dataframe with all market data.
    
    Returns:
        pd.DataFrame: Master dataframe with all fetched and derived data
    """
    # Initialize with business day date range
    date_range = pd.bdate_range(start=START_DATE, end=END_DATE)
    master_df = pd.DataFrame({"date": date_range})
    
    # Merge FRED data
    for display_name, fred_id in SERIES.items():
        fred_df = get_fred_series(display_name, fred_id)
        master_df = master_df.merge(fred_df, on="date", how="left")
    
    # Merge stablecoin data
    stable_df = get_stablecoin_marketcap()
    master_df = master_df.merge(stable_df, on="date", how="left")
    
    # Sort and forward fill
    master_df.sort_values("date", inplace=True)
    master_df.ffill(inplace=True)
    
    # Add derived metrics
    master_df["SOFR_Spread"] = master_df["SOFR"] - master_df["FFR"]
    
    # Fetch Yahoo Finance data for additional charts/indicators
    yf_data = {
        "SPY": fetch_yf_series("SPY", "SPY"),
        "VIX": fetch_yf_series("^VIX", "VIX"),
        "GLD": fetch_yf_series("GLD", "GLD"),
        "VTIP": fetch_yf_series("VTIP", "VTIP"),
        "TLT": fetch_yf_series("TLT", "TLT"),
        "CRCL": fetch_yf_series("CRCL", "CRCL"),
        "DRAM": fetch_yf_series("DRAM", "DRAM"),
        "JNK": fetch_yf_series("JNK", "JNK"),
        "EMB": fetch_yf_series("EMB", "EMB"),
        "BTC": fetch_yf_series("BTC-USD", "BTC")
    }
    
    return master_df, yf_data