#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
complex_dash.py

Production-grade Streamlit macro / crypto dashboard
with real market stress composite integration.
"""

import os
import time
import datetime
import requests

import numpy as np
import pandas as pd
import yfinance as yf
import streamlit as st
import altair as alt

from dotenv import load_dotenv

from metrics.stress_composite import (
    build_stress_composite,
    latest_stress_snapshot
)

# -----------------------------------------------------------------------------
# ENVIRONMENT
# -----------------------------------------------------------------------------

load_dotenv()

FRED_API_KEY = os.getenv("FRED_API_KEY")

if not FRED_API_KEY:
    st.error(
        "FRED_API_KEY not found in environment variables."
    )
    st.stop()

# -----------------------------------------------------------------------------
# DATE RANGE
# -----------------------------------------------------------------------------

TODAY = datetime.date.today()

END_DATE = TODAY - datetime.timedelta(days=1)

# IMPORTANT:
# Need enough history for rolling windows
START_DATE = END_DATE - datetime.timedelta(days=365)

# -----------------------------------------------------------------------------
# FRED SERIES
# -----------------------------------------------------------------------------

SERIES = {
    "SOFR": "SOFR",
    "FFR": "DFF",
    "DGS10": "DGS10"
}

# -----------------------------------------------------------------------------
# HEALTH CHECKS
# -----------------------------------------------------------------------------

def check_fred_api():

    try:

        url = (
            "https://api.stlouisfed.org/"
            "fred/series/observations"
        )

        params = {
            "series_id": "DFF",
            "api_key": FRED_API_KEY,
            "file_type": "json",
            "observation_start": "2024-01-01",
            "observation_end": "2024-01-02"
        }

        response = requests.get(
            url,
            params=params,
            timeout=5
        )

        if response.status_code == 200:

            data = response.json()

            if (
                "observations" in data
                and len(data["observations"]) > 0
            ):
                return True, "FRED API: OK"

        return False, (
            f"FRED API: Error "
            f"{response.status_code}"
        )

    except Exception as e:

        return (
            False,
            f"FRED API: Connection failed "
            f"({str(e)[:50]}...)"
        )


def check_stablecoins_api():

    try:

        url = (
            "https://stablecoins.llama.fi/"
            "stablecoincharts/all"
        )

        response = requests.get(
            url,
            timeout=5
        )

        if response.status_code == 200:

            data = response.json()

            if isinstance(data, list) and len(data) > 0:
                return True, "Stablecoins API: OK"

        return (
            False,
            f"Stablecoins API: "
            f"Error {response.status_code}"
        )

    except Exception as e:

        return (
            False,
            f"Stablecoins API: "
            f"Connection failed "
            f"({str(e)[:50]}...)"
        )


def check_yfinance_api():

    try:

        spy = yf.download(
            "SPY",
            period="1d",
            progress=False
        )

        if not spy.empty:
            return True, "Yahoo Finance: OK"

        return False, "Yahoo Finance: No data returned"

    except Exception as e:

        return (
            False,
            f"Yahoo Finance: Connection failed "
            f"({str(e)[:50]}...)"
        )

# -----------------------------------------------------------------------------
# DATA FETCHERS
# -----------------------------------------------------------------------------

def get_fred_series(series_name, series_id):

    url = (
        "https://api.stlouisfed.org/"
        "fred/series/observations"
    )

    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "observation_start":
            START_DATE.strftime("%Y-%m-%d"),
        "observation_end":
            END_DATE.strftime("%Y-%m-%d")
    }

    response = requests.get(url, params=params)

    data = response.json()

    df = pd.DataFrame(data["observations"])

    df["date"] = pd.to_datetime(df["date"])

    df["value"] = pd.to_numeric(
        df["value"],
        errors="coerce"
    )

    df.rename(
        columns={"value": series_name},
        inplace=True
    )

    return df[["date", series_name]]


def get_stablecoin_marketcap():

    try:

        url = (
            "https://stablecoins.llama.fi/"
            "stablecoincharts/all"
        )

        response = requests.get(url, timeout=10)

        response.raise_for_status()

        data = response.json()

        records = []

        for entry in data:

            date = datetime.datetime.fromtimestamp(
                int(entry["date"])
            )

            total_circulating = entry.get(
                "totalCirculatingUSD",
                {}
            )

            total_usd = sum(
                total_circulating.values()
            )

            records.append({
                "date": date,
                "Stablecoin Mkt Cap": total_usd
            })

        df = pd.DataFrame(records)

        df = df[
            (df["date"] >= pd.Timestamp(START_DATE))
            &
            (df["date"] <= pd.Timestamp(END_DATE))
        ]

        df.set_index("date", inplace=True)

        df = df.resample("B").last()

        df.ffill(inplace=True)

        df.reset_index(inplace=True)

        return df

    except Exception as e:

        st.warning(
            f"Stablecoin API error: {str(e)}"
        )

        return pd.DataFrame(
            columns=[
                "date",
                "Stablecoin Mkt Cap"
            ]
        )

# -----------------------------------------------------------------------------
# MASTER DATAFRAME
# -----------------------------------------------------------------------------

date_range = pd.bdate_range(
    start=START_DATE,
    end=END_DATE
)

master_df = pd.DataFrame({
    "date": date_range
})

# -----------------------------------------------------------------------------
# MERGE FRED DATA
# -----------------------------------------------------------------------------

for display_name, fred_id in SERIES.items():

    fred_df = get_fred_series(
        display_name,
        fred_id
    )

    master_df = master_df.merge(
        fred_df,
        on="date",
        how="left"
    )

# -----------------------------------------------------------------------------
# MERGE STABLECOIN DATA
# -----------------------------------------------------------------------------

stable_df = get_stablecoin_marketcap()

master_df = master_df.merge(
    stable_df,
    on="date",
    how="left"
)

master_df.sort_values(
    "date",
    inplace=True
)

master_df.ffill(inplace=True)

# -----------------------------------------------------------------------------
# YAHOO FINANCE DATA
# -----------------------------------------------------------------------------

def fetch_yf_series(ticker, column_name):

    df = yf.download(
        ticker,
        start=START_DATE,
        end=END_DATE,
        progress=False
    )

    df = df.reset_index()[["Date", "Close"]]

    df.columns = ["date", column_name]

    df["date"] = pd.to_datetime(df["date"])

    return df


spy  = fetch_yf_series("SPY", "SPY")
vix  = fetch_yf_series("^VIX", "VIX")
gld  = fetch_yf_series("GLD", "GLD")
vtip = fetch_yf_series("VTIP", "VTIP")
tlt  = fetch_yf_series("TLT", "TLT")
crcl = fetch_yf_series("CRCL", "CRCL")
dram = fetch_yf_series("DRAM", "DRAM")
jnk  = fetch_yf_series("JNK", "JNK")
emb  = fetch_yf_series("EMB", "EMB")
btc  = fetch_yf_series("BTC-USD", "BTC")

# -----------------------------------------------------------------------------
# DERIVED METRICS
# -----------------------------------------------------------------------------

master_df["SOFR_Spread"] = (
    master_df["SOFR"] -
    master_df["FFR"]
)

# -----------------------------------------------------------------------------
# STREAMLIT
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="Market Dashboard",
    layout="wide"
)

st.title("📊 Market Data Dashboard")

# -----------------------------------------------------------------------------
# SIDEBAR HEALTH
# -----------------------------------------------------------------------------

with st.sidebar:

    st.subheader("🔧 System Health")

    if "health_checks" not in st.session_state:

        st.session_state.health_checks = {}

        st.session_state.last_check = 0

    current_time = time.time()

    if (
        current_time -
        st.session_state.last_check > 30
        or not st.session_state.health_checks
    ):

        with st.spinner("Checking APIs..."):

            fred_ok, fred_msg = check_fred_api()

            stable_ok, stable_msg = (
                check_stablecoins_api()
            )

            yahoo_ok, yahoo_msg = (
                check_yfinance_api()
            )

            st.session_state.health_checks = {
                "FRED": (fred_ok, fred_msg),
                "Stablecoins": (
                    stable_ok,
                    stable_msg
                ),
                "Yahoo": (
                    yahoo_ok,
                    yahoo_msg
                )
            }

            st.session_state.last_check = current_time

    for service, (ok, msg) in (
        st.session_state.health_checks.items()
    ):

        if ok:
            st.success(f"✅ {msg}")
        else:
            st.error(f"❌ {msg}")

# -----------------------------------------------------------------------------
# ALTAIR THEME
# -----------------------------------------------------------------------------

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

alt.themes.register(
    "custom_theme",
    custom_theme
)

alt.themes.enable("custom_theme")

axis_style = alt.Axis(
    labelColor="#e6eaf1",
    titleColor="#e6eaf1",
    labelFontSize=12,
    titleFontSize=14,
    titleFontWeight="bold",
    gridColor="#31333F"
)

# -----------------------------------------------------------------------------
# BASIC CHARTS
# -----------------------------------------------------------------------------

st.subheader("10Y Treasury Yield")

chart_dgs10 = alt.Chart(
    master_df
).mark_line().encode(

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

st.altair_chart(
    chart_dgs10,
    width="stretch"
)

# -----------------------------------------------------------------------------
# STRESS COMPOSITE
# -----------------------------------------------------------------------------

st.subheader(
    "📈 Market Stress Composite Index"
)

try:

    # -------------------------------------------------------------------------
    # REAL INPUT SERIES
    # -------------------------------------------------------------------------

    vix_series = (
        vix
        .set_index("date")["VIX"]
        .astype(float)
    )

    jnk_series = (
        jnk
        .set_index("date")["JNK"]
        .astype(float)
    )

    tlt_series = (
        tlt
        .set_index("date")["TLT"]
        .astype(float)
    )

    stablecoin_series = (
        master_df
        .set_index("date")[
            "Stablecoin Mkt Cap"
        ]
        .astype(float)
    )

    btc["returns"] = (
        btc["BTC"]
        .pct_change()
    )

    btc_returns = (
        btc
        .set_index("date")[
            "returns"
        ]
    )

    # -------------------------------------------------------------------------
    # CREDIT STRESS PROXY
    # -------------------------------------------------------------------------

    credit_proxy = (
        (tlt_series / jnk_series)
        .pct_change()
        .rolling(5)
        .mean()
    )

    # -------------------------------------------------------------------------
    # STABLECOIN DOMINANCE PROXY
    # -------------------------------------------------------------------------

    stablecoin_dominance = (
        stablecoin_series
        .pct_change()
        .rolling(7)
        .mean()
    )

    # -------------------------------------------------------------------------
    # FUNDING PROXY
    # -------------------------------------------------------------------------

    funding_proxy = (
        btc_returns
        .rolling(3)
        .mean()
        * 0.05
    )

    # -------------------------------------------------------------------------
    # ALIGN SERIES
    # -------------------------------------------------------------------------

    stress_inputs = pd.concat([
        vix_series.rename("vix"),
        credit_proxy.rename("credit"),
        stablecoin_dominance.rename(
            "stablecoin"
        ),
        btc_returns.rename(
            "btc_returns"
        ),
        funding_proxy.rename(
            "funding"
        )
    ], axis=1)

    stress_inputs.sort_index(
        inplace=True
    )

    stress_inputs.ffill(
        inplace=True
    )

    stress_inputs.dropna(
        inplace=True
    )

    # -------------------------------------------------------------------------
    # BUILD COMPOSITE
    # -------------------------------------------------------------------------

    stress_df = build_stress_composite(
        vix=stress_inputs["vix"],
        baa_aaa_spread=stress_inputs[
            "credit"
        ],
        stablecoin_dominance=stress_inputs[
            "stablecoin"
        ],
        btc_returns=stress_inputs[
            "btc_returns"
        ],
        funding_rate=stress_inputs[
            "funding"
        ]
    )

    stress_df.dropna(inplace=True)

    # -------------------------------------------------------------------------
    # SNAPSHOT
    # -------------------------------------------------------------------------

    snapshot = latest_stress_snapshot(
        stress_df
    )

    # -------------------------------------------------------------------------
    # METRICS
    # -------------------------------------------------------------------------

    col1, col2, col3, col4, col5 = (
        st.columns(5)
    )

    with col1:

        st.metric(
            "Stress Score",
            f"{snapshot['stress_score']}"
        )

    with col2:

        st.metric(
            "Regime",
            snapshot["regime"]
        )

    with col3:

        st.metric(
            "VIX Stress",
            f"{snapshot['vix_score']}"
        )

    with col4:

        st.metric(
            "Credit Stress",
            f"{snapshot['credit_score']}"
        )

    with col5:

        st.metric(
            "Stablecoin Stress",
            f"{snapshot['stablecoin_score']}"
        )

    # -------------------------------------------------------------------------
    # STRESS CHART
    # -------------------------------------------------------------------------

    df_reset = stress_df.reset_index()
    min_date = df_reset["date"].min()
    max_date = df_reset["date"].max()

    bands_df = pd.DataFrame([
        {"start": min_date, "end": max_date, "ymin": 0,  "ymax": 25,  "regime": "Low Stress"},
        {"start": min_date, "end": max_date, "ymin": 25, "ymax": 50,  "regime": "Moderate Stress"},
        {"start": min_date, "end": max_date, "ymin": 50, "ymax": 75,  "regime": "High Stress"},
        {"start": min_date, "end": max_date, "ymin": 75, "ymax": 100, "regime": "Crisis"}
    ])

    rules_df = pd.DataFrame({"y": [25, 50, 75]})

    bands = alt.Chart(bands_df).mark_rect().encode(
        x=alt.X("start:T", axis=axis_style, title=None),
        x2=alt.X2("end:T"),
        y=alt.Y("ymin:Q", axis=None),
        y2=alt.Y2("ymax:Q"),
        color=alt.Color(
            "regime:N",
            scale=alt.Scale(
                domain=["Crisis", "High Stress", "Moderate Stress", "Low Stress"],
                range=[
                    "rgba(244, 67, 54, 0.45)",   # Crisis (Red)
                    "rgba(255, 152, 0, 0.33)",   # High Stress (Orange)
                    "rgba(255, 235, 59, 0.24)",  # Moderate Stress (Yellow)
                    "rgba(76, 175, 80, 0.16)"    # Low Stress (Green)
                ]
            ),
            legend=alt.Legend(
                title="Stress Regime",
                orient="right",
                labelColor="white",
                titleColor="white",
                labelFontSize=11,
                titleFontSize=12
            )
        ),
        tooltip=alt.value(None)
    )

    rules = alt.Chart(rules_df).mark_rule(
        color="#31333F",
        strokeWidth=1.5,
        strokeDash=[4, 4]
    ).encode(
        y=alt.Y("y:Q")
    )

    line = alt.Chart(df_reset).mark_line(
        color="#00E5FF",
        strokeWidth=2.5
    ).encode(
        x=alt.X(
            "date:T",
            axis=axis_style,
            title=None
        ),
        y=alt.Y(
            "stress_composite:Q",
            axis=axis_style,
            scale=alt.Scale(domain=[0, 100]),
            title="Stress Composite Index"
        ),
        tooltip=[
            "date:T",
            alt.Tooltip("stress_composite:Q", format=".2f", title="Stress Score"),
            alt.Tooltip("stress_regime:N", title="Regime")
        ]
    )

    stress_chart = alt.layer(bands, rules, line).interactive()

    st.altair_chart(
        stress_chart,
        width="stretch"
    )

    # -------------------------------------------------------------------------
    # COMPONENT BREAKDOWN
    # -------------------------------------------------------------------------

    st.subheader(
        "Component Breakdown"
    )

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

    st.altair_chart(
        component_chart,
        width="stretch"
    )

except Exception as e:

    st.error(
        f"Error generating stress composite: "
        f"{str(e)}"
    )
