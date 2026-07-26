from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class CampaignResult:
    product_name: str
    budget: float
    cpc: float
    conversion_rate: float
    commission: float
    clicks: float
    sales: float
    revenue: float
    profit: float
    roas: float
    roi: float
    break_even_conversion_rate: float

    def as_record(self) -> dict[str, float | str]:
        return asdict(self)


def calculate_campaign(
    product_name: str,
    budget: float,
    cpc: float,
    conversion_rate_percent: float,
    commission: float,
) -> CampaignResult:
    if budget < 0:
        raise ValueError("Budget cannot be negative.")
    if cpc <= 0:
        raise ValueError("CPC must be greater than zero.")
    if commission <= 0:
        raise ValueError("Commission must be greater than zero.")
    if not 0 <= conversion_rate_percent <= 100:
        raise ValueError("Conversion rate must be between 0 and 100.")

    conversion_rate = conversion_rate_percent / 100
    clicks = budget / cpc
    sales = clicks * conversion_rate
    revenue = sales * commission
    profit = revenue - budget
    roas = revenue / budget if budget else 0.0
    roi = profit / budget if budget else 0.0
    break_even_conversion_rate = cpc / commission

    return CampaignResult(
        product_name=product_name.strip() or "Unnamed product",
        budget=round(budget, 2),
        cpc=round(cpc, 2),
        conversion_rate=conversion_rate,
        commission=round(commission, 2),
        clicks=round(clicks, 2),
        sales=round(sales, 2),
        revenue=round(revenue, 2),
        profit=round(profit, 2),
        roas=round(roas, 4),
        roi=round(roi, 4),
        break_even_conversion_rate=round(break_even_conversion_rate, 6),
    )
