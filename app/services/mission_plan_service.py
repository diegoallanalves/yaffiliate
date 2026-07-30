from __future__ import annotations

from app.models.discovery_product import DiscoveryProduct
from app.models.mission_plan import (
    MissionPlan,
    MissionTask,
)
from app.models.product_analysis import ProductAnalysis


class MissionPlanService:
    """
    Converts the AI product analysis into an actionable
    mission plan that guides the affiliate marketer.
    """

    def generate(
        self,
        product: DiscoveryProduct,
        analysis: ProductAnalysis,
    ) -> MissionPlan:

        tasks: list[MissionTask] = []

        priority = 1

        # ---------- SEO ----------

        if analysis.seo_potential in (
            "Excellent",
            "Strong",
        ):
            tasks.extend(
                [
                    MissionTask(
                        title="Research target keywords",
                        description=(
                            "Identify high-volume and "
                            "low-competition keywords."
                        ),
                        category="SEO",
                        priority=priority,
                        estimated_minutes=30,
                    ),
                    MissionTask(
                        title="Write an SEO article",
                        description=(
                            "Publish one long-form article "
                            "targeting the primary keyword."
                        ),
                        category="SEO",
                        priority=priority + 1,
                        estimated_minutes=90,
                    ),
                ]
            )

            priority += 2

        # ---------- Landing Page ----------

        if analysis.landing_page_potential in (
            "Excellent",
            "Strong",
        ):
            tasks.append(
                MissionTask(
                    title="Create landing page",
                    description=(
                        "Build a focused landing page "
                        "with one CTA."
                    ),
                    category="Landing Page",
                    priority=priority,
                    estimated_minutes=90,
                )
            )

            priority += 1

        # ---------- Email ----------

        if analysis.email_marketing_potential in (
            "Excellent",
            "Strong",
        ):
            tasks.append(
                MissionTask(
                    title="Build email sequence",
                    description=(
                        "Create a 4-email nurture sequence."
                    ),
                    category="Email",
                    priority=priority,
                    estimated_minutes=60,
                )
            )

            priority += 1

        # ---------- Google Ads ----------

        if analysis.google_ads_potential in (
            "Excellent",
            "Strong",
        ):
            tasks.append(
                MissionTask(
                    title="Launch Google Ads test",
                    description=(
                        "Create a small campaign to "
                        "validate conversions."
                    ),
                    category="Google Ads",
                    priority=priority,
                    estimated_minutes=45,
                )
            )

            priority += 1

        # ---------- Review ----------

        tasks.append(
            MissionTask(
                title="Review campaign performance",
                description=(
                    "Evaluate SEO traffic, CTR, "
                    "conversion rate and EPC."
                ),
                category="Review",
                priority=priority,
                estimated_minutes=30,
            )
        )

        return MissionPlan(
            product_name=product.product_name,
            mission_title=(
                f"Launch {product.product_name}"
            ),
            objective=(
                "Generate the first affiliate sales "
                "using a controlled strategy."
            ),
            primary_channel="SEO",
            estimated_total_minutes=sum(
                task.estimated_minutes
                for task in tasks
            ),
            tasks=tasks,
        )