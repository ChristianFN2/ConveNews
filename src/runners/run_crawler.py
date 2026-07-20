"""
Entry point for the crawling pipeline.

This script loads the crawler configuration
file and executes the complete crawling pipeline.
"""

from src.config.config_loader import load_crawler_config
from src.services.crawler import rss_collector, content_extractor
from src.repositories.article_repository import ArticleRepository


def main() -> None:
    config = load_crawler_config()

    repo = ArticleRepository(
        collected_articles_file=(
            config.collected_articles_file
        ),
        extracted_articles_file=(
            config.extracted_articles_file
        ),
    )

    existing_collected_articles = (
        repo.load_collected_articles()
    )

    collected_articles = (
        rss_collector.collect_from_rss_feeds(
            existing_collected_articles,
            config.feed_urls_file,
            config.max_articles_per_feed,
            config.collection_window_days,
        )
    )

    repo.save_collected_articles(
        collected_articles
    )

    extracted_articles = (
        content_extractor.extract_content_from_articles(
            collected_articles,
            config.stats_file,
            config.state_file,
            config.extraction_retention_days,
        )
    )

    repo.save_extracted_articles(
        extracted_articles
    )


if __name__ == "__main__":
    main()