from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd

DB_PATH = Path(__file__).resolve().parent / "data" / "filtrify_platform.db"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialise_database() -> None:
    with get_connection() as connection:
        connection.execute(
            '''
            CREATE TABLE IF NOT EXISTS campaign_scenarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                product_name TEXT NOT NULL,
                budget REAL NOT NULL,
                cpc REAL NOT NULL,
                conversion_rate REAL NOT NULL,
                commission REAL NOT NULL,
                clicks REAL NOT NULL,
                sales REAL NOT NULL,
                revenue REAL NOT NULL,
                profit REAL NOT NULL,
                roas REAL NOT NULL,
                roi REAL NOT NULL,
                break_even_conversion_rate REAL NOT NULL
            )
            '''
        )


def save_campaign_scenario(values: dict[str, Any]) -> None:
    columns = ", ".join(values.keys())
    placeholders = ", ".join("?" for _ in values)
    with get_connection() as connection:
        connection.execute(
            f"INSERT INTO campaign_scenarios ({columns}) VALUES ({placeholders})",
            tuple(values.values()),
        )


def load_campaign_scenarios() -> pd.DataFrame:
    initialise_database()
    with get_connection() as connection:
        return pd.read_sql_query(
            "SELECT * FROM campaign_scenarios ORDER BY created_at DESC, id DESC",
            connection,
        )
