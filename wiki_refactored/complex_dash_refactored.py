    # VIX
    st.write("**VIX Index Daily Price")
    vix_chart = alt.Chart(etf_data["VIX"], width=800, height=400).mark_line().encode(
        x=alt.X("date:T", axis=create_axis_style()),
        y=alt.Y("VIX Index (Volatility):Q", axis=create_axis_style()),
        tooltip=["date:T", "VIX Index (Volatility):Q"]
    ).interactive()
    st.altair_chart(vix_chart, width="stretch")
    st.altair_chart(vix_chart, width="stretch")