"""Streamlit dashboard for the Capital Intelligence Platform."""

from datetime import datetime, timezone

import pandas as pd
import streamlit as st

from core.database import initialize_database
from core.portfolio import get_mandates, get_portfolio_totals
from core.seed import seed_mandates
from intelligence.pipeline import run_intelligence
from providers.economic_snapshot import load_dashboard_data


st.set_page_config(
    page_title="Capital Intelligence Platform",
    page_icon="📊",
    layout="wide",
)

initialize_database()
seed_mandates()

st.title("Capital Intelligence Platform")
st.caption(
    "Explainable AI CIO · Economic intelligence · Paper trading"
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Executive Dashboard",
        "Economic Intelligence",
        "CIO Intelligence",
        "Investment Mandates",
        "System Status",
    ],
)

dashboard_data = load_dashboard_data()
decision = run_intelligence(save=False)
totals = get_portfolio_totals()

updated_time = datetime.now(
    timezone.utc
).strftime("%B %d, %Y at %H:%M UTC")


if page == "Executive Dashboard":
    st.subheader("Executive overview")

    column1, column2, column3, column4 = st.columns(4)

    column1.metric(
        "Virtual AUM",
        f"${totals['nav']:,.0f}",
    )

    column2.metric(
        "Available Cash",
        f"${totals['cash']:,.0f}",
    )

    column3.metric(
        "Market Regime",
        decision.regime,
    )

    column4.metric(
        "CIO Confidence",
        f"{decision.confidence:.0%}",
    )

    st.divider()

    st.subheader("Chief Investment Officer posture")

    posture_column, source_column = st.columns(2)

    posture_column.metric(
        "Risk Posture",
        decision.risk_posture,
    )

    source_column.metric(
        "Data Source",
        dashboard_data.data_source,
    )

    st.write(decision.rationale)

    allocation = pd.DataFrame(
        [
            {
                "Asset Class": "Equities",
                "Weight": decision.equities,
            },
            {
                "Asset Class": "Bonds",
                "Weight": decision.bonds,
            },
            {
                "Asset Class": "Cash",
                "Weight": decision.cash,
            },
            {
                "Asset Class": "Alternatives",
                "Weight": decision.alternatives,
            },
        ]
    )

    st.subheader("Recommended model allocation")
    st.bar_chart(
        allocation.set_index("Asset Class")
    )

    st.caption(f"Dashboard refreshed {updated_time}")


elif page == "Economic Intelligence":
    st.subheader("Live economic intelligence")

    readings = dashboard_data.readings

    if readings is None:
        st.warning(
            "Live FRED readings are unavailable. "
            "The intelligence engine is using sample data."
        )

        st.write(
            f"System status: {dashboard_data.status}"
        )

    else:
        row1_column1, row1_column2, row1_column3 = st.columns(3)

        row1_column1.metric(
            "Unemployment Rate",
            f"{readings.unemployment_rate:.1f}%",
        )

        row1_column2.metric(
            "Estimated Inflation",
            f"{readings.inflation_rate:.2f}%",
        )

        row1_column3.metric(
            "Federal Funds Rate",
            f"{readings.federal_funds_rate:.2f}%",
        )

        row2_column1, row2_column2, row2_column3 = st.columns(3)

        row2_column1.metric(
            "2-Year Treasury",
            f"{readings.two_year_yield:.2f}%",
        )

        row2_column2.metric(
            "10-Year Treasury",
            f"{readings.ten_year_yield:.2f}%",
        )

        row2_column3.metric(
            "Yield Curve Spread",
            f"{readings.yield_curve_spread:.2f}%",
        )

        if readings.yield_curve_spread < 0:
            st.warning(
                "The Treasury yield curve is inverted. "
                "Short-term yields exceed long-term yields."
            )
        else:
            st.success(
                "The Treasury yield curve is positively sloped."
            )

        st.info(
            f"Data source: {dashboard_data.data_source}"
        )

    st.caption(f"Dashboard refreshed {updated_time}")


elif page == "CIO Intelligence":
    st.subheader("AI Chief Investment Officer")

    column1, column2, column3 = st.columns(3)

    column1.metric(
        "Market Regime",
        decision.regime,
    )

    column2.metric(
        "Confidence",
        f"{decision.confidence:.0%}",
    )

    column3.metric(
        "Risk Posture",
        decision.risk_posture,
    )

    allocation = pd.DataFrame(
        [
            {
                "Asset Class": "Equities",
                "Weight": decision.equities,
            },
            {
                "Asset Class": "Bonds",
                "Weight": decision.bonds,
            },
            {
                "Asset Class": "Cash",
                "Weight": decision.cash,
            },
            {
                "Asset Class": "Alternatives",
                "Weight": decision.alternatives,
            },
        ]
    )

    st.subheader("Recommended allocation")

    allocation["Allocation"] = allocation[
        "Weight"
    ].map(lambda value: f"{value:.0%}")

    st.dataframe(
        allocation[
            ["Asset Class", "Allocation"]
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Decision rationale")
    st.write(decision.rationale)


elif page == "Investment Mandates":
    st.subheader("Eight virtual investment mandates")

    mandates = pd.DataFrame(
        get_mandates()
    )

    st.dataframe(
        mandates,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "Each mandate began with $25,000 in virtual capital."
    )


else:
    st.subheader("System status")

    if dashboard_data.readings is not None:
        st.success("FRED economic data connected")
    else:
        st.warning(dashboard_data.status)

    st.success("Database initialized")
    st.success("Eight investment mandates loaded")
    st.success("CIO intelligence pipeline operational")
    st.success("GitHub validation workflow configured")

    st.write(
        f"Current data source: "
        f"**{dashboard_data.data_source}**"
    )

    st.caption(f"Status checked {updated_time}")


st.divider()

st.caption(
    "Research and paper-trading software only. "
    "This platform does not provide individualized investment advice."
)
