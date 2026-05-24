#!/usr/bin/env python3
# Test to replicate exactly what happens in the dashboard for VIX

import sys
import os
sys.path.insert(0, '/home/allan-jackson/Downloads/Randall')

import pandas as pd
import streamlit as st
import altair as alt
from datetime import date, timedelta

def create_axis_style():
    return alt.Axis(
        labelColor="black",
        titleColor="black",
        labelFontSize=12,
        titleFontSize=14,
        titleFontWeight="bold",
        gridColor="lightgray"
    )

def create_line_chart(data, x_col, y_col, title, y_scale=None, color=None, tooltip=None):
    axis_style = create_axis_style()
    chart = alt.Chart(data).mark_line().encode(
        x=alt.X(f"{x_col}:T", axis=axis_style),
        y=alt.Y(
            f"{y_col}:Q",
            scale=y_scale,
            axis=axis_style
        ),
        tooltip=tooltip or [f"{x_col}:T", f"{y_col}:Q"]
    ).interactive()
    if color:
        chart = chart.encode(color=color)
    return chart.properties(title=title)

def test_vix_chart_creation():
    print("=== Testing VIX Chart Creation (Exact Dashboard Replication) ===")
    
    # Recreate the exact date range from dashboard
    TODAY = date.today()
    END_DATE = TODAY - timedelta(days=1)
    START_DATE = END_DATE - timedelta(days=60)
    
    print(f"Date range: {START_DATE} to {END_DATE}")
    
    # Fetch VIX data exactly as fetch_all_etf_data does it for VIX
    import yfinance as yf
    
    def get_etf_data(symbol, name):
        try:
            df = yf.download(symbol, start=START_DATE, end=END_DATE, progress=False)
            if df.empty:
                print(f"No data returned for {name} ({symbol}) from Yahoo Finance")
                return pd.DataFrame(columns=["date", name])
            df = df.reset_index()
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [col[0] for col in df.columns]
            df.columns = [str(col).lower() for col in df.columns]
            df = df[['date', 'close']].copy()
            df.columns = ["date", name]
            df["date"] = pd.to_datetime(df["date"])
            if df["date"].dt.tz is not None:
                df["date"] = df["date"].dt.tz_localize(None)
            return df
        except Exception as e:
            print(f"Error fetching {name} ({symbol}) from Yahoo Finance: {str(e)}")
            return pd.DataFrame(columns=["date", name])
    
    # Test VIX with multiple symbols (as in fetch_all_etf_data)
    vix_symbols = ["^VIX", "VIX", "VIXY"]
    vix_data = None
    for vix_symbol in vix_symbols:
        try:
            vix_data = get_etf_data(vix_symbol, "VIX Index (Volatility)")
            if not vix_data.empty:
                print(f"Successfully fetched VIX data using symbol: {vix_symbol}")
                break
        except Exception:
            continue
    
    if vix_data is None or vix_data.empty:
        print("ERROR: Unable to fetch VIX data from any source")
        return
    
    print(f"VIX data shape: {vix_data.shape}")
    print(f"VIX columns: {vix_data.columns.tolist()}")
    print(f"VIX data sample:\n{vix_data.head()}")
    
    # Now create the chart EXACTLY as done in the dashboard
    print("\n--- Creating VIX chart as in dashboard ---")
    try:
        vix_chart = create_line_chart(
            vix_data, "date", "VIX Index (Volatility)",
            "VIX Index Daily Price"
        )
        print("SUCCESS: VIX chart created")
        
        # Get the chart spec to verify it's valid
        chart_spec = vix_chart.to_dict()
        print(f"Chart spec keys: {list(chart_spec.keys())}")
        
        # Check if data is present in the spec
        if 'data' in chart_spec and 'values' in chart_spec['data']:
            values = chart_spec['data']['values']
            print(f"Chart contains {len(values)} data points")
            if len(values) > 0:
                print(f"First data point: {values[0]}")
            else:
                print("WARNING: Chart data is empty!")
        else:
            print("WARNING: No data found in chart spec")
            
    except Exception as e:
        print(f"ERROR creating VIX chart: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test what happens if we use the original approach from complex_dash.py
    print("\n--- Testing original approach from complex_dash.py ---")
    try:
        # Recreate the vix dataframe as in original code
        vix_raw = yf.download("^VIX", start=START_DATE, end=END_DATE, progress=False)
        vix_raw = vix_raw.reset_index()
        if isinstance(vix_raw.columns, pd.MultiIndex):
            vix_raw.columns = [col[0] for col in vix_raw.columns]
        vix_raw.columns = [str(col).lower() for col in vix_raw.columns]
        vix_orig = vix_raw[['date', 'close']].copy()
        vix_orig.columns = ["date", "VIX"]
        vix_orig["date"] = pd.to_datetime(vix_orig["date"])
        if vix_orig["date"].dt.tz is not None:
            vix_orig["date"] = vix_orig["date"].dt.tz_localize(None)
        
        axis_style = create_axis_style()
        chart_vix = alt.Chart(vix_orig).mark_line().encode(
            x=alt.X("date:T", axis=axis_style),
            y=alt.Y("VIX:Q", axis=axis_style),
            tooltip=["date:T", "VIX:Q"]
        ).interactive()
        
        print("SUCCESS: Original approach chart created")
        chart_spec_orig = chart_vix.to_dict()
        if 'data' in chart_spec_orig and 'values' in chart_spec_orig['data']:
            values_orig = chart_spec_orig['data']['values']
            print(f"Original chart contains {len(values_orig)} data points")
        else:
            print("WARNING: Original chart data is empty!")
            
    except Exception as e:
        print(f"ERROR creating original approach chart: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_vix_chart_creation()