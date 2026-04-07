import datetime
from src.montecarlo import MonteCarloSimulation
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="HSY Award Valuation", layout="wide", initial_sidebar_state="collapsed"
)

with st.sidebar:
    st.title("Inputs")
    initial_price = st.number_input("Current Stock Price", value=172.13, step=1.0)
    reward_price = st.number_input("Reward Price", value=300.00, step=1.0)
    volatility = st.number_input("Volatility", value=0.2356, step=0.01, format="%.4f")
    risk_free_rate = st.number_input(
        "Risk Free Rate", value=0.03577, step=0.001, format="%.5f"
    )
    dividend_yield = st.number_input(
        "Dividend Yield", value=0.03202, step=0.001, format="%.5f"
    )
    run = st.button("Run Simulation", use_container_width=True)
if "results" not in st.session_state or run:
    with st.spinner("Running Simulations..."):
        st.session_state.results = MonteCarloSimulation(
            stock_price=initial_price,
            risk_free_rate=risk_free_rate,
            dividend_yield=dividend_yield,
            volatility=volatility,
            reward_price=reward_price,
        ).simulation()

res = st.session_state.results
st.title("HSY Performance Award Valuation")
st.caption("Monte Carlo GBM risk-neutral framework 100,000 iterations")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Fair Value per Award", f"${res['fair_value'] / 100:,.2f}")
c2.metric("Total Fair Value", f"${res['fair_value']:,.2f}")
c3.metric("Vesting Probability", f"{res['vest_pct']:.2f}%")
c4.metric("Expected Value of All Runs", f"${res['final_price_all_runs']:,.2f}")
st.divider()

stock_paths = res["stock_paths"]
vested = res["vested"]
total_trading_days = res["total_trading_days"]
business_days = pd.bdate_range(
    start=datetime.date(2025, 10, 30), periods=total_trading_days
)
fig = go.Figure()
uninvested_paths = np.where(~vested)[0]
for i in np.random.choice(
    uninvested_paths, size=min(20, len(uninvested_paths)), replace=False
):
    fig.add_trace(
        go.Scatter(
            x=business_days,
            y=stock_paths[i],
            mode="lines",
            line=dict(color="gray", width=0.5),
            showlegend=False,
            hoverinfo="skip",
        )
    )
vested_paths = np.where(vested)[0]
for path, i in enumerate(
    np.random.choice(vested_paths, size=min(20, len(vested_paths)), replace=False)
):
    fig.add_trace(
        go.Scatter(
            x=business_days,
            y=stock_paths[i],
            mode="lines",
            line=dict(color="#388bfd", width=1.0),
            opacity=0.6,
            name="Vested" if path == 0 else None,
            showlegend=(path == 0),
            hoverinfo="skip",
        )
    )
fig.add_hline(
    y=reward_price,
    line=dict(color="red", dash="dash", width=1.5),
    # annotation_text=f"${reward_price:,.0f} Reward Price",
    # annotation_font_color="red",
)

fig.update_layout(
    height=420,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(title="Date", tickformat="%b '%y", gridcolor="#2a2a2a"),
    yaxis=dict(title="HSY Price ($)", gridcolor="#2a2a2a"),
    margin=dict(l=50, r=20, t=20, b=50),
)
st.subheader("Simulated Price Paths")
st.plotly_chart(fig, use_container_width=True)

st.divider()
