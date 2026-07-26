from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.repositories.sql_server import get_sql_server_engine


class ProductRepository:
    def __init__(self, engine: Engine | None = None) -> None:
        self.engine = engine or get_sql_server_engine()

    def list_affiliate_networks(self) -> list[dict[str, Any]]:
        """
        Return all affiliate networks available in SQL Server.

        Used by the Product Research page to populate the
        Affiliate Network dropdown.
        """
        query = text(
            """
            SELECT
                NetworkID,
                NetworkName
            FROM AffiliateNetworks
            ORDER BY NetworkName
            """
        )

        with self.engine.connect() as connection:
            rows = connection.execute(query).mappings().all()

        return [dict(row) for row in rows]

    def create_product(
        self,
        *,
        product_name: str,
        network_id: int | None = None,
        category: str | None = None,
        language_code: str | None = None,
        country_code: str | None = None,
        price: float = 0,
        commission_amount: float = 0,
        commission_percent: float = 0,
        sales_page_url: str | None = None,
        affiliate_url: str | None = None,
        status: str = "Research",
        notes: str | None = None,
    ) -> int:
        if not product_name.strip():
            raise ValueError("Product name is required.")

        query = text(
            """
            INSERT INTO Products (
                NetworkID,
                ProductName,
                Category,
                LanguageCode,
                CountryCode,
                Price,
                CommissionAmount,
                CommissionPercent,
                SalesPageURL,
                AffiliateURL,
                Status,
                Notes
            )
            OUTPUT INSERTED.ProductID
            VALUES (
                :network_id,
                :product_name,
                :category,
                :language_code,
                :country_code,
                :price,
                :commission_amount,
                :commission_percent,
                :sales_page_url,
                :affiliate_url,
                :status,
                :notes
            )
            """
        )

        parameters = {
            "network_id": network_id,
            "product_name": product_name.strip(),
            "category": category,
            "language_code": language_code,
            "country_code": country_code,
            "price": price,
            "commission_amount": commission_amount,
            "commission_percent": commission_percent,
            "sales_page_url": sales_page_url,
            "affiliate_url": affiliate_url,
            "status": status,
            "notes": notes,
        }

        with self.engine.begin() as connection:
            product_id = connection.execute(
                query,
                parameters,
            ).scalar_one()

        return int(product_id)

    def get_product(
        self,
        product_id: int,
    ) -> dict[str, Any] | None:
        query = text(
            """
            SELECT
                p.ProductID,
                p.NetworkID,
                n.NetworkName,
                p.ProductName,
                p.Category,
                p.LanguageCode,
                p.CountryCode,
                p.Price,
                p.CommissionAmount,
                p.CommissionPercent,
                p.SalesPageURL,
                p.AffiliateURL,
                p.Status,
                p.Notes,
                p.CreatedAt,
                p.UpdatedAt
            FROM Products p
            LEFT JOIN AffiliateNetworks n
                ON n.NetworkID = p.NetworkID
            WHERE p.ProductID = :product_id
            """
        )

        with self.engine.connect() as connection:
            row = connection.execute(
                query,
                {"product_id": product_id},
            ).mappings().first()

        return dict(row) if row else None

    def list_products(
        self,
        *,
        status: str | None = None,
        search: str | None = None,
    ) -> list[dict[str, Any]]:
        query = """
            SELECT
                ProductID,
                ProductName,
                NetworkName,
                Category,
                LanguageCode,
                CountryCode,
                Price,
                CommissionAmount,
                CommissionPercent,
                EPC,
                GravityScore,
                SearchVolume,
                CompetitionScore,
                EstimatedCPC,
                GoogleTrendScore,
                RefundRate,
                OpportunityScore,
                MetricDate,
                Status
            FROM vw_ProductOpportunitySummary
            WHERE 1 = 1
        """

        parameters: dict[str, Any] = {}

        if status:
            query += " AND Status = :status"
            parameters["status"] = status

        if search:
            query += " AND ProductName LIKE :search"
            parameters["search"] = f"%{search.strip()}%"

        query += " ORDER BY ProductName"

        with self.engine.connect() as connection:
            rows = connection.execute(
                text(query),
                parameters,
            ).mappings().all()

        return [dict(row) for row in rows]

    def update_product(
        self,
        product_id: int,
        **changes: Any,
    ) -> bool:
        allowed_columns = {
            "network_id": "NetworkID",
            "product_name": "ProductName",
            "category": "Category",
            "language_code": "LanguageCode",
            "country_code": "CountryCode",
            "price": "Price",
            "commission_amount": "CommissionAmount",
            "commission_percent": "CommissionPercent",
            "sales_page_url": "SalesPageURL",
            "affiliate_url": "AffiliateURL",
            "status": "Status",
            "notes": "Notes",
        }

        filtered_changes = {
            key: value
            for key, value in changes.items()
            if key in allowed_columns
        }

        if not filtered_changes:
            raise ValueError("No valid product fields were supplied.")

        if (
            "product_name" in filtered_changes
            and not str(filtered_changes["product_name"]).strip()
        ):
            raise ValueError("Product name cannot be empty.")

        set_clauses = [
            f"{allowed_columns[key]} = :{key}"
            for key in filtered_changes
        ]

        set_clauses.append("UpdatedAt = SYSUTCDATETIME()")

        query = text(
            f"""
            UPDATE Products
            SET {", ".join(set_clauses)}
            WHERE ProductID = :product_id
            """
        )

        parameters = {
            **filtered_changes,
            "product_id": product_id,
        }

        with self.engine.begin() as connection:
            result = connection.execute(
                query,
                parameters,
            )

        return result.rowcount > 0

    def delete_product(
        self,
        product_id: int,
    ) -> bool:
        query = text(
            """
            DELETE FROM Products
            WHERE ProductID = :product_id
            """
        )

        with self.engine.begin() as connection:
            result = connection.execute(
                query,
                {"product_id": product_id},
            )

        return result.rowcount > 0

    def add_product_metric(
        self,
        *,
        product_id: int,
        epc: float | None = None,
        gravity_score: float | None = None,
        search_volume: int | None = None,
        competition_score: float | None = None,
        estimated_cpc: float | None = None,
        google_trend_score: float | None = None,
        refund_rate: float | None = None,
        opportunity_score: float | None = None,
        data_source: str | None = None,
    ) -> int:
        query = text(
            """
            INSERT INTO ProductMetrics (
                ProductID,
                EPC,
                GravityScore,
                SearchVolume,
                CompetitionScore,
                EstimatedCPC,
                GoogleTrendScore,
                RefundRate,
                OpportunityScore,
                DataSource
            )
            OUTPUT INSERTED.ProductMetricID
            VALUES (
                :product_id,
                :epc,
                :gravity_score,
                :search_volume,
                :competition_score,
                :estimated_cpc,
                :google_trend_score,
                :refund_rate,
                :opportunity_score,
                :data_source
            )
            """
        )

        parameters = {
            "product_id": product_id,
            "epc": epc,
            "gravity_score": gravity_score,
            "search_volume": search_volume,
            "competition_score": competition_score,
            "estimated_cpc": estimated_cpc,
            "google_trend_score": google_trend_score,
            "refund_rate": refund_rate,
            "opportunity_score": opportunity_score,
            "data_source": data_source,
        }

        with self.engine.begin() as connection:
            metric_id = connection.execute(
                query,
                parameters,
            ).scalar_one()

        return int(metric_id)

    def get_latest_product_metric(
        self,
        product_id: int,
    ) -> dict[str, Any] | None:
        query = text(
            """
            SELECT TOP 1
                ProductMetricID,
                ProductID,
                EPC,
                GravityScore,
                SearchVolume,
                CompetitionScore,
                EstimatedCPC,
                GoogleTrendScore,
                RefundRate,
                OpportunityScore,
                MetricDate,
                DataSource,
                CreatedAt
            FROM ProductMetrics
            WHERE ProductID = :product_id
            ORDER BY
                MetricDate DESC,
                ProductMetricID DESC
            """
        )

        with self.engine.connect() as connection:
            row = connection.execute(
                query,
                {"product_id": product_id},
            ).mappings().first()

        return dict(row) if row else None

    def list_product_metrics(
        self,
        product_id: int,
    ) -> list[dict[str, Any]]:
        """
        Return the complete metric history for one product.
        """
        query = text(
            """
            SELECT
                ProductMetricID,
                ProductID,
                EPC,
                GravityScore,
                SearchVolume,
                CompetitionScore,
                EstimatedCPC,
                GoogleTrendScore,
                RefundRate,
                OpportunityScore,
                MetricDate,
                DataSource,
                CreatedAt
            FROM ProductMetrics
            WHERE ProductID = :product_id
            ORDER BY
                MetricDate DESC,
                ProductMetricID DESC
            """
        )

        with self.engine.connect() as connection:
            rows = connection.execute(
                query,
                {"product_id": product_id},
            ).mappings().all()

        return [dict(row) for row in rows]