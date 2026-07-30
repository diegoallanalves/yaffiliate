from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class SEOSection:
    heading: str
    content: str


@dataclass(slots=True)
class SEOArticle:
    title: str
    meta_description: str
    target_keyword: str

    introduction: str

    sections: list[SEOSection] = field(
        default_factory=list
    )

    conclusion: str = ""

    call_to_action: str = ""

    estimated_word_count: int = 0

    seo_score: float = 0.0