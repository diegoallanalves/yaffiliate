from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st


def metric_history_chart(
    dataframe: pd.DataFrame,
    y_column: str,
    title: str,
    *,
    height: int = 300,
    y_label: str | None = None,
) -> None:
    """
    Display a reusable historical line chart.

    The dataframe must contain:
    - RecordedAt
    - the requested y_column
    """
    required_columns = {"RecordedAt", y_column}

    if dataframe.empty:
        st.info(f"No historical data is available for {title.lower()}.")
        return

    if not required_columns.issubset(dataframe.columns):
        st.warning(
            f"The required data for {title.lower()} is unavailable."
        )
        return

    chart_df = dataframe[
        ["RecordedAt", y_column]
    ].copy()

    chart_df[y_column] = pd.to_numeric(
        chart_df[y_column],
        errors="coerce",
    )

    chart_df = chart_df.dropna(
        subset=["RecordedAt", y_column]
    )

    if len(chart_df) < 2:
        st.info(
            f"At least two snapshots are required to chart "
            f"{title.lower()}."
        )
        return

    chart = px.line(
        chart_df,
        x="RecordedAt",
        y=y_column,
        markers=True,
        title=title,
        labels={
            "RecordedAt": "",
            y_column: y_label or y_column,
        },
    )

    chart.update_traces(
        line={
            "width": 3,
        },
        marker={
            "size": 8,
        },
        hovertemplate=(
            "<b>%{x|%d %b %Y %H:%M}</b><br>"
            f"{y_label or y_column}: %{{y:,.2f}}"
            "<extra></extra>"
        ),
    )

    chart.update_layout(
        template="plotly_dark",
        height=height,
        margin={
            "l": 20,
            "r": 20,
            "t": 55,
            "b": 20,
        },
        hovermode="x unified",
        showlegend=False,
    )

    st.plotly_chart(
        chart,
        width="stretch",
    )