from dataclasses import dataclass
from pathlib import Path

@dataclass
class NewsletterConfig:
    newsletter_profiles: Path
    relevance_threshold: float
    candidate_articles_file: Path
    evaluated_articles_file: Path
    newsletters_file: Path
    average_reading_speed_wpm: int

    newsletter_template: str
    article_template: str