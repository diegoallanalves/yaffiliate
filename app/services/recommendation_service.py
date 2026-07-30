from __future__ import annotations

from app.models.recommendation import Recommendation
from app.services.opportunity_score_service import OpportunityFactors


class RecommendationService:
    """
    Generates practical affiliate-marketing recommendations
    from structured product metrics.

    This first version is rule-based. Later, AI and historical
    performance data can improve the recommendations.
    """

    def generate(
        self,
        *,
        opportunity_score: float,
        factors: OpportunityFactors,
    ) -> Recommendation:
        opportunity_level = self._get_opportunity_level(
            opportunity_score
        )

        risk_level = self._get_risk_level(
            factors=factors,
        )

        difficulty = self._get_difficulty(
            factors=factors,
        )

        recommended_channel = self._get_recommended_channel(
            factors=factors,
        )

        expected_roi = self._get_expected_roi(
            opportunity_score=opportunity_score,
            risk_level=risk_level,
        )

        recommended_budget = self._get_recommended_budget(
            opportunity_score=opportunity_score,
            risk_level=risk_level,
            estimated_cpc=factors.estimated_cpc,
        )

        reasoning = self._build_reasoning(
            factors=factors,
            opportunity_score=opportunity_score,
        )

        next_actions = self._build_next_actions(
            recommended_channel=recommended_channel,
            risk_level=risk_level,
        )

        return Recommendation(
            opportunity_score=opportunity_score,
            opportunity_level=opportunity_level,
            risk_level=risk_level,
            difficulty=difficulty,
            recommended_channel=recommended_channel,
            expected_roi=expected_roi,
            recommended_budget=recommended_budget,
            reasoning=reasoning,
            next_actions=next_actions,
        )

    @staticmethod
    def _get_opportunity_level(
        opportunity_score: float,
    ) -> str:
        if opportunity_score >= 80:
            return "Excellent"

        if opportunity_score >= 65:
            return "Good"

        if opportunity_score >= 50:
            return "Moderate"

        if opportunity_score >= 35:
            return "Weak"

        return "Poor"

    @staticmethod
    def _get_risk_level(
        *,
        factors: OpportunityFactors,
    ) -> str:
        risk_points = 0

        if factors.refund_rate >= 15:
            risk_points += 2

        elif factors.refund_rate >= 8:
            risk_points += 1

        if factors.competition_score >= 75:
            risk_points += 2

        elif factors.competition_score >= 50:
            risk_points += 1

        if factors.google_trend_score < 30:
            risk_points += 2

        elif factors.google_trend_score < 50:
            risk_points += 1

        if factors.search_volume < 500:
            risk_points += 2

        elif factors.search_volume < 2000:
            risk_points += 1

        if risk_points >= 5:
            return "High"

        if risk_points >= 3:
            return "Medium"

        return "Low"

    @staticmethod
    def _get_difficulty(
        *,
        factors: OpportunityFactors,
    ) -> str:
        if (
            factors.competition_score >= 70
            or factors.estimated_cpc >= 5
        ):
            return "High"

        if (
            factors.competition_score >= 40
            or factors.estimated_cpc >= 2
        ):
            return "Medium"

        return "Low"

    @staticmethod
    def _get_recommended_channel(
        *,
        factors: OpportunityFactors,
    ) -> str:
        if (
            factors.search_volume >= 3000
            and factors.competition_score <= 55
        ):
            return "SEO"

        if (
            factors.estimated_cpc <= 2.5
            and factors.commission_amount >= 100
        ):
            return "Google Ads"

        if (
            factors.google_trend_score >= 70
            and factors.search_volume < 3000
        ):
            return "Social Media"

        if factors.commission_percent >= 50:
            return "Email Marketing"

        return "Content Marketing"

    @staticmethod
    def _get_expected_roi(
        *,
        opportunity_score: float,
        risk_level: str,
    ) -> str:
        if opportunity_score >= 80 and risk_level == "Low":
            return "High"

        if opportunity_score >= 60 and risk_level != "High":
            return "Medium"

        return "Uncertain"

    @staticmethod
    def _get_recommended_budget(
        *,
        opportunity_score: float,
        risk_level: str,
        estimated_cpc: float,
    ) -> float:
        if risk_level == "High":
            base_clicks = 30

        elif opportunity_score >= 75:
            base_clicks = 100

        elif opportunity_score >= 55:
            base_clicks = 60

        else:
            base_clicks = 30

        estimated_budget = base_clicks * max(
            estimated_cpc,
            0.50,
        )

        return round(estimated_budget, 2)

    @staticmethod
    def _build_reasoning(
        *,
        factors: OpportunityFactors,
        opportunity_score: float,
    ) -> list[str]:
        reasons: list[str] = []

        if opportunity_score >= 65:
            reasons.append(
                "The overall opportunity score is above average."
            )

        else:
            reasons.append(
                "The overall opportunity score requires cautious testing."
            )

        if factors.commission_amount >= 100:
            reasons.append(
                "The commission per sale supports paid or content acquisition."
            )

        else:
            reasons.append(
                "The commission per sale may limit advertising flexibility."
            )

        if factors.search_volume >= 3000:
            reasons.append(
                "Search demand appears strong enough to justify keyword research."
            )

        else:
            reasons.append(
                "Search demand may be too limited for a search-only strategy."
            )

        if factors.competition_score <= 40:
            reasons.append(
                "Competition is relatively low."
            )

        elif factors.competition_score <= 65:
            reasons.append(
                "Competition is moderate and should be validated."
            )

        else:
            reasons.append(
                "Competition is high and may increase acquisition costs."
            )

        if factors.refund_rate <= 5:
            reasons.append(
                "The refund rate is low."
            )

        elif factors.refund_rate <= 10:
            reasons.append(
                "The refund rate is acceptable but should be monitored."
            )

        else:
            reasons.append(
                "The refund rate introduces meaningful commercial risk."
            )

        if factors.google_trend_score >= 70:
            reasons.append(
                "Google Trends indicates strong current interest."
            )

        elif factors.google_trend_score >= 45:
            reasons.append(
                "Google Trends indicates stable or moderate interest."
            )

        else:
            reasons.append(
                "Google Trends indicates weak current interest."
            )

        return reasons

    @staticmethod
    def _build_next_actions(
        *,
        recommended_channel: str,
        risk_level: str,
    ) -> list[str]:
        actions = [
            "Verify all product claims and affiliate-network rules.",
            "Review the sales page and customer feedback.",
            "Create a small test before scaling.",
        ]

        if recommended_channel == "SEO":
            actions.append(
                "Build a keyword cluster and publish helpful search content."
            )

        elif recommended_channel == "Google Ads":
            actions.append(
                "Prepare a tightly controlled Google Ads test campaign."
            )

        elif recommended_channel == "Social Media":
            actions.append(
                "Test short-form content and audience engagement."
            )

        elif recommended_channel == "Email Marketing":
            actions.append(
                "Create a permission-based educational email sequence."
            )

        else:
            actions.append(
                "Create educational content before investing in paid traffic."
            )

        if risk_level == "High":
            actions.append(
                "Do not scale until refund, competition and conversion data are validated."
            )

        return actions