"""
Entry point for the crawling pipeline.

This script loads the crawler configuration from the default configuration
file and executes the complete crawling pipeline.
"""

from pathlib import Path

from src.config.config_loader import load_config
from src.services.crawler import rss_collector, content_extractor
from src.repositories.article_repository import ArticleRepository

DEFAULT_CONFIG_FILE = (
    Path(__file__).resolve().parents[2]
    / "config"
    / "pipeline.yaml"
)


def main() -> None:
    config = load_config(DEFAULT_CONFIG_FILE)

    repo = ArticleRepository(
        collected_articles_file=(
            config.crawler.collected_articles_file
        ),
        extracted_articles_file=(
            config.crawler.extracted_articles_file
        ),
    )

    existing_collected_articles = (
        repo.load_collected_articles()
    )

    collected_articles = (
        rss_collector.collect_from_rss_feeds(
            existing_collected_articles,
            config.crawler.feed_urls_file,
            config.crawler.max_articles_per_feed,
            config.crawler.collection_window_days,
        )
    )

    repo.save_collected_articles(
        collected_articles
    )

    extracted_articles = (
        content_extractor.extract_content_from_articles(
            collected_articles,
            config.crawler.stats_file,
            config.crawler.state_file,
            config.crawler.extraction_retention_days,
        )
    )

    repo.save_extracted_articles(
        extracted_articles
    )


if __name__ == "__main__":
    main()