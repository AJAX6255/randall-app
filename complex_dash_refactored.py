#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
complex_dash.py

Production-grade Streamlit macro / crypto dashboard
with real market stress composite integration.

Refactored version with separated concerns:
- data_fetcher.py: Handles all data acquisition
- stress_calculator.py: Handles stress composite calculations
- visualizations.py: Handles all chart generation
- This file: Main application logic and UI orchestration
"""

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# Import our refactored modules
from data_fetcher import (
    check_fred_api,
    check_stablecoins_api,
    check_yfinance_api,
    build_master_dataframe
)
from stress_calculator import build_stress_composite_from_raw_data
from visualizations import (
    create_treasury_yield_chart,
    create_stress_composite_chart,
    create_component_breakdown_chart,
    create_additional_market_charts,
    axis_style
)

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="Market Dashboard",
    layout="wide"
)

st.title("📊 Market Data Dashboard")

# -----------------------------------------------------------------------------
# SIDEBAR HEALTH CHECKS
# -----------------------------------------------------------------------------

with st.sidebar:
    st.subheader("🔧 System Health")
    
    # Initialize health checks in session state if not present
    if "health_checks" not in st.session_state:
        st.session_state.health_checks = {}
        st.session_state.last_check = 0
    
    current_time = st.session_state.get('last_check', 0)
    # In a real app, we'd use time.time() but for simplicity in this example,
    # we'll check every time for now (can be optimized later)
    
    with st.spinner("Checking APIs..."):
        fred_ok, fred_msg = check_fred_api()
        stable_ok, stable_msg = check_stablecoins_api()
        yahoo_ok, yahoo_msg = check_yfinance_api()
        
        st.session_state.health_checks = {
            "FRED": (fred_ok, fred_msg),
            "Stablecoins": (stable_ok, stable_msg),
            "Yahoo": (yahoo_ok, yahoo_msg)
        }
        st.session_state.last_check = current_time  # Would be time.time() in practice
    
    # Display health check results
    for service, (ok, msg) in st.session_state.health_checks.items():
        if ok:
            st.success(f"✅ {msg}")
        else:
            st.error(f"❌ {msg}")

# -----------------------------------------------------------------------------
# MAIN DASHBOARD LOGIC
# -----------------------------------------------------------------------------

try:
    # Step 1: Fetch all data
    with st.spinner("Fetching market data..."):
        master_df, yf_data = build_master_dataframe()
        
        # Add BTC returns column if not present (should be in yf_data['BTC'] already)
        if 'BTC' in yf_data and 'returns' not in yf_data['BTC'].columns:
            yf_data['BTC']['returns'] = yf_data['BTC']['BTC'].pct_change()
    
    # Step 2: Calculate stress composite
    with st.spinner("Calculating stress composite..."):
        # Extract the specific dataframes needed for stress calculation
        vix_df = yf_data['VIX'][['date', 'VIX']].copy()
        tlt_df = yf_data['TLT'][['date', 'TLT']].copy()
        jnk_df = yf_data['JNK'][['date', 'JNK']].copy()
        
        # Stablecoin data is in master_df
        stablecoin_df = master_df[['date', 'Stablecoin Mkt Cap']].copy()
        
        # BTC data with returns
        btc_df = yf_data['BTC'][['date', 'BTC', 'returns']].copy()
        
        # Build stress composite
        stress_df, snapshot = build_stress_composite_from_raw_data(
            vix_data=vix_df,
            tlt_data=tlt_df,
            jnk_data=jnk_df,
            stablecoin_data=stablecoin_df,
            btc_data=btc_df
        )
    
    # Step 3: Display dashboard components
    
    # Stress composite chart
    st.subheader("📈 Market Stress Composite Index")
    stress_chart = create_stress_composite_chart(stress_df)
    st.altair_chart(stress_chart, width="stretch")
    
    # Component breakdown
    st.subheader("Component Breakdown")
    component_chart = create_component_breakdown_chart(stress_df)
    st.altair_chart(component_chart, width="stretch")
    # -----------------------------------------------------------------------------
    # DYNAMIC MARKET CHART EXPLORER
    # -----------------------------------------------------------------------------

    st.subheader("📈 Market Chart Explorer")

    # -------------------------------------------------------------------------
    # BUILD MASTER MARKET DATAFRAME
    # -------------------------------------------------------------------------

    market_df = master_df[[
        "date",
        "SOFR",
        "FFR",
        "DGS10",
        "SOFR_Spread",
        "Stablecoin Mkt Cap"
    ]].copy()

    # Merge market series from yf_data dictionary
    datasets = [
        yf_data['SPY'],
        yf_data['VIX'],
        yf_data['GLD'],
        yf_data['VTIP'],
        yf_data['TLT'],
        yf_data['CRCL'],
        yf_data['DRAM'],
        yf_data['JNK'],
        yf_data['EMB'],
        yf_data['BTC']
    ]

    for ds in datasets:

        market_df = market_df.merge(
            ds,
            on="date",
            how="left"
        )

    # Sort + fill

    market_df.sort_values(
        "date",
        inplace=True
    )

    market_df.ffill(
        inplace=True
    )

    # -------------------------------------------------------------------------
    # AVAILABLE SERIES
    # -------------------------------------------------------------------------

    available_columns = [

        "SPY",
        "VIX",
        "GLD",
        "VTIP",
        "TLT",
        "CRCL",
        "DRAM",
        "JNK",
        "EMB",
        "BTC",
        "SOFR",
        "FFR",
        "DGS10",
        "SOFR_Spread",
        "Stablecoin Mkt Cap"
    ]

    # -------------------------------------------------------------------------
    # USER SELECTION
    # -------------------------------------------------------------------------

    selected_columns = st.multiselect(
        "Select market series to plot",
        options=available_columns,
        default=["SPY", "VIX"]
    )

    # Normalize option
    normalize = st.checkbox("Normalize Series (Percent Change from First)", value=False)

    # -------------------------------------------------------------------------
    # PLOT
    # -------------------------------------------------------------------------

    if len(selected_columns) > 0:

        plot_df = market_df[
            ["date"] + selected_columns
        ].copy()

        # Apply normalization if selected
        if normalize:
            for col in selected_columns:
                plot_df[col] = (plot_df[col] / plot_df[col].iloc[0]) * 100

        melted_df = plot_df.melt(
            id_vars="date",
            var_name="Series",
            value_name="Value"
        )

        # Update tooltip based on normalization
        if normalize:
            tooltip_fields = [
                "date:T",
                "Series:N",
                alt.Tooltip("Value:Q", format=".2f", title="Normalized Value (%)")
            ]
            y_axis_label = "Normalized Value (Starting at 100)"
        else:
            tooltip_fields = [
                "date:T",
                "Series:N",
                "Value:Q"
            ]
            y_axis_label = "Value"

        dynamic_chart = alt.Chart(
            melted_df
        ).mark_line().encode(

            x=alt.X(
                "date:T",
                axis=axis_style
            ),

            y=alt.Y(
                "Value:Q",
                axis=axis_style,
                title=y_axis_label
            ),

            color=alt.Color(
                "Series:N"
            ),

            tooltip=tooltip_fields

        ).interactive()

        st.altair_chart(
            dynamic_chart,
            width="stretch"
        )

    else:

        st.info(
            "Select at least one series."
        )
    
    # Additional charts (optional - can be uncommented if desired)
    # st.subheader("Additional Market Indicators")
    # additional_charts = create_additional_market_charts(yf_data)
    # for name, chart in additional_charts.items():
    #     st.subheader(name)
    #     st.altair_chart(chart, width="stretch")
    
except Exception as e:
    st.error(f"Error in dashboard: {str(e)}")
    st.exception(e)  # Show full traceback for debugging
