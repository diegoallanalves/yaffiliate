
from __future__ import annotations

from app.models.recommendation import Recommendation
from app.services.opportunity_score_service import (
    OpportunityFactors,
    OpportunityScoreService,
)


class RecommendationService:
    """
    Generates practical affiliate-marketing recommendations
    from structured product metrics.

    This version distinguishes missing data (None) from
    confirmed zero values.

    Recommendations are rule-based and should not treat
    unknown metrics as evidence of low risk or low costs.
    """

    @staticmethod
    def _known(value: float | int | None) -> bool:
        """Return True when a metric contains a valid number."""
        return OpportunityScoreService._known(value)

    def generate(
        self,
        *,
        opportunity_score: float,
        factors: OpportunityFactors,
    ) -> Recommendation:

        coverage = OpportunityScoreService().calculate_coverage(
            factors
        )

        opportunity_level = (
            self._get_opportunity_level(opportunity_score)
            if coverage >= 70
            else "Insufficient Data"
        )

        risk_level = self._get_risk_level(factors=factors)

        difficulty = self._get_difficulty(factors=factors)

        recommended_channel = self._get_recommended_channel(
            factors=factors
        )

        expected_roi = (
            self._get_expected_roi(
                opportunity_score=opportunity_score,
                risk_level=risk_level,
            )
            if coverage >= 70
            else "Uncertain"
        )

        recommended_budget = self._get_recommended_budget(
            opportunity_score=opportunity_score,
            risk_level=risk_level,
            estimated_cpc=factors.estimated_cpc,
            coverage=coverage,
        )

        reasoning = self._build_reasoning(
            factors=factors,
            opportunity_score=opportunity_score,
            coverage=coverage,
        )

        next_actions = self._build_next_actions(
            recommended_channel=recommended_channel,
            risk_level=risk_level,
            coverage=coverage,
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

    @classmethod
    def _get_risk_level(
        cls,
        *,
        factors: OpportunityFactors,
    ) -> str:

        required_metrics = (
            factors.refund_rate,
            factors.competition_score,
            factors.google_trend_score,
            factors.search_volume,
        )

        # Do not claim low risk when risk data is missing.
        if not all(
            cls._known(value)
            for value in required_metrics
        ):
            return "Unknown"

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

    @classmethod
    def _get_difficulty(
        cls,
        *,
        factors: OpportunityFactors,
    ) -> str:

        competition = factors.competition_score
        cpc = factors.estimated_cpc

        if (
            (
                cls._known(competition)
                and competition >= 70
            )
            or (
                cls._known(cpc)
                and cpc >= 5
            )
        ):
            return "High"

        if not (
            cls._known(competition)
            and cls._known(cpc)
        ):
            return "Unknown"

        if competition >= 40 or cpc >= 2:
            return "Medium"

        return "Low"

    @classmethod
    def _get_recommended_channel(
        cls,
        *,
        factors: OpportunityFactors,
    ) -> str:

        volume = factors.search_volume
        competition = factors.competition_score
        cpc = factors.estimated_cpc
        commission = factors.commission_amount
        trends = factors.google_trend_score
        commission_percent = factors.commission_percent

        if (
            cls._known(volume)
            and cls._known(competition)
            and volume >= 3000
            and competition <= 55
        ):
            return "SEO"

        if (
            cls._known(cpc)
            and cls._known(commission)
            and cpc <= 2.5
            and commission >= 100
        ):
            return "Google Ads"

        if (
            cls._known(trends)
            and cls._known(volume)
            and trends >= 70
            and volume < 3000
        ):
            return "Social Media"

        if (
            cls._known(commission_percent)
            and commission_percent >= 50
        ):
            return "Email Marketing"

        return "Content Marketing"

    @staticmethod
    def _get_expected_roi(
        *,
        opportunity_score: float,
        risk_level: str,
    ) -> str:

        if risk_level == "Unknown":
            return "Uncertain"

        if opportunity_score >= 80 and risk_level == "Low":
            return "High"

        if opportunity_score >= 60 and risk_level != "High":
            return "Medium"

        return "Uncertain"

    @classmethod
    def _get_recommended_budget(
        cls,
        *,
        opportunity_score: float,
        risk_level: str,
        estimated_cpc: float | None,
        coverage: float = 100.0,
    ) -> float:

        # No reliable budget without researched CPC.
        if not cls._known(estimated_cpc):
            return 0.0

        # Do not recommend spending with insufficient data.
        if coverage < 70 or risk_level == "Unknown":
            return 0.0

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

    @classmethod
    def _build_reasoning(
        cls,
        *,
        factors: OpportunityFactors,
        opportunity_score: float,
        coverage: float = 100.0,
    ) -> list[str]:

        reasons: list[str] = []

        if coverage < 70:
            reasons.append(
                f"Research coverage is {coverage:.0f}%. "
                "The opportunity score is provisional. "
                "Collect more data before making investment decisions."
            )

        elif opportunity_score >= 65:
            reasons.append(
                "The weighted opportunity score is above average "
                "under the current scoring rules."
            )

        else:
            reasons.append(
                "The weighted opportunity score suggests "
                "cautious testing."
            )

        # Commission analysis
        if not cls._known(factors.commission_amount):
            reasons.append(
                "Commission per sale is unknown."
            )

        elif factors.commission_amount >= 100:
            reasons.append(
                "The commission per sale may support "
                "paid or content acquisition."
            )

        else:
            reasons.append(
                "The commission per sale may limit "
                "advertising flexibility."
            )

        # Search demand analysis
        if not cls._known(factors.search_volume):
            reasons.append(
                "Monthly search demand has not been researched."
            )

        elif factors.search_volume >= 3000:
            reasons.append(
                "Search demand appears strong enough "
                "to justify keyword research."
            )

        else:
            reasons.append(
                "Recorded search demand may be too limited "
                "for a search-only strategy."
            )

        # Competition analysis
        if not cls._known(factors.competition_score):
            reasons.append(
                "Competition has not yet been assessed."
            )

        elif factors.competition_score <= 40:
            reasons.append(
                "Recorded competition is relatively low."
            )

        elif factors.competition_score <= 65:
            reasons.append(
                "Competition is moderate and should be validated."
            )

        else:
            reasons.append(
                "Competition is high and may increase "
                "acquisition costs."
            )

        # Refund analysis
        if not cls._known(factors.refund_rate):
            reasons.append(
                "The product refund rate is unknown."
            )

        elif factors.refund_rate <= 5:
            reasons.append(
                "The recorded refund rate is low."
            )

        elif factors.refund_rate <= 10:
            reasons.append(
                "The refund rate should be monitored."
            )

        else:
            reasons.append(
                "The refund rate introduces commercial risk."
            )

        # Google Trends analysis
        if not cls._known(factors.google_trend_score):
            reasons.append(
                "Google Trends research is not yet available."
            )

        elif factors.google_trend_score >= 70:
            reasons.append(
                "Google Trends indicates strong current interest."
            )

        elif factors.google_trend_score >= 45:
            reasons.append(
                "Google Trends indicates moderate interest."
            )

        else:
            reasons.append(
                "Google Trends indicates weak current interest."
            )

        # Advertising cost analysis
        if not cls._known(factors.estimated_cpc):
            reasons.append(
                "Advertising cost is unknown. "
                "No paid advertising budget can be recommended."
            )

        elif coverage < 70:
            reasons.append(
                "A paid advertising budget is withheld "
                "until more research data is available."
            )

        return reasons

    @staticmethod
    def _build_next_actions(
        *,
        recommended_channel: str,
        risk_level: str,
        coverage: float = 100.0,
    ) -> list[str]:

        actions = [
            "Verify all product claims and affiliate-network rules.",
            "Review the sales page and customer feedback.",
            "Create a small test before scaling.",
        ]

        if coverage < 70:
            actions.append(
                "Complete missing market research before "
                "committing an advertising budget."
            )

        if recommended_channel == "SEO":
            actions.append(
                "Build a keyword cluster and publish "
                "helpful search content."
            )

        elif recommended_channel == "Google Ads":
            if coverage >= 70 and risk_level != "Unknown":
                actions.append(
                    "Prepare a tightly controlled "
                    "Google Ads test campaign."
                )
            else:
                actions.append(
                    "Validate advertising costs and market risks "
                    "before launching Google Ads."
                )

        elif recommended_channel == "Social Media":
            actions.append(
                "Test short-form content and audience engagement."
            )

        elif recommended_channel == "Email Marketing":
            actions.append(
                "Create a permission-based educational "
                "email sequence."
            )

        else:
            actions.append(
                "Create educational content before "
                "investing in paid traffic."
            )

        if risk_level == "High":
            actions.append(
                "Do not scale until refund, competition "
                "and conversion data are validated."
            )

        elif risk_level == "Unknown":
            actions.append(
                "Assess refund rates, competition, "
                "search demand and market trends "
                "to establish the risk level."
            )

        return actions
