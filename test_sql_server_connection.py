from sqlalchemy import text

from app.repositories.sql_server import get_sql_server_engine


def main() -> None:
    engine = get_sql_server_engine()

    with engine.connect() as connection:
        database_name = connection.execute(
            text("SELECT DB_NAME()")
        ).scalar_one()

        sql_version = connection.execute(
            text("SELECT @@VERSION")
        ).scalar_one()

    print(f"Connected to: {database_name}")
    print(sql_version)


if __name__ == "__main__":
    main()