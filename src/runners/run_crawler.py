"""
Entry point for the crawling pipeline.

This script loads the crawler configuration
file and executes the complete crawling pipeline.
"""

from src.config.config_loader import load_crawler_config
from src.config.config_loader import load_source_config
from src.services.crawler import rss_collector, content_extractor, extracted_articles_cleaner
from src.repositories.article_repository import ArticleRepository
from src.repositories.source_repository import SourceRepository


def main() -> None:
    crawler_config = load_crawler_config()
    source_config = load_source_config()

    article_repo = ArticleRepository(
        collected_articles_file=(
            crawler_config.collected_articles_file
        ),
        extracted_articles_file=(
            crawler_config.extracted_articles_file
        ),
    )
    source_repo = SourceRepository(
        sources_file=source_config.sources_file
    )

    prev_collected_articles = (
        article_repo.load_collected_articles()
    )

    feed_urls = [
        source.link
        for source in source_repo.load_sources()
    ]

    new_collected_articles = (
        rss_collector.collect_from_rss_feeds(
            existing_articles=prev_collected_articles,
            feed_urls=feed_urls,
            max_articles_per_feed=crawler_config.max_articles_per_feed,
            collection_window_days=crawler_config.collection_window_days,
        )
    )

    article_repo.save_collected_articles(
        new_collected_articles
    )

    prev_extracted_articles = article_repo.load_extracted_articles()

    expired_articles = extracted_articles_cleaner.get_expired_articles(
        prev_extracted_articles,
        crawler_config.extraction_retention_days)
    
    article_repo.remove_extracted_articles(
        expired_articles
    )

    expired_links = {
        article.link
        for article in expired_articles
    }

    current_extracted_articles = [
        article
        for article in prev_extracted_articles
        if article.link not in expired_links
    ]

    existing_links = {
        article.link
        for article in current_extracted_articles
    }

    articles_to_extract = [
        article
        for article in new_collected_articles
        if article.link not in existing_links
    ]

    new_extracted_articles = (
        content_extractor.extract_content_from_articles(
            articles_to_extract
        )
    )

    article_repo.append_extracted_articles(
        new_extracted_articles
    )


if __name__ == "__main__":
    main()