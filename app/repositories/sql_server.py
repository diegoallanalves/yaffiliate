from __future__ import annotations

import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

load_dotenv()


def get_sql_server_engine() -> Engine:
    server = os.getenv(
        "DB_SERVER",
        r"LAPTOP-HSERDTUR\SQLEXPRESS",
    )
    database = os.getenv("DB_NAME", "FiltrifyAI")
    driver = os.getenv(
        "DB_DRIVER",
        "ODBC Driver 18 for SQL Server",
    )

    odbc_connection = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )

    connection_url = (
        "mssql+pyodbc:///?odbc_connect="
        + quote_plus(odbc_connection)
    )

    return create_engine(
        connection_url,
        pool_pre_ping=True,
        future=True,
    )