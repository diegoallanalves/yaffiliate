from dataclasses import dataclass

@dataclass
class BusinessConsultantReport:

    executive_summary: str

    commercial_strategy: str

    seo_strategy: str

    google_ads_strategy: str

    email_strategy: str

    landing_page_strategy: str

    risk_analysis: str

    next_actions: list[str]

    final_verdict: str

    confidence_score: float