#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
stress_calculator.py

Handles all stress composite calculations for the Randall market dashboard.
Responsible for:
- Calculating derived metrics from raw market data
- Preparing input series for the stress composite model
- Building the stress composite using metrics.stress_composite
- Generating snapshot metrics for dashboard display
"""

import numpy as np
import pandas as pd
from metrics.stress_composite import (
    build_stress_composite,
    latest_stress_snapshot
)

def calculate_credit_stress_proxy(tlt_series, jnk_series):
    """
    Calculate credit stress proxy using JNK/TLT ratio.
    Based on the idea that falling junk bond prices relative to Treasuries 
    indicate increasing credit stress.
    
    Args:
        tlt_series (pd.Series): TLT ETF prices (Treasury proxy)
        jnk_series (pd.Series): JNK ETF prices (junk bond proxy)
        
    Returns:
        pd.Series: Credit stress proxy (higher values = more stress)
    """
    # Calculate JNK/TLT ratio (falling ratio indicates credit stress)
    ratio = jnk_series / tlt_series
    # Calculate percentage change and smooth with rolling mean
    # Negative changes in ratio indicate stress, so we invert for positive stress values
    stress_proxy = (-ratio.pct_change()).rolling(5).mean()
    return stress_proxy

def calculate_stablecoin_dominance_proxy(stablecoin_marketcap_series, total_crypto_marketcap_estimate=None):
    """
    Calculate stablecoin dominance proxy.
    Uses stablecoin market cap changes as a proxy for flight-to-safety.
    
    Args:
        stablecoin_marketcap_series (pd.Series): Total stablecoin market cap
        total_crypto_marketcap_estimate (pd.Series, optional): Total crypto market cap
        
    Returns:
        pd.Series: Stablecoin dominance proxy (higher values = more stress)
    """
    # If we had total crypto market cap, we'd calculate actual dominance
    # For now, use percentage change in stablecoin market cap as proxy
    # Increasing stablecoin market cap can indicate flight to safety
    dominance_proxy = stablecoin_marketcap_series.pct_change().rolling(7).mean()
    return dominance_proxy

def calculate_funding_proxy(btc_returns_series):
    """
    Calculate funding rate proxy using BTC returns.
    Uses rolling average of BTC returns as a proxy for funding rates.
    
    Args:
        btc_returns_series (pd.Series): BTC percentage returns
        
    Returns:
        pd.Series: Funding proxy (higher values = more stress)
    """
    # Simple proxy: 3-day rolling average of returns scaled
    # In reality, positive returns might indicate crowded longs (negative funding)
    # But for simplicity, we'll use absolute returns as stress indicator
    funding_proxy = btc_returns_series.rolling(3).mean() * 0.05
    return funding_proxy

def prepare_stress_inputs(vix_data, tlt_data, jnk_data, stablecoin_data, btc_data):
    """
    Prepare and align all input series for stress composite calculation.
    
    Args:
        vix_data (pd.DataFrame): VIX data with 'date' and 'VIX' columns
        tlt_data (pd.DataFrame): TLT data with 'date' and 'TLT' columns
        jnk_data (pd.DataFrame): JNK data with 'date' and 'JNK' columns
        stablecoin_data (pd.DataFrame): Stablecoin market cap data with 'date' and 'Stablecoin Mkt Cap' columns
        btc_data (pd.DataFrame): BTC data with 'date', 'BTC', and 'returns' columns
        
    Returns:
        pd.DataFrame: Aligned and cleaned input series for stress composite
    """
    # Extract series and set date as index
    vix_series = vix_data.set_index("date")["VIX"].astype(float)
    tlt_series = tlt_data.set_index("date")["TLT"].astype(float)
    jnk_series = jnk_data.set_index("date")["JNK"].astype(float)
    stablecoin_series = stablecoin_data.set_index("date")["Stablecoin Mkt Cap"].astype(float)
    btc_returns = btc_data.set_index("date")["returns"].astype(float)
    
    # Calculate derived metrics
    credit_proxy = calculate_credit_stress_proxy(tlt_series, jnk_series)
    stablecoin_dominance = calculate_stablecoin_dominance_proxy(stablecoin_series)
    funding_proxy = calculate_funding_proxy(btc_returns)
    
    # Combine all inputs
    stress_inputs = pd.concat([
        vix_series.rename("vix"),
        credit_proxy.rename("credit"),
        stablecoin_dominance.rename("stablecoin"),
        btc_returns.rename("btc_returns"),
        funding_proxy.rename("funding")
    ], axis=1)
    
    # Align, clean, and prepare data
    stress_inputs.sort_index(inplace=True)
    stress_inputs.ffill(inplace=True)  # Forward fill missing values
    stress_inputs.dropna(inplace=True)  # Drop any remaining NaN values
    
    return stress_inputs

def build_stress_composite_from_raw_data(vix_data, tlt_data, jnk_data, stablecoin_data, btc_data):
    """
    Build stress composite index from raw market data.
    
    Args:
        vix_data, tlt_data, jnk_data, stablecoin_data, btc_data: 
            DataFrames from Yahoo Finance with 'date' and value columns
            
    Returns:
        tuple: (stress_df, snapshot) where stress_df contains the full time series
               and snapshot contains the latest values for dashboard display
    """
    # Prepare input series
    stress_inputs = prepare_stress_inputs(vix_data, tlt_data, jnk_data, stablecoin_data, btc_data)
    
    # Build stress composite using the established function
    stress_df = build_stress_composite(
        vix=stress_inputs["vix"],
        baa_aaa_spread=stress_inputs["credit"],
        stablecoin_dominance=stress_inputs["stablecoin"],
        btc_returns=stress_inputs["btc_returns"],
        funding_rate=stress_inputs["funding"]
    )
    
    # Clean the result
    stress_df.dropna(inplace=True)
    
    # Generate snapshot for dashboard metrics
    snapshot = latest_stress_snapshot(stress_df)
    
    return stress_df, snapshot