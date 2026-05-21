#!/usr/bin/env python3
# Test to replicate the exact dashboard flow and see what's happening with VIX

import sys
import os
sys.path.insert(0, '/home/allan-jackson/Downloads/Randall')

# Set up environment to mimic what streamlit does
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'

import pandas as pd
import streamlit as st
import altair as alt
from datetime import date, timedelta
import yfinance as yf

# Import our refactored functions
from complex_dash_refactored import (
    FRED_API_KEY, SERIES, ETF_SYMBOLS, 
    get_fred_series, get_stablecoin_marketcap, 
    get_etf_data, fetch_all_etf_data, build_master_dataframe,
    create_axis_style, create_line_chart, create_dual_line_chart
)

def test_dashboard_vix_flow():
    print("=== Testing Dashboard VIX Flow ===")
    
    # Check if we're in a streamlit-like environment
    print(f"Streamlit available: {hasattr(st, 'session_state')}")
    
    # Test 1: Check if we can fetch all ETF data
    print("\n1. Testing fetch_all_etf_data:")
    try:
        etf_data = fetch_all_etf_data()
        print(f"   Fetched data for {len(etf_data)} symbols")
        for symbol, df in etf_data.items():
            print(f"   {symbol}: {df.shape} rows, columns: {list(df.columns)}")
            if not df.empty:
                print(f"      Sample data:\n{df.head(2)}")
            else:
                print(f"      EMPTY DATAFRAME")
    except Exception as e:
        print(f"   ERROR in fetch_all_etf_data: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 2: Check VIX data specifically
    print("\n2. Checking VIX data specifically:")
    vix_df = etf_data.get("VIX")
    if vix_df is not None:
        print(f"   VIX DataFrame shape: {vix_df.shape}")
        print(f"   VIX columns: {list(vix_df.columns)}")
        if not vix_df.empty:
            print(f"   VIX data types:\n{vix_df.dtypes}")
            print(f"   VIX sample:\n{vix_df.head()}")
            
            # Check for NaN values
            vix_col = "VIX Index (Volatility)"
            if vix_col in vix_df.columns:
                nan_count = vix_df[vix_col].isna().sum()
                print(f"   NaN values in {vix_col}: {nan_count}/{len(vix_df)}")
                if nan_count == len(vix_df):
                    print(f"   WARNING: All values in {vix_col} are NaN!")
                else:
                    print(f"   Value range: {vix_df[vix_col].min()} to {vix_df[vix_col].max()}")
        else:
            print("   VIX DataFrame is EMPTY")
    else:
        print("   VIX key not found in etf_data")
    
    # Test 3: Test chart creation with VIX data
    print("\n3. Testing chart creation:")
    if vix_df is not None and not vix_df.empty:
        try:
            # Create the exact same chart as in dashboard
            vix_chart = create_line_chart(
                vix_df, "date", "VIX Index (Volatility)",
                "VIX Index Daily Price"
            )
            print("   SUCCESS: VIX chart created")
            
            # Check chart properties
            chart_dict = vix_chart.to_dict()
            print(f"   Chart has title: {'title' in chart_dict}")
            if 'title' in chart_dict:
                print(f"   Chart title: {chart_dict['title']}")
            
            # Try to render it in a mock streamlit way
            print("   Attempting to render chart (this would normally show in Streamlit)...")
            # In real Streamlit, this would be: st.altair_chart(vix_chart, width="stretch")
            # For testing, we'll just verify the chart object is valid
            print(f"   Chart object type: {type(vix_chart)}")
            
        except Exception as e:
            print(f"   ERROR creating VIX chart: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("   SKIPPED: No valid VIX data to chart")
    
    # Test 4: Test the full dashboard flow (just the VIX part)
    print("\n4. Testing full dashboard flow for VIX section:")
    try:
        # This replicates what happens in main() function
        master_df = build_master_dataframe()
        etf_data = fetch_all_etf_data()
        
        print(f"   Master DF shape: {master_df.shape}")
        print(f"   ETF data fetched for: {list(etf_data.keys())}")
        
        # Now replicate the VIX section from main()
        print("   Replicating VIX dashboard section:")
        print('   st.write("**VIX Index Daily Price**")')
        
        vix_chart = create_line_chart(
            etf_data["VIX"], "date", "VIX Index (Volatility)",
            "VIX Index Daily Price"
        )
        print('   vix_chart = create_line_chart(...)')
        print('   st.altair_chart(vix_chart, width="stretch")')
        
        # Verify the chart is valid
        if hasattr(vix_chart, 'to_dict'):
            spec = vix_chart.to_dict()
            print(f"   Chart specification generated successfully")
            print(f"   Chart keys: {list(spec.keys())}")
        else:
            print("   ERROR: Chart object doesn't have to_dict method")
            
    except Exception as e:
        print(f"   ERROR in dashboard flow: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dashboard_vix_flow()