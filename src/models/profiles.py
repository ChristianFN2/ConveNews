from dataclasses import dataclass

from models.queries import SearchQuery

@dataclass
class NewsletterProfile:
    profile_id: int
    user_id: int

    profile_title: str
    interest_description: str
    selected_keywords: list[str]
    target_language: str
    max_articles_included: int
    included_sources: list[str]
    covered_period_days: int
    reading_time_minutes: int

    is_initialization_pending: bool
    interest_summary: str | None
    generated_queries: list[SearchQuery] = []
