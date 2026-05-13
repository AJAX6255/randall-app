#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 28 13:11:41 2026

@author: randall
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 28 00:48:26 2026
Streamlit Dashboard for Market Data
@author: randall
"""
import yfinance as yf
import pandas as pd
import requests
import datetime
import streamlit as st

FRED_API_KEY = "c1bb49f53350af1c4195497fa3f1c38a"

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

st.markdown(f"Data from **{START_DATE}** to **{END_DATE}**")

# Show raw data
if st.checkbox("Show raw data"):
    st.dataframe(master_df)

import altair as alt

axis_style = alt.Axis(
    labelColor="black",
    titleColor="black",
    labelFontSize=12,
    titleFontSize=14,
    titleFontWeight="bold",
    gridColor="lightgray"
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




# Optional: Altair interactive chart
import altair as alt

st.subheader("VIX Index Daily Price")

chart_vix = alt.Chart(vix).mark_line().encode(
    x=alt.X("date:T", axis=axis_style),
    y=alt.Y("VIX:Q", axis=axis_style),
    tooltip=["date:T", "VIX:Q"]
).interactive()

st.altair_chart(chart_vix, width="stretch")

st.subheader("SPY ETF Daily Price")

chart_spy = alt.Chart(spy).mark_line().encode(
    x=alt.X("date:T"),
    y=alt.Y(
        "SPY:Q",
        scale=alt.Scale(domain=[600, 800])   # 👈 THIS IS THE KEY
    ),
    tooltip=["date:T", "SPY:Q"]
).interactive()

st.altair_chart(chart_spy, width="stretch")

st.subheader("GLD ETF Daily Price")

chart_gld = alt.Chart(gld).mark_line().encode(
    x=alt.X("date:T"),
    y=alt.Y(
        "GLD:Q",
        scale=alt.Scale(zero=False)  # keeps movement visible
    ),
    tooltip=["date:T", "GLD:Q"]
).interactive()

st.altair_chart(chart_gld, width="stretch")

# ------------------------
# VTIP Chart
# ------------------------
st.subheader("VTIP ETF Daily Price")

chart_vtip = alt.Chart(vtip).mark_line().encode(
    x=alt.X("date:T"),
    y=alt.Y(
        "VTIP:Q",
        scale=alt.Scale(zero=False)
    ),
    tooltip=["date:T", "VTIP:Q"]
).interactive()

st.altair_chart(chart_vtip, width="stretch")


# ------------------------
# TLT Chart
# ------------------------
st.subheader("TLT ETF Daily Price")

chart_tlt = alt.Chart(tlt).mark_line().encode(
    x=alt.X("date:T"),
    y=alt.Y(
        "TLT:Q",
        scale=alt.Scale(zero=False)
    ),
    tooltip=["date:T", "TLT:Q"]
).interactive()

st.altair_chart(chart_tlt, width="stretch")


# ------------------------
# CRCL Chart
# ------------------------
st.subheader("CRCL Daily Price")

chart_crcl = alt.Chart(crcl).mark_line().encode(
    x=alt.X("date:T"),
    y=alt.Y(
        "CRCL:Q",
        scale=alt.Scale(zero=False)
    ),
    tooltip=["date:T", "CRCL:Q"]
).interactive()

st.altair_chart(chart_crcl, width="stretch")


# ------------------------
# DRAM Chart
# ------------------------
st.subheader("DRAM Daily Price")

chart_dram = alt.Chart(dram).mark_line().encode(
    x=alt.X("date:T"),
    y=alt.Y(
        "DRAM:Q",
        scale=alt.Scale(zero=False)
    ),
    tooltip=["date:T", "DRAM:Q"]
).interactive()

st.altair_chart(chart_dram, width="stretch")


# ------------------------
# JNK Chart
# ------------------------
st.subheader("JNK ETF Daily Price")

chart_jnk = alt.Chart(jnk).mark_line().encode(
    x=alt.X("date:T"),
    y=alt.Y(
        "JNK:Q",
        scale=alt.Scale(zero=False)
    ),
    tooltip=["date:T", "JNK:Q"]
).interactive()

st.altair_chart(chart_jnk, width="stretch")


# ------------------------
# EMB Chart
# ------------------------
st.subheader("EMB ETF Daily Price")

chart_emb = alt.Chart(emb).mark_line().encode(
    x=alt.X("date:T"),
    y=alt.Y(
        "EMB:Q",
        scale=alt.Scale(zero=False)
    ),
    tooltip=["date:T", "EMB:Q"]
).interactive()

st.altair_chart(chart_emb, width="stretch")
