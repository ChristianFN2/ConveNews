from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

@dataclass
class NewsletterConfig:
    newsletter_profiles: Path
    relevance_threshold: float
    retrieved_articles_file: Path
    evaluated_articles_file: Path
    newsletters_file: Path
    average_reading_speed_wpm: int

@dataclass
class Newsletter:
    html: str

@dataclass
class NewsletterContent:
    profile_title: str
    interest_description: str
    keywords: list[str]
    articles: list[NewsletterArticle]
    generation_date: datetime
    target_language: str
    convenews_url: str
    about_url: str

@dataclass
class NewsletterArticle:
    title: str
    source: str
    published: str
    link: str
    article_summary: str
    relevance_score: float