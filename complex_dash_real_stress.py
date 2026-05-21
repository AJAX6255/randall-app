#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 28 13:11:41 2026

@author: randall
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Streamlit Dashboard for Market Data with Real Stress Composite
@author: randall
"""

import yfinance as yf
import pandas as pd
import requests
import datetime
import streamlit as st
import time
import os
import numpy as np
from dotenv import load_dotenv
from metrics.stress_composite import (
    build_stress_composite,
    latest_stress_snapshot
)

# Load environment variables from .env file
load_dotenv()

# Health check functions
def check_fred_api():
    """Check if FRED API is accessible"""
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
    """Check if stablecoins.llama.fi API is accessible"""
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
    """Check if Yahoo Finance (via yfinance) is accessible"""
    try:
        # Try to get data for a well-known ticker
        spy = yf.download("SPY", period="1d", progress=False)
        if not spy.empty:
            return True, "Yahoo Finance: OK"
        return False, "Yahoo Finance: No data returned"
    except Exception as e:
        return False, f"Yahoo Finance: Connection failed ({str(e)[:50]}...)"

# Load FRED API key from environment variable
FRED_API_KEY = os.getenv('FRED_API_KEY')
if not FRED_API_KEY:
    st.error("FRED_API_KEY not found in environment variables. Please set it in your .env file.")
    st.stop()

TODAY = datetime.date.today()
END_DATE = TODAY - datetime.timedelta(days=1)
START_DATE = END_DATE - datetime.timedelta(days=60)

SERIES = {
    "SOFR": "SOFR",
    "FFR": "DFF",
    "DGS10": "DGS10"
}

# ------------------------
# Functions
# ------------------------
def get_fred_series(series_id):
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
    df["date"] = pd.to_datetime(df["date"]).dt.date
    df[series_id] = pd.to_numeric(df["value"], errors="coerce")
    return df[["date", series_id]]

def get_stablecoin_marketcap():
    url = "https://stablecoins.llama.fi/stablecoincharts/all"
    response = requests.get(url)
    data = response.json()
    
    records = []
   
    for entry in data:
        date = datetime.datetime.fromtimestamp(int(entry["date"])).date()
        total_circulating = entry.get("totalCirculatingUSD", {})
        total_usd = sum(total_circulating.values())
        records.append({"date": date, "Stablecoin Mkt Cap": total_usd})
       
    df = pd.DataFrame(records)

    # Filter range
    df = df[(df["date"] >= START_DATE) & (df["date"] <= END_DATE)]

    # Convert to datetime index
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)

    # Align to business days (take last available value)
    df = df.resample("B").last()

    df.reset_index(inplace=True)
    df["date"] = df["date"].dt.date

    return df

# ------------------------
# Build Master DataFrame
# ------------------------
date_range = pd.bdate_range(start=START_DATE, end=END_DATE)
master_df = pd.DataFrame({"date": date_range.date})

# Merge FRED data
for name, series_id in SERIES.items():
    df = get_fred_series(series_id)
    master_df = master_df.merge(df, on="date", how="left")

# Merge stablecoin data
stable_df = get_stablecoin_marketcap()
master_df = master_df.merge(stable_df, on="date", how="left")

# Handle missing data
master_df = master_df.sort_values("date")
master_df.ffill(inplace=True)

# ------------------------
# Fetch SPY and VIX Data
# ------------------------
spy = yf.download("SPY", start=START_DATE, end=END_DATE, progress=False)
vix = yf.download("^VIX", start=START_DATE, end=END_DATE, progress=False)

# ------------------------
# Fetch GLD Data
# ------------------------
#gld = yf.download("GLD", start=START_DATE, end=END_DATE, progress=False)
# ------------------------
# Fetch ETF / Market Data
# ------------------------
gld  = yf.download("GLD",  start=START_DATE, end=END_DATE, progress=False)
vtip = yf.download("VTIP", start=START_DATE, end=END_DATE, progress=False)
tlt  = yf.download("TLT",  start=START_DATE, end=END_DATE, progress=False)

crcl = yf.download("CRCL", start=START_DATE, end=END_DATE, progress=False)
dram = yf.download("DRAM", start=START_DATE, end=END_DATE, progress=False)
jnk  = yf.download("JNK",  start=START_DATE, end=END_DATE, progress=False)
emb  = yf.download("EMB",  start=START_DATE, end=END_DATE, progress=False)
# Reset index and standardize
gld = gld.reset_index()[["Date", "Close"]]
gld.columns = ["date", "GLD"]
gld["date"] = pd.to_datetime(gld["date"])

# VTIP
vtip = vtip.reset_index()[["Date", "Close"]]
vtip.columns = ["date", "VTIP"]
vtip["date"] = pd.to_datetime(vtip["date"])

# TLT
tlt = tlt.reset_index()[["Date", "Close"]]
tlt.columns = ["date", "TLT"]
tlt["date"] = pd.to_datetime(tlt["date"])

# CRCL
crcl = crcl.reset_index()[["Date", "Close"]]
crcl.columns = ["date", "CRCL"]
crcl["date"] = pd.to_datetime(crcl["date"])

# DRAM
dram = dram.reset_index()[["Date", "Close"]]
dram.columns = ["date", "DRAM"]
dram["date"] = pd.to_datetime(dram["date"])

# JNK
jnk = jnk.reset_index()[["Date", "Close"]]
jnk.columns = ["date", "JNK"]
jnk["date"] = pd.to_datetime(jnk["date"])

# EMB
emb = emb.reset_index()[["Date", "Close"]]
emb.columns = ["date", "EMB"]
emb["date"] = pd.to_datetime(emb["date"])

# Reset index and standardize
spy = spy.reset_index()[["Date", "Close"]]
spy.columns = ["date", "SPY"]
spy["date"] = pd.to_datetime(spy["date"])

vix = vix.reset_index()[["Date", "Close"]]
vix.columns = ["date", "VIX"]
vix["date"] = pd.to_datetime(vix["date"])

# Calculate SOFR spread
master_df["SOFR_Spread"] = master_df["SOFR"] - master_df["DFF"]
master_df.rename(columns={"DFF": "FFR"}, inplace=True)

# ------------------------
# Streamlit Dashboard
# ------------------------
st.set_page_config(page_title="Market Dashboard", layout="wide")
st.title("📊 Market Data Dashboard")

# Health check indicators in sidebar
with st.sidebar:
    st.subheader("🔧 System Health")
    
    # Initialize session state for health checks if not present
    if 'health_checks' not in st.session_state:
        st.session_state.health_checks = {}
        st.session_state.last_check = 0
    
    # Run health checks every 30 seconds (to avoid excessive API calls)
    current_time = time.time()
    if current_time - st.session_state.last_check > 30 or not st.session_state.health_checks:
        with st.spinner("Checking API health..."):
            fred_ok, fred_msg = check_fred_api()
            stablecoins_ok, stablecoins_msg = check_stablecoins_api()
            yahoo_ok, yahoo_msg = check_yfinance_api()
            
            st.session_state.health_checks = {
                'FRED': (fred_ok, fred_msg),
                'Stablecoins': (stablecoins_ok, stablecoins_msg),
                'Yahoo Finance': (yahoo_ok, yahoo_msg)
            }
            st.session_state.last_check = current_time
    
    # Display health status
    for service, (ok, msg) in st.session_state.health_checks.items():
        if ok:
            st.success(f"✅ {msg}")
        else:
            st.error(f"❌ {msg}")

st.markdown(f"Data from **{START_DATE}** to **{END_DATE}**")

# Show raw data
if st.checkbox("Show raw data"):
    st.dataframe(master_df)

import altair as alt

# Custom theme for dark background with light text
def custom_theme():
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

alt.themes.register("custom_theme", custom_theme)
alt.themes.enable("custom_theme")

axis_style = alt.Axis(
    labelColor="#e6eaf1",
    titleColor="#e6eaf1",
    labelFontSize=12,
    titleFontSize=14,
    titleFontWeight="bold",
    gridColor="#31333F"
)
# Line charts
# Separate the DSG10 line chart from the SOFR - FFR chart and expand the y-axis scale
st.subheader("10-Year Treasury Yield (DGS10)")

dgs_min = master_df["DGS10"].min()
dgs_max = master_df["DGS10"].max()
padding = (dgs_max - dgs_min) * 0.1  # 10% padding

# Make the axis labels dark and easier to read using axis_style
chart_dgs10 = alt.Chart(master_df).mark_line().encode(
    x=alt.X("date:T", axis=axis_style),
    y=alt.Y(
        "DGS10:Q",
        scale=alt.Scale(domain=[dgs_min - padding, dgs_max + padding]),
        axis=axis_style
    ),
    tooltip=["date:T", "DGS10:Q"]
).interactive()

st.altair_chart(chart_dgs10, width="stretch")

st.subheader("SOFR vs FFR (Zoomed Spread View)")

# Melt data for Altair
rates_df = master_df[["date", "SOFR", "FFR"]].melt(id_vars="date")

# Tight y-axis around the two series
min_rate = rates_df["value"].min()
max_rate = rates_df["value"].max()

# Expand slightly so lines aren’t on borders
padding = (max_rate - min_rate) * 0.5  # exaggerates spread visibility


# Make chart with axis_style and designate line colors red and blue
chart_rates = alt.Chart(rates_df).mark_line().encode(
    x=alt.X("date:T", axis=axis_style),
    y=alt.Y(
        "value:Q",
        scale=alt.Scale(domain=[min_rate - padding, max_rate + padding]),
        axis=axis_style
    ),
    color=alt.Color(
        "variable:N",
        scale=alt.Scale(
            domain=["SOFR", "FFR"],
            range=["red", "blue"]
        ),
        legend=alt.Legend(title="Rate")
    ),
    tooltip=["date:T", "variable:N", "value:Q"]
).interactive()

st.altair_chart(chart_rates, width="stretch")

st.subheader("SOFR Spread (SOFR - FFR)")
st.line_chart(master_df[["date", "SOFR_Spread"]].set_index("date"))

st.subheader("Stablecoin Market Cap (USD) — Zoomed View")

sc_min = master_df["Stablecoin Mkt Cap"].min()
sc_max = master_df["Stablecoin Mkt Cap"].max()

# Add small padding so the line isn't touching edges
padding = (sc_max - sc_min) * 0.1

# Make chart with axis_style and pad scale
chart_stable = alt.Chart(master_df).mark_line().encode(
    x=alt.X("date:T", axis=axis_style),
    y=alt.Y(
        "Stablecoin Mkt Cap:Q",
        scale=alt.Scale(domain=[sc_min - padding, sc_max + padding]),
        axis=axis_style
    ),
    tooltip=["date:T", "Stablecoin Mkt Cap:Q"]
).interactive()

st.altair_chart(chart_stable, width="stretch")

# Show percent change in Stablecoin Market Cap chart
master_df["Stablecoin % Change"] = master_df["Stablecoin Mkt Cap"].pct_change() * 100

st.subheader("Stablecoin Market Cap (% Change)")

# Make chart with axis_style
chart_pct = alt.Chart(master_df).mark_line().encode(
    x=alt.X("date:T", axis=axis_style),
    y=alt.Y("Stablecoin % Change:Q", axis=axis_style),
    tooltip=["date:T", "Stablecoin % Change:Q"]
).interactive()

st.altair_chart(chart_pct, width="stretch")

st.subheader("VIX Index Daily Price")

chart_vix = alt.Chart(vix).mark_line().encode(
    x=alt.X("date:T", axis=axis_style),
    y=alt.Y("VIX:Q", axis=axis_style),
    tooltip=["date:T", "VIX:Q"]
).interactive()

st.altair_chart(chart_vix, width="stretch")

st.subheader("SPY ETF Daily Price")

chart_spy = alt.Chart(spy).mark_line().encode(
    x=alt.X("date:T", axis=axis_style),
    y=alt.Y(
        "SPY:Q",
        scale=alt.Scale(domain=[600, 800]),
        axis=axis_style
    ),
    tooltip=["date:T", "SPY:Q"]
).interactive()

st.altair_chart(chart_spy, width="stretch")

st.subheader("GLD ETF Daily Price")

chart_gld = alt.Chart(gld).mark_line().encode(
    x=alt.X("date:T", axis=axis_style),
    y=alt.Y(
        "GLD:Q",
        scale=alt.Scale(zero=False),  # keeps movement visible
        axis=axis_style
    ),
    tooltip=["date:T", "GLD:Q"]
).interactive()

st.altair_chart(chart_gld, width="stretch")

# ------------------------
# VTIP Chart
# ------------------------
st.subheader("VTIP ETF Daily Price")

chart_vtip = alt.Chart(vtip).mark_line().encode(
    x=alt.X("date:T", axis=axis_style),
    y=alt.Y(
        "VTIP:Q",
        scale=alt.Scale(zero=False),
        axis=axis_style
    ),
    tooltip=["date:T", "VTIP:Q"]
).interactive()

st.altair_chart(chart_vtip, width="stretch")

# ------------------------
# TLT Chart
# ------------------------
st.subheader("TLT ETF Daily Price")

chart_tlt = alt.Chart(tlt).mark_line().encode(
    x=alt.X("date:T", axis=axis_style),
    y=alt.Y(
        "TLT:Q",
        scale=alt.Scale(zero=False),
        axis=axis_style
    ),
    tooltip=["date:T", "TLT:Q"]
).interactive()

st.altair_chart(chart_tlt, width="stretch")

# ------------------------
# CRCL Chart
# ------------------------
st.subheader("CRCL Daily Price")

chart_crcl = alt.Chart(crcl).mark_line().encode(
    x=alt.X("date:T", axis=axis_style),
    y=alt.Y(
        "CRCL:Q",
        scale=alt.Scale(zero=False),
        axis=axis_style
    ),
    tooltip=["date:T", "CRCL:Q"]
).interactive()

st.altair_chart(chart_crcl, width="stretch")

# ------------------------
# DRAM Chart
# ------------------------
st.subheader("DRAM Daily Price")

chart_dram = alt.Chart(dram).mark_line().encode(
    x=alt.X("date:T", axis=axis_style),
    y=alt.Y(
        "DRAM:Q",
        scale=alt.Scale(zero=False),
        axis=axis_style
    ),
    tooltip=["date:T", "DRAM:Q"]
).interactive()

st.altair_chart(chart_dram, width="stretch")

# ------------------------
# JNK Chart
# ------------------------
st.subheader("JNK ETF Daily Price")

chart_jnk = alt.Chart(jnk).mark_line().encode(
    x=alt.X("date:T", axis=axis_style),
    y=alt.Y(
        "JNK:Q",
        scale=alt.Scale(zero=False),
        axis=axis_style
    ),
    tooltip=["date:T", "JNK:Q"]
).interactive()

st.altair_chart(chart_jnk, width="stretch")

# ------------------------
# EMB Chart
# ------------------------
st.subheader("EMB ETF Daily Price")

chart_emb = alt.Chart(emb).mark_line().encode(
    x=alt.X("date:T", axis=axis_style),
    y=alt.Y(
        "EMB:Q",
        scale=alt.Scale(zero=False),
        axis=axis_style
    ),
    tooltip=["date:T", "EMB:Q"]
).interactive()

st.altair_chart(chart_emb, width="stretch")

# ------------------------
# STRESS COMPOSITE INDICATOR (REAL DATA)
# ------------------------
st.subheader("📈 Market Stress Composite Index (Real Data)")

try:
    # Prepare REAL data for stress composite from what we already fetched
    
    # VIX data (already have)
    vix_series = vix.set_index("date")["VIX"]
    
    # Credit spread proxy: BAA-AAA spread
    # Using JNK (junk bond ETF) as BAA proxy and TLT (treasury ETF) as AAA proxy
    # Calculate returns/spread between them
    jnk_data = jnk.set_index("date")["JNK"]
    tlt_data = tlt.set_index("date")["TLT"]
    
    # Calculate simple proxy for credit spread: (TLT - JNK) / TLT or similar
    # Actually, let's use the ratio or difference in returns
    jnk_returns = jnk_data.pct_change()
    tlt_returns = tlt_data.pct_change()
    # Credit spread proxy: when junk bonds underperform treasuries, spread widens
    credit_spread_proxy = (tlt_returns - jnk_returns).fillna(0)  # This needs to be made positive and scaled
    
    # Better approach: use price ratio - when JNK/TLT ratio decreases, credit stress increases
    # But let's make a simple proxy that works with our minmax_scale function
    # We'll use the negative correlation: when JNK underperforms (negative returns relative to TLT), stress increases
    credit_spread_series = -(jnk_returns - tlt_returns).fillna(0)  # Negative when JNK does worse than TLT
    
    # Stablecoin dominance (we have market cap, need % of total crypto market approx)
    # For now, we'll use the market cap directly and normalize it (it will show trends)
    stablecoin_series = stable_df.set_index("date")["Stablecoin Mkt Cap"]
    
    # BTC returns (we don't have BTC data yet, let's add it)
    btc_data = yf.download("BTC-USD", start=START_DATE, end=END_DATE, progress=False)
    if not btc_data.empty:
        btc_data = btc_data.reset_index()[["Date", "Close"]]
        btc_data.columns = ["date", "BTC"]
        btc_data["date"] = pd.to_datetime(btc_data["date"])
        btc_returns_series = btc_data.set_index("date")["BTC"].pct_change()
    else:
        # Fallback if BTC download fails
        btc_returns_series = pd.Series(0, index=pd.bdate_range(start=START_DATE, end=END_DATE))
    
    # Funding rate proxy (we don't have real funding rates, use volatility proxy)
    # Using BTC volatility as a proxy for funding rate stress
    if not btc_data.empty:
        btc_vol = btc_returns_series.rolling(30).std() * np.sqrt(365)  # Annualized
        funding_rate_series = btc_vol.bfill().ffill()
    else:
        funding_rate_series = pd.Series(0.01, index=pd.bdate_range(start=START_DATE, end=END_DATE))  # Low constant
    
    # Ensure all series have the same index (business days)
    common_index = pd.bdate_range(start=START_DATE, end=END_DATE)
    
    # Align all series to common index
    vix_aligned = vix_series.reindex(common_index)
    credit_aligned = credit_spread_series.reindex(common_index)
    stablecoin_aligned = stablecoin_series.reindex(common_index)
    btc_returns_aligned = btc_returns_series.reindex(common_index)
    funding_aligned = funding_rate_series.reindex(common_index)
    
    # Fill any remaining NaN values
    vix_aligned = vix_aligned.bfill().ffill()
    credit_aligned = credit_aligned.bfill().ffill()
    stablecoin_aligned = stablecoin_aligned.bfill().ffill()
    btc_returns_aligned = btc_returns_aligned.bfill().ffill()
    funding_aligned = funding_aligned.bfill().ffill()
    
    # Build stress composite with REAL data
    stress_df = build_stress_composite(
        vix=vix_aligned,
        baa_aaa_spread=credit_aligned,
        stablecoin_dominance=stablecoin_aligned,
        btc_returns=btc_returns_aligned,
        funding_rate=funding_aligned
    )
    
    # Get latest snapshot
    snapshot = latest_stress_snapshot(stress_df)
    
    # Display metrics in columns
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="Stress Score",
            value=f"{snapshot['stress_score']}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="Market Regime",
            value=snapshot['regime']
        )
    
    with col3:
        st.metric(
            label="VIX Stress",
            value=f"{snapshot['vix_score']}"
        )
    
    with col4:
        st.metric(
            label="Credit Stress",
            value=f"{snapshot['credit_score']}"
        )
    
    with col5:
        st.metric(
            label="Stablecoin Stress",
            value=f"{snapshot['stablecoin_score']}"
        )
    
    # Stress composite chart
    stress_chart = alt.Chart(stress_df.reset_index()).mark_line().encode(
        x=alt.X('date:T', axis=axis_style),
        y=alt.Y('stress_composite:Q', axis=axis_style),
        color=alt.Color('stress_regime:N', scale=alt.Scale(
            domain=['Low Stress', 'Moderate Stress', 'High Stress', 'Crisis'],
            range=['green', 'yellow', 'orange', 'red']
        )),
        tooltip=['date:T', 'stress_composite:Q', 'stress_regime:N']
    ).interactive()
    
    st.altair_chart(stress_chart, width="stretch")
    
    # Component breakdown
    st.subheader("Component Breakdown")
    component_data = stress_df[['vix_score', 'credit_score', 'stablecoin_score', 'btc_vol_score', 'funding_score']].reset_index()
    component_melted = component_data.melt(id_vars=['date'], var_name='component', value_name='score')
    
    component_chart = alt.Chart(component_melted).mark_line().encode(
        x=alt.X('date:T', axis=axis_style),
        y=alt.Y('score:Q', axis=axis_style),
        color='component:N',
        tooltip=['date:T', 'component:N', 'score:Q']
    ).interactive()
    
    st.altair_chart(component_chart, width="stretch")
    
    # Show what data we're using
    with st.expander("📊 Data Sources Used"):
        st.write("**VIX**: CBOE Volatility Index (^VIX)")
        st.write("**Credit Spread Proxy**: JNK (junk bonds) vs TLT (treasuries) relative performance")
        st.write("**Stablecoin Dominance**: Stablecoin market cap from stablecoins.llama.fi")
        st.write("**BTC Returns**: Bitcoin USD price changes")
        st.write("**Funding Rate Proxy**: BTC volatility (annualized)")
    
except Exception as e:
    st.error(f"Error generating stress composite: {str(e)}")
    st.info("Falling back to placeholder data...")
    
    # Fallback to sample data if real data fails
    dates = pd.bdate_range(start=START_DATE, end=END_DATE)
    sample_data = pd.DataFrame({
        'date': dates,
        'vix': np.random.uniform(15, 35, len(dates)),  # Proxy VIX
        'baa_aaa_spread': np.random.uniform(1.0, 2.5, len(dates)),  # Proxy credit spread
        'stablecoin_dominance': np.random.uniform(5.0, 8.0, len(dates)),  # Proxy stablecoin dominance
        'btc_returns': np.random.normal(0, 0.03, len(dates)),  # Proxy BTC returns
        'funding_rate': np.random.normal(0, 0.0005, len(dates))  # Proxy funding rate
    })
    sample_data.set_index('date', inplace=True)
    
    # Build stress composite
    stress_df = build_stress_composite(
        vix=sample_data['vix'],
        baa_aaa_spread=sample_data['baa_aaa_spread'],
        stablecoin_dominance=sample_data['stablecoin_dominance'],
        btc_returns=sample_data['btc_returns'],
        funding_rate=sample_data['funding_rate']
    )
    
    # Get latest snapshot
    snapshot = latest_stress_snapshot(stress_df)
    
    # Display metrics in columns
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="Stress Score",
            value=f"{snapshot['stress_score']}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="Market Regime",
            value=snapshot['regime']
        )
    
    with col3:
        st.metric(
            label="VIX Stress",
            value=f"{snapshot['vix_score']}"
        )
    
    with col4:
        st.metric(
            label="Credit Stress",
            value=f"{snapshot['credit_score']}"
        )
    
    with col5:
        st.metric(
            label="Stablecoin Stress",
            value=f"{snapshot['stablecoin_score']}"
        )
    
    # Stress composite chart
    stress_chart = alt.Chart(stress_df.reset_index()).mark_line().encode(
        x=alt.X('date:T', axis=axis_style),
        y=alt.Y('stress_composite:Q', axis=axis_style),
        color=alt.Color('stress_regime:N', scale=alt.Scale(
            domain=['Low Stress', 'Moderate Stress', 'High Stress', 'Crisis'],
            range=['green', 'yellow', 'orange', 'red']
        )),
        tooltip=['date:T', 'stress_composite:Q', 'stress_regime:N']
    ).interactive()
    
    st.altair_chart(stress_chart, width="stretch")
    
    # Component breakdown
    st.subheader("Component Breakdown")
    component_data = stress_df[['vix_score', 'credit_score', 'stablecoin_score', 'btc_vol_score', 'funding_score']].reset_index()
    component_melted = component_data.melt(id_vars=['date'], var_name='component', value_name='score')
    
    component_chart = alt.Chart(component_melted).mark_line().encode(
        x=alt.X('date:T', axis=axis_style),
        y=alt.Y('score:Q', axis=axis_style),
        color='component:N',
        tooltip=['date:T', 'component:N', 'score:Q']
    ).interactive()
    
    st.altair_chart(component_chart, width="stretch")