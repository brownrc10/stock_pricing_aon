import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from src.montecarlo import MonteCarloSimulation
from src.stockmarket import StockMarketInfo


@st.cache_data(show_spinner=False)
def run_simulation(
    stock_price: float,
    risk_free_rate: float,
    dividend_yield: float,
    volatility: float,
    reward_price: float,
):
    """
    USING METHOD TO ALLOW CACHING SO THAT WHEN THE STOCK REFRESHES
    THE ENTIRE DASHBOARD DOES NOT REFRESH
    """
    return MonteCarloSimulation(
        stock_price=stock_price,
        risk_free_rate=risk_free_rate,
        dividend_yield=dividend_yield,
        volatility=volatility,
        reward_price=reward_price,
    ).simulation()


st.set_page_config(
    page_title="HSY Award Valuation", layout="wide", initial_sidebar_state="collapsed"
)

# https://discuss.streamlit.io/t/streamlit-autorefresh/14519
# Set to 30 seconds
st_autorefresh(interval=90_000, key="price_refresh")

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

if "sim_inputs" not in st.session_state:
    st.session_state.sim_inputs = dict(
        stock_price=172.13,
        risk_free_rate=0.03577,
        dividend_yield=0.03202,
        volatility=0.2356,
        reward_price=300.00,
    )
if run:
    run_simulation.clear()
    st.session_state.sim_inputs = dict(
        stock_price=initial_price,
        risk_free_rate=risk_free_rate,
        dividend_yield=dividend_yield,
        volatility=volatility,
        reward_price=reward_price,
    )

if "results" not in st.session_state or run:
    with st.spinner("Running Simulations..."):
        st.session_state.results = run_simulation(**st.session_state.sim_inputs)
        res = st.session_state.results
        vested = res["vested"]

        uninvested_paths = np.where(~vested)[0]
        vested_paths = np.where(vested)[0]
        st.session_state.sampled_unvested = np.random.choice(
            uninvested_paths, size=min(20, len(uninvested_paths)), replace=False
        )
        st.session_state.sampled_vested = np.random.choice(
            vested_paths, size=min(20, len(vested_paths)), replace=False
        )
        st.session_state.percentiles = res["percentiles"]
percentiles = st.session_state.percentiles

res = st.session_state.results
st.title("HSY Performance Award Valuation")
st.caption("Monte Carlo GBM risk-neutral framework 50,000 iterations")
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Fair Value per Award", f"${res['fair_value'] / 100:,.2f}")
c2.metric("Total Fair Value", f"${res['fair_value']:,.2f}")
c3.metric("Vesting Probability", f"{res['vest_pct']:.2f}%")
c4.metric("Mean Value of Vested", f"${res['final_price_vested']:,.2f}")
c5.metric("Expected Value of All Runs", f"${res['final_price_all_runs']:,.2f}")
if "market_info" not in st.session_state:
    st.session_state.market_info = StockMarketInfo()
info = st.session_state.market_info
if info.is_open:
    prev_price = info.last_price
    info.refresh()
    c6.metric(
        label="HSY Live Price",
        value=f"${info.last_price:,.2f}",
        delta=StockMarketInfo.price_change(info.last_price, prev_price),
        delta_color=StockMarketInfo.price_change_color(info.last_price, prev_price),
    )
else:
    c6.metric(label="HSY Last Price", value=f"${info.last_price:,.2f}")
st.divider()

stock_paths = res["stock_paths"]
vested = res["vested"]
total_trading_days = res["total_trading_days"]
business_days = pd.bdate_range(
    start=datetime.date(2025, 10, 30), periods=total_trading_days
)

# https://plotly.com/python/graph-objects/

tab1, tab2 = st.tabs(["Simulated Paths", "Confidence Intervals"])
with tab1:
    fig = go.Figure()

    for i in st.session_state.sampled_unvested:
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
    for path, i in enumerate(st.session_state.sampled_vested):
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
        y=st.session_state.sim_inputs["reward_price"],
        line=dict(color="red", dash="dash", width=2.5),
    )
    fig.update_layout(
        height=420,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(font=dict(size=16)),
        xaxis=dict(
            title=dict(text="Date", font=dict(size=16)),
            tickfont=dict(size=16),
            tickformat="%b '%y",
            gridcolor="#2a2a2a",
        ),
        yaxis=dict(
            title=dict(text="HSY Price ($)", font=dict(size=16)),
            tickfont=dict(size=16),
            gridcolor="#2a2a2a",
        ),
        margin=dict(l=50, r=20, t=20, b=50),
    )
    st.subheader("Simulated Price Paths")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    fig2 = go.Figure()

    p10, p25, p50, p75, p90 = percentiles

    fig2.add_trace(
        go.Scatter(
            x=business_days,
            y=p10,
            mode="lines",
            line=dict(width=0),
            showlegend=True,
            name="10th Percentile",
            hoverinfo="skip",
        )
    )
    fig2.add_trace(
        go.Scatter(
            x=business_days,
            y=p25,
            mode="lines",
            line=dict(width=0),
            fill="tonexty",
            fillcolor="rgba(56,139,253,0.20)",
            name="25th Percentile",
            hoverinfo="skip",
        )
    )
    fig2.add_trace(
        go.Scatter(
            x=business_days,
            y=p50,
            mode="lines",
            line=dict(color="#60a5fa", width=2),
            fill="tonexty",
            fillcolor="rgba(56,139,253,0.35)",
            name="median",
        )
    )
    fig2.add_trace(
        go.Scatter(
            x=business_days,
            y=p75,
            mode="lines",
            line=dict(width=0),
            fill="tonexty",
            fillcolor="rgba(56,139,253,0.35)",
            name="75th Percentile",
            hoverinfo="skip",
        )
    )
    fig2.add_trace(
        go.Scatter(
            x=business_days,
            y=p90,
            mode="lines",
            line=dict(width=0),
            fill="tonexty",
            fillcolor="rgba(56,139,253,0.20)",
            name="90th Percentile",
            hoverinfo="skip",
        )
    )

    fig2.add_hline(
        y=st.session_state.sim_inputs["reward_price"],
        line=dict(color="red", dash="dash", width=1.5),
    )
    fig2.update_layout(
        height=420,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(font=dict(size=16)),
        xaxis=dict(
            title=dict(text="Date", font=dict(size=16)),
            tickfont=dict(size=16),
            tickformat="%b '%y",
            gridcolor="#2a2a2a",
        ),
        yaxis=dict(
            title=dict(text="HSY Price ($)", font=dict(size=16)),
            tickfont=dict(size=16),
            gridcolor="#2a2a2a",
        ),
        margin=dict(l=60, r=20, t=20, b=60),
    )

    st.plotly_chart(fig2, use_container_width=True)


st.divider()
