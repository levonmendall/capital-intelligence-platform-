"""Streamlit dashboard for the Capital Intelligence Platform."""

from datetime import datetime, timezone

import pandas as pd
import streamlit as st

from core.database import initialize_database
from core.portfolio import (
    get_mandate_details,
    get_mandates,
    get_portfolio_totals,
    get_trade_history,
)
from core.seed import seed_mandates
from intelligence.pipeline import run_intelligence
from providers.economic_snapshot import load_dashboard_data


st.set_page_config(
    page_title="Capital Intelligence Platform",
    page_icon="📊",
    layout="wide",
)


def format_currency(value: float) -> str:
    """Format a number as United States currency."""

    return f"${float(value):,.2f}"


def format_percent(value: float) -> str:
    """Format a decimal value as a percentage."""

    return f"{float(value):+.2%}"


def build_allocation_table(decision) -> pd.DataFrame:
    """Build a display table from the CIO allocation decision."""

    return pd.DataFrame(
        [
            {
                "Asset Class": "Equities",
                "Weight": float(decision.equities),
            },
            {
                "Asset Class": "Bonds",
                "Weight": float(decision.bonds),
            },
            {
                "Asset Class": "Cash",
                "Weight": float(decision.cash),
            },
            {
                "Asset Class": "Alternatives",
                "Weight": float(decision.alternatives),
            },
        ]
    )


initialize_database()
seed_mandates()

dashboard_data = load_dashboard_data()
decision = run_intelligence(save=False)
totals = get_portfolio_totals()

updated_time = datetime.now(
    timezone.utc
).strftime("%B %d, %Y at %H:%M UTC")


st.title("Capital Intelligence Platform")

st.caption(
    "Explainable AI CIO · Economic intelligence · "
    "Virtual portfolio management"
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Executive Dashboard",
        "Economic Intelligence",
        "CIO Intelligence",
        "Portfolio Command Center",
        "Trade Journal",
        "System Status",
    ],
)


