#!/usr/bin/env python3
# Check for potential issues in the VIX charting that might cause it not to display

import sys
import os
sys.path.insert(0, '/home/allan-jackson/Downloads/Randall')

import pandas as pd
import altair as alt
from datetime import date, timedelta
import yfinance as yf

def check_chart_issues():
    print("=== Checking for Chart Display Issues ===")
    
    # Get VIX data
    TODAY = date.today()
    END_DATE = TODAY - timedelta(days=1)
    START_DATE = END_DATE - timedelta(days=60)
    
    vix_raw = yf.download("^VIX", start=START_DATE, end=END_DATE, progress=False)
    vix_df = vix_raw.reset_index()[["Date", "Close"]]
    vix_df.columns = ["date", "VIX Index (Volatility)"]
    vix_df["date"] = pd.to_datetime(vix_df["date"])
    
    print(f"VIX data: {vix_df.shape[0]} rows")
    print(f"Date range: {vix_df['date'].min()} to {vix_df['date'].max()}")
    print(f"VIX range: {vix_df['VIX Index (Volatility)'].min():.2f} to {vix_df['VIX Index (Volatility)'].max():.2f}")
    
    # Check 1: Chart creation with explicit width/height
    print("\n1. Testing chart with explicit properties:")
    try:
        chart = alt.Chart(vix_df, width=600, height=400).mark_line().encode(
            x='date:T',
            y='VIX Index (Volatility):Q'
        ).interactive()
        print("   Chart created with explicit width/height")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check 2: Chart properties
    print("\n2. Testing chart properties:")
    try:
        base_chart = alt.Chart(vix_df).mark_line().encode(
            x='date:T',
            y='VIX Index (Volatility):Q'
        ).interactive()
        
        # Check if we can get the underlying spec
        spec = base_chart.to_dict()
        print(f"   Chart spec has data: {'data' in spec}")
        if 'data' in spec:
            print(f"   Data section: {spec['data']}")
            if 'values' in spec['data']:
                print(f"   Number of data points: {len(spec['data']['values'])}")
            elif 'name' in spec['data']:
                print(f"   Data referenced by name: {spec['data']['name']}")
                if 'datasets' in spec and spec['data']['name'] in spec['datasets']:
                    print(f"   Dataset found with {len(spec['datasets'][spec['data']['name'])} points")
                else:
                    print("   WARNING: Dataset name not found in datasets!")
            else:
                print("   Data section has neither 'values' nor 'name'")
        
        # Check encoding
        if 'encoding' in spec:
            print(f"   Encoding channels: {list(spec['encoding'].keys())}")
        
    except Exception as e:
        print(f"   Error checking chart properties: {e}")
        import traceback
        traceback.print_exc()
    
    # Check 3: Potential issues with the create_line_chart function
    print("\n3. Testing create_line_chart function step by step:")
    try:
        # Replicate the axis style creation
        axis_style = alt.Axis(
            labelColor="black",
            titleColor="black",
            labelFontSize=12,
            titleFontSize=14,
            titleFontWeight="bold",
            gridColor="lightgray"
        )
        print("   Axis style created")
        
        # Create the chart step by step
        chart = alt.Chart(vix_df).mark_line()
        print("   Base chart with mark_line created")
        
        # Add encoding
        chart = chart.encode(
            x=alt.X('date:T', axis=axis_style),
            y=alt.Y('VIX Index (Volatility):Q', axis=axis_style),
            tooltip=['date:T', 'VIX Index (Volatility):Q']
        )
        print("   Encoding added")
        
        # Make interactive
        chart = chart.interactive()
        print("   Interactive mode enabled")
        
        # Add properties
        chart = chart.properties(title="VIX Index Daily Price")
        print("   Title added")
        
        # Check final spec
        spec = chart.to_dict()
        print(f"   Final chart spec keys: {list(spec.keys())}")
        
    except Exception as e:
        print(f"   Error in step-by-step chart creation: {e}")
        import traceback
        traceback.print_exc()
    
    # Check 4: Compare with a working chart (like SPY)
    print("\n4. Comparing with SPY chart (known to work):")
    try:
        spy_raw = yf.download("SPY", start=START_DATE, end=END_DATE, progress=False)
        spy_df = spy_raw.reset_index()[["Date", "Close"]]
        spy_df.columns = ["date", "SPY ETF (S&P 500)"]
        spy_df["date"] = pd.to_datetime(spy_df["date"])
        
        spy_chart = alt.Chart(spy_df).mark_line().encode(
            x='date:T',
            y='SPY ETF (S&P 500):Q'
        ).interactive()
        
        spy_spec = spy_chart.to_dict()
        print(f"   SPY chart spec keys: {list(spy_spec.keys())}")
        if 'data' in spy_spec:
            print(f"   SPY data section: {spy_spec['data']}")
            if 'values' in spy_spec['data']:
                print(f"   SPY data points: {len(spy_spec['data']['values'])}")
            elif 'name' in spy_spec['data']:
                print(f"   SPY data referenced by name: {spy_spec['data']['name']}")
                if 'datasets' in spy_spec and spy_spec['data']['name'] in spy_spec['datasets']:
                    print(f"   SPY dataset points: {len(spy_spec['datasets'][spy_spec['data']['name'])}")
        
    except Exception as e:
        print(f"   Error creating SPY chart: {e}")

if __name__ == "__main__":
    check_chart_issues()