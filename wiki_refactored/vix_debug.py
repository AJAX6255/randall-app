#!/usr/bin/env python3
# Add a checkbox to troubleshoot VIX display and test various chart rendering approaches

import sys
import os
sys.path.insert(0, '/home/allan-jackson/Downloads/Randall')

import streamlit as st
import pandas as pd
import altair as alt
from datetime import date, timedelta
import yfinance as yf

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

def main():
    st.set_page_config(page_title="VIX Debug Dashboard", layout="wide")
    st.title("🔍 VIX Debugging Dashboard")
    
    # Get date range
    TODAY = date.today()
    END_DATE = TODAY - timedelta(days=1)
    START_DATE = END_DATE - timedelta(days=60)
    
    st.markdown(f"Data from **{START_DATE}** to **{END_DATE}**")
    
    # Fetch VIX data
    with st.spinner("Fetching VIX data..."):
        try:
            vix_raw = yf.download("^VIX", start=START_DATE, end=END_DATE, progress=False)
            if vix_raw.empty:
                st.error("No VIX data returned from Yahoo Finance")
                return
                
            vix_df = vix_raw.reset_index()[["Date", "Close"]]
            vix_df.columns = ["date", "VIX Index (Volatility)"]
            vix_df["date"] = pd.to_datetime(vix_df["date"])
            
            st.success(f"Successfully fetched {len(vix_df)} rows of VIX data")
            
        except Exception as e:
            st.error(f"Error fetching VIX data: {e}")
            return
    
    # Show raw data
    if st.checkbox("Show raw VIX data"):
        st.subheader("Raw VIX Data")
        st.dataframe(vix_df)
        st.write(f"Data shape: {vix_df.shape}")
        st.write(f"Date range: {vix_df['date'].min()} to {vix_df['date'].max()}")
        st.write(f"VIX range: {vix_df['VIX Index (Volatility)'].min():.2f} to {vix_df['VIX Index (Volatility)'].max():.2f}")
    
    # Chart rendering options
    st.subheader("Chart Rendering Options")
    
    chart_method = st.radio(
        "Select chart method:",
        ["Standard Altair chart", "Create line chart function", "Chart with explicit properties"]
    )
    
    if chart_method == "Standard Altair chart":
        st.write("Creating chart with: alt.Chart(df).mark_line().encode(...)")
        chart = alt.Chart(vix_df).mark_line().encode(
            x='date:T',
            y='VIX Index (Volatility):Q'
        ).interactive()
        
    elif chart_method == "Create line chart function":
        st.write("Creating chart with: create_line_chart() function")
        chart = create_line_chart(
            vix_df, "date", "VIX Index (Volatility)",
            "VIX Index Daily Price"
        )
        
    else:  # Chart with explicit properties
        st.write("Creating chart with explicit width/height")
        chart = alt.Chart(vix_df, width=800, height=400).mark_line().encode(
            x=alt.X('date:T', axis=create_axis_style()),
            y=alt.Y('VIX Index (Volatility):Q', axis=create_axis_style())
        ).interactive()
    
    # Display chart
    st.subheader("VIX Chart Display")
    if st.checkbox("Show VIX chart", value=True):
        try:
            st.altair_chart(chart, use_container_width=True)
            st.success("Chart displayed successfully!")
        except Exception as e:
            st.error(f"Error displaying chart: {e}")
            st.exception(e)
    
    # Show chart properties for debugging
    if st.checkbox("Show chart debugging info"):
        st.subheader("Chart Debugging Information")
        try:
            chart_dict = chart.to_dict()
            st.json(chart_dict)
            
            # Check if data is present
            if 'data' in chart_dict:
                st.write("Data section found:", chart_dict['data'])
                if 'values' in chart_dict['data']:
                    st.write(f"Inline data points: {len(chart_dict['data']['values'])}")
                elif 'name' in chart_dict['data']:
                    ref_name = chart_dict['data']['name']
                    st.write(f"Data referenced by name: {ref_name}")
                    if 'datasets' in chart_dict and ref_name in chart_dict['datasets']:
                        dataset_points = len(chart_dict['datasets'][ref_name])
                        st.write(f"Dataset points: {dataset_points}")
                    else:
                        st.warning("Referenced dataset not found in datasets!")
            else:
                st.warning("No data section found in chart spec!")
                
        except Exception as e:
            st.error(f"Error getting chart info: {e}")

if __name__ == "__main__":
    main()