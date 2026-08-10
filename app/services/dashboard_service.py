"""Revenue-focused dashboard data for YAffiliate."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from app.config import BETA_USER_ID
from app.repositories.campaign_repository import CampaignRepository
from app.repositories.database import read_table
from app.services.campaign_record_service import campaign_display_name
from app.services.scoring import add_opportunity_score


@dataclass(frozen=True, slots=True)
class DashboardSnapshot:
    products: pd.DataFrame
    scenarios: pd.DataFrame
    keywords: pd.DataFrame
    campaigns: list[dict[str, Any]]

    @property
    def campaign_count(self) -> int:
        return len(self.campaigns)

    @property
    def modelled_profit(self) -> float:
        if self.scenarios.empty or "profit" not in self.scenarios:
            return 0.0
        return float(pd.to_numeric(self.scenarios["profit"], errors="coerce").fillna(0).sum())

    @property
    def average_roas(self) -> float:
        if self.scenarios.empty or "roas" not in self.scenarios:
            return 0.0
        series = pd.to_numeric(self.scenarios["roas"], errors="coerce").dropna()
        return float(series.mean()) if not series.empty else 0.0


class DashboardService:
    """Combine local research data with cloud campaign activity."""

    def __init__(
        self,
        *,
        campaign_repository: CampaignRepository | None = None,
        user_id: str = BETA_USER_ID,
    ) -> None:
        self.campaign_repository = campaign_repository or CampaignRepository()
        self.user_id = user_id

    def get_snapshot(self) -> DashboardSnapshot:
        products = add_opportunity_score(read_table("products"))
        scenarios = read_table("campaign_scenarios")
        keywords = read_table("keywords")

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
        )

    @staticmethod
    def campaign_display_name(row: dict[str, Any]) -> str:
        """Return a readable saved-campaign name."""
        return campaign_display_name(row)
