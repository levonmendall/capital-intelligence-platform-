"""Streamlit dashboard for the Capital Intelligence Platform."""

import pandas as pd
import streamlit as st

from core.database import initialize_database
from core.portfolio import get_mandates, get_portfolio_totals
from core.seed import seed_mandates
from intelligence.pipeline import run_intelligence


st.set_page_config(
    page_title="Capital Intelligence Platform",
    page_icon="📊",
    layout="wide",
)

initialize_database()
seed_mandates()

st.title("Capital Intelligence Platform")
st.caption("Explainable AI CIO · Research and paper trading only")

page = st.sidebar.radio(
    "Navigation",
    [
        "Executive Dashboard",
        "CIO Intelligence",
        "Investment Mandates",
    ],
)

if page == "Executive Dashboard":
    totals = get_portfolio_totals()
    decision = run_intelligence(save=False)

    column1, column2, column3, column4 = st.columns(4)

    column1.metric(
        "Virtual AUM",
        f"${totals['nav']:,.0f}",
    )
    column2.metric(
        "Cash",
        f"${totals['cash']:,.0f}",
    )
    column3.metric(
        "Mandates",
        totals["mandate_count"],
    )
    column4.metric(
        "Market Regime",
        decision.regime,
    )

    st.subheader("Current CIO posture")
    st.write(
        f"**{decision.risk_posture}** with "
        f"**{decision.confidence:.0%} confidence**"
    )
    st.write(decision.rationale)

elif page == "CIO Intelligence":
    decision = run_intelligence()

    column1, column2, column3 = st.columns(3)

    column1.metric("Regime", decision.regime)
    column2.metric("Confidence", f"{decision.confidence:.0%}")
    column3.metric("Risk posture", decision.risk_posture)

    allocation = pd.DataFrame(
        [
            {"Asset Class": "Equities", "Weight": decision.equities},
            {"Asset Class": "Bonds", "Weight": decision.bonds},
            {"Asset Class": "Cash", "Weight": decision.cash},
            {
                "Asset Class": "Alternatives",
                "Weight": decision.alternatives,
            },
        ]
    )

    st.subheader("Recommended allocation")
    st.bar_chart(allocation.set_index("Asset Class"))
    st.dataframe(
        allocation,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Decision rationale")
    st.write(decision.rationale)

else:
    mandates = get_mandates()

    st.subheader("Eight virtual investment mandates")
    st.dataframe(
        pd.DataFrame(mandates),
        use_container_width=True,
        hide_index=True,
    )
