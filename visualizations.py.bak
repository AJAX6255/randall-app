#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
visualizations.py

Handles all visualization components for the Randall market dashboard.
Responsible for:
- Altair theme configuration
- Axis styling
- Chart generation functions for all dashboard components
"""

import altair as alt
import pandas as pd

# -----------------------------------------------------------------------------
# ALTAIR THEME AND STYLING
# -----------------------------------------------------------------------------

def custom_theme():
    """
    Custom Altair theme for dark dashboard styling.
    
    Returns:
        dict: Altair theme configuration
    """
    return {
        "config": {
            "axis": {
                "grid": True,
                "gridColor": "#31333F",
                "domainColor": "#31333F",
                "tickColor": "#31333F",
                "labelColor": "white",
                "titleColor": "white"
            },
            "view": {
                "stroke": "transparent"
            },
            "background": "#0E1117"
        }
    }

# Register and enable the custom theme
alt.themes.register("custom_theme", custom_theme)
alt.themes.enable("custom_theme")

# Axis style for consistent chart appearance
axis_style = alt.Axis(
    labelColor="#e6eaf1",
    titleColor="#e6eaf1",
    labelFontSize=12,
    titleFontSize=14,
    titleFontWeight="bold",
    gridColor="#31333F"
)

# -----------------------------------------------------------------------------
# CHART GENERATION FUNCTIONS
# -----------------------------------------------------------------------------

def create_treasury_yield_chart(master_df):
    """
    Create 10Y Treasury yield chart.
    
    Args:
        master_df (pd.DataFrame): Master dataframe containing DGS10 data
        
    Returns:
        alt.Chart: Interactive Altair chart
    """
    chart_dgs10 = alt.Chart(master_df).mark_line().encode(
        x=alt.X(
            "date:T",
            axis=axis_style
        ),
        y=alt.Y(
            "DGS10:Q",
            axis=axis_style
        ),
        tooltip=[
            "date:T",
            "DGS10:Q"
        ]
    ).interactive()
    
    return chart_dgs10

def create_stress_composite_chart(stress_df):
    """
    Create market stress composite index chart with regime coloring.
    
    Args:
        stress_df (pd.DataFrame): Stress composite dataframe with date index
        
    Returns:
        alt.Chart: Interactive Altair chart
    """
    stress_chart = alt.Chart(
        stress_df.reset_index()
    ).mark_line().encode(
        x=alt.X(
            "date:T",
            axis=axis_style
        ),
        y=alt.Y(
            "stress_composite:Q",
            axis=axis_style
        ),
        color=alt.Color(
            "stress_regime:N",
            scale=alt.Scale(
                domain=[
                    "Low Stress",
                    "Moderate Stress",
                    "High Stress",
                    "Crisis"
                ],
                range=[
                    "green",
                    "yellow",
                    "orange",
                    "red"
                ]
            )
        ),
        tooltip=[
            "date:T",
            "stress_composite:Q",
            "stress_regime:N"
        ]
    ).interactive()
    
    return stress_chart

def create_component_breakdown_chart(stress_df):
    """
    Create component breakdown chart showing individual stress components.
    
    Args:
        stress_df (pd.DataFrame): Stress composite dataframe
        
    Returns:
        alt.Chart: Interactive Altair chart
    """
    # Prepare component data for plotting
    component_data = (
        stress_df[[
            "vix_score",
            "credit_score",
            "stablecoin_score",
            "btc_vol_score",
            "funding_score"
        ]]
        .reset_index()
    )
    
    component_melted = (
        component_data.melt(
            id_vars=["date"],
            var_name="component",
            value_name="score"
        )
    )
    
    component_chart = alt.Chart(
        component_melted
    ).mark_line().encode(
        x=alt.X(
            "date:T",
            axis=axis_style
        ),
        y=alt.Y(
            "score:Q",
            axis=axis_style
        ),
        color="component:N",
        tooltip=[
            "date:T",
            "component:N",
            "score:Q"
        ]
    ).interactive()
    
    return component_chart

def create_additional_market_charts(yf_data):
    """
    Create additional market charts for SPY, GLD, etc.
    
    Args:
        yf_data (dict): Dictionary of Yahoo Finance dataframes
        
    Returns:
        dict: Dictionary of additional charts
    """
    charts = {}
    
    # SPY chart
    if "SPY" in yf_data:
        charts["SPY"] = alt.Chart(yf_data["SPY"]).mark_line().encode(
            x=alt.X("date:T", axis=axis_style),
            y=alt.Y("SPY:Q", axis=axis_style),
            tooltip=["date:T", "SPY:Q"]
        ).interactive()
    
    # VIX chart
    if "VIX" in yf_data:
        charts["VIX"] = alt.Chart(yf_data["VIX"]).mark_line().encode(
            x=alt.X("date:T", axis=axis_style),
            y=alt.Y("VIX:Q", axis=axis_style),
            tooltip=["date:T", "VIX:Q"]
        ).interactive()
    
    # Gold chart
    if "GLD" in yf_data:
        charts["GLD"] = alt.Chart(yf_data["GLD"]).mark_line().encode(
            x=alt.X("date:T", axis=axis_style),
            y=alt.Y("GLD:Q", axis=axis_style),
            tooltip=["date:T", "GLD:Q"]
        ).interactive()
    
    return charts