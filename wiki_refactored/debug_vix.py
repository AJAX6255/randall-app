#!/usr/bin/env python3
# Debug script to check VIX data and charting

import sys
import os
sys.path.insert(0, '/home/allan-jackson/Downloads/Randall')

import pandas as pd
import yfinance as yf
import altair as alt
from datetime import date, timedelta

def debug_vix():
    print("=== VIX DEBUGGING ===")
    
    # Recreate the date range from the refactored code
    TODAY = date.today()
    END_DATE = TODAY - timedelta(days=1)
    START_DATE = END_DATE - timedelta(days=60)
    
    print(f"Date range: {START_DATE} to {END_DATE}")
    
    # Test 1: Direct yfinance download
    print("\n1. Testing direct yfinance download:")
    try:
        vix_raw = yf.download("^VIX", start=START_DATE, end=END_DATE, progress=False)
        print(f"   ^VIX download shape: {vix_raw.shape}")
        if not vix_raw.empty:
            print(f"   Columns: {list(vix_raw.columns)}")
            print(f"   First few rows:\n{vix_raw.head()}")
        else:
            print("   ^VIX returned empty DataFrame")
    except Exception as e:
        print(f"   ^VIX download error: {e}")
    
    # Test 2: Processed data (as used in dashboard)
    print("\n2. Testing processed VIX data:")
    try:
        vix_raw = yf.download("^VIX", start=START_DATE, end=END_DATE, progress=False)
        if not vix_raw.empty:
            vix_df = vix_raw.reset_index()[["Date", "Close"]]
            vix_df.columns = ["date", "VIX Index (Volatility)"]
            vix_df["date"] = pd.to_datetime(vix_df["date"])
            print(f"   Processed VIX shape: {vix_df.shape}")
            print(f"   Columns: {list(vix_df.columns)}")
            print(f"   First few rows:\n{vix_df.head()}")
            print(f"   Data types:\n{vix_df.dtypes}")
        else:
            print("   No raw data to process")
    except Exception as e:
        print(f"   Processing error: {e}")
    
    # Test 3: Altair chart creation
    print("\n3. Testing Altair chart creation:")
    try:
        # Create axis style (from refactored code)
        axis_style = alt.Axis(
            labelColor="black",
            titleColor="black",
            labelFontSize=12,
            titleFontSize=14,
            titleFontWeight="bold",
            gridColor="lightgray"
        )
        
        # Create chart
        vix_raw = yf.download("^VIX", start=START_DATE, end=END_DATE, progress=False)
        if not vix_raw.empty:
            vix_df = vix_raw.reset_index()[["Date", "Close"]]
            vix_df.columns = ["date", "VIX Index (Volatility)"]
            vix_df["date"] = pd.to_datetime(vix_df["date"])
            
            chart = alt.Chart(vix_df).mark_line().encode(
                x=alt.X('date:T', axis=axis_style),
                y=alt.Y('VIX Index (Volatility):Q', axis=axis_style),
                tooltip=['date:T', 'VIX Index (Volatility):Q']
            ).interactive()
            
            print("   Chart created successfully!")
            # Try to convert to dict to see if it's valid
            spec = chart.to_dict()
            print(f"   Chart spec has keys: {list(spec.keys())}")
        else:
            print("   No data to chart")
    except Exception as e:
        print(f"   Chart creation error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Check what's actually in etf_data from fetch_all_etf_data
    print("\n4. Testing fetch_all_etf_data function:")
    try:
        # Import the function from our refactored code
        from complex_dash_refactored import fetch_all_etf_data
        etf_data = fetch_all_etf_data()
        vix_data = etf_data["VIX"]
        print(f"   VIX data shape: {vix_data.shape}")
        print(f"   VIX columns: {list(vix_data.columns)}")
        if not vix_data.empty:
            print(f"   First few rows:\n{vix_data.head()}")
        else:
            print("   VIX data is empty!")
    except Exception as e:
        print(f"   Error fetching etf_data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_vix()