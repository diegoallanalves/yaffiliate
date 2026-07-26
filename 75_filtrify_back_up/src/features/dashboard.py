from __future__ import annotations

import pandas as pd


def prepare_dashboard_data(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    result = df.copy()
    result["conversion_rate_percent"] = result["conversion_rate"] * 100
    result["break_even_conversion_percent"] = (
        result["break_even_conversion_rate"] * 100
    )
    result["roi_percent"] = result["roi"] * 100
    return result
