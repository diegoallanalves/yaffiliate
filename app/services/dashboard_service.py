
"""Revenue-focused dashboard data for YAffiliate."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any

import pandas as pd

from app.repositories.campaign_repository import CampaignRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.database import get_setting, read_table
from app.services.campaign_record_service import campaign_display_name
from app.services.currency_service import SUPPORTED_CURRENCIES, convert_currency


@dataclass(frozen=True, slots=True)
class DashboardSnapshot:
    products: pd.DataFrame
    scenarios: pd.DataFrame
    keywords: pd.DataFrame
    campaigns: list[dict[str, Any]]
    reporting_currency: str = "BRL"
    product_load_error: str | None = None

    @property
    def campaign_count(self) -> int:
        return len(self.campaigns)

    def _converted_scenarios(self):
        converted = []
        skipped = 0

        for _, row in self.scenarios.iterrows():
            source = row.get("currency_code")
            source = str(source).strip().upper() if pd.notna(source) else ""

            if source not in SUPPORTED_CURRENCIES:
                skipped += 1
                continue

            try:
                values = [
                    float(row[column])
                    for column in ("profit", "revenue", "budget")
                ]
                if not all(isfinite(value) for value in values):
                    raise ValueError("Invalid financial amount")
            except (KeyError, TypeError, ValueError):
                skipped += 1
                continue

            amounts = [
                convert_currency(value, source, self.reporting_currency)
                for value in values
            ]

            if any(value is None for value in amounts):
                skipped += 1
                continue

            converted.append(tuple(float(value) for value in amounts))

        return converted, skipped

    @property
    def excluded_scenario_count(self) -> int:
        return self._converted_scenarios()[1]

    @property
    def modelled_profit(self) -> float:
        rows, _ = self._converted_scenarios()
        return sum(profit for profit, _, _ in rows)

    @property
    def average_roas(self) -> float:
        rows, _ = self._converted_scenarios()
        revenue = sum(row[1] for row in rows)
        budget = sum(row[2] for row in rows)
        return revenue / budget if budget > 0 else 0.0


class DashboardService:
    """Combine Supabase products and campaigns with local scenario data."""

    def __init__(
        self,
        *,
        user_id: str,
        campaign_repository: CampaignRepository | None = None,
        product_repository: ProductRepository | None = None,
    ) -> None:
        if not user_id:
            raise ValueError("An authenticated user ID is required.")

        self.user_id = user_id
        self.campaign_repository = (
            campaign_repository or CampaignRepository()
        )
        self.product_repository = (
            product_repository or ProductRepository()
        )

    def get_snapshot(self) -> DashboardSnapshot:
        product_load_error = None

        try:
            products = pd.DataFrame(
                self.product_repository.list_products()
            )

            products = products.rename(
                columns={
                    "ProductID": "product_id",
                    "ProductName": "name",
                    "NetworkName": "network",
                    "OpportunityScore": "opportunity_score",
                    "CommissionAmount": "commission",
                    "SearchVolume": "search_volume",
                    "CurrencyCode": "currency_code",
                }
            )

            if "opportunity_score" not in products.columns:
                products["opportunity_score"] = pd.Series(
                    dtype="float64"
                )

        except Exception as error:
            products = pd.DataFrame()
            product_load_error = str(error)

        scenarios = read_table("campaign_scenarios")
        keywords = read_table("keywords")

        currency = str(
            get_setting("currency", "BRL") or "BRL"
        ).strip().upper()

        if currency not in SUPPORTED_CURRENCIES:
            currency = "BRL"

        try:
            campaigns = self.campaign_repository.list_campaigns(
                self.user_id,
                limit=5,
            )
        except Exception:
            campaigns = []

        return DashboardSnapshot(
            products=products,
            scenarios=scenarios,
            keywords=keywords,
            campaigns=campaigns,
            reporting_currency=currency,
            product_load_error=product_load_error,
        )

    @staticmethod
    def campaign_display_name(row: dict[str, Any]) -> str:
        return campaign_display_name(row)
