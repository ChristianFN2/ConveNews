from dataclasses import dataclass
from pathlib import Path


@dataclass
class CrawlerConfig:
    feed_urls_file: Path
    collected_articles_file: Path
    extracted_articles_file: Path
    max_articles_per_feed: int
    collection_window_days: int
    extraction_retention_days: int
    stats_file: Path
    state_file: Path