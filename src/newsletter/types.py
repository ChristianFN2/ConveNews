from dataclasses import dataclass
from datetime import datetime

@dataclass
class NewsletterConfig:
    max_articles: int
    relevance_threshold: float

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