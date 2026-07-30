from __future__ import annotations

from typing import Any

from app.services.portfolio_service import PortfolioService


class MissionService:
    """
    Builds a practical daily mission from portfolio intelligence.

    The first version is deterministic and rule-based.
    Later versions can include AI, historical performance,
    user preferences and campaign results.
    """

    def __init__(
        self,
        portfolio_service: PortfolioService | None = None,
    ) -> None:
        self.portfolio_service = (
            portfolio_service or PortfolioService()
        )

    def get_daily_mission(self) -> dict[str, Any] | None:
        summary = self.portfolio_service.get_portfolio_summary()

        top_product = summary.get("top_product")

        if top_product is None:
            return None

        opportunity_score = float(
            top_product.get("OpportunityScore") or 0
        )

        priority = self._get_priority(
            opportunity_score
        )

        estimated_hours = self._estimate_hours(
            priority=priority,
        )

        estimated_profit = self._estimate_profit(
            commission_amount=float(
                top_product.get("CommissionAmount") or 0
            ),
            search_volume=int(
                top_product.get("SearchVolume") or 0
            ),
            opportunity_score=opportunity_score,
        )

        tasks = self._build_tasks(
            priority_action=str(
                top_product.get("PriorityAction")
                or "Run a small controlled market test"
            ),
            decision=str(
                top_product.get("Decision")
                or "Test cautiously"
            ),
            recommended_channel=self._infer_channel(
                top_product
            ),
        )

        return {
            "product_id": int(top_product["ProductID"]),
            "product_name": str(
                top_product.get("ProductName")
                or "Unnamed product"
            ),
            "network": str(
                top_product.get("NetworkName")
                or "Not set"
            ),
            "category": str(
                top_product.get("Category")
                or "Not set"
            ),
            "opportunity_score": opportunity_score,
            "decision": str(
                top_product.get("Decision")
                or "Not available"
            ),
            "priority": priority,
            "priority_action": str(
                top_product.get("PriorityAction")
                or "No action available"
            ),
            "recommended_channel": self._infer_channel(
                top_product
            ),
            "estimated_hours": estimated_hours,
            "estimated_profit": estimated_profit,
            "tasks": tasks,
            "reason": self._build_reason(
                top_product
            ),
        }

    @staticmethod
    def _get_priority(
        opportunity_score: float,
    ) -> str:
        if opportunity_score >= 80:
            return "High"

        if opportunity_score >= 65:
            return "Medium"

        if opportunity_score >= 50:
            return "Controlled test"

        return "Low"

    @staticmethod
    def _estimate_hours(
        *,
        priority: str,
    ) -> float:
        if priority == "High":
            return 3.0

        if priority == "Medium":
            return 2.0

        if priority == "Controlled test":
            return 1.5

        return 1.0

    @staticmethod
    def _estimate_profit(
        *,
        commission_amount: float,
        search_volume: int,
        opportunity_score: float,
    ) -> float:
        """
        Early directional estimate only.

        This is not a financial forecast. It provides a rough
        planning value until real conversion data is available.
        """
        estimated_clicks = search_volume * 0.02
        estimated_conversion_rate = max(
            opportunity_score / 1000,
            0.01,
        )

        estimated_sales = (
            estimated_clicks
            * estimated_conversion_rate
        )

        estimated_profit = (
            estimated_sales
            * commission_amount
        )

        return round(
            max(estimated_profit, 0),
            2,
        )

    @staticmethod
    def _infer_channel(
        product: dict[str, Any],
    ) -> str:
        search_volume = int(
            product.get("SearchVolume") or 0
        )

        competition_score = float(
            product.get("CompetitionScore") or 0
        )

        google_trend_score = float(
            product.get("GoogleTrendScore") or 0
        )

        commission_amount = float(
            product.get("CommissionAmount") or 0
        )

        estimated_cpc = float(
            product.get("EstimatedCPC") or 0
        )

        if (
            search_volume >= 3000
            and competition_score <= 55
        ):
            return "SEO"

        if (
            estimated_cpc <= 2.5
            and commission_amount >= 100
        ):
            return "Google Ads"

        if google_trend_score >= 70:
            return "Social Media"

        return "Content Marketing"

    @staticmethod
    def _build_tasks(
        *,
        priority_action: str,
        decision: str,
        recommended_channel: str,
    ) -> list[str]:
        tasks = [
            "Review the product sales page and validate all claims.",
            priority_action,
        ]

        if recommended_channel == "SEO":
            tasks.extend(
                [
                    "Choose one primary keyword.",
                    "Outline one helpful SEO article.",
                    "Prepare an internal-linking plan.",
                ]
            )

        elif recommended_channel == "Google Ads":
            tasks.extend(
                [
                    "Define one tightly controlled keyword group.",
                    "Write three compliant ad variations.",
                    "Set a strict daily test budget.",
                ]
            )

        elif recommended_channel == "Social Media":
            tasks.extend(
                [
                    "Create one short-form content concept.",
                    "Prepare one call to action.",
                    "Define the audience segment to test.",
                ]
            )

        else:
            tasks.extend(
                [
                    "Create one educational content asset.",
                    "Define one lead magnet idea.",
                    "Prepare one email follow-up.",
                ]
            )

        if decision == "Test cautiously":
            tasks.append(
                "Do not scale until real conversion data is available."
            )

        return tasks

    @staticmethod
    def _build_reason(
        product: dict[str, Any],
    ) -> str:
        product_name = str(
            product.get("ProductName")
            or "This product"
        )

        score = float(
            product.get("OpportunityScore") or 0
        )

        action = str(
            product.get("PriorityAction")
            or "run a controlled test"
        )

        return (
            f"{product_name} is currently the highest-ranked "
            f"product in the portfolio with an opportunity score "
            f"of {score:.1f}/100. The recommended focus is to "
            f"{action.lower()}."
        )