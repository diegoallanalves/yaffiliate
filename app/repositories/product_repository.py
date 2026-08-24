"""Supabase repository for YAffiliate products."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.services.supabase_service import SupabaseService


class ProductRepository:
    """
    Read and write the authenticated user's product data.

    IMPORTANT:
    Do not keep a long-lived Supabase client here. Streamlit modules can
    create repository objects before the user signs in. A fresh client is
    therefore created for every repository operation so the current
    Supabase session is restored before RLS-protected requests.
    """

    @staticmethod
    def _client():
        return SupabaseService().client

    def _current_user_id(self) -> str:
        client = self._client()

        try:
            response = client.auth.get_user()
        except Exception as exc:
            raise ValueError(
                "An authenticated Supabase session is required."
            ) from exc

        user = getattr(response, "user", None)
        user_id = getattr(user, "id", None)

        if not user_id:
            raise ValueError(
                "An authenticated Supabase session is required."
            )

        return str(user_id)

    def list_affiliate_networks(self) -> list[dict[str, Any]]:
        response = (
            self._client()
            .table("affiliate_networks")
            .select("network_id,network_name")
            .order("network_name")
            .execute()
        )

        return [
            {
                "NetworkID": row.get("network_id"),
                "NetworkName": row.get("network_name"),
            }
            for row in (response.data or [])
        ]

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

        user_id = self._current_user_id()
        client = self._client()

        response = (
            client
            .table("products")
            .insert(
                {
                    "user_id": user_id,
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
            )
            .execute()
        )

        rows = list(response.data or [])

        if not rows:
            raise RuntimeError(
                "Supabase did not return the created product."
            )

        return int(rows[0]["product_id"])

    def get_product(
        self,
        product_id: int,
    ) -> dict[str, Any] | None:
        response = (
            self._client()
            .table("products")
            .select("*,affiliate_networks(network_name)")
            .eq("product_id", product_id)
            .limit(1)
            .execute()
        )

        rows = list(response.data or [])

        return self._format_product(rows[0]) if rows else None

    def list_products(
        self,
        *,
        status: str | None = None,
        search: str | None = None,
    ) -> list[dict[str, Any]]:
        query = (
            self._client()
            .table("products")
            .select("*,affiliate_networks(network_name)")
        )

        if status:
            query = query.eq("status", status)

        if search and search.strip():
            query = query.ilike(
                "product_name",
                f"%{search.strip()}%",
            )

        response = query.order("product_name").execute()

        products: list[dict[str, Any]] = []

        for row in (response.data or []):
            product = self._format_product(row)

            product_id = product.get("ProductID")

            metric = (
                self.get_latest_product_metric(
                    int(product_id)
                )
                if product_id is not None
                else None
            ) or {}

            product.update(
                {
                    "EPC": metric.get("EPC"),
                    "GravityScore": metric.get(
                        "GravityScore"
                    ),
                    "SearchVolume": metric.get(
                        "SearchVolume"
                    ),
                    "CompetitionScore": metric.get(
                        "CompetitionScore"
                    ),
                    "EstimatedCPC": metric.get(
                        "EstimatedCPC"
                    ),
                    "GoogleTrendScore": metric.get(
                        "GoogleTrendScore"
                    ),
                    "RefundRate": metric.get("RefundRate"),
                    "OpportunityScore": metric.get(
                        "OpportunityScore"
                    ),
                    "MetricDate": metric.get("MetricDate"),
                }
            )

            products.append(product)

        return products

    def update_product(
        self,
        product_id: int,
        **changes: Any,
    ) -> bool:
        allowed_columns = {
            "network_id",
            "product_name",
            "category",
            "language_code",
            "country_code",
            "price",
            "commission_amount",
            "commission_percent",
            "sales_page_url",
            "affiliate_url",
            "status",
            "notes",
        }

        filtered_changes = {
            key: value
            for key, value in changes.items()
            if key in allowed_columns
        }

        if not filtered_changes:
            raise ValueError(
                "No valid product fields were supplied."
            )

        if (
            "product_name" in filtered_changes
            and not str(
                filtered_changes["product_name"]
            ).strip()
        ):
            raise ValueError(
                "Product name cannot be empty."
            )

        if "product_name" in filtered_changes:
            filtered_changes["product_name"] = str(
                filtered_changes["product_name"]
            ).strip()

        filtered_changes["updated_at"] = (
            datetime.now(timezone.utc).isoformat()
        )

        response = (
            self._client()
            .table("products")
            .update(filtered_changes)
            .eq("product_id", product_id)
            .execute()
        )

        return bool(response.data)

    def delete_product(
        self,
        product_id: int,
    ) -> bool:
        response = (
            self._client()
            .table("products")
            .delete()
            .eq("product_id", product_id)
            .execute()
        )

        return bool(response.data)

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
        response = (
            self._client()
            .table("product_metrics")
            .insert(
                {
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
            )
            .execute()
        )

        rows = list(response.data or [])

        if not rows:
            raise RuntimeError(
                "Supabase did not return the created product metric."
            )

        return int(rows[0]["product_metric_id"])

    def get_latest_product_metric(
        self,
        product_id: int,
    ) -> dict[str, Any] | None:
        response = (
            self._client()
            .table("product_metrics")
            .select("*")
            .eq("product_id", product_id)
            .order("metric_date", desc=True)
            .order("product_metric_id", desc=True)
            .limit(1)
            .execute()
        )

        rows = list(response.data or [])

        return self._format_metric(rows[0]) if rows else None

    def list_product_metrics(
        self,
        product_id: int,
    ) -> list[dict[str, Any]]:
        response = (
            self._client()
            .table("product_metrics")
            .select("*")
            .eq("product_id", product_id)
            .order("metric_date", desc=True)
            .order("product_metric_id", desc=True)
            .execute()
        )

        return [
            self._format_metric(row)
            for row in (response.data or [])
        ]

    @staticmethod
    def _format_product(
        row: dict[str, Any],
    ) -> dict[str, Any]:
        network = row.get("affiliate_networks") or {}

        return {
            "ProductID": row.get("product_id"),
            "NetworkID": row.get("network_id"),
            "NetworkName": network.get("network_name"),
            "ProductName": row.get("product_name"),
            "Category": row.get("category"),
            "LanguageCode": row.get("language_code"),
            "CountryCode": row.get("country_code"),
            "Price": row.get("price"),
            "CommissionAmount": row.get(
                "commission_amount"
            ),
            "CommissionPercent": row.get(
                "commission_percent"
            ),
            "SalesPageURL": row.get("sales_page_url"),
            "AffiliateURL": row.get("affiliate_url"),
            "Status": row.get("status"),
            "Notes": row.get("notes"),
            "CreatedAt": row.get("created_at"),
            "UpdatedAt": row.get("updated_at"),
        }

    @staticmethod
    def _format_metric(
        row: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "ProductMetricID": row.get(
                "product_metric_id"
            ),
            "ProductID": row.get("product_id"),
            "EPC": row.get("epc"),
            "GravityScore": row.get("gravity_score"),
            "SearchVolume": row.get("search_volume"),
            "CompetitionScore": row.get(
                "competition_score"
            ),
            "EstimatedCPC": row.get("estimated_cpc"),
            "GoogleTrendScore": row.get(
                "google_trend_score"
            ),
            "RefundRate": row.get("refund_rate"),
            "OpportunityScore": row.get(
                "opportunity_score"
            ),
            "MetricDate": row.get("metric_date"),
            "DataSource": row.get("data_source"),
            "CreatedAt": row.get("created_at"),
        }