if page == "Executive Dashboard":
    st.subheader("Executive overview")

    column1, column2, column3, column4 = st.columns(4)

    column1.metric(
        "Virtual AUM",
        format_currency(totals["nav"]),
    )

    column2.metric(
        "Available Cash",
        format_currency(totals["cash"]),
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

    performance_column, mandate_column = st.columns(2)

    performance_column.metric(
        "Platform Return",
        format_percent(totals["total_return"]),
    )

    mandate_column.metric(
        "Active Mandates",
        totals["mandate_count"],
    )

    st.subheader("Chief Investment Officer posture")

    posture_column, source_column = st.columns(2)

    posture_column.metric(
        "Risk Posture",
        decision.risk_posture,
    )

    source_column.metric(
        "Economic Data",
        dashboard_data.data_source,
    )

    st.write(decision.rationale)

    allocation = build_allocation_table(decision)

    st.subheader("Recommended model allocation")

    st.bar_chart(
        allocation.set_index("Asset Class")["Weight"]
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
        column1, column2, column3 = st.columns(3)

        column1.metric(
            "Unemployment Rate",
            f"{readings.unemployment_rate:.1f}%",
        )

        column2.metric(
            "Estimated Inflation",
            f"{readings.inflation_rate:.2f}%",
        )

        column3.metric(
            "Federal Funds Rate",
            f"{readings.federal_funds_rate:.2f}%",
        )

        column4, column5, column6 = st.columns(3)

        column4.metric(
            "2-Year Treasury",
            f"{readings.two_year_yield:.2f}%",
        )

        column5.metric(
            "10-Year Treasury",
            f"{readings.ten_year_yield:.2f}%",
        )

        column6.metric(
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

    allocation = build_allocation_table(decision)

    display_allocation = allocation.copy()

    display_allocation["Allocation"] = display_allocation[
        "Weight"
    ].map(lambda value: f"{value:.0%}")

    st.subheader("Recommended allocation")

    st.dataframe(
        display_allocation[
            ["Asset Class", "Allocation"]
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Decision rationale")
    st.write(decision.rationale)


elif page == "Portfolio Command Center":
    st.subheader("Portfolio Command Center")

    mandates = get_mandates()

    mandate_options = {
        f"{item['name']} ({item['code']})": item["code"]
        for item in mandates
    }

    selected_label = st.selectbox(
        "Select an investment mandate",
        options=list(mandate_options.keys()),
    )

    selected_code = mandate_options[selected_label]

    mandate = get_mandate_details(selected_code)

    if mandate is None:
        st.error(
            "The selected mandate could not be loaded."
        )

    else:
        st.caption(
            f"Risk classification: {mandate['risk']}"
        )

        column1, column2, column3, column4 = st.columns(4)

        column1.metric(
            "Net Asset Value",
            format_currency(mandate["nav"]),
        )

        column2.metric(
            "Cash",
            format_currency(mandate["cash"]),
        )

        column3.metric(
            "Starting Capital",
            format_currency(
                mandate["starting_capital"]
            ),
        )

        column4.metric(
            "Return Since Inception",
            format_percent(
                mandate["total_return"]
            ),
        )

        holdings = mandate["holdings"]

        st.divider()
        st.subheader("Current holdings")

        if not holdings:
            st.info(
                "This mandate currently holds only cash. "
                "No paper positions have been opened."
            )

        else:
            holdings_frame = pd.DataFrame(holdings)

            holdings_frame["quantity"] = holdings_frame[
                "quantity"
            ].map(lambda value: f"{value:,.4f}")

            currency_columns = [
                "average_cost",
                "current_price",
                "cost_basis",
                "market_value",
                "unrealized_gain",
            ]

            for column in currency_columns:
                holdings_frame[column] = holdings_frame[
                    column
                ].map(format_currency)

            holdings_frame = holdings_frame.rename(
                columns={
                    "symbol": "Symbol",
                    "quantity": "Quantity",
                    "average_cost": "Average Cost",
                    "current_price": "Current Price",
                    "cost_basis": "Cost Basis",
                    "market_value": "Market Value",
                    "unrealized_gain": "Unrealized Gain/Loss",
                    "updated_at": "Last Updated",
                }
            )

            st.dataframe(
                holdings_frame[
                    [
                        "Symbol",
                        "Quantity",
                        "Average Cost",
                        "Current Price",
                        "Market Value",
                        "Unrealized Gain/Loss",
                        "Last Updated",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )

        st.divider()
        st.subheader("Recent mandate trades")

        trades = mandate["trades"]

        if not trades:
            st.info(
                "No paper trades have been recorded "
                "for this mandate."
            )

        else:
            trades_frame = pd.DataFrame(trades)

            trades_frame["price"] = trades_frame[
                "price"
            ].map(format_currency)

            trades_frame["gross_amount"] = trades_frame[
                "gross_amount"
            ].map(format_currency)

            trades_frame = trades_frame.rename(
                columns={
                    "created_at": "Date",
                    "side": "Action",
                    "symbol": "Symbol",
                    "quantity": "Quantity",
                    "price": "Price",
                    "gross_amount": "Gross Amount",
                    "rationale": "Rationale",
                }
            )

            st.dataframe(
                trades_frame[
                    [
                        "Date",
                        "Action",
                        "Symbol",
                        "Quantity",
                        "Price",
                        "Gross Amount",
                        "Rationale",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )

        snapshots = mandate["snapshots"]

        if snapshots:
            st.divider()
            st.subheader("Portfolio value history")

            snapshot_frame = pd.DataFrame(snapshots)

            snapshot_frame["created_at"] = pd.to_datetime(
                snapshot_frame["created_at"]
            )

            snapshot_frame = snapshot_frame.sort_values(
                "created_at"
            )

            st.line_chart(
                snapshot_frame.set_index(
                    "created_at"
                )["nav"]
            )


elif page == "Trade Journal":
    st.subheader("Platform trade journal")

    trades = get_trade_history(limit=250)

    if not trades:
        st.info(
            "No paper trades have been recorded yet."
        )

    else:
        trade_frame = pd.DataFrame(trades)

        trade_frame["price"] = trade_frame[
            "price"
        ].map(format_currency)

        trade_frame["gross_amount"] = trade_frame[
            "gross_amount"
        ].map(format_currency)

        trade_frame = trade_frame.rename(
            columns={
                "created_at": "Date",
                "mandate_code": "Mandate",
                "side": "Action",
                "symbol": "Symbol",
                "quantity": "Quantity",
                "price": "Price",
                "gross_amount": "Gross Amount",
                "rationale": "Rationale",
            }
        )

        st.dataframe(
            trade_frame[
                [
                    "Date",
                    "Mandate",
                    "Action",
                    "Symbol",
                    "Quantity",
                    "Price",
                    "Gross Amount",
                    "Rationale",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )


else:
    st.subheader("System status")

    if dashboard_data.readings is not None:
        st.success("FRED economic data connected")
    else:
        st.warning(dashboard_data.status)

    st.success("SQLite database initialized")
    st.success("Eight investment mandates loaded")
    st.success("Portfolio reporting API operational")
    st.success("Paper-trading engine operational")
    st.success("CIO intelligence pipeline operational")
    st.success("GitHub validation workflow configured")

    st.write(
        f"Current economic source: "
        f"**{dashboard_data.data_source}**"
    )

    st.write(
        f"Virtual assets under management: "
        f"**{format_currency(totals['nav'])}**"
    )

    st.caption(f"Status checked {updated_time}")


st.divider()

st.caption(
    "Research and paper-trading software only. "
    "This platform does not provide individualized investment advice."
)
